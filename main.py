#!/usr/bin/env python3
import sys
import os

# Determine runtime environment and update import paths
dev_dir = os.path.dirname(os.path.realpath(__file__))
if os.path.exists(os.path.join(dev_dir, "webapp_manager")):
    # Running from dev checkout / local source folder
    sys.path.insert(0, dev_dir)
else:
    # Running from system install location, load package from share
    sys.path.insert(0, os.path.expanduser("~/.local/share/kde-webapp-manager"))
    sys.path.insert(0, "/usr/share/kde-webapp-manager")
    sys.path.insert(0, "/app/share/kde-webapp-manager")

from webapp_manager.gui import main

if __name__ == "__main__":
    main()
