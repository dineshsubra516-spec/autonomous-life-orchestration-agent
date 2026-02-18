#!/usr/bin/env python3
"""
Day Planner - Auto Public Tunnel
Automatically exposes your local app to the internet
"""

import subprocess
import sys
import time
import os

def run_localhost_tunnel():
    """
    Start a persistent public tunnel using localhost.run
    No authentication required - instant public access!
    """
    print("""
╔════════════════════════════════════════════════════════════╗
║  🌐 DAY PLANNER - AUTO PUBLIC TUNNEL                       ║
║                                                             ║
║  Making your app publicly accessible...                    ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check if server is running
    try:
        import requests
        response = requests.get('http://127.0.0.1:8000/api/destinations', timeout=2)
        if response.status_code == 200:
            print("✅ Day Planner server is running on http://127.0.0.1:8000\n")
        else:
            print("❌ Server is not responding properly\n")
            return False
    except:
        print("❌ Server is not running on port 8000\n")
        return False
    
    # Start localhost.run SSH tunnel
    print("🔗 Starting public tunnel via localhost.run...")
    print("   (This creates a public URL accessible by anyone)\n")
    
    try:
        # ssh -R creates a reverse tunnel: forwards localhost.run traffic to our local 8000
        cmd = [
            'ssh',
            '-R', '80:127.0.0.1:8000',
            'localhost.run'
        ]
        
        print("📡 Launching tunnel...")
        print("─" * 60)
        
        # Run SSH tunnel - this will stay open
        subprocess.run(cmd, check=False)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tunnel stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting tunnel: {e}")
        return False

def generate_public_url_file():
    """Create a file that shows the public URL"""
    url_file = "/tmp/day_planner_public_url.txt"
    
    message = """
╔═════════════════════════════════════════════════════════════╗
║                                                              ║
║            🌍 DAY PLANNER PUBLIC URL                         ║
║                                                              ║
║  Your app is now accessible to anyone with this link:      ║
║                                                              ║
║  👉 Check the terminal running localhost.run for the URL    ║
║                                                              ║
║  Format will be something like:                             ║
║     https://abc123.localhost.run                            ║
║                                                              ║
║  Share this link - no setup needed for visitors!            ║
║                                                              ║
╚═════════════════════════════════════════════════════════════╝
    """
    
    with open(url_file, 'w') as f:
        f.write(message)
    
    print(message)

if __name__ == "__main__":
    # Show the tunnel startup
    print("""
📋 SETUP: This script creates a public tunnel to your Day Planner

   No authentication needed!
   No third-party accounts required!
   Anyone can visit your URL!
   
   ✨ Your app will be live in seconds via localhost.run
    """)
    
    input("Press Enter to start the public tunnel...")
    
    generate_public_url_file()
    success = run_localhost_tunnel()
    
    sys.exit(0 if success else 1)
