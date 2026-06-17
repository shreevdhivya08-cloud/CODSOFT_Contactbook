#!/usr/bin/env python3
"""
ContactBook — entry point.
Run:  python main.py
"""

import sys
import os

# Add the project root to sys.path so imports resolve correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import ContactBookApp


def main() -> None:
    app = ContactBookApp()
    app.mainloop()


if __name__ == "__main__":
    main()
