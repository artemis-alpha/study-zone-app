# theme.py
import wx

# ---- APP COLORS ----
APP_BG = wx.Colour(245, 247, 250)        # light grey
SIDEBAR_BG = wx.Colour(207, 177, 251)       # dark blue
CONTENT_BG = wx.Colour(255, 255, 255)    # white

TITLE_TEXT = wx.Colour(255, 255, 255)
NORMAL_TEXT = wx.Colour(40, 40, 40)
SUB_TEXT = wx.Colour(100, 100, 100)

BUTTON_PRIMARY_BG = wx.Colour(76, 175, 80)       # green
BUTTON_SECONDARY_BG = wx.Colour(66, 133, 244)    # blue
BUTTON_TEXT = wx.WHITE
BUTTON_WARNING_BG = wx.Colour(244, 67, 54)

TIMER_COLOR = wx.Colour(33, 150, 243)    # blue
EMOTION_COLOR = wx.Colour(233, 30, 99)   # pink
TASK_COLOR = wx.Colour(255, 152, 0)      # orange

# Light backgrounds for panels
TIMER_PANEL_BG = wx.Colour(227, 242, 253)        # light blue
EMOTION_PANEL_BG = wx.Colour(255, 228, 235)      # light pink
TASK_PANEL_BG = wx.Colour(255, 243, 224)         # light orange
HOME_PANEL_BG = wx.Colour(255, 255, 255)         # white

HIGHLIGHT_COLOR = wx.Colour(240, 240, 240)

BORDER_COLOR = wx.Colour(220, 220, 220)

# Helper function for fonts
def get_font(size=10, weight=wx.FONTWEIGHT_NORMAL, italic=False):
    font = wx.Font()
    font.SetPointSize(size)
    font.SetFamily(wx.FONTFAMILY_DEFAULT)
    font.SetStyle(wx.FONTSTYLE_NORMAL)
    font.SetWeight(weight)
    if italic:
        font.SetStyle(wx.FONTSTYLE_ITALIC)
    return font

# Predefined fonts
FONT_TITLE = get_font(18, wx.FONTWEIGHT_BOLD)
FONT_SUBTITLE = get_font(14, wx.FONTWEIGHT_BOLD)
FONT_NORMAL = get_font(10, wx.FONTWEIGHT_NORMAL)
FONT_SMALL = get_font(9, wx.FONTWEIGHT_NORMAL)

BORDER_RADIUS = 8
CONTENT_PADDING = 10
