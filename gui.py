import wx
import wx.adv
from database import DatabaseManager
from api_client import ZenQuotesAPI
from emotional_tracker import EmotionalTracker
from timer import TimerPanel
from tasks import TaskManager
import theme


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Personal Productivity App", size=(1000, 700))
        self.db_manager = DatabaseManager()
        self.api_client = ZenQuotesAPI()
        # Initialize with None, we'll create when needed with correct parent
        self.emotional_tracker = None
        self.task_manager = TaskManager(self, self.db_manager)
        
        self.create_ui()
        self.Centre()
    
    def create_ui(self):
        # Create splitter window
        self.splitter = wx.SplitterWindow(self)
        
        # Create sidebar
        self.sidebar_panel = wx.Panel(self.splitter)
        self.sidebar_panel.SetBackgroundColour(theme.SIDEBAR_BG)
        
        # Create main content area
        self.content_panel = wx.Panel(self.splitter)
        self.content_panel.SetBackgroundColour(theme.CONTENT_BG)
        
        # Create a sizer for the content panel
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel.SetSizer(self.content_sizer)
        
        # Set up splitter
        self.splitter.SplitVertically(self.sidebar_panel, self.content_panel, 200)
        self.splitter.SetMinimumPaneSize(200)
        
        self.create_sidebar()
        
        # Show home page by default
        self.show_home_page()
    
    def create_sidebar(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # App title
        title = wx.StaticText(self.sidebar_panel, label="Study Zone")
        title.SetFont(theme.FONT_TITLE)
        title.SetForegroundColour(theme.TITLE_TEXT)
        vbox.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        
        vbox.Add(wx.StaticLine(self.sidebar_panel), 0, wx.EXPAND | wx.ALL, 5)
        
        # Navigation buttons
        nav_buttons = [
            ("Home", self.show_home_page),
            ("Add Task", self.show_add_task_page),
            ("View Tasks", self.show_view_tasks_page),
            ("Timer", self.show_timer_page),
            ("Emotional Tracker", self.show_emotional_tracker_page)
        ]
        
        for label, handler in nav_buttons:
            btn = wx.Button(self.sidebar_panel, label=label)
            btn.SetFont(theme.FONT_NORMAL)
            btn.SetBackgroundColour(theme.BUTTON_SECONDARY_BG)
            btn.SetForegroundColour(theme.BUTTON_TEXT)
            btn.SetMinSize((180, 35))
            btn.Bind(wx.EVT_BUTTON, handler)
            vbox.Add(btn, 0, wx.ALL | wx.EXPAND, 5)
        
        self.sidebar_panel.SetSizer(vbox)
    
    def clear_content(self):
        # Destroy all children of content panel
        for child in self.content_panel.GetChildren():
            child.Destroy()
        
        # Clear and reset the sizer
        self.content_sizer.Clear(delete_windows=True)
        self.content_panel.SetSizer(self.content_sizer)
    
    def show_home_page(self, event=None):
        self.clear_content()
        
        # Thought of the day
        thought_panel = wx.Panel(self.content_panel)
        thought_panel.SetBackgroundColour(theme.HIGHLIGHT_COLOR)
        thought_sizer = wx.BoxSizer(wx.VERTICAL)
        
        thought_title = wx.StaticText(thought_panel, label="Thought of the Day")
        thought_title.SetFont(theme.get_font(14, wx.FONTWEIGHT_BOLD))
        thought_title.SetForegroundColour(theme.SUB_TEXT)
        thought_sizer.Add(thought_title, 0, wx.ALL, 10)
        
        thought_text = self.api_client.get_thought_of_day()
        thought_label = wx.StaticText(thought_panel, label=thought_text)
        thought_label.SetFont(theme.get_font(12, wx.FONTWEIGHT_NORMAL, italic=True))
        thought_label.Wrap(600)
        thought_sizer.Add(thought_label, 0, wx.ALL | wx.EXPAND, 10)
        
        thought_panel.SetSizer(thought_sizer)
        self.content_sizer.Add(thought_panel, 0, wx.ALL | wx.EXPAND, 15)
        
        self.content_sizer.Add(wx.StaticLine(self.content_panel), 0, wx.EXPAND | wx.ALL, 10)
        
        # Calendar
        calendar_label = wx.StaticText(self.content_panel, label="Calendar")
        calendar_label.SetFont(theme.FONT_SUBTITLE)
        calendar_label.SetForegroundColour(theme.NORMAL_TEXT)
        self.content_sizer.Add(calendar_label, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        self.calendar = wx.adv.CalendarCtrl(self.content_panel, style=wx.adv.CAL_SHOW_HOLIDAYS)
        self.calendar.Bind(wx.adv.EVT_CALENDAR_SEL_CHANGED, self.on_date_selected)
        self.content_sizer.Add(self.calendar, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        # Tasks for selected date
        self.tasks_label = wx.StaticText(self.content_panel, label="Tasks for selected date:")
        self.tasks_label.SetFont(theme.get_font(12, wx.FONTWEIGHT_BOLD))
        self.tasks_label.SetForegroundColour(theme.NORMAL_TEXT)
        self.content_sizer.Add(self.tasks_label, 0, wx.ALL, 10)
        
        self.tasks_list = wx.ListBox(self.content_panel, style=wx.LB_SINGLE)
        self.tasks_list.SetBackgroundColour(wx.WHITE)
        self.content_sizer.Add(self.tasks_list, 1, wx.ALL | wx.EXPAND, 10)
        
        # Show today's tasks initially
        self.update_tasks_for_date(self.calendar.GetDate().FormatISODate())
        
        # Force layout update
        self.content_panel.Layout()
        self.Layout()
    
    def on_date_selected(self, event):
        selected_date = self.calendar.GetDate().FormatISODate()
        self.update_tasks_for_date(selected_date)
    
    def update_tasks_for_date(self, date):
        tasks = self.db_manager.get_tasks_by_date(date)
        self.tasks_list.Clear()
        
        if not tasks:
            self.tasks_list.Append("No tasks for this date")
        else:
            for task in tasks:
                status = "✅ Completed" if task[4] else "⭕ Pending"
                self.tasks_list.Append(f"{status}: {task[1]}")
        
        self.tasks_label.SetLabel(f"Tasks for {date}:")
    
    def show_add_task_page(self, event=None):
        self.clear_content()
        panel = self.task_manager.create_add_task_panel()
        # Make sure the panel has content_panel as parent
        panel.Reparent(self.content_panel)
        self.content_sizer.Add(panel, 1, wx.EXPAND)
        self.content_panel.Layout()
        self.Layout()
    
    def show_view_tasks_page(self, event=None):
        self.clear_content()
        panel = self.task_manager.create_view_tasks_panel()
        # Make sure the panel has content_panel as parent
        panel.Reparent(self.content_panel)
        self.content_sizer.Add(panel, 1, wx.EXPAND)
        self.content_panel.Layout()
        self.Layout()
    
    def show_timer_page(self, event=None):
        self.clear_content()
    
        # Create TimerPanel directly in content_panel
        timer_panel = TimerPanel(self.content_panel)
        self.content_sizer.Add(timer_panel, 1, wx.EXPAND)
    
        self.content_panel.Layout()
        self.Layout()
    
    def show_emotional_tracker_page(self, event=None):
        self.clear_content()
        
        # Create EmotionalTracker with content_panel as parent
        emotional_tracker = EmotionalTracker(self.content_panel, self.db_manager)
        panel = emotional_tracker.create_tracker_panel()
        self.content_sizer.Add(panel, 1, wx.EXPAND)
        
        self.content_panel.Layout()
        self.Layout()