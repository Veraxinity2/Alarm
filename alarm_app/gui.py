import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Notify", "0.7")
from gi.repository import Gtk, GLib, Notify
import datetime

from alarm_app.alarms import AlarmManager
from alarm_app.weather import WeatherChecker
from alarm_app import settings as app_settings

class AlarmAppGUI:
    def __init__(self):
        self.settings = app_settings.load_settings()
        self.alarm_manager = AlarmManager()
        self.weather = WeatherChecker()
        Notify.init("Alarm App")

        self.window = Gtk.Window(title="Alarm App")
        self.window.set_default_size(400, 500)
        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", True)

        header = Gtk.HeaderBar(title="Alarm App")
        header.set_show_close_button(True)
        self.window.set_titlebar(header)

        # Gear icon for settings
        settings_button = Gtk.Button()
        icon = Gtk.Image.new_from_icon_name("emblem-system-symbolic", Gtk.IconSize.BUTTON)
        settings_button.set_image(icon)
        settings_button.connect("clicked", self.open_settings)
        header.pack_end(settings_button)

        self.notebook = Gtk.Notebook()
        self.window.add(self.notebook)

        self.init_alarm_tab()
        self.init_stopwatch_tab()
        self.init_timer_tab()

        GLib.timeout_add_seconds(1, self.update_clock)
        GLib.timeout_add_seconds(30, self.check_alarms)
        GLib.timeout_add_seconds(300, self.check_weather)

        self.window.connect("destroy", Gtk.main_quit)

    def open_settings(self, _):
        dialog = Gtk.Dialog(title="Settings", transient_for=self.window, flags=0)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        box = dialog.get_content_area()

        # Font size option
        font_label = Gtk.Label(label="Font Size")
        font_combo = Gtk.ComboBoxText()
        for size in ["small", "medium", "large"]:
            font_combo.append_text(size)
        font_combo.set_active(["small", "medium", "large"].index(self.settings["font_size"]))
        box.add(font_label)
        box.add(font_combo)

        # Milliseconds checkbox
        ms_check = Gtk.CheckButton(label="Show milliseconds in stopwatch")
        ms_check.set_active(self.settings.get("show_milliseconds", False))
        box.add(ms_check)

        def on_response(_, response_id):
            if response_id == Gtk.ResponseType.CLOSE:
                self.settings["font_size"] = font_combo.get_active_text()
                self.settings["show_milliseconds"] = ms_check.get_active()
                app_settings.save_settings(self.settings)
                self.apply_settings()
                dialog.destroy()

        dialog.connect("response", on_response)
        dialog.show_all()

    def apply_settings(self):
        font = {
            "small": "16",
            "medium": "24",
            "large": "32"
        }.get(self.settings["font_size"], "24")

        self.clock_label.set_markup(f"<span font='{font}'>{datetime.datetime.now().strftime('%I:%M:%S %p')}</span>")
        self.stopwatch_label.set_markup(f"<span font='{font}'>--:--</span>")
        self.timer_label.set_markup(f"<span font='{font}'>--:--</span>")

    # ---------------------- Alarm Tab ----------------------

    def init_alarm_tab(self):
        self.alarm_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=10)
        self.notebook.append_page(self.alarm_tab, Gtk.Label(label="Alarms"))

        self.clock_label = Gtk.Label()
        self.clock_label.set_markup("<span font='24'>--:--:--</span>")
        self.alarm_tab.pack_start(self.clock_label, False, False, 0)

        self.weather_label = Gtk.Label(label="Weather: loading...")
        self.alarm_tab.pack_start(self.weather_label, False, False, 0)

        time_box = Gtk.Box(spacing=5)
        self.hour_entry = Gtk.Entry()
        self.hour_entry.set_placeholder_text("Hour (1–12)")
        self.minute_entry = Gtk.Entry()
        self.minute_entry.set_placeholder_text("Minute (0–59)")
        time_box.pack_start(self.hour_entry, True, True, 0)
        time_box.pack_start(self.minute_entry, True, True, 0)
        self.alarm_tab.pack_start(time_box, False, False, 0)

        self.message_entry = Gtk.Entry()
        self.message_entry.set_placeholder_text("Message")
        self.alarm_tab.pack_start(self.message_entry, False, False, 0)

        self.recurring_check = Gtk.CheckButton(label="Repeat daily")
        self.alarm_tab.pack_start(self.recurring_check, False, False, 0)

        add_button = Gtk.Button(label="Add Alarm")
        add_button.connect("clicked", self.add_alarm)
        self.alarm_tab.pack_start(add_button, False, False, 0)

        self.alarm_list = Gtk.ListBox()
        self.alarm_tab.pack_start(self.alarm_list, True, True, 0)

        self.update_alarm_list()
    def update_clock(self):
        now = datetime.datetime.now().strftime("%I:%M:%S %p")
        font = {
            "small": "16",
            "medium": "24",
            "large": "32"
        }.get(self.settings["font_size"], "24")
        self.clock_label.set_markup(f"<span font='{font}'>{now}</span>")
        return True

    def add_alarm(self, _):
        try:
            hour = int(self.hour_entry.get_text())
            minute = int(self.minute_entry.get_text())
            message = self.message_entry.get_text().strip()
            recurring = self.recurring_check.get_active()

            if hour < 1 or hour > 12 or minute < 0 or minute > 59:
                raise ValueError

            now = datetime.datetime.now()
            if now.strftime("%p") == "PM" and hour != 12:
                hour += 12
            if now.strftime("%p") == "AM" and hour == 12:
                hour = 0

            self.alarm_manager.add_alarm(hour, minute, message, recurring)
            self.update_alarm_list()

            self.hour_entry.set_text("")
            self.minute_entry.set_text("")
            self.message_entry.set_text("")
            self.recurring_check.set_active(False)

        except ValueError:
            print("Invalid alarm input")

    def update_alarm_list(self):
        for child in self.alarm_list.get_children():
            self.alarm_list.remove(child)

        for alarm in self.alarm_manager.get_upcoming():
            time_str = alarm.time.strftime("%I:%M %p")
            recur = " (daily)" if alarm.recurring else ""
            label = Gtk.Label(label=f"{time_str} - {alarm.message}{recur}", xalign=0)
            self.alarm_list.add(label)

        self.alarm_list.show_all()

    def check_alarms(self):
        due = self.alarm_manager.check_alarms()
        for alarm in due:
            self.show_notification(alarm.message)
        self.update_alarm_list()
        return True

    def show_notification(self, message):
        note = Notify.Notification.new("🔔 Alarm", message, None)
        note.show()

    def check_weather(self):
        try:
            weather, temp = self.weather.get_weather()
            if weather:
                self.weather_label.set_text(f"Weather: {weather}, {temp}°C")
                if self.weather.should_alert(weather):
                    self.show_notification(f"⚠️ Weather: {weather}")
        except Exception as e:
            print(f"[Weather Error] {e}")
        return True

    # ---------------------- Stopwatch Tab ----------------------

    def init_stopwatch_tab(self):
        self.stopwatch_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=10)
        self.notebook.append_page(self.stopwatch_tab, Gtk.Label(label="Stopwatch"))

        self.stopwatch_label = Gtk.Label(label="00:00:00")
        self.stopwatch_tab.pack_start(self.stopwatch_label, False, False, 0)

        btn_box = Gtk.Box(spacing=5)
        start_btn = Gtk.Button(label="Start")
        stop_btn = Gtk.Button(label="Stop")
        reset_btn = Gtk.Button(label="Reset")
        start_btn.connect("clicked", self.start_stopwatch)
        stop_btn.connect("clicked", self.stop_stopwatch)
        reset_btn.connect("clicked", self.reset_stopwatch)
        btn_box.pack_start(start_btn, True, True, 0)
        btn_box.pack_start(stop_btn, True, True, 0)
        btn_box.pack_start(reset_btn, True, True, 0)
        self.stopwatch_tab.pack_start(btn_box, False, False, 0)

        self.stopwatch_running = False
        self.stopwatch_seconds = 0
        GLib.timeout_add(100, self.update_stopwatch)

    def update_stopwatch(self):
        if self.stopwatch_running:
            self.stopwatch_seconds += 0.1
        total = int(self.stopwatch_seconds)
        ms = int((self.stopwatch_seconds - total) * 100)
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60

        if self.settings.get("show_milliseconds", False):
            text = f"{h:02}:{m:02}:{s:02}.{ms:02}"
        else:
            text = f"{h:02}:{m:02}:{s:02}"

        font = {
            "small": "16",
            "medium": "24",
            "large": "32"
        }.get(self.settings["font_size"], "24")
        self.stopwatch_label.set_markup(f"<span font='{font}'>{text}</span>")
        return True

    def start_stopwatch(self, _): self.stopwatch_running = True
    def stop_stopwatch(self, _): self.stopwatch_running = False
    def reset_stopwatch(self, _):
        self.stopwatch_running = False
        self.stopwatch_seconds = 0

    # ---------------------- Timer Tab ----------------------

    def init_timer_tab(self):
        self.timer_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=10)
        self.notebook.append_page(self.timer_tab, Gtk.Label(label="Timer"))

        self.timer_label = Gtk.Label(label="00:00")
        self.timer_tab.pack_start(self.timer_label, False, False, 0)

        self.timer_entry = Gtk.Entry()
        self.timer_entry.set_placeholder_text("Minutes")
        self.timer_tab.pack_start(self.timer_entry, False, False, 0)

        btn_box = Gtk.Box(spacing=5)
        start_btn = Gtk.Button(label="Start Timer")
        stop_btn = Gtk.Button(label="Stop")
        reset_btn = Gtk.Button(label="Reset")
        start_btn.connect("clicked", self.start_timer)
        stop_btn.connect("clicked", self.stop_timer)
        reset_btn.connect("clicked", self.reset_timer)
        btn_box.pack_start(start_btn, True, True, 0)
        btn_box.pack_start(stop_btn, True, True, 0)
        btn_box.pack_start(reset_btn, True, True, 0)
        self.timer_tab.pack_start(btn_box, False, False, 0)

        self.timer_running = False
        self.timer_seconds = 0
        GLib.timeout_add_seconds(1, self.update_timer)

    def start_timer(self, _):
        try:
            minutes = int(self.timer_entry.get_text())
            self.timer_seconds = minutes * 60
            self.timer_running = True
        except:
            print("Invalid timer input")

    def stop_timer(self, _): self.timer_running = False
    def reset_timer(self, _):
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_label.set_text("00:00")

    def update_timer(self):
        if self.timer_running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            m, s = self.timer_seconds // 60, self.timer_seconds % 60
            font = {
                "small": "16",
                "medium": "24",
                "large": "32"
            }.get(self.settings["font_size"], "24")
            self.timer_label.set_markup(f"<span font='{font}'>{m:02}:{s:02}</span>")
            if self.timer_seconds == 0:
                self.show_notification("⏳ Timer finished!")
        return True

    def run(self):
        self.window.show_all()
        self.apply_settings()
        Gtk.main()
