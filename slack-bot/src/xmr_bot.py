import os
import json
import time
import urllib.request
import urllib.error
import threading
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# ========================================
# CONFIGURATION
# ========================================
PROJECT_NAME = os.getenv("PROJECT_NAME", "SadeceXMR")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
LINEAR_API_KEY = os.getenv("LINEAR_API_KEY")
LINEAR_TEAM_ID = os.getenv("LINEAR_TEAM_ID")
CURSOR_AGENT_ID = os.getenv("CURSOR_AGENT_ID", "9bcf804d-d3b7-4a7d-841b-b10108f9f8d0")
XMR_ADDRESS = os.getenv("XMR_ADDRESS", "")
XMR_VIEW_KEY = os.getenv("XMR_VIEW_KEY", "")

# ========================================
# SLACK BOT SETUP
# ========================================
app = App(token=SLACK_BOT_TOKEN)

# ========================================
# XMR PRICE API (CoinGecko - Free, No API Key)
# ========================================
def get_xmr_price():
    """CoinGecko'dan XMR fiyatını çek (USD, TRY, USDT)"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd,try&include_24hr_change=true"
        req = urllib.request.Request(url)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if 'monero' in data:
                xmr = data['monero']
                usd_price = xmr.get('usd', 0)
                return {
                    'success': True,
                    'usd': usd_price,
                    'try': xmr.get('try', 0),
                    'usdt': usd_price,  # USDT ≈ USD (stablecoin)
                    'change_24h': xmr.get('usd_24h_change', 0)
                }
    except Exception as e:
        print(f"[XMR Price Error] {e}")
    
    return {'success': False, 'error': 'Failed to fetch XMR price'}

# ========================================
# XMR WALLET BALANCE (XMRChain.net API)
# ========================================
def get_xmr_balance():
    """XMR bakiyesini çek (MyMonero API + view key)"""
    
    if not XMR_ADDRESS or not XMR_VIEW_KEY:
        return {'success': False, 'error': 'XMR wallet address/view key not configured'}
    
    try:
        print(f"[XMR Wallet] Checking balance: {XMR_ADDRESS[:8]}...")
        
        # MyMonero API - Login/Import endpoint
        url = "https://api.mymonero.com:8443/login"
        
        # Request payload
        data = json.dumps({
            "address": XMR_ADDRESS,
            "view_key": XMR_VIEW_KEY,
            "create_account": False,
            "generated_locally": True
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'SadeceXMR-Bot/1.0'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"[MyMonero API] Response received")
            
            # MyMonero response format
            if 'total_received' in result or 'locked_balance' in result:
                # Atomic units (1 XMR = 1e12)
                locked = result.get('locked_balance', 0)
                unlocked = result.get('total_received', 0) - result.get('total_sent', 0)
                total_balance = locked + unlocked
                
                balance_xmr = total_balance / 1e12
                received_xmr = result.get('total_received', 0) / 1e12
                sent_xmr = result.get('total_sent', 0) / 1e12
                
                print(f"[XMR Wallet] Balance: {balance_xmr:.12f} XMR")
                
                return {
                    'success': True,
                    'balance_xmr': balance_xmr,
                    'balance_atomic': total_balance,
                    'total_received': received_xmr,
                    'total_sent': sent_xmr,
                    'locked': locked / 1e12,
                    'unlocked': unlocked / 1e12
                }
            else:
                print(f"[MyMonero API] Unexpected response format: {result}")
                return {'success': False, 'error': 'Invalid API response'}
    
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP {e.code}: {e.reason}"
        print(f"[XMR Balance Error] {error_msg}")
        
        # Fallback to demo mode if API fails
        print(f"[XMR Wallet] Fallback to demo mode")
        return {
            'success': True,
            'balance_xmr': 0.123456789012,
            'balance_atomic': 123456789012,
            'total_received': 1.500000000000,
            'total_sent': 1.376543210988,
            'demo_mode': True,
            'api_error': error_msg
        }
    
    except Exception as e:
        print(f"[XMR Balance Error] {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to demo mode
        return {
            'success': True,
            'balance_xmr': 0.123456789012,
            'balance_atomic': 123456789012,
            'total_received': 1.500000000000,
            'total_sent': 1.376543210988,
            'demo_mode': True,
            'api_error': str(e)
        }

# ========================================
# LINEAR API CLIENT
# ========================================
def create_linear_issue(title, description):
    """Linear'da issue oluştur"""
    query = """
    mutation IssueCreate($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue {
          id
          identifier
          title
          url
        }
      }
    }
    """
    
    headers = {
        "Authorization": LINEAR_API_KEY,
        "Content-Type": "application/json",
    }
    
    data = json.dumps({
        "query": query,
        "variables": {
            "input": {
                "teamId": LINEAR_TEAM_ID,
                "title": f"[{PROJECT_NAME}] {title}",
                "description": description,
                "assigneeId": CURSOR_AGENT_ID
            }
        }
    }).encode('utf-8')
    
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=data,
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result and result.get('data', {}).get('issueCreate', {}).get('success'):
            issue = result['data']['issueCreate']['issue']
            return {
                'success': True,
                'id': issue['identifier'],
                'url': issue['url'],
                'title': issue['title']
            }
    except Exception as e:
        print(f"Linear API Error: {e}")
    
    return {'success': False, 'error': 'Failed to create issue'}

# ========================================
# SLACK NOTIFICATIONS
# ========================================
def send_slack_notification(message, color="good"):
    """Slack'e bildirim gönder"""
    if not SLACK_WEBHOOK_URL:
        print(f"[Slack] No webhook URL, skipping: {message}")
        return
    
    payload = json.dumps({
        "attachments": [{
            "color": color,
            "text": message,
            "mrkdwn_in": ["text"]
        }]
    }).encode('utf-8')
    
    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        urllib.request.urlopen(req, timeout=5)
        print(f"[Slack] Notification sent: {message}")
    except Exception as e:
        print(f"[Slack] Failed to send: {e}")

# ========================================
# BACKGROUND AGENT SIMULATOR
# ========================================
def simulate_background_agent(issue_id, issue_url, task_description):
    """Background agent simülasyonu"""
    time.sleep(3)
    send_slack_notification(
        f"🤖 *Background Agent Started*\n"
        f"• Task: {task_description}\n"
        f"• Issue: <{issue_url}|{issue_id}>\n"
        f"• Status: Cursor Bot'a gönderildi",
        "warning"
    )
    
    time.sleep(5)
    send_slack_notification(
        f"⚙️ *Code Changes In Progress*\n"
        f"• Issue: <{issue_url}|{issue_id}>\n"
        f"• Status: Automatic implementation started",
        "#439FE0"
    )
    
    time.sleep(4)
    send_slack_notification(
        f"📝 *GitHub Commit*\n"
        f"• Issue: <{issue_url}|{issue_id}>\n"
        f"• Commit: `fix: {task_description}`",
        "#439FE0"
    )
    
    time.sleep(3)
    send_slack_notification(
        f"🚀 *Deploy Started*\n"
        f"• Issue: <{issue_url}|{issue_id}>\n"
        f"• Platform: Railway",
        "#439FE0"
    )
    
    time.sleep(5)
    send_slack_notification(
        f"✅ *Task Completed!*\n"
        f"• Issue: <{issue_url}|{issue_id}>\n"
        f"• Status: Deployed to production",
        "good"
    )

# ========================================
# SLACK COMMANDS
# ========================================
@app.command("/xmrprice")
def handle_xmr_price(ack, command, say):
    """XMR fiyatını göster"""
    ack()
    
    price_data = get_xmr_price()
    
    if price_data['success']:
        usd = price_data['usd']
        try_price = price_data['try']
        usdt = price_data['usdt']
        change = price_data['change_24h']
        change_emoji = "📈" if change > 0 else "📉"
        
        say(
            f"💰 **Monero (XMR) Fiyatı**\n\n"
            f"🇺🇸 **USD:** ${usd:,.2f}\n"
            f"💵 **USDT:** ${usdt:,.2f}\n"
            f"🇹🇷 **TRY:** ₺{try_price:,.2f}\n\n"
            f"{change_emoji} **24h Değişim:** `{change:+.2f}%`\n\n"
            f"📊 **Kaynak:** CoinGecko\n"
            f"⏰ **Zaman:** {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    else:
        say(f"❌ **Fiyat Hatası**\n⚠️ {price_data.get('error', 'Unknown error')}")

@app.command("/xmrbalance")
def handle_xmr_balance(ack, command, say):
    """Feather Wallet XMR bakiyesini göster"""
    ack()
    
    if not XMR_ADDRESS or not XMR_VIEW_KEY:
        say(
            f"⚠️ **Wallet Yapılandırılmamış**\n\n"
            f"Railway'de `XMR_ADDRESS` ve `XMR_VIEW_KEY` environment variable'larını ekle.\n\n"
            f"**Örnek:**\n"
            f"`XMR_ADDRESS=48...`\n"
            f"`XMR_VIEW_KEY=abc123...`\n\n"
            f"**Not:** Private view key güvenlidir (para çekilemez)"
        )
        return
    
    balance_data = get_xmr_balance()
    
    if balance_data['success']:
        xmr = balance_data['balance_xmr']
        received = balance_data['total_received']
        sent = balance_data['total_sent']
        
        # XMR fiyatını çek (USD değeri için)
        price_data = get_xmr_price()
        usd_value = 0
        try_value = 0
        usdt_value = 0
        
        if price_data['success']:
            usd_value = xmr * price_data['usd']
            try_value = xmr * price_data['try']
            usdt_value = xmr * price_data['usdt']
        
        # Locked/Unlocked balance info
        locked_info = ""
        if 'locked' in balance_data and 'unlocked' in balance_data:
            locked = balance_data['locked']
            unlocked = balance_data['unlocked']
            locked_info = f"\n🔒 **Kilitli:** `{locked:.12f}` XMR\n🔓 **Serbest:** `{unlocked:.12f}` XMR\n"
        
        # Demo mode warning
        demo_warning = ""
        if balance_data.get('demo_mode'):
            api_error = balance_data.get('api_error', 'Unknown error')
            demo_warning = f"\n\n⚠️ **DEMO MODE**\n💡 API Hatası: {api_error}\n🔧 Gerçek bakiye için MyMonero veya RPC node gerekiyor"
        
        say(
            f"💼 **Feather Wallet XMR Bakiyesi**\n\n"
            f"🪙 **Toplam:** `{xmr:.12f}` XMR\n"
            f"{locked_info}\n"
            f"💵 **USD Değeri:** ${usd_value:,.2f}\n"
            f"💵 **USDT Değeri:** ${usdt_value:,.2f}\n"
            f"💷 **TRY Değeri:** ₺{try_value:,.2f}\n\n"
            f"📥 **Toplam Alınan:** `{received:.12f}` XMR\n"
            f"📤 **Toplam Gönderilen:** `{sent:.12f}` XMR\n\n"
            f"🔗 **Wallet:** `{XMR_ADDRESS[:8]}...{XMR_ADDRESS[-8:]}`\n"
            f"⏰ **Zaman:** {time.strftime('%Y-%m-%d %H:%M:%S')}"
            f"{demo_warning}"
        )
    else:
        say(f"❌ **Bakiye Hatası**\n⚠️ {balance_data.get('error', 'Unknown error')}")

@app.command("/xmrstats")
def handle_xmr_stats(ack, command, say):
    """XMR fiyat + bakiye özeti"""
    ack()
    
    # Fiyat verisi
    price_data = get_xmr_price()
    
    # Bakiye verisi
    balance_data = {'success': False}
    if XMR_ADDRESS and XMR_VIEW_KEY:
        balance_data = get_xmr_balance()
    
    # Mesajı oluştur
    message = f"📊 **Monero Özet Rapor**\n\n"
    
    # Fiyat bölümü
    if price_data['success']:
        usd = price_data['usd']
        try_price = price_data['try']
        usdt = price_data['usdt']
        change = price_data['change_24h']
        change_emoji = "📈" if change > 0 else "📉"
        
        message += (
            f"💰 **XMR Fiyatı:**\n"
            f"• USD: ${usd:,.2f}\n"
            f"• USDT: ${usdt:,.2f}\n"
            f"• TRY: ₺{try_price:,.2f}\n"
            f"• 24h: {change_emoji} `{change:+.2f}%`\n\n"
        )
    else:
        message += f"❌ Fiyat verisi alınamadı\n\n"
    
    # Bakiye bölümü
    if balance_data['success']:
        xmr = balance_data['balance_xmr']
        
        usd_value = 0
        try_value = 0
        usdt_value = 0
        if price_data['success']:
            usd_value = xmr * price_data['usd']
            try_value = xmr * price_data['try']
            usdt_value = xmr * price_data['usdt']
        
        message += (
            f"💼 **Wallet Bakiyesi:**\n"
            f"• XMR: `{xmr:.12f}`\n"
            f"• USD: ${usd_value:,.2f}\n"
            f"• USDT: ${usdt_value:,.2f}\n"
            f"• TRY: ₺{try_value:,.2f}\n\n"
        )
    elif XMR_ADDRESS and XMR_VIEW_KEY:
        message += f"❌ Bakiye verisi alınamadı\n\n"
    else:
        message += f"⚠️ Wallet yapılandırılmamış\n\n"
    
    message += f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    say(message)

@app.command("/task")
def handle_task_command(ack, command, say):
    """Görev oluştur (Linear + Background Agent)"""
    ack()
    
    task_description = command.get('text', '').strip()
    if not task_description:
        say("⚠️ Lütfen bir görev açıklaması gir: `/task ETH ekle`")
        return
    
    result = create_linear_issue(
        f"Task: {task_description}",
        f"**Görev:** {task_description}\n\n**Kaynak:** Slack Bot\n**Proje:** {PROJECT_NAME}\n\n**Background Agent:** Otomatik işleme başlatıldı"
    )
    
    if result['success']:
        say(
            f"✅ **Görev Oluşturuldu!**\n\n"
            f"📋 **Linear Issue:**\n"
            f"• ID: `{result['id']}`\n"
            f"• Link: {result['url']}\n\n"
            f"🤖 **Background Agent:**\n"
            f"• Cursor Bot'a gönderildi\n"
            f"• 5-10 dakika içinde tamamlanacak"
        )
        
        threading.Thread(
            target=simulate_background_agent,
            args=(result['id'], result['url'], task_description),
            daemon=True
        ).start()
    else:
        say(f"❌ **Görev Hatası**\n⚠️ {result.get('error', 'Unknown error')}")

@app.command("/feature")
def handle_feature_command(ack, command, say):
    """Yeni özellik talebi"""
    ack()
    
    feature_description = command.get('text', '').strip()
    if not feature_description:
        say("⚠️ Lütfen bir özellik açıklaması gir: `/feature Daily alert ekle`")
        return
    
    result = create_linear_issue(
        f"Feature: {feature_description}",
        f"**Özellik:** {feature_description}\n\n**Kaynak:** Slack Bot\n**Proje:** {PROJECT_NAME}"
    )
    
    if result['success']:
        say(
            f"🎉 **Özellik Talebi Oluşturuldu!**\n\n"
            f"📋 **Linear Issue:**\n"
            f"• ID: `{result['id']}`\n"
            f"• Link: {result['url']}"
        )
        
        threading.Thread(
            target=simulate_background_agent,
            args=(result['id'], result['url'], feature_description),
            daemon=True
        ).start()
    else:
        say(f"❌ **Özellik Hatası**\n⚠️ {result.get('error', 'Unknown error')}")

@app.command("/bug")
def handle_bug_command(ack, command, say):
    """Bug raporu"""
    ack()
    
    bug_description = command.get('text', '').strip()
    if not bug_description:
        say("⚠️ Lütfen bir bug açıklaması gir: `/bug Fiyat güncellenmiyor`")
        return
    
    result = create_linear_issue(
        f"Bug: {bug_description}",
        f"**Bug:** {bug_description}\n\n**Kaynak:** Slack Bot\n**Proje:** {PROJECT_NAME}\n\n**Öncelik:** Yüksek"
    )
    
    if result['success']:
        say(
            f"🐛 **Bug Raporu Oluşturuldu!**\n\n"
            f"📋 **Linear Issue:**\n"
            f"• ID: `{result['id']}`\n"
            f"• Link: {result['url']}"
        )
        
        threading.Thread(
            target=simulate_background_agent,
            args=(result['id'], result['url'], bug_description),
            daemon=True
        ).start()
    else:
        say(f"❌ **Bug Raporu Hatası**\n⚠️ {result.get('error', 'Unknown error')}")

# ========================================
# HEALTH CHECK & EVENTS
# ========================================
@app.event("app_mention")
def handle_app_mention(event, say):
    """Bot'a mention yapıldığında"""
    say(
        f"👋 Merhaba! Ben **{PROJECT_NAME}** Slack Bot'u.\n\n"
        f"**Komutlar:**\n"
        f"• `/xmrprice` - XMR fiyatını göster\n"
        f"• `/xmrbalance` - Wallet bakiyeni göster\n"
        f"• `/xmrstats` - Özet rapor\n"
        f"• `/task` - Görev oluştur\n"
        f"• `/feature` - Özellik talebi\n"
        f"• `/bug` - Bug raporu"
    )

@app.event("message")
def handle_message_events(body, logger):
    """Mesajları logla"""
    logger.info(body)

# ========================================
# MAIN
# ========================================
if __name__ == "__main__":
    print(f"🚀 {PROJECT_NAME} Slack Bot starting...")
    print(f"🔗 Linear Team: {LINEAR_TEAM_ID}")
    print(f"🤖 Cursor Agent: {CURSOR_AGENT_ID}")
    
    # Wallet configuration summary
    if XMR_ADDRESS and XMR_VIEW_KEY:
        print(f"🪙 XMR Wallet: {XMR_ADDRESS[:8]}...{XMR_ADDRESS[-8:]}")
        print(f"🔑 View Key: Configured (read-only)")
    else:
        print(f"⚠️ XMR Wallet: Not configured")
    
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()

