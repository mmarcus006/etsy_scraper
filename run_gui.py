#!/usr/bin/env python
"""
Simple launcher script for the Etsy Scraper GUI.
Run this file to start the Streamlit web interface.
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path

def main():
    """Launch the Streamlit GUI."""
    print("=" * 50)
    print("🚀 Starting Etsy Scraper GUI...")
    print("=" * 50)
    
    # Get the path to the GUI file
    gui_path = Path(__file__).parent / "gui.py"
    
    if not gui_path.exists():
        print(f"❌ Error: GUI file not found at {gui_path}")
        sys.exit(1)
    
    print(f"📁 GUI file: {gui_path}")
    print("🌐 Opening web interface...")
    print("\n" + "=" * 50)
    print("The GUI will open in your browser at:")
    print("http://localhost:8501")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(gui_path),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--theme.primaryColor", "#4CAF50",
            "--theme.backgroundColor", "#FFFFFF",
            "--theme.secondaryBackgroundColor", "#F0F2F6",
            "--theme.textColor", "#262730"
        ])
    except KeyboardInterrupt:
        print("\n\n✅ GUI stopped by user")
    except Exception as e:
        print(f"\n❌ Error running GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()