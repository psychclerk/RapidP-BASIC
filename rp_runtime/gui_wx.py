"""
RapidP-BASIC wxPython GUI Runtime
Mirrors the interface of gui.py (tkinter) for wxPython backend
"""
import wx
import wx.grid as wxgrid
import datetime
import os

# Global app instance
_app = None


def _bgr_to_wx_colour(value):
    """Convert RapidP BGR integer to wx.Colour."""
    if isinstance(value, int):
        r = value & 0xFF
        g = (value >> 8) & 0xFF
        b = (value >> 16) & 0xFF
        return wx.Colour(r, g, b)
    return None

def get_app():
    global _app
    if _app is None:
        _app = wx.App(False)
    return _app

def run_app():
    app = get_app()
    app.MainLoop()

def quit_app():
    global _app
    if _app:
        # Close all open frames
        for top in wx.GetTopLevelWindows():
            top.Close()
        _app.ExitMainLoop()
        _app = None

# Base Component Class
class PComponent:
    def __init__(self, handle=None):
        self.handle = handle
        self._events = {}
        self._tag = None
        self._font = PFont(owner=self)
    
    def set_tag(self, tag):
        self._tag = tag
    
    def get_tag(self):
        return self._tag
    
    def bind_event(self, event_name, callback):
        self._events[event_name] = callback
    
    def trigger_event(self, event_name, *args):
        if event_name in self._events:
            self._events[event_name](*args)


class PFont:
    """RapidP-compatible font object for wx controls."""
    def __init__(self, owner=None):
        self._owner = owner
        self._name = "Segoe UI" if os.name == "nt" else "Helvetica"
        self._size = 9
        self._color = 0
        self._bold = 0
        self._italic = 0
        self._underline = 0
        self._strikeout = 0

    def _apply(self):
        if self._owner is not None and hasattr(self._owner, "_apply_font"):
            self._owner._apply_font()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)
        self._apply()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = int(value)
        self._apply()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = int(value) if value else 0
        self._apply()

    @property
    def bold(self):
        return self._bold

    @bold.setter
    def bold(self, value):
        self._bold = int(value)
        self._apply()

    @property
    def italic(self):
        return self._italic

    @italic.setter
    def italic(self, value):
        self._italic = int(value)
        self._apply()

    @property
    def underline(self):
        return self._underline

    @underline.setter
    def underline(self, value):
        self._underline = int(value)
        self._apply()

    @property
    def strikeout(self):
        return self._strikeout

    @strikeout.setter
    def strikeout(self, value):
        self._strikeout = int(value)
        self._apply()

# Form
class PForm(PComponent):
    def __init__(self, parent=None):
        # Ensure app is created first
        get_app()
        self._frame = wx.Frame(parent, -1, "Form")
        super().__init__(self._frame)
        self._frame.SetSize(800, 600)
        self._frame.SetPosition((100, 100))
        self._panel = wx.Panel(self._frame)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._panel.SetSizer(self._sizer)
        
        # Bind close event
        self._frame.Bind(wx.EVT_CLOSE, self._on_close)
        
        self.caption = "Form"
        self.width = 800
        self.height = 600
        self.left = 100
        self.top = 100

    def _on_close(self, event):
        self.trigger_event('onclose')
        event.Skip()

    def show(self):
        self._frame.Show(True)
        # Trigger onload after showing
        wx.CallAfter(self.trigger_event, 'onload')

    def showmodal(self):
        # wxPython modal is different, we simulate by disabling parent if any
        self._frame.ShowModal() if self._frame.GetParent() else self.show()

    def hide(self):
        self._frame.Hide()

    def close(self):
        self._frame.Close()

    # Properties
    def get_caption(self):
        return self._frame.GetTitle()
    def set_caption(self, val):
        self._frame.SetTitle(val)
    caption = property(get_caption, set_caption)

    def get_width(self):
        return self._frame.GetSize().width
    def set_width(self, val):
        sz = self._frame.GetSize()
        self._frame.SetSize(val, sz.height)
    width = property(get_width, set_width)

    def get_height(self):
        return self._frame.GetSize().height
    def set_height(self, val):
        sz = self._frame.GetSize()
        self._frame.SetSize(sz.width, val)
    height = property(get_height, set_height)

    def get_left(self):
        return self._frame.GetPosition().x
    def set_left(self, val):
        pos = self._frame.GetPosition()
        self._frame.SetPosition((val, pos.y))
    left = property(get_left, set_left)

    def get_top(self):
        return self._frame.GetPosition().y
    def set_top(self, val):
        pos = self._frame.GetPosition()
        self._frame.SetPosition((pos.x, val))
    top = property(get_top, set_top)

    def center(self):
        """Center the form on the screen"""
        self._frame.Centre()

# Common properties mixin for controls
class ControlMixin:
    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._font = value
        self._apply_font()

    def _apply_font(self):
        if not getattr(self, "handle", None):
            return
        try:
            weight = wx.FONTWEIGHT_BOLD if self._font.bold else wx.FONTWEIGHT_NORMAL
            style = wx.FONTSTYLE_ITALIC if self._font.italic else wx.FONTSTYLE_NORMAL
            font = wx.Font(
                self._font.size,
                wx.FONTFAMILY_DEFAULT,
                style,
                weight,
                bool(self._font.underline),
                self._font.name
            )
            self.handle.SetFont(font)
            fg = _bgr_to_wx_colour(self._font.color)
            if fg is not None:
                self.handle.SetForegroundColour(fg)
        except Exception:
            # Keep behavior non-fatal for controls that don't support font operations.
            pass

    def get_left(self):
        # wx doesn't expose left/top easily without sizers, using dummy for now or GetPosition if not in sizer
        # For proper layout, wx uses Sizers. RapidP BASIC usually uses absolute.
        # We will try to support absolute positioning by not using sizers for children or using Fixed BoxSizers
        return getattr(self, '_left', 0)
    
    def set_left(self, val):
        self._left = val
        if hasattr(self, 'handle') and self.handle:
            # If using sizers, this might be ignored unless we use spacer or specific logic
            # For simplicity in migration, we assume absolute positioning logic needs to be enforced
            # But wx strongly prefers sizers. We will try SetPosition if possible.
            try:
                self.handle.Move(val, self.get_top())
            except: pass

    def get_top(self):
        return getattr(self, '_top', 0)

    def set_top(self, val):
        self._top = val
        if hasattr(self, 'handle') and self.handle:
            try:
                self.handle.Move(self.get_left(), val)
            except: pass

    def get_width(self):
        return getattr(self, '_width', 100)

    def set_width(self, val):
        self._width = val
        if hasattr(self, 'handle') and self.handle:
            self.handle.SetSize(val, self.get_height())

    def get_height(self):
        return getattr(self, '_height', 30)

    def set_height(self, val):
        self._height = val
        if hasattr(self, 'handle') and self.handle:
            self.handle.SetSize(self.get_width(), val)

    def get_enabled(self):
        return self.handle.IsEnabled() if self.handle else True
    def set_enabled(self, val):
        if self.handle: self.handle.Enable(val)
    enabled = property(get_enabled, set_enabled)

    def get_visible(self):
        return self.handle.IsShown() if self.handle else True
    def set_visible(self, val):
        if self.handle: 
            if val: self.handle.Show()
            else: self.handle.Hide()
    visible = property(get_visible, set_visible)

# Helper function to get the actual wx parent from a RapidP component
def _get_wx_parent(parent):
    """Get the actual wx widget to use as parent for child controls."""
    if hasattr(parent, '_panel'):
        return parent._panel
    elif hasattr(parent, 'handle'):
        return parent.handle
    else:
        return parent

# Label
class PLabel(PComponent, ControlMixin):
    def __init__(self, parent):
        real_parent = _get_wx_parent(parent)
        handle = wx.StaticText(real_parent, -1, "")
        super().__init__(handle)
        self.parent = parent
        self._caption = ""
        self._font = PFont(owner=self)
        
    def get_caption(self):
        return self._caption
    def set_caption(self, val):
        self._caption = val
        if self.handle: self.handle.SetLabel(val)
    caption = property(get_caption, set_caption)

# Button
class PButton(PComponent, ControlMixin):
    def __init__(self, parent):
        real_parent = _get_wx_parent(parent)
        handle = wx.Button(real_parent, -1, "Button")
        super().__init__(handle)
        self.parent = parent
        handle.Bind(wx.EVT_BUTTON, lambda e: self.trigger_event('onclick'))

    def get_caption(self):
        return self.handle.GetLabel()
    def set_caption(self, val):
        self.handle.SetLabel(val)
    caption = property(get_caption, set_caption)

# Edit (TextBox)
class PEdit(PComponent, ControlMixin):
    def __init__(self, parent):
        real_parent = _get_wx_parent(parent)
        handle = wx.TextCtrl(real_parent, -1, "")
        super().__init__(handle)
        self.parent = parent
        handle.Bind(wx.EVT_TEXT, lambda e: self.trigger_event('onchange'))

    def get_text(self):
        return self.handle.GetValue()
    def set_text(self, val):
        self.handle.SetValue(val)
    text = property(get_text, set_text)
    
    # Alias for compatibility
    caption = property(get_text, set_text)

# ComboBox
class PComboBox(PComponent, ControlMixin):
    def __init__(self, parent):
        real_parent = _get_wx_parent(parent)
        handle = wx.ComboBox(real_parent, -1, "", choices=[], style=wx.CB_DROPDOWN)
        super().__init__(handle)
        self.parent = parent
        handle.Bind(wx.EVT_COMBOBOX, lambda e: self.trigger_event('onchange'))

    def additems(self, items):
        # items can be list or string separated by something? Assuming list
        if isinstance(items, str):
            # Handle rapidp string array simulation if needed, usually passed as list
            pass 
        self.handle.AppendItems(items)
    
    def clear(self):
        self.handle.Clear()
        
    def get_selectedindex(self):
        return self.handle.GetSelection()
    def set_selectedindex(self, val):
        self.handle.SetSelection(val)
    selectedindex = property(get_selectedindex, set_selectedindex)
    
    def get_text(self):
        return self.handle.GetValue()
    def set_text(self, val):
        self.handle.SetValue(val)
    text = property(get_text, set_text)

# ListBox
class PListBox(PComponent, ControlMixin):
    def __init__(self, parent):
        real_parent = _get_wx_parent(parent)
        handle = wx.ListBox(real_parent, -1, choices=[])
        super().__init__(handle)
        self.parent = parent
        handle.Bind(wx.EVT_LISTBOX, lambda e: self.trigger_event('onclick'))
        handle.Bind(wx.EVT_LISTBOX_DCLICK, lambda e: self.trigger_event('ondblclick'))

    def additem(self, item):
        self.handle.Append(item)
        
    def clear(self):
        self.handle.Clear()
        
    def get_selectedindex(self):
        return self.handle.GetSelection()
    def set_selectedindex(self, val):
        self.handle.SetSelection(val)
    selectedindex = property(get_selectedindex, set_selectedindex)

# CheckBox
class PCheckBox(PComponent, ControlMixin):
    def __init__(self, parent):
        real_parent = _get_wx_parent(parent)
        handle = wx.CheckBox(real_parent, -1, "Check")
        super().__init__(handle)
        self.parent = parent
        handle.Bind(wx.EVT_CHECKBOX, lambda e: self.trigger_event('onchange'))

    def get_checked(self):
        return self.handle.GetValue()
    def set_checked(self, val):
        self.handle.SetValue(val)
    checked = property(get_checked, set_checked)
    
    def get_caption(self):
        return self.handle.GetLabel()
    def set_caption(self, val):
        self.handle.SetLabel(val)
    caption = property(get_caption, set_caption)

# RadioButton
class PRadioButton(PComponent, ControlMixin):
    def __init__(self, parent):
        # In wx, radio buttons in same parent with same style are auto-grouped
        real_parent = _get_wx_parent(parent)
        handle = wx.RadioButton(real_parent, -1, "Option", style=wx.RB_GROUP)
        super().__init__(handle)
        self.parent = parent
        handle.Bind(wx.EVT_RADIOBUTTON, lambda e: self.trigger_event('onclick'))

    def get_checked(self):
        return self.handle.GetValue()
    def set_checked(self, val):
        self.handle.SetValue(val)
    checked = property(get_checked, set_checked)

    def get_caption(self):
        return self.handle.GetLabel()
    def set_caption(self, val):
        self.handle.SetLabel(val)
    caption = property(get_caption, set_caption)

# GroupBox
class PGroupBox(PComponent, ControlMixin):
    def __init__(self, parent):
        # Determine the actual parent window/panel
        if hasattr(parent, '_panel'):
            real_parent = parent._panel
        elif hasattr(parent, 'handle'):
            real_parent = parent.handle
        else:
            real_parent = parent
            
        handle = wx.StaticBox(real_parent, -1, "Group")
        self.box_sizer = wx.StaticBoxSizer(handle, wx.VERTICAL)
        # Store reference to the actual parent for child controls
        self._panel = real_parent
        # We don't add box_sizer to parent here, user must manage layout or we assume absolute
        # For absolute positioning mimic, we just keep the handle
        super().__init__(handle)
        self.parent = parent
        
    def get_caption(self):
        return self.handle.GetLabel()
    def set_caption(self, val):
        self.handle.SetLabel(val)
    caption = property(get_caption, set_caption)

# TabControl & TabItem
class PTabItem(PComponent, ControlMixin):
    def __init__(self, parent):
        # PTabItem is logically a page in wx.Notebook
        # We create a panel that will be added to the notebook
        self._panel = wx.Panel(parent.handle)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._panel.SetSizer(self._sizer)
        super().__init__(self._panel)
        self.parent = parent
        self._caption = "Tab"

    def get_caption(self):
        return self._caption
    def set_caption(self, val):
        self._caption = val
        # Find index and set page text
        if self.parent and self.parent.handle:
            idx = self.parent.handle.GetPageCount() - 1 # Assuming added immediately
            # This is tricky because we need to know the index. 
            # Better to set caption when adding to notebook.
    caption = property(get_caption, set_caption)

class PTabControl(PComponent, ControlMixin):
    def __init__(self, parent):
        real_parent = _get_wx_parent(parent)
        handle = wx.Notebook(real_parent, -1)
        super().__init__(handle)
        self.parent = parent
        handle.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, lambda e: self.trigger_event('onchange'))

    def add_tab(self, tab_item):
        self.handle.AddPage(tab_item._panel, tab_item._caption)
        
    def get_selectedindex(self):
        return self.handle.GetSelection()
    def set_selectedindex(self, val):
        self.handle.SetSelection(val)
    selectedindex = property(get_selectedindex, set_selectedindex)

# ListView
class PListView(PComponent, ControlMixin):
    def __init__(self, parent):
        real_parent = _get_wx_parent(parent)
        handle = wx.ListCtrl(real_parent, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        super().__init__(handle)
        self.parent = parent
        handle.Bind(wx.EVT_LIST_ITEM_SELECTED, lambda e: self.trigger_event('onclick'))
        handle.Bind(wx.EVT_LIST_ITEM_ACTIVATED, lambda e: self.trigger_event('ondblclick'))
        handle.Bind(wx.EVT_RIGHT_DOWN, self._on_right_click)
        self._context_menu = None

    def _on_right_click(self, event):
        if self._context_menu:
            self._frame_menu = wx.Menu()
            # Map rapidp menu items to wx
            # This requires passing menu structure from rapidp code, simplified for now
            pass 
        event.Skip()

    def addcolumn(self, header, width=100):
        idx = self.handle.GetColumnCount()
        self.handle.InsertColumn(idx, header, width=width)

    def addrow(self, items):
        idx = self.handle.GetItemCount()
        self.handle.InsertItem(idx, str(items[0]) if items else "")
        for i, val in enumerate(items[1:], 1):
            self.handle.SetItem(idx, i, str(val))
            
    def clear(self):
        self.handle.DeleteAllItems()
        
    def get_selectedindex(self):
        return self.handle.GetFirstSelected()
    selectedindex = property(get_selectedindex)
    
    def get_subitem(self, row, col):
        return self.handle.GetItemText(row, col)

# StringGrid
class PStringGrid(PComponent, ControlMixin):
    def __init__(self, parent):
        real_parent = _get_wx_parent(parent)
        handle = wxgrid.Grid(real_parent, -1)
        super().__init__(handle)
        self.parent = parent
        handle.Bind(wxgrid.EVT_GRID_CELL_CHANGE, lambda e: self.trigger_event('onchange'))
        handle.Bind(wxgrid.EVT_GRID_SELECT_CELL, lambda e: self.trigger_event('onclick'))
        
        self._rows = 0
        self._cols = 0
        self._data = [] # Internal cache for 'cells' property

    def get_rows(self):
        return self._rows
    def set_rows(self, val):
        if val > self._rows:
            self.handle.AppendRows(val - self._rows)
            # Extend internal data
            while len(self._data) < val:
                if len(self._data) == 0:
                    self._data.append([""] * max(1, self._cols))
                else:
                    self._data.append([""] * len(self._data[0]))
        elif val < self._rows:
            self.handle.DeleteRows(self._rows - val, val)
            self._data = self._data[:val]
        self._rows = val
    rows = property(get_rows, set_rows)

    def get_cols(self):
        return self._cols
    def set_cols(self, val):
        if val > self._cols:
            self.handle.AppendCols(val - self._cols)
            # Extend internal data rows
            for row in self._data:
                while len(row) < val:
                    row.append("")
        elif val < self._cols:
            self.handle.DeleteCols(self._cols - val, val)
            for row in self._data:
                del row[val:]
        self._cols = val
    cols = property(get_cols, set_cols)

    def get_cells(self):
        # Sync internal data from grid if needed, but primarily serve as setter target
        # For rapidp, we often set cells[row][col] = val. 
        # We need a mutable structure.
        # Let's ensure _data matches grid size
        if len(self._data) != self._rows or (self._rows > 0 and len(self._data[0]) != self._cols):
             self._data = [["" for _ in range(self._cols)] for _ in range(self._rows)]
        return self._data
        
    def set_cells(self, val):
        self._data = val
        # Update grid UI
        for r, row_data in enumerate(val):
            for c, cell_data in enumerate(row_data):
                if r < self.handle.GetNumberRows() and c < self.handle.GetNumberCols():
                    self.handle.SetCellValue(r, c, str(cell_data))
    cells = property(get_cells, set_cells)

    def get_selectedrow(self):
        return self.handle.GetGridCursorRow()
    selectedrow = property(get_selectedrow)

    def set_colwidth(self, col_idx, width):
        self.handle.SetColSize(col_idx, width)

# ProgressBar
class PProgressBar(PComponent, ControlMixin):
    def __init__(self, parent):
        real_parent = _get_wx_parent(parent)
        handle = wx.Gauge(real_parent, -1, 100)
        super().__init__(handle)
        self.parent = parent

    def get_position(self):
        return self.handle.GetValue()
    def set_position(self, val):
        self.handle.SetValue(val)
    position = property(get_position, set_position)

# Timer
class PTimer(PComponent):
    def __init__(self, parent=None):
        super().__init__()
        self._timer = wx.Timer()
        self._interval = 1000
        self._timer.Bind(wx.EVT_TIMER, lambda e: self.trigger_event('ontimer'))
        
    def get_interval(self):
        return self._interval
    def set_interval(self, val):
        self._interval = val
        self._timer.Start(val)
    interval = property(get_interval, set_interval)
    
    def start(self):
        self._timer.Start(self._interval)
        
    def stop(self):
        self._timer.Stop()

# StatusBar
class PStatusBar(PComponent):
    def __init__(self, parent):
        # Create a status bar on the frame
        sb = parent._frame.CreateStatusBar()
        super().__init__(sb)
        self.parent = parent
        
    def get_simplestatus(self):
        return self.handle.GetStatusText()
    def set_simplestatus(self, val):
        self.handle.SetStatusText(val)
    simplestatus = property(get_simplestatus, set_simplestatus)

# MainMenu & MenuItem
class PMenuItem(PComponent):
    def __init__(self, parent, caption=""):
        super().__init__()
        self.caption = caption
        self.parent = parent
        self._subitems = []
        self._wx_item = None

    def add_menu_item(self, item):
        self._subitems.append(item)
        
    def build(self, wx_menu):
        if self._subitems:
            submenu = wx.Menu()
            for sub in self._subitems:
                sub.build(submenu)
            wx_menu.AppendSubMenu(submenu, self.caption)
        else:
            # Leaf item
            wx_id = wx.NewIdRef()
            wx_item = wx_menu.Append(wx_id, self.caption)
            self._wx_item = wx_item
            # Bind event roughly to parent form's menu handler if needed
            # Simplified: assume onclick is bound to the form or handled globally
            # In rapidp, menu items usually trigger subs directly. 
            # Here we rely on the generated code to bind events to this object if needed.
            # But wx needs an ID. We'll store the ID for binding later if required.

class PMainMenu(PComponent):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self._items = []
        self._menubar = wx.MenuBar()

    def add_menu_item(self, item):
        self._items.append(item)
        
    def build(self):
        for item in self._items:
            menu = wx.Menu()
            item.build(menu)
            self._menubar.Append(menu, item.caption)
        self.parent._frame.SetMenuBar(self._menubar)

# RichEdit (Simple Multiline TextCtrl)
class PRichEdit(PComponent, ControlMixin):
    def __init__(self, parent):
        real_parent = _get_wx_parent(parent)
        handle = wx.TextCtrl(real_parent, -1, "", style=wx.TE_MULTILINE | wx.TE_RICH2)
        super().__init__(handle)
        self.parent = parent

    def get_text(self):
        return self.handle.GetValue()
    def set_text(self, val):
        self.handle.SetValue(val)
    text = property(get_text, set_text)

# Panel
class PPanel(PComponent, ControlMixin):
    def __init__(self, parent):
        real_parent = _get_wx_parent(parent)
        handle = wx.Panel(real_parent, -1)
        super().__init__(handle)
        self.parent = parent
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.handle.SetSizer(self._sizer)

# TrackBar (Slider)
class PTrackBar(PComponent, ControlMixin):
    def __init__(self, parent):
        real_parent = _get_wx_parent(parent)
        handle = wx.Slider(real_parent, -1, 0, 0, 100, style=wx.SL_HORIZONTAL)
        super().__init__(handle)
        self.parent = parent
        self._min = 0
        self._max = 100
        self.handle.Bind(wx.EVT_SLIDER, self._on_change)
    
    def _on_change(self, event):
        self.trigger_event('onchange')
    
    @property
    def position(self):
        return self.handle.GetValue()
    
    @position.setter
    def position(self, val):
        self.handle.SetValue(int(val))
    
    @property
    def min(self):
        return self._min
    
    @min.setter
    def min(self, val):
        self._min = int(val)
        self.handle.SetRange(self._min, self._max)
    
    @property
    def max(self):
        return self._max
    
    @max.setter
    def max(self, val):
        self._max = int(val)
        self.handle.SetRange(self._min, self._max)
    
    @property
    def orientation(self):
        # 0 = horizontal, 1 = vertical
        style = self.handle.GetWindowStyle()
        return 1 if style & wx.SL_VERTICAL else 0
    
    @orientation.setter
    def orientation(self, val):
        # Note: wxPython slider orientation can't be changed after creation
        # This is a limitation compared to Tkinter
        pass

# Helper for Message Box
def msgbox(prompt, title="Message", flags=0):
    app = get_app()
    dlg = None
    if flags == 0: # OK
        dlg = wx.MessageDialog(None, prompt, title, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return 1
    elif flags == 1: # Yes/No
        dlg = wx.MessageDialog(None, prompt, title, wx.YES_NO | wx.ICON_QUESTION)
        res = dlg.ShowModal()
        dlg.Destroy()
        return 1 if res == wx.ID_YES else 0
    elif flags == 2: # Retry/Cancel
        dlg = wx.MessageDialog(None, prompt, title, wx.RETRY_CANCEL | wx.ICON_EXCLAMATION)
        res = dlg.ShowModal()
        dlg.Destroy()
        return 1 if res == wx.ID_RETRY else 0
    return 0
