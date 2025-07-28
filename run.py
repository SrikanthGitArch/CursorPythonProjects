#!/usr/bin/env python3
"""
WhatsApp Clone - Startup Script
Run this script to start the WhatsApp clone application
"""

import sys
import os

def main():
    print("🚀 Starting WhatsApp Clone...")
    print("📱 A modern messaging application built with Python!")
    print("-" * 50)
    
    # Check if Flask is installed
    try:
        import flask
        import flask_socketio
        print("✅ Dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with:")
        print("pip install --break-system-packages Flask Flask-SocketIO")
        return 1
    
    # Import and run the app
    try:
        from app import socketio, app
        print("🌐 Server starting on http://localhost:5000")
        print("📝 Features available:")
        print("   • Real-time messaging")
        print("   • Personal and group chats")
        print("   • Emoji support")
        print("   • File attachments")
        print("   • Search functionality")
        print("   • Auto-responses for demo")
        print("-" * 50)
        print("🔗 Open http://localhost:5000 in your browser")
        print("Press Ctrl+C to stop the server")
        
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down WhatsApp Clone...")
        return 0
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())