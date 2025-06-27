import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from alarm_app.gui import AlarmAppGUI

def main():
    app = AlarmAppGUI()
    app.run()

if __name__ == "__main__":
    main()
