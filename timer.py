import wx
import os
import theme

# Try to import platform-specific sound
try:
    import winsound   # Windows sound
    WINDOWS_SOUND = True
except ImportError:
    WINDOWS_SOUND = False


class TimerPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour(theme.TIMER_PANEL_BG)

        self.is_running = False
        self.remaining_time = 0
        self.total_time = 0

        # wx Timer (better than threading)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.run_timer, self.timer)

        self.build_ui()

    def build_ui(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(self, label="Focus Timer")
        title.SetFont(theme.FONT_SUBTITLE)
        title.SetForegroundColour(theme.NORMAL_TEXT)
        vbox.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        
        # Timer display
        self.timer_display = wx.StaticText(self, label="25:00", style=wx.ALIGN_CENTER)
        self.timer_display.SetFont(wx.Font(48, wx.FONTFAMILY_DEFAULT,
                                           wx.FONTSTYLE_NORMAL,
                                           wx.FONTWEIGHT_BOLD))
        self.timer_display.SetForegroundColour(theme.TIMER_COLOR)
        vbox.Add(self.timer_display, 0, wx.ALL | wx.ALIGN_CENTER, 20)
        
        # Progress indicator
        progress_sizer = wx.BoxSizer(wx.VERTICAL)
        
        progress_label = wx.StaticText(self, label="Progress:")
        progress_label.SetFont(theme.FONT_SMALL)
        progress_label.SetForegroundColour(theme.SUB_TEXT)
        progress_sizer.Add(progress_label, 0, wx.ALL, 5)
        
        self.progress_gauge = wx.Gauge(self, range=100, size=(-1, 10))
        self.progress_gauge.SetValue(0)
        self.progress_gauge.SetBackgroundColour(wx.Colour(230, 230, 230))
        self.progress_gauge.SetForegroundColour(theme.TIMER_COLOR)
        progress_sizer.Add(self.progress_gauge, 0, wx.ALL | wx.EXPAND, 5)
        
        vbox.Add(progress_sizer, 0, wx.ALL | wx.EXPAND, 10)
        
        # Inputs in white panel
        input_panel = wx.Panel(self)
        input_panel.SetBackgroundColour(wx.WHITE)
        grid = wx.FlexGridSizer(2, 2, 10, 10)
        
        minutes_label = wx.StaticText(input_panel, label="Minutes:")
        minutes_label.SetFont(theme.get_font(11, wx.FONTWEIGHT_BOLD))
        minutes_label.SetForegroundColour(theme.SUB_TEXT)
        grid.Add(minutes_label, 0, wx.ALIGN_CENTER_VERTICAL)
        
        self.minutes_input = wx.SpinCtrl(input_panel, min=0, max=180, initial=25)
        self.minutes_input.SetFont(theme.FONT_NORMAL)
        grid.Add(self.minutes_input, 0, wx.EXPAND)
        
        seconds_label = wx.StaticText(input_panel, label="Seconds:")
        seconds_label.SetFont(theme.get_font(11, wx.FONTWEIGHT_BOLD))
        seconds_label.SetForegroundColour(theme.SUB_TEXT)
        grid.Add(seconds_label, 0, wx.ALIGN_CENTER_VERTICAL)
        
        self.seconds_input = wx.SpinCtrl(input_panel, min=0, max=59, initial=0)
        self.seconds_input.SetFont(theme.FONT_NORMAL)
        grid.Add(self.seconds_input, 0, wx.EXPAND)
        
        input_panel.SetSizer(grid)
        vbox.Add(input_panel, 0, wx.ALL | wx.EXPAND, 10)
        
        # Description
        desc_label = wx.StaticText(self, label="Timer Description:")
        desc_label.SetFont(theme.get_font(11, wx.FONTWEIGHT_BOLD))
        desc_label.SetForegroundColour(theme.SUB_TEXT)
        vbox.Add(desc_label, 0, wx.ALL, 5)
        
        desc_panel = wx.Panel(self)
        desc_panel.SetBackgroundColour(wx.WHITE)
        desc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.desc_input = wx.TextCtrl(desc_panel, value="Focus Time")
        self.desc_input.SetFont(theme.FONT_NORMAL)
        desc_sizer.Add(self.desc_input, 1, wx.ALL | wx.EXPAND, 5)
        
        desc_panel.SetSizer(desc_sizer)
        vbox.Add(desc_panel, 0, wx.ALL | wx.EXPAND, 5)
        
        # Buttons
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.start_btn = wx.Button(self, label="▶ Start")
        self.pause_btn = wx.Button(self, label="⏸ Pause")
        self.reset_btn = wx.Button(self, label="↺ Reset")
        
        # Style buttons
        self.start_btn.SetBackgroundColour(theme.BUTTON_PRIMARY_BG)
        self.start_btn.SetForegroundColour(theme.BUTTON_TEXT)
        self.start_btn.SetFont(theme.get_font(11, wx.FONTWEIGHT_BOLD))
        self.start_btn.SetMinSize((90, 35))
        
        self.pause_btn.SetBackgroundColour(theme.BUTTON_SECONDARY_BG)
        self.pause_btn.SetForegroundColour(theme.BUTTON_TEXT)
        self.pause_btn.SetFont(theme.get_font(11, wx.FONTWEIGHT_BOLD))
        self.pause_btn.SetMinSize((90, 35))
        
        self.reset_btn.SetBackgroundColour(theme.BUTTON_SECONDARY_BG)
        self.reset_btn.SetForegroundColour(theme.BUTTON_TEXT)
        self.reset_btn.SetFont(theme.get_font(11, wx.FONTWEIGHT_BOLD))
        self.reset_btn.SetMinSize((90, 35))
        
        self.start_btn.Bind(wx.EVT_BUTTON, self.on_start)
        self.pause_btn.Bind(wx.EVT_BUTTON, self.on_pause)
        self.reset_btn.Bind(wx.EVT_BUTTON, self.on_reset)
        
        hbox.Add(self.start_btn, 0, wx.ALL, 5)
        hbox.Add(self.pause_btn, 0, wx.ALL, 5)
        hbox.Add(self.reset_btn, 0, wx.ALL, 5)
        
        vbox.Add(hbox, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        
        self.SetSizer(vbox)

    # -------------------- Buttons --------------------

    def on_start(self, event):
        if self.remaining_time <= 0:
            minutes = self.minutes_input.GetValue()
            seconds = self.seconds_input.GetValue()
            self.remaining_time = (minutes * 60) + seconds
            self.total_time = self.remaining_time
            
            # Reset progress gauge
            if hasattr(self, 'progress_gauge'):
                self.progress_gauge.SetValue(0)

        if self.remaining_time == 0:
            wx.MessageBox("Set a time greater than 0.", "Error")
            return

        self.is_running = True
        self.start_btn.SetLabel("▶ Resume")
        self.timer.Start(1000)   # 1 second interval

    def on_pause(self, event):
        self.is_running = False
        self.timer.Stop()

    def on_reset(self, event):
        self.is_running = False
        self.timer.Stop()

        minutes = self.minutes_input.GetValue()
        seconds = self.seconds_input.GetValue()

        self.remaining_time = (minutes * 60) + seconds
        self.update_display(self.remaining_time)
        self.start_btn.SetLabel("▶ Start")
        
        # Reset progress gauge
        if hasattr(self, 'progress_gauge'):
            self.progress_gauge.SetValue(0)

    # -------------------- Timer --------------------

    def run_timer(self, event):
        if self.remaining_time > 0 and self.is_running:
            self.update_display(self.remaining_time)
            self.remaining_time -= 1
        else:
            self.timer.Stop()
            self.timer_complete()

    def update_display(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        self.timer_display.SetLabel(f"{mins:02d}:{secs:02d}")
        
        # Update progress gauge if total_time > 0
        if hasattr(self, 'progress_gauge') and self.total_time > 0:
            progress = int(((self.total_time - seconds) / self.total_time) * 100)
            self.progress_gauge.SetValue(progress)

    # -------------------- Alarm --------------------

    def play_alarm(self):
        if WINDOWS_SOUND:
            winsound.Beep(1000, 800)   # Frequency, duration
            winsound.Beep(1200, 800)
            winsound.Beep(1500, 800)
        else:
            # Cross platform fallback
            wx.Bell()

    def timer_complete(self):
        self.is_running = False
        self.remaining_time = 0
        self.start_btn.SetLabel("▶ Start")
        
        # Set progress to 100%
        if hasattr(self, 'progress_gauge'):
            self.progress_gauge.SetValue(100)

        self.play_alarm()

        wx.MessageBox(
            f"Timer Completed!\n\nTask: {self.desc_input.GetValue()}",
            "Timer", wx.OK | wx.ICON_INFORMATION
        )