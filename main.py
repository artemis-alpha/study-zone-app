import wx
from gui import MainFrame

class TaskManagerApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame()
        self.frame.Show()
        return True

if __name__ == "__main__":
    app = TaskManagerApp()
    app.MainLoop()


