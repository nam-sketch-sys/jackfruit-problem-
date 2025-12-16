import wx
import wikipedia
import requests
import datetime
import threading
import time
import string
import random
import json
import os

# -----------------------------
# WEATHER API KEY
# -----------------------------
API_KEY = "83f2c584591cd2c5e41d3a7fedee3a02"

# -----------------------------
# PASSWORD FUNCTIONS                 #done
# -----------------------------
def check_password_strength(password):
    score = 0
    if len(password) >= 8: score += 1
    if any(c.islower() for c in password): score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in string.punctuation for c in password): score += 1

    levels = ["Very Weak", "Weak", "Moderate", "Strong", "Very Strong"]
    return levels[min(score, 4)]

def generate_password(length=12):
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(length))

# -----------------------------       #done
# WEATHER FUNCTION
# -----------------------------
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        data = requests.get(url).json()
        if data["cod"] != 200:
            return "City not found"
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"{city}: {temp}°C, {desc}"
    except:
        return "Error fetching weather"

# -----------------------------        #done
# REMINDER THREAD
# -----------------------------
reminders = []

def reminder_thread(callback):
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        for r in reminders:
            if r["time"] == now and not r["done"]:
                callback(f"Reminder: {r['text']}")
                r["done"] = True
        time.sleep(30)

# -----------------------------
# TO-DO LIST STORAGE
# -----------------------------
TODO_FILE = "todo.json"

def load_todo():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    return []

def save_todo(tasks):
    with open(TODO_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

# -----------------------------
# MAIN GUI
# -----------------------------           #done
class SmartUtilityBot(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Smart Utility Bot", size=(600, 500))
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(panel, label="Smart Utility Bot")
        title.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox.Add(title, 0, wx.ALIGN_CENTER | wx.TOP, 15)

        buttons = [
            ("Time & Date", self.show_time),
            ("Weather", self.open_weather),
            ("Wikipedia Search", self.open_wiki),
            ("Set Reminder", self.open_reminder),
            ("Password Tools", self.open_password),
            ("Calculator", self.open_calculator),
            ("Unit Converter", self.open_converter),
            ("Text Utilities", self.open_text_utils),
            ("To-Do List", self.open_todo_list),
        ]

        grid = wx.GridSizer(5, 2, 10, 10)
        for label, handler in buttons:
            btn = wx.Button(panel, label=label)
            btn.Bind(wx.EVT_BUTTON, handler)
            grid.Add(btn, 0, wx.EXPAND)

        vbox.Add(grid, 1, wx.ALL | wx.EXPAND, 20)

        self.output = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        vbox.Add(self.output, 1, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(vbox)
        self.Show()

        threading.Thread(target=reminder_thread, args=(self.show_popup,), daemon=True).start()

    def log(self, msg):
        self.output.AppendText(msg + "\n")

    # -----------------------------
    # TIME & DATE                      #done
    # -----------------------------
    def show_time(self, event):
        now = datetime.datetime.now()
        self.log(f"Date: {now.strftime('%Y-%m-%d')}")
        self.log(f"Time: {now.strftime('%H:%M:%S')}")

    # -----------------------------
    # WEATHER                             #done
    # -----------------------------
    def open_weather(self, event):
        dlg = wx.TextEntryDialog(self, "Enter city name:", "Weather")
        if dlg.ShowModal() == wx.ID_OK:
            self.log(get_weather(dlg.GetValue()))
        dlg.Destroy()

    # -----------------------------
    # WIKIPEDIA                                   #done
    # -----------------------------
    def open_wiki(self, event):
        dlg = wx.TextEntryDialog(self, "Search Wikipedia:", "Wikipedia")
        if dlg.ShowModal() == wx.ID_OK:
            try:
                summary = wikipedia.summary(dlg.GetValue(), sentences=2)
                self.log(summary)
            except:
                self.log("No results found")
        dlg.Destroy()

    # -----------------------------
    # REMINDER
    # -----------------------------          #done
    def open_reminder(self, event):
        dlg = wx.TextEntryDialog(self, "Enter reminder (HH:MM - text):", "Reminder")
        if dlg.ShowModal() == wx.ID_OK:
            try:
                time_part, msg = dlg.GetValue().split("-", 1)
                reminders.append({"time": time_part.strip(), "text": msg.strip(), "done": False})
                self.log("Reminder set successfully")
            except:
                self.log("Invalid format")
        dlg.Destroy()

    def show_popup(self, msg):
        wx.CallAfter(wx.MessageBox, msg, "Reminder")

    # -----------------------------
    # PASSWORD                          #done
    # -----------------------------
    def open_password(self, event):
        dlg = wx.TextEntryDialog(self, "Enter password:", "Password Tool")
        if dlg.ShowModal() == wx.ID_OK:
            self.log("Strength: " + check_password_strength(dlg.GetValue()))
            self.log("Generated Password: " + generate_password())
        dlg.Destroy()

    # -----------------------------      #done
    # CALCULATOR                     
    # -----------------------------
    def open_calculator(self, event):
        dlg = wx.TextEntryDialog(self, "Enter expression:", "Calculator")
        if dlg.ShowModal() == wx.ID_OK:
            try:
                self.log(f"Result: {eval(dlg.GetValue())}")
            except:
                self.log("Invalid expression")
        dlg.Destroy()

    # -----------------------------
    # CONVERTER
    # -----------------------------
    def open_converter(self, event):
        dlg = wx.TextEntryDialog(self, "Enter 25C or 77F:", "Converter")
        if dlg.ShowModal() == wx.ID_OK:
            val = dlg.GetValue().upper()
            try:
                if val.endswith("C"):
                    c = float(val[:-1])
                    self.log(f"{c}°C = {(c * 9/5) + 32}°F")
                elif val.endswith("F"):
                    f = float(val[:-1])
                    self.log(f"{f}°F = {(f - 32) * 5/9}°C")
                else:
                    self.log("Invalid format")
            except:
                self.log("Conversion error")
        dlg.Destroy()

    # -----------------------------
    # TEXT UTILITIES
    # -----------------------------         #done
    def open_text_utils(self, event):
        dlg = wx.TextEntryDialog(self, "Enter text:", "Text Utilities")
        if dlg.ShowModal() == wx.ID_OK:
            text = dlg.GetValue()
            self.log(f"Words: {len(text.split())}, Characters: {len(text)}")
            self.log(text.upper())
            self.log(text.lower())
        dlg.Destroy()

    # -----------------------------
    # TO-DO LIST (SINGLE LINE + SAVED)
    # -----------------------------
    def open_todo_list(self, event):
        tasks = load_todo()

        todo_frame = wx.Frame(self, title="To-Do List", size=(400, 500))
        panel = wx.Panel(todo_frame)
        vbox = wx.BoxSizer(wx.VERTICAL)

        checklist = wx.CheckListBox(panel, choices=[t["text"] for t in tasks])
        vbox.Add(checklist, 1, wx.EXPAND | wx.ALL, 10)

        for i, t in enumerate(tasks):
            if t["done"]:
                checklist.Check(i)

        add_btn = wx.Button(panel, label="Add New Task")
        vbox.Add(add_btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        def add_task(event):
            dlg = wx.TextEntryDialog(todo_frame, "Enter new task:", "Add Task")
            if dlg.ShowModal() == wx.ID_OK:
                text = dlg.GetValue().strip()
                if text:
                    tasks.append({"text": text, "done": False})
                    save_todo(tasks)
                    checklist.Append(text)
                    self.log(f"Task added: {text}")
            dlg.Destroy()

        add_btn.Bind(wx.EVT_BUTTON, add_task)

        def on_check(event):
            idx = event.GetSelection()
            tasks[idx]["done"] = checklist.IsChecked(idx)
            save_todo(tasks)
            self.log("Task updated")

        checklist.Bind(wx.EVT_CHECKLISTBOX, on_check)

        panel.SetSizer(vbox)
        todo_frame.Show()

# -----------------------------
# RUN APP
# -----------------------------
app = wx.App()
SmartUtilityBot()
app.MainLoop()
