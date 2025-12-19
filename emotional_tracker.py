import wx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import theme


class EmotionalTracker:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        
    def create_tracker_panel(self):
        panel = wx.Panel(self.parent)
        panel.SetBackgroundColour(theme.EMOTION_PANEL_BG)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="Emotional Tracker")
        title.SetFont(theme.FONT_SUBTITLE)
        title.SetForegroundColour(theme.NORMAL_TEXT)
        sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        
        # Mood selection
        mood_label = wx.StaticText(panel, label="How are you feeling today?")
        mood_label.SetFont(theme.get_font(12, wx.FONTWEIGHT_BOLD))
        mood_label.SetForegroundColour(theme.SUB_TEXT)
        sizer.Add(mood_label, 0, wx.ALL, 10)
        
        self.mood_choices = ["Happy", "Sad", "Anxious", "Excited", 
                            "Tired", "Angry", "Peaceful", "Stressed"]
        self.mood_combo = wx.ComboBox(panel, choices=self.mood_choices, 
                                      style=wx.CB_READONLY, size=(300, -1))
        self.mood_combo.SetFont(theme.FONT_NORMAL)
        sizer.Add(self.mood_combo, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        
        # Rating
        rating_label = wx.StaticText(panel, label="Rate your day (1-10):")
        rating_label.SetFont(theme.get_font(12, wx.FONTWEIGHT_BOLD))
        rating_label.SetForegroundColour(theme.SUB_TEXT)
        sizer.Add(rating_label, 0, wx.ALL, 10)
        
        self.rating_slider = wx.Slider(panel, minValue=1, maxValue=10, value=5,
                                       style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.rating_slider.SetTickFreq(1)
        sizer.Add(self.rating_slider, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        
        # Notes
        notes_label = wx.StaticText(panel, label="Notes (optional):")
        notes_label.SetFont(theme.get_font(12, wx.FONTWEIGHT_BOLD))
        notes_label.SetForegroundColour(theme.SUB_TEXT)
        sizer.Add(notes_label, 0, wx.ALL, 10)
        
        self.notes_textctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1, 80))
        self.notes_textctrl.SetFont(theme.FONT_NORMAL)
        sizer.Add(self.notes_textctrl, 0, wx.ALL | wx.EXPAND, 10)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        save_btn = wx.Button(panel, label="Save Entry")
        view_btn = wx.Button(panel, label="View Analysis")
        
        save_btn.SetBackgroundColour(theme.EMOTION_COLOR)
        save_btn.SetForegroundColour(theme.BUTTON_TEXT)
        save_btn.SetFont(theme.get_font(11, wx.FONTWEIGHT_BOLD))
        
        view_btn.SetBackgroundColour(theme.BUTTON_SECONDARY_BG)
        view_btn.SetForegroundColour(theme.BUTTON_TEXT)
        view_btn.SetFont(theme.get_font(11, wx.FONTWEIGHT_BOLD))
        
        save_btn.Bind(wx.EVT_BUTTON, self.on_save_entry)
        view_btn.Bind(wx.EVT_BUTTON, self.on_view_analysis)
        
        button_sizer.Add(save_btn, 0, wx.ALL, 5)
        button_sizer.Add(view_btn, 0, wx.ALL, 5)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)
        
        panel.SetSizer(sizer)
        return panel
    
    def on_save_entry(self, event):
        mood = self.mood_combo.GetValue()
        rating = self.rating_slider.GetValue()
        notes = self.notes_textctrl.GetValue()
        
        if not mood:
            wx.MessageBox("Please select a mood!", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        self.db_manager.add_emotional_entry(mood, rating, notes)
        wx.MessageBox("Entry saved!", "Success", wx.OK | wx.ICON_INFORMATION)
        
        self.mood_combo.SetValue("")
        self.rating_slider.SetValue(5)
        self.notes_textctrl.SetValue("")
    
    def on_view_analysis(self, event):
        dialog = AnalysisDialog(self.parent, self.db_manager)
        dialog.ShowModal()
        dialog.Destroy()


class AnalysisDialog(wx.Dialog):
    def __init__(self, parent, db_manager):
        super().__init__(parent, title="Emotional Analysis - Last 4 Days", size=(800, 500))
        self.db_manager = db_manager
        self.SetBackgroundColour(wx.WHITE)
        self.create_ui()
        self.load_data()
    
    def create_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Left side - Pie chart
        left_panel = wx.Panel(panel)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        chart_title = wx.StaticText(left_panel, label="Mood Distribution")
        chart_title.SetFont(theme.get_font(14, wx.FONTWEIGHT_BOLD))
        left_sizer.Add(chart_title, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        self.figure = Figure(figsize=(4, 3), dpi=100)
        self.canvas = FigureCanvas(left_panel, -1, self.figure)
        left_sizer.Add(self.canvas, 1, wx.ALL | wx.EXPAND, 10)
        
        left_panel.SetSizer(left_sizer)
        sizer.Add(left_panel, 1, wx.ALL | wx.EXPAND, 10)
        
        # Right side - Table
        right_panel = wx.Panel(panel)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        table_title = wx.StaticText(right_panel, label="Daily Ratings")
        table_title.SetFont(theme.get_font(14, wx.FONTWEIGHT_BOLD))
        right_sizer.Add(table_title, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        # Create list control for table
        self.list_ctrl = wx.ListCtrl(right_panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list_ctrl.InsertColumn(0, "Date", width=100)
        self.list_ctrl.InsertColumn(1, "Mood", width=100)
        self.list_ctrl.InsertColumn(2, "Rating", width=80)
        self.list_ctrl.InsertColumn(3, "Notes", width=200)
        
        right_sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        
        # Close button
        close_btn = wx.Button(right_panel, label="Close")
        close_btn.SetBackgroundColour(theme.BUTTON_SECONDARY_BG)
        close_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))
        right_sizer.Add(close_btn, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        right_panel.SetSizer(right_sizer)
        sizer.Add(right_panel, 1, wx.ALL | wx.EXPAND, 10)
        
        panel.SetSizer(sizer)
        
        # Dialog sizer
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        dialog_sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(dialog_sizer)
    
    def load_data(self):
        # Get data for last 4 days
        entries = self.db_manager.get_recent_emotional_entries(4)
        
        # Clear previous data
        self.list_ctrl.DeleteAllItems()
        self.figure.clear()
        
        if not entries:
            # No data message
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "No data\nfor last 4 days", 
                   ha='center', va='center', fontsize=14)
            ax.axis('off')
            self.canvas.draw()
            return
        
        # Prepare mood data for pie chart
        mood_counts = {}
        for entry in entries:
            mood = entry[2]
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        # Create pie chart
        ax = self.figure.add_subplot(111)
        if mood_counts:
            labels = list(mood_counts.keys())
            sizes = list(mood_counts.values())
            
            # Simple color palette
            colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', 
                     '#FF99CC', '#99FFFF', '#FFFF99', '#CC99FF']
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                  colors=colors[:len(labels)])
            ax.set_title('Last 4 Days Moods', fontsize=12)
            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, "No mood data", ha='center', va='center', fontsize=12)
            ax.axis('off')
        
        self.canvas.draw()
        
        # Fill table with data
        for i, entry in enumerate(entries):
            date_str = entry[1]
            mood = entry[2]
            rating = entry[3]
            notes = entry[4] if entry[4] else ""
            
            index = self.list_ctrl.InsertItem(i, date_str)
            self.list_ctrl.SetItem(index, 1, mood)
            self.list_ctrl.SetItem(index, 2, str(rating))
            self.list_ctrl.SetItem(index, 3, notes)
            
            # Color code rating
            if rating >= 8:
                self.list_ctrl.SetItemTextColour(index, wx.Colour(0, 150, 0))  # Green
            elif rating >= 5:
                self.list_ctrl.SetItemTextColour(index, wx.Colour(200, 120, 0))  # Orange
            else:
                self.list_ctrl.SetItemTextColour(index, wx.Colour(200, 0, 0))  # Red