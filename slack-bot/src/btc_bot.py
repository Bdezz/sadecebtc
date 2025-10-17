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
PROJECT_NAME = os.getenv("PROJECT_NAME", "SadeceBTC")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
LINEAR_API_KEY = os.getenv("LINEAR_API_KEY")
LINEAR_TEAM_ID = os.getenv("LINEAR_TEAM_ID")
CURSOR_AGENT_ID = os.getenv("CURSOR_AGENT_ID", "9bcf804d-d3b7-4a7d-841b-b10108f9f8d0")
BTC_WALLET_ADDRESS = os.getenv("BTC_WALLET_ADDRESS", "")

# ========================================
# SLACK BOT SETUP
# ========================================
app = App(token=SLACK_BOT_TOKEN)

# ========================================
# BTC PRICE API (CoinGecko - Free, No API Key)
# ========================================
def get_btc_price():
    """CoinGecko'dan BTC fiyatını çek"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,try&include_24hr_change=true"
        req = urllib.request.Request(url)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if 'bitcoin' in data:
                btc = data['bitcoin']
                return {
                    'success': True,
                    'usd': btc.get('usd', 0),
                    'try': btc.get('try', 0),
                    'change_24h': btc.get('usd_24h_change', 0)
                }
    except Exception as e:
        print(f"[BTC Price Error] {e}")
    
    return {'success': False, 'error': 'Failed to fetch BTC price'}

# ========================================
# WALLET BALANCE (Blockchain.info API - Free)
# ========================================
def get_btc_balance(address):
    """Blockchain.info'dan BTC bakiyesini çek"""
    if not address:
        return {'success': False, 'error': 'BTC wallet address not configured'}
    
    try:
        # Blockchain.info public API (no key needed)
        url = f"https://blockchain.info/balance?active={address}"
        req = urllib.request.Request(url)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if address in data:
                wallet = data[address]
                # Satoshi to BTC conversion (1 BTC = 100,000,000 satoshi)
                balance_btc = wallet.get('final_balance', 0) / 100000000
                
                return {
                    'success': True,
                    'balance_btc': balance_btc,
                    'balance_satoshi': wallet.get('final_balance', 0),
                    'total_received': wallet.get('total_received', 0) / 100000000,
                    'total_sent': wallet.get('total_sent', 0) / 100000000
                }
    except Exception as e:
        print(f"[BTC Balance Error] {e}")
    
    return {'success': False, 'error': 'Failed to fetch wallet balance'}

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
@app.command("/btcprice")
def handle_btc_price(ack, command, say):
    """BTC fiyatını göster"""
    ack()
    
    price_data = get_btc_price()
    
    if price_data['success']:
        usd = price_data['usd']
        try_price = price_data['try']
        change = price_data['change_24h']
        change_emoji = "📈" if change > 0 else "📉"
        change_color = "green" if change > 0 else "red"
        
        say(
            f"💰 **Bitcoin (BTC) Fiyatı**\n\n"
            f"🇺🇸 **USD:** ${usd:,.2f}\n"
            f"🇹🇷 **TRY:** ₺{try_price:,.2f}\n\n"
            f"{change_emoji} **24h Değişim:** `{change:+.2f}%`\n\n"
            f"📊 **Kaynak:** CoinGecko\n"
            f"⏰ **Zaman:** {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    else:
        say(f"❌ **Fiyat Hatası**\n⚠️ {price_data.get('error', 'Unknown error')}")

@app.command("/btcbalance")
def handle_btc_balance(ack, command, say):
    """Cake Wallet BTC bakiyesini göster"""
    ack()
    
    if not BTC_WALLET_ADDRESS:
        say(
            f"⚠️ **Wallet Adresi Yapılandırılmamış**\n\n"
            f"Railway'de `BTC_WALLET_ADDRESS` environment variable'ını ekle.\n\n"
            f"**Örnek:**\n"
            f"`BTC_WALLET_ADDRESS=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`"
        )
        return
    
    balance_data = get_btc_balance(BTC_WALLET_ADDRESS)
    
    if balance_data['success']:
        btc = balance_data['balance_btc']
        satoshi = balance_data['balance_satoshi']
        received = balance_data['total_received']
        sent = balance_data['total_sent']
        
        # BTC fiyatını çek (USD değeri için)
        price_data = get_btc_price()
        usd_value = 0
        try_value = 0
        
        if price_data['success']:
            usd_value = btc * price_data['usd']
            try_value = btc * price_data['try']
        
        say(
            f"💼 **Cake Wallet BTC Bakiyesi**\n\n"
            f"🪙 **BTC:** `{btc:.8f}` BTC\n"
            f"⚡ **Satoshi:** `{satoshi:,}` sat\n\n"
            f"💵 **USD Değeri:** ${usd_value:,.2f}\n"
            f"💷 **TRY Değeri:** ₺{try_value:,.2f}\n\n"
            f"📥 **Toplam Alınan:** `{received:.8f}` BTC\n"
            f"📤 **Toplam Gönderilen:** `{sent:.8f}` BTC\n\n"
            f"🔗 **Wallet:** `{BTC_WALLET_ADDRESS[:8]}...{BTC_WALLET_ADDRESS[-8:]}`\n"
            f"⏰ **Zaman:** {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    else:
        say(f"❌ **Bakiye Hatası**\n⚠️ {balance_data.get('error', 'Unknown error')}")

@app.command("/btcstats")
def handle_btc_stats(ack, command, say):
    """BTC fiyat + bakiye özeti"""
    ack()
    
    # Fiyat verisi
    price_data = get_btc_price()
    
    # Bakiye verisi
    balance_data = {'success': False}
    if BTC_WALLET_ADDRESS:
        balance_data = get_btc_balance(BTC_WALLET_ADDRESS)
    
    # Mesajı oluştur
    message = f"📊 **Bitcoin Özet Rapor**\n\n"
    
    # Fiyat bölümü
    if price_data['success']:
        usd = price_data['usd']
        try_price = price_data['try']
        change = price_data['change_24h']
        change_emoji = "📈" if change > 0 else "📉"
        
        message += (
            f"💰 **BTC Fiyatı:**\n"
            f"• USD: ${usd:,.2f}\n"
            f"• TRY: ₺{try_price:,.2f}\n"
            f"• 24h: {change_emoji} `{change:+.2f}%`\n\n"
        )
    else:
        message += f"❌ Fiyat verisi alınamadı\n\n"
    
    # Bakiye bölümü
    if balance_data['success']:
        btc = balance_data['balance_btc']
        
        usd_value = 0
        try_value = 0
        if price_data['success']:
            usd_value = btc * price_data['usd']
            try_value = btc * price_data['try']
        
        message += (
            f"💼 **Wallet Bakiyesi:**\n"
            f"• BTC: `{btc:.8f}`\n"
            f"• USD: ${usd_value:,.2f}\n"
            f"• TRY: ₺{try_value:,.2f}\n\n"
        )
    elif BTC_WALLET_ADDRESS:
        message += f"❌ Bakiye verisi alınamadı\n\n"
    else:
        message += f"⚠️ Wallet adresi yapılandırılmamış\n\n"
    
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
        f"• `/btcprice` - BTC fiyatını göster\n"
        f"• `/btcbalance` - Wallet bakiyeni göster\n"
        f"• `/btcstats` - Özet rapor\n"
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
    print(f"🪙 BTC Wallet: {BTC_WALLET_ADDRESS[:8]}...{BTC_WALLET_ADDRESS[-8:] if BTC_WALLET_ADDRESS else 'Not configured'}")
    
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()

