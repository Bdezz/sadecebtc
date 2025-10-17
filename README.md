# 🔒 SadeceXMR - Monero Price & Balance Tracker

**Privacy-focused cryptocurrency tracking bot for Monero (XMR)**

---

## 🎯 Features

- 💰 **Real-time XMR Price** (USD, TRY, USDT)
- 💼 **Feather Wallet Balance** (Read-only with view key)
- 📊 **Quick Stats** (Price + Balance overview)
- 🔗 **Linear Integration** (Issue tracking with auto-assignment)
- 🤖 **Background Agent** (Automated task management)

---

## 🚀 Quick Setup

### 1️⃣ **GitHub Repository**
```bash
git clone https://github.com/yourusername/sadecebtc.git
cd sadecebtc
```

### 2️⃣ **Slack App Setup**
1. Go to https://api.slack.com/apps
2. **Create New App** → From scratch
3. **App Name:** `SadeceXMR` | **Workspace:** Your workspace
4. **Socket Mode:** Enable ✅
5. **Bot Token Scopes:**
   - `chat:write`
   - `commands`
   - `app_mentions:read`
   - `channels:read`
   - `groups:read`
6. **Slash Commands:** Create:
   - `/xmrprice` - Show XMR price
   - `/xmrbalance` - Show wallet balance
   - `/xmrstats` - Quick stats
   - `/task` - Create task
   - `/feature` - Feature request
   - `/bug` - Bug report
7. **Install App to Workspace**
8. **Copy Tokens:**
   - Bot Token: `xoxb-...`
   - App Token: `xapp-...`
   - Signing Secret: Settings → Basic Information

### 3️⃣ **Feather Wallet Keys**
1. Open Feather Wallet
2. **Wallet → Keys**
3. Copy:
   - **Primary Address** (48...)
   - **Private View Key** (abc123...)

**Security:** View key is READ-ONLY (cannot spend funds)

### 4️⃣ **Railway Deployment**
1. Go to https://railway.app
2. **New Project** → **Deploy from GitHub**
3. Select `sadecebtc` repository
4. **Settings:**
   - **Root Directory:** `slack-bot`
   - **Start Command:** `python -u src/xmr_bot.py`
5. **Add Environment Variables:**

```env
PROJECT_NAME=SadeceXMR
SLACK_BOT_TOKEN=xoxb-9679972569621-...
SLACK_APP_TOKEN=xapp-1-A09MBF2BZT2-...
SLACK_SIGNING_SECRET=bbf353c15108569...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
LINEAR_API_KEY=lin_api_...
LINEAR_TEAM_ID=bce9aea6-3e82-4bfa-9234-f474bcbecc75
CURSOR_AGENT_ID=9bcf804d-d3b7-4a7d-841b-b10108f9f8d0
XMR_ADDRESS=48...
XMR_VIEW_KEY=abc123...
PORT=8080
```

6. **Deploy!** 🚀

---

## 📱 Slack Commands

| Command | Description |
|---------|-------------|
| `/xmrprice` | Show XMR price (USD/TRY/USDT) |
| `/xmrbalance` | Show Feather Wallet balance |
| `/xmrstats` | Quick overview (price + balance) |
| `/task <description>` | Create a task in Linear |
| `/feature <description>` | Request a new feature |
| `/bug <description>` | Report a bug |

---

## 🔐 Security

- ✅ **View Key:** Read-only access (cannot spend funds)
- ✅ **Private Key:** NEVER shared or stored
- ✅ **Monero Privacy:** Transactions are private by default
- ⚠️ **Balance Visibility:** Anyone with view key can see balance

**NEVER share your Private Spend Key!**

---

## 🛠️ Tech Stack

- **Language:** Python 3.11
- **Framework:** Slack Bolt SDK
- **APIs:**
  - CoinGecko (Price data)
  - XMRChain.net (Wallet balance)
- **Deployment:** Railway.app
- **Project Management:** Linear

---

## 📊 Example Output

### `/xmrprice`
```
💰 Monero (XMR) Fiyatı

🇺🇸 USD: $157.32
💵 USDT: $157.28
🇹🇷 TRY: ₺5,342.89

📈 24h Değişim: +2.45%

📊 Kaynak: CoinGecko
⏰ Zaman: 2025-10-17 19:44:23
```

### `/xmrbalance`
```
💼 Feather Wallet XMR Bakiyesi

🪙 XMR: 1.234567890123 XMR

💵 USD Değeri: $194.12
💵 USDT Değeri: $194.08
💷 TRY Değeri: ₺6,593.41

📥 Toplam Alınan: 2.500000000000 XMR
📤 Toplam Gönderilen: 1.265432109877 XMR

🔗 Wallet: 48abcdef...xyz12345
⏰ Zaman: 2025-10-17 19:45:10
```

---

## 🎯 Roadmap

- [ ] Multiple wallet support
- [ ] Price alerts
- [ ] Transaction history
- [ ] Portfolio tracking
- [ ] Other privacy coins (ZEC, DASH)

---

## 📝 License

MIT License - see LICENSE file

---

## 👤 Author

Built with ❤️ for privacy-conscious crypto enthusiasts

---

## 🆘 Support

Issues: Create a Linear issue via `/bug` command  
Feature Requests: Use `/feature` command in Slack
