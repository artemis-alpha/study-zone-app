import wx
import wx.adv
import theme


class TaskManager:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
    
    def create_add_task_panel(self):
        panel = wx.Panel(self.parent)
        panel.SetBackgroundColour(theme.TASK_PANEL_BG)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="Add New Task")
        title.SetFont(theme.FONT_SUBTITLE)
        title.SetForegroundColour(theme.NORMAL_TEXT)
        vbox.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        
        # Create a white content panel for better contrast
        content_panel = wx.Panel(panel)
        content_panel.SetBackgroundColour(wx.WHITE)
        content_vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Task title
        title_label = wx.StaticText(content_panel, label="Task Title:")
        title_label.SetFont(theme.get_font(12, wx.FONTWEIGHT_BOLD))
        title_label.SetForegroundColour(theme.SUB_TEXT)
        content_vbox.Add(title_label, 0, wx.ALL, 10)
        
        self.title_input = wx.TextCtrl(content_panel)
        self.title_input.SetFont(theme.FONT_NORMAL)
        content_vbox.Add(self.title_input, 0, wx.ALL | wx.EXPAND, 10)
        
        # Task description
        desc_label = wx.StaticText(content_panel, label="Description:")
        desc_label.SetFont(theme.get_font(12, wx.FONTWEIGHT_BOLD))
        desc_label.SetForegroundColour(theme.SUB_TEXT)
        content_vbox.Add(desc_label, 0, wx.ALL, 10)
        
        self.desc_input = wx.TextCtrl(content_panel, style=wx.TE_MULTILINE, size=(-1, 100))
        self.desc_input.SetFont(theme.FONT_NORMAL)
        content_vbox.Add(self.desc_input, 0, wx.ALL | wx.EXPAND, 10)
        
        # Due date
        date_label = wx.StaticText(content_panel, label="Due Date:")
        date_label.SetFont(theme.get_font(12, wx.FONTWEIGHT_BOLD))
        date_label.SetForegroundColour(theme.SUB_TEXT)
        content_vbox.Add(date_label, 0, wx.ALL, 10)
        
        self.date_picker = wx.adv.DatePickerCtrl(content_panel, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        content_vbox.Add(self.date_picker, 0, wx.ALL | wx.EXPAND, 10)
        
        # Add the content panel to main panel
        content_panel.SetSizer(content_vbox)
        vbox.Add(content_panel, 1, wx.ALL | wx.EXPAND, 10)
        
        # Add button
        add_btn = wx.Button(panel, label="Add Task")
        add_btn.SetBackgroundColour(theme.BUTTON_PRIMARY_BG)
        add_btn.SetForegroundColour(theme.BUTTON_TEXT)
        add_btn.SetFont(theme.get_font(11, wx.FONTWEIGHT_BOLD))
        add_btn.SetMinSize((120, 35))
        add_btn.Bind(wx.EVT_BUTTON, self.on_add_task)
        
        vbox.Add(add_btn, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        panel.SetSizer(vbox)
        panel.Layout()
        return panel
    
    def create_view_tasks_panel(self):
        panel = wx.Panel(self.parent)
        panel.SetBackgroundColour(theme.TASK_PANEL_BG)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="All Tasks")
        title.SetFont(theme.FONT_SUBTITLE)
        title.SetForegroundColour(theme.NORMAL_TEXT)
        vbox.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        
        # Create a white panel for the list
        list_panel = wx.Panel(panel)
        list_panel.SetBackgroundColour(wx.WHITE)
        list_vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Tasks list
        self.tasks_list = wx.ListBox(list_panel, style=wx.LB_SINGLE | wx.LB_NEEDED_SB)
        self.tasks_list.SetBackgroundColour(wx.WHITE)
        self.tasks_list.SetFont(theme.FONT_NORMAL)
        
        self.tasks_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_task_selected)
        list_vbox.Add(self.tasks_list, 1, wx.ALL | wx.EXPAND, 10)
        
        list_panel.SetSizer(list_vbox)
        vbox.Add(list_panel, 1, wx.ALL | wx.EXPAND, 10)
        
        # Refresh button
        refresh_btn = wx.Button(panel, label="Refresh")
        refresh_btn.SetBackgroundColour(theme.BUTTON_SECONDARY_BG)
        refresh_btn.SetForegroundColour(theme.BUTTON_TEXT)
        refresh_btn.SetFont(theme.FONT_NORMAL)
        refresh_btn.SetMinSize((100, 35))
        refresh_btn.Bind(wx.EVT_BUTTON, self.refresh_tasks)
        
        vbox.Add(refresh_btn, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        panel.SetSizer(vbox)
        panel.Layout()
        self.refresh_tasks()
        return panel
    
    def on_add_task(self, event):
        title = self.title_input.GetValue().strip()
        description = self.desc_input.GetValue().strip()
        due_date = self.date_picker.GetValue().FormatISODate()
        
        if not title:
            wx.MessageBox("Please enter a task title!", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        self.db_manager.add_task(title, description, due_date)
        wx.MessageBox("Task added successfully!", "Success", wx.OK | wx.ICON_INFORMATION)
        
        # Clear inputs
        self.title_input.SetValue("")
        self.desc_input.SetValue("")
    
    def refresh_tasks(self, event=None):
        self.tasks_list.Clear()
        tasks = self.db_manager.get_all_tasks()
        for task in tasks:
            status = "✅" if task[4] else "⭕"
            display_text = f"{status} {task[1]} {task[3]}"
            # Store task ID as client data
            self.tasks_list.Append(display_text)
            # Set client data for the last appended item
            self.tasks_list.SetClientData(self.tasks_list.GetCount() - 1, task[0])
    
    def on_task_selected(self, event):
        selection = self.tasks_list.GetSelection()
        if selection == wx.NOT_FOUND:
            return
        
        task_id = self.tasks_list.GetClientData(selection)
        if task_id is None:
            return
        
        dialog = EditTaskDialog(self.parent, self, task_id)
        if dialog.ShowModal() == wx.ID_OK:
            self.refresh_tasks()
        dialog.Destroy()


class EditTaskDialog(wx.Dialog):
    def __init__(self, parent, task_manager, task_id):
        super().__init__(parent, title="Edit Task", size=(500, 400))
        self.task_manager = task_manager
        self.task_id = task_id
        self.task = self.task_manager.db_manager.get_task(task_id)
        self.create_ui()
        self.Layout()
        self.Fit()  # Adjust size to fit contents

    def create_ui(self):
        # Main panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour(theme.TASK_PANEL_BG)
        
        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="Edit Task")
        title.SetFont(theme.FONT_SUBTITLE)
        title.SetForegroundColour(theme.NORMAL_TEXT)
        main_sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        
        # Create a white content panel
        content_panel = wx.Panel(panel)
        content_panel.SetBackgroundColour(wx.WHITE)
        content_vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Task title
        title_label = wx.StaticText(content_panel, label="Task Title:")
        title_label.SetFont(theme.get_font(11, wx.FONTWEIGHT_BOLD))
        title_label.SetForegroundColour(theme.SUB_TEXT)
        content_vbox.Add(title_label, 0, wx.ALL, 8)
        
        self.title_input = wx.TextCtrl(content_panel, value=self.task[1])
        self.title_input.SetFont(theme.FONT_NORMAL)
        content_vbox.Add(self.title_input, 0, wx.ALL | wx.EXPAND, 8)
        
        # Task description
        desc_label = wx.StaticText(content_panel, label="Description:")
        desc_label.SetFont(theme.get_font(11, wx.FONTWEIGHT_BOLD))
        desc_label.SetForegroundColour(theme.SUB_TEXT)
        content_vbox.Add(desc_label, 0, wx.ALL, 8)
        
        self.desc_input = wx.TextCtrl(content_panel, value=self.task[2] or "", 
                                     style=wx.TE_MULTILINE, size=(-1, 60))
        self.desc_input.SetFont(theme.FONT_NORMAL)
        content_vbox.Add(self.desc_input, 0, wx.ALL | wx.EXPAND, 8)
        
        # Due date
        date_label = wx.StaticText(content_panel, label="Due Date:")
        date_label.SetFont(theme.get_font(11, wx.FONTWEIGHT_BOLD))
        date_label.SetForegroundColour(theme.SUB_TEXT)
        content_vbox.Add(date_label, 0, wx.ALL, 8)
        
        # Try to parse the date from the task
        due_date = self.task[3]
        
        # Create date picker with compact size
        self.date_picker = wx.adv.DatePickerCtrl(content_panel, 
                                                style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY,
                                                size=(200, -1))
        
        # Set the date
        if due_date:
            try:
                # Parse ISO date string (YYYY-MM-DD)
                year, month, day = map(int, due_date.split('-'))
                wx_date = wx.DateTime()
                wx_date.Set(day, month - 1, year)  # month is 0-based in wxDateTime
                if wx_date.IsValid():
                    self.date_picker.SetValue(wx_date)
                else:
                    self.date_picker.SetValue(wx.DateTime.Now())
            except (ValueError, IndexError):
                self.date_picker.SetValue(wx.DateTime.Now())
        else:
            self.date_picker.SetValue(wx.DateTime.Now())
        
        content_vbox.Add(self.date_picker, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 8)
        
        # Completed checkbox
        self.completed_cb = wx.CheckBox(content_panel, label="Task Completed")
        self.completed_cb.SetFont(theme.FONT_NORMAL)
        self.completed_cb.SetValue(bool(self.task[4]))
        content_vbox.Add(self.completed_cb, 0, wx.ALL, 15)
        
        content_panel.SetSizer(content_vbox)
        main_sizer.Add(content_panel, 1, wx.ALL | wx.EXPAND, 10)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        save_btn = wx.Button(panel, label="Save")
        delete_btn = wx.Button(panel, label="Delete")
        cancel_btn = wx.Button(panel, label="Cancel")
        
        # Style buttons
        save_btn.SetBackgroundColour(theme.BUTTON_PRIMARY_BG)
        save_btn.SetForegroundColour(theme.BUTTON_TEXT)
        save_btn.SetFont(theme.FONT_NORMAL)
        save_btn.SetMinSize((80, 30))
        
        delete_btn.SetBackgroundColour(theme.BUTTON_WARNING_BG)
        delete_btn.SetForegroundColour(theme.BUTTON_TEXT)
        delete_btn.SetFont(theme.FONT_NORMAL)
        delete_btn.SetMinSize((80, 30))
        
        cancel_btn.SetBackgroundColour(theme.BUTTON_SECONDARY_BG)
        cancel_btn.SetForegroundColour(theme.BUTTON_TEXT)
        cancel_btn.SetFont(theme.FONT_NORMAL)
        cancel_btn.SetMinSize((80, 30))
        
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        cancel_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        
        button_sizer.Add(save_btn, 0, wx.ALL, 5)
        button_sizer.Add(delete_btn, 0, wx.ALL, 5)
        button_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        panel.SetSizer(main_sizer)
        panel.Layout()

        # Set the dialog's sizer to include the panel (this fixes the expansion issue)
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        dialog_sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(dialog_sizer)
        self.Layout()

    def on_save(self, event):
        title = self.title_input.GetValue().strip()
        description = self.desc_input.GetValue().strip()
        due_date = self.date_picker.GetValue().FormatISODate()
        completed = 1 if self.completed_cb.GetValue() else 0
        
        if not title:
            wx.MessageBox("Please enter a task title!", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        self.task_manager.db_manager.update_task(self.task_id, title, description, due_date, completed)
        self.EndModal(wx.ID_OK)
    
    def on_delete(self, event):
        confirm = wx.MessageBox("Are you sure you want to delete this task?", "Confirm Delete", 
                              wx.YES_NO | wx.ICON_QUESTION)
        if confirm == wx.YES:
            self.task_manager.db_manager.delete_task(self.task_id)
            self.EndModal(wx.ID_OK)