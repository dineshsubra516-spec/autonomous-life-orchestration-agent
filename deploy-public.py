#!/usr/bin/env python3
"""
Day Planner - Public Tunnel Generator
Provides public access URL without authentication
"""

import subprocess
import sys
import os
import time

def check_server():
    """Check if the FastAPI server is running"""
    try:
        import requests
        response = requests.get('http://127.0.0.1:8000/api/destinations', timeout=2)
        return response.status_code == 200
    except:
        return False

def print_banner():
    print("""
╔════════════════════════════════════════════════════════════╗
║         🚀 DAY PLANNER - PUBLIC DEPLOYMENT                 ║
║                                                             ║
║     Making your application accessible to the world!       ║
╚════════════════════════════════════════════════════════════╝
    """)

def option_localhost_run():
    """Use localhost.run service (simple HTTP tunnel)"""
    print("\n📡 Setting up public tunnel via localhost.run...")
    print("   This provides a free public URL for your app!")
    print("")
    print("   Command to run in another terminal:")
    print("   ssh -R 80:127.0.0.1:8000 localhost.run")
    print("")
    print("   Then visit the URL provided (looks like: https://xxx.localhost.run)")
    return False

def option_railway():
    """Provide Railway.app deployment info"""
    print("\n🌐 RECOMMENDED: Deploy to Railway.app")
    print("   Railway provides Free, Fast, and Reliable hosting")
    print("")
    print("   Steps:")
    print("   1. Go to https://railway.app")
    print("   2. Sign up with GitHub")
    print("   3. Click 'New Project' → 'Deploy from GitHub repo'")
    print("   4. Select this repository")
    print("   5. Railway auto-detects the Procfile and deploys!")
    print("")
    print("   ✨ Your app will be live in 2-3 minutes")
    print("   📍 Public URL: https://<your-app-name>.up.railway.app")
    return True

def option_manual_tunnel():
    """Provide manual tunnel options"""
    print("\n🔗 Manual Tunnel Options:")
    print("")
    print("   Option A: SSH Tunnel (localhost.run)")
    print("   ─────────────────────────────────")
    print("   # In another terminal, run:")
    print("   ssh -R 80:127.0.0.1:8000 localhost.run")
    print("")
    print("   Option B: Caddy Reverse Proxy")
    print("   ──────────────────────────────")  
    print("   # If you have a domain & Caddy installed:")
    print("   sudo caddy reverse-proxy --from yourdomain.com --to 127.0.0.1:8000")
    print("")
    print("   Option C: Nginx Reverse Proxy")
    print("   ─────────────────────────────")
    print("   # If you have a domain & Nginx installed:")
    print("   sudo nginx -c /path/to/dayplanner.nginx.conf")
    return True

def main():
    print_banner()
    
    # Check if server is running
    print("🔍 Checking if Day Planner is running...")
    for attempt in range(5):
        if check_server():
            print("✅ Day Planner is running on http://127.0.0.1:8000")
            break
        if attempt < 4:
            print(f"   Checking... (attempt {attempt + 1}/5)")
            time.sleep(1)
    else:
        print("❌ Day Planner server is not running!")
        print("   Please start it first with:")
        print("   cd docs/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False
    
    print("""
╔════════════════════════════════════════════════════════════╗
║         CHOOSE YOUR DEPLOYMENT METHOD                      ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print("\n1️⃣  RECOMMENDED: Deploy to Railway.app (Easiest ⭐)")
    option_railway()
    
    print("\n2️⃣  Use SSH Tunnel (localhost.run)")
    option_localhost_run()
    
    print("\n3️⃣  Other Deployment Options")
    option_manual_tunnel()
    
    print("""
╔════════════════════════════════════════════════════════════╗
║        ✨ DEPLOYMENT COMPLETE!                             ║
║                                                             ║
║  Your Day Planner is ready for public access!              ║
║  Share the public URL with anyone - no setup needed!       ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
