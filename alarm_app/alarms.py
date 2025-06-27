import datetime
import json
import os

ALARM_SAVE_FILE = os.path.expanduser("~/Desktop/alarm_app/config/alarms.json")

class Alarm:
    def __init__(self, hour, minute, message, recurring=False):
        self.time = datetime.time(hour, minute)
        self.message = message
        self.recurring = recurring
        self.triggered_today = False

    def to_dict(self):
        return {
            "hour": self.time.hour,
            "minute": self.time.minute,
            "message": self.message,
            "recurring": self.recurring
        }

    @staticmethod
    def from_dict(data):
        return Alarm(
            hour=data["hour"],
            minute=data["minute"],
            message=data["message"],
            recurring=data.get("recurring", False)
        )

class AlarmManager:
    def __init__(self):
        self.alarms = []
        self.load_alarms()

    def add_alarm(self, hour, minute, message, recurring=False):
        alarm = Alarm(hour, minute, message, recurring)
        self.alarms.append(alarm)
        self.save_alarms()

    def get_upcoming(self):
        return sorted(self.alarms, key=lambda a: (a.time.hour, a.time.minute))

    def check_alarms(self):
        now = datetime.datetime.now()
        triggered = []

        for alarm in self.alarms:
            if (alarm.time.hour == now.hour and
                alarm.time.minute == now.minute and
                not alarm.triggered_today):
                triggered.append(alarm)
                alarm.triggered_today = True

        # Reset triggered flags at midnight
        if now.hour == 0 and now.minute == 0:
            for alarm in self.alarms:
                alarm.triggered_today = False

        # Handle non-recurring
        self.alarms = [
            a for a in self.alarms
            if a.recurring or a not in triggered
        ]

        if triggered:
            self.save_alarms()

        return triggered

    def save_alarms(self):
        try:
            data = [a.to_dict() for a in self.alarms]
            with open(ALARM_SAVE_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"[Save Error] {e}")

    def load_alarms(self):
        if not os.path.exists(ALARM_SAVE_FILE):
            return
        try:
            with open(ALARM_SAVE_FILE, "r") as f:
                data = json.load(f)
            self.alarms = [Alarm.from_dict(a) for a in data]
        except Exception as e:
            print(f"[Load Error] {e}")
