# 🌐 CONNECTION GUIDE - GitHub Codespaces

## For Organization Laptop Users

If you're accessing this from an **organization laptop** with connection restrictions, follow these steps:

---

## ✅ CORRECT URLS

### Local (Dev Container)
```
Backend API:     http://localhost:8000
Frontend UI:     http://localhost:8080/bestsellers.html
```

### GitHub Codespaces Public (Organization Laptop)
```
Backend API:     https://crispy-spoon-wr69v5j66q7whjwq-8000.app.github.dev/health
Frontend UI:     https://crispy-spoon-wr69v5j66q7whjwq-8080.app.github.dev/bestsellers.html
```

---

## 🔧 STARTUP SCRIPT

To start both services automatically:

```bash
cd /workspaces/Amazon-Seller-Daashboard
chmod +x scripts/start_api.sh
./scripts/start_api.sh
```

This will start:
- ✅ **Backend API** on port 8000
- ✅ **Frontend HTTP Server** on port 8080

And display all available URLs.

---

## 🚨 TROUBLESHOOTING

### Issue: "Connection refused" on organization laptop

**Solution:** Use the GitHub Codespaces public URL instead:
- ❌ Don't use: `http://localhost:8080`
- ✅ Use: `https://crispy-spoon-wr69v5j66q7whjwq-8080.app.github.dev/bestsellers.html`

### Issue: Ports already in use

Check running processes:
```bash
lsof -i :8000  # Check port 8000
lsof -i :8080  # Check port 8080
```

Kill if needed:
```bash
pkill -f "uvicorn"        # Kill backend
pkill -f "http.server"    # Kill frontend
```

Then restart:
```bash
./scripts/start_api.sh
```

### Issue: Backend API not responding

Check logs:
```bash
tail -f /tmp/backend.log
```

Verify it's running:
```bash
curl -s http://localhost:8000/health
```

### Issue: Frontend page blank/loading

Check frontend logs:
```bash
tail -f /tmp/frontend.log
```

The HTML file exists at:
```bash
ls -la frontend/bestsellers.html
```

---

## 📊 SERVICES STATUS

| Service | Status | Port | URL |
|---------|--------|------|-----|
| Backend API | ✅ Running | 8000 | `https://crispy-spoon-...8000.app.github.dev` |
| Frontend UI | ✅ Running | 8080 | `https://crispy-spoon-...8080.app.github.dev/bestsellers.html` |
| Database | ✅ Connected | - | `/workspaces/.../amazon_sourcing.db` |

---

## 🎯 QUICK START (Organization Laptop)

1. **Open in browser:**
   ```
   https://crispy-spoon-wr69v5j66q7whjwq-8080.app.github.dev/bestsellers.html
   ```

2. **See the dashboard:**
   - Category ID: 1378568031 (pre-filled)
   - Limit: Top 100 Products (default)
   - Click "Analyze" button

3. **Results display:**
   - ✅ Cache status badge
   - 💰 Token cost badge
   - 📅 Last synced & Next sync timestamps
   - 📊 Results table with 7 dimensions

---

## 🔐 FIREWALL/PROXY ISSUES

If you still get "Connection refused":

1. **Check if port forwarding is enabled:**
   ```bash
   # In VS Code terminal
   # Ports tab should show:
   # - 8000 (public/private)
   # - 8080 (public/private)
   ```

2. **If ports aren't forwarding:**
   - Click "Ports" tab in terminal
   - Right-click port → "Make Public"
   - Copy the forwarded URL

3. **Use the forwarded URL:**
   - Example: `https://user-workspace-8080.app.github.dev`

---

## ✨ WORKING FEATURES

When you access the UI, you'll see:

✅ **Cache Status**
- ✅ From Cache / 🔄 Fresh Fetch badge
- ✅ 0 Tokens / 💰 XXX Tokens badge
- 📅 Last synced timestamp
- 📅 Next sync with countdown

✅ **Results Table**
- Ranked products (#1, #2, etc.)
- ASIN (clickable to Amazon)
- Product title
- 7 scoring dimensions with bars:
  - 💰 Profitability
  - 📈 Demand
  - 🛡️ Stability
  - 📦 Buybox Strength
  - ⚠️ OOS Risk
  - 📊 Supply Gap
  - 📅 Non-Seasonal
- Overall score

✅ **Interactive Features**
- Enter different category IDs
- Change product limit (10-200)
- Manual refresh button
- Auto-loading on page load

---

## 📝 NOTES

- **Database:** SQLite, auto-caching for 7 days
- **Token Cost:** First fetch ~235 tokens, cached queries 0 tokens
- **Response Time:** 20-50ms for cached, 5-7s for fresh fetch
- **Mobile Friendly:** Responsive design works on all devices

---

## 🆘 NEED HELP?

Check these files for more info:
- API Docs: `docs/ARCHITECTURE.md`
- UI Guide: `UI_INTEGRATION_SUMMARY.md`
- System Overview: `FINAL_SYSTEM_SUMMARY.md`

---

**Last Updated:** February 1, 2026  
**Status:** ✅ All systems operational
