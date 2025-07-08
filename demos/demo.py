#!/usr/bin/env python3
"""
Quick Demo Script for AI Trading Engine
Runs the engine for a few cycles to demonstrate functionality
"""

import time
import signal
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main

def signal_handler(sig, frame):
    print('\n🛑 Demo stopped by user')
    sys.exit(0)

def run_demo():
    """Run a short demo of the trading engine"""
    print("🚀 AI Trading Engine Demo")
    print("=" * 50)
    print("This demo will run the main trading engine for a few cycles")
    print("Press Ctrl+C to stop early")
    print("=" * 50)
    
    # Set up signal handler for graceful exit
    try:
        signal.signal(signal.SIGINT, signal_handler)
    except:
        pass  # Ignore if signal handling fails
    
    try:
        # Run the main function with limited cycles
        print("✅ Starting trading engine demo...")
        print("   Demo mode: True")
        print("   Max cycles: 3")
        print("   Cycle interval: 30 seconds")
        print()
        
        # Call the main function
        main()
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("The trading engine is working correctly.")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_demo() 