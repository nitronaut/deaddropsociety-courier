#!/usr/bin/env python3
"""
Dead Drop Society - Entry Point
Run this file to start the game
"""

import sys
import os

# Add the game directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.main import DeadDropSociety

if __name__ == "__main__":
    game = DeadDropSociety()
    game.run()
