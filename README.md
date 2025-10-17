# 💰 SadeceBTC - Bitcoin Tracker Slack Bot

**Anlık BTC fiyatı + Cake Wallet bakiyesi** takip sistemi.

---

## 🎯 Özellikler

### **Slack Komutları:**
- `/btcprice` → Anlık BTC fiyatını göster (USD + TRY)
- `/btcbalance` → Cake Wallet BTC bakiyeni göster
- `/btcstats` → Hem fiyat hem bakiye (özet rapor)
- `/task` → Görev oluştur (Linear + Background Agent)
- `/feature` → Yeni özellik talebi
- `/bug` → Bug raporu

### **Entegrasyonlar:**
- ✅ **Slack Bot** (real-time komutlar)
- ✅ **CoinGecko API** (ücretsiz BTC fiyat verisi)
- ✅ **Blockchain.info API** (wallet bakiye sorgulama)
- ✅ **Linear** (issue tracking + Cursor assign)
- ✅ **Background Agent** (otomatik Slack bildirimleri)
- ✅ **Railway** (auto deploy)

---

## 🚀 Hızlı Başlangıç

### **1. GitHub Repo Oluştur**
```bash
# GitHub'da yeni repo: https://github.com/capulunn/sadecebtc
git init
git add .
git commit -m "Initial commit: SadeceBTC"
git branch -M main
git remote add origin https://github.com/capulunn/sadecebtc.git
git push -u origin main
```

### **2. Slack App Setup**

#### **Slash Commands Ekle:**
1. https://api.slack.com/apps → **Your App**
2. **Slash Commands** → **Create New Command**:
   - `/btcprice` → Description: "Get current BTC price"
   - `/btcbalance` → Description: "Check wallet balance"
   - `/btcstats` → Description: "BTC summary report"
   - `/task` → Description: "Create a task"
   - `/feature` → Description: "Request feature"
   - `/bug` → Description: "Report bug"

#### **Bot Token Scopes:**
- `chat:write`
- `commands`
- `app_mentions:read`

#### **Event Subscriptions:**
- Enable Events
- Subscribe to: `app_mention`, `message.channels`

#### **Incoming Webhooks:**
- Enable Incoming Webhooks
- Add New Webhook to Workspace → Copy URL

### **3. Railway Deployment**

#### **Create New Project:**
1. **Railway** → **New Project** → **Deploy from GitHub repo**
2. **Select Repo:** `capulunn/sadecebtc`
3. **Service Name:** `sadecebtc-bot`
4. **Root Directory:** `/slack-bot`

#### **Add Environment Variables:**
```bash
# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_SIGNING_SECRET=...

# Linear
LINEAR_API_KEY=lin_api_...
LINEAR_TEAM_ID=bce9aea6-3e82-4bfa-9234-f474bcbecc75
CURSOR_AGENT_ID=9bcf804d-d3b7-4a7d-841b-b10108f9f8d0

# BTC Data
BTC_WALLET_ADDRESS=your-btc-wallet-address

# Deployment
PORT=8080
PROJECT_NAME=SadeceBTC
```

#### **Deploy:**
- Railway otomatik deploy başlatır
- Health check: Logs'da "SadeceBTC Slack Bot starting..." göreceksin

### **4. Test Et**

Slack'te:
```
/btcprice          → BTC fiyatını göster
/btcbalance        → Wallet bakiyeni göster
/btcstats          → Özet rapor
/task ETH ekle     → Görev oluştur (Linear + Background Agent)
```

---

## 🔑 API Keys Nereden Alınır?

### **1. Slack:**
- https://api.slack.com/apps → **Your App** → **OAuth & Permissions**
  - `SLACK_BOT_TOKEN` (xoxb-...)
- **Basic Information** → **App-Level Tokens**
  - `SLACK_APP_TOKEN` (xapp-...)
- **Incoming Webhooks** → **Webhook URL**
  - `SLACK_WEBHOOK_URL`

### **2. Linear:**
- https://linear.app/cokoloko/settings/api
  - `LINEAR_API_KEY` (lin_api_...)
- **Team ID:** Zaten var (`bce9aea6-3e82-4bfa-9234-f474bcbecc75`)
- **Cursor Agent ID:** Zaten var (`9bcf804d-d3b7-4a7d-841b-b10108f9f8d0`)

### **3. BTC Wallet Address:**
- **Cake Wallet** → **Receive** → **Copy Bitcoin Address**
- Örnek: `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`

### **4. CoinGecko (Opsiyonel):**
- Ücretsiz API (günde 50 call limit)
- API key gerekmez (public endpoint kullanıyoruz)

---

## 📊 Kullanım Örnekleri

### **BTC Fiyat Sorgula:**
```
/btcprice
```
**Yanıt:**
```
💰 Bitcoin (BTC) Fiyatı

🇺🇸 USD: $43,250.00
🇹🇷 TRY: ₺1,298,750.00

📈 24h Değişim: +2.45%

📊 Kaynak: CoinGecko
⏰ Zaman: 2025-10-17 22:15:30
```

### **Wallet Bakiye Sorgula:**
```
/btcbalance
```
**Yanıt:**
```
💼 Cake Wallet BTC Bakiyesi

🪙 BTC: 0.05234000 BTC
⚡ Satoshi: 5,234,000 sat

💵 USD Değeri: $2,264.15
💷 TRY Değeri: ₺67,924.50

📥 Toplam Alınan: 0.10000000 BTC
📤 Toplam Gönderilen: 0.04766000 BTC

🔗 Wallet: 1A1zP1eP...v7DivfNa
⏰ Zaman: 2025-10-17 22:15:30
```

### **Özet Rapor:**
```
/btcstats
```
**Yanıt:**
```
📊 Bitcoin Özet Rapor

💰 BTC Fiyatı:
• USD: $43,250.00
• TRY: ₺1,298,750.00
• 24h: 📈 +2.45%

💼 Wallet Bakiyesi:
• BTC: 0.05234000
• USD: $2,264.15
• TRY: ₺67,924.50

⏰ 2025-10-17 22:15:30
```

### **Görev Oluştur:**
```
/task ETH ekle
```
**Yanıt:**
```
✅ Görev Oluşturuldu!

📋 Linear Issue:
• ID: COK-11
• Link: https://linear.app/cokoloko/issue/COK-11/...

🤖 Background Agent:
• Cursor Bot'a gönderildi
• 5-10 dakika içinde tamamlanacak
```

**(Slack'te background agent progress bildirimleri gelir)**

---

## 🏗️ Proje Yapısı

```
sadecebtc/
├── slack-bot/
│   ├── src/
│   │   └── btc_bot.py          # Ana Slack bot
│   ├── Dockerfile               # Docker image
│   ├── requirements.txt         # Python dependencies
│   └── env.example              # Environment variables template
└── README.md                    # Bu dosya
```

---

## 🔧 Özelleştirme

### **Farklı Coinler Eklemek İçin:**

`btc_bot.py` dosyasında:
```python
# ETH eklemek için
@app.command("/ethprice")
def handle_eth_price(ack, command, say):
    # CoinGecko API: ethereum
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd,try"
    # ... rest of the code
```

### **Farklı Wallet Servisleri:**

```python
# Cake Wallet yerine farklı bir servis kullanmak için
# get_btc_balance() fonksiyonunu düzenle
```

---

## 🎯 Roadmap

- ✅ BTC fiyat tracking
- ✅ Wallet bakiye sorgulama
- ✅ Slack entegrasyonu
- ✅ Linear + Background Agent
- ⏳ ETH + BNB + XMR ekleme
- ⏳ Daily price alerts
- ⏳ Price threshold notifications
- ⏳ Portfolio tracking (multiple wallets)

---

## 🐛 Troubleshooting

### **"Wallet adresi yapılandırılmamış" Hatası:**
```bash
# Railway'de BTC_WALLET_ADDRESS ekle:
BTC_WALLET_ADDRESS=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

### **"Fiyat verisi alınamadı" Hatası:**
- CoinGecko API rate limit aşılmış olabilir (günde 50 call)
- Birkaç dakika bekle ve tekrar dene

### **"Bakiye verisi alınamadı" Hatası:**
- Blockchain.info API geçici olarak down olabilir
- Wallet adresi yanlış girilmiş olabilir (kontrol et)

---

## 📄 License

MIT License - istediğin gibi kullanabilirsin!

---

## 🤝 Contributing

Pull request'ler hoş geldin! Özellik ekleme veya bug fix için:
1. Fork et
2. Feature branch oluştur
3. Commit yap
4. Pull request gönder

---

## 💬 Support

Sorular için:
- **Slack:** @capul
- **Linear:** https://linear.app/cokoloko
- **GitHub Issues:** https://github.com/capulunn/sadecebtc/issues

---

**Made with ❤️ by capul**

