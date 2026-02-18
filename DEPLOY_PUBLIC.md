# 🚀 Day Planner - Public Deployment Guide

Your Day Planner is ready to be deployed for public access! Anyone with the link can visit and use your app. Choose your preferred deployment method below:

---

## ⭐ **RECOMMENDED: Deploy to Railway.app** (Easiest)

Railway is free, fast, and automatically deploys from your GitHub repository.

### Steps:

1. **Go to** [railway.app](https://railway.app)

2. **Sign up** with your GitHub account
   
3. **Create New Project** → Select "Deploy from GitHub repo"

4. **Select this repository** (autonomous-life-orchestration-agent)

5. **Railway auto-detects** the `Procfile` and deploys automatically!

6. **Get your public URL** in the Railway dashboard
   - Format: `https://<your-app-name>.up.railway.app`

### ✨ Your app will be live in **2-3 minutes**!

---

## 🔗 **Alternative #1: localhost.run (Quick Testing)**

For quick public access without deployment:

```bash
# In another terminal, run:
ssh -R 80:127.0.0.1:8000 localhost.run
```

This gives you a temporary public URL (looks like `https://abc123.localhost.run`). Valid for a few hours.

---

## 🐳 **Alternative #2: Deploy with Docker**

If you have Docker installed:

```bash
# Build the Docker image
docker build -t day-planner .

# Run the container
docker run -p 8000:8000 day-planner

# Then access at http://localhost:8000
```

Deploy the Docker image to:
- Docker Hub
- AWS ECR
- Google Container Registry
- Any Docker-compatible hosting service

---

## 🌐 **Alternative #3: Render.com**

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Create a new Web Service
4. Connect your GitHub repository
5. Configure:
   - **Build Command:** `pip install -r docs/backend/requirements.txt`
   - **Start Command:** `cd docs/backend && uvicorn app.main:app --host 0.0.0.0 --port 10000`
6. Deploy!

---

## 📝 **Alternative #4: Manual Server Deployment**

If you have a VPS or dedicated server:

```bash
# SSH into your server
ssh user@your-server.com

# Clone the repository
git clone <your-repo-url>
cd autonomous-life-orchestration-agent

# Install dependencies
cd docs/backend
pip install -r requirements.txt

# Run with Gunicorn (for production)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app --worker-class uvicorn.workers.UvicornWorker

# Or use Supervisor/Systemd for auto-restart
# (See production setup guides)
```

---

## ✅ **Verify Your Deployment**

Once deployed, verify the app is working:

```bash
# Test the API
curl https://<your-public-url>/api/destinations

# Visit in browser
https://<your-public-url>
```

You should see the Day Planner dashboard!

---

## 🎁 **Share the Link**

Once deployed:

```
📱 Share this link with anyone:
https://<your-public-url>

✨ They can access it without any installation or setup!
```

---

## 🆘 **Troubleshooting**

### "Port is already in use"
```bash
# Kill the process using port 8000
lsof -i :8000
kill -9 <PID>
```

### "Module not found"
```bash
# Make sure all dependencies are installed
cd docs/backend
pip install -r requirements.txt
```

### "App not responding"
```bash
# Check if FastAPI server is running
curl http://127.0.0.1:8000/api/destinations

# Check logs
tail -f /tmp/server.log  # if using background process
```

---

## 🎯 **Recommended Setup Summary**

| Method | Time | Cost | Ease | Uptime |
|--------|------|------|------|--------|
| Railway.app | 3 min | Free | ⭐⭐⭐ | 99.9% |
| localhost.run | 1 min | Free | ⭐⭐⭐ | 2-3 hrs |
| Render.com | 5 min | Free | ⭐⭐⭐ | 99.5% |
| Docker | 10 min | Varies | ⭐⭐ | 99.9% |
| Manual VPS | 30 min | $5+/mo | ⭐ | 99.99% |

---

## 📞 **Need Help?**

Check the official documentation:
- [Railway Docs](https://docs.railway.app)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [localhost.run Help](http://localhost.run)

---

**Your Day Planner is now ready for the world! 🌍**
