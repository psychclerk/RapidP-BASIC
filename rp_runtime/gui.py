import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import os
import glob
import fnmatch

try:
    from tkhtmlview import HTMLLabel
except ImportError:
    HTMLLabel = None

try:
    import pygame
except ImportError:
    pygame = None

# Global app context to hold the main Tk instance
_tk_root = None
_main_form = None

def get_root():
    global _tk_root
    if _tk_root is None:
        _tk_root = tk.Tk()
        _tk_root.withdraw() # Hide the default root, we will show PForms manually
    return _tk_root

class PObject:
    def __init__(self):
        self._events = {}

    def bind_event(self, event_name, callback):
        self._events[event_name.lower()] = callback

    def trigger_event(self, event_name, *args):
        cb = self._events.get(event_name.lower())
        if cb:
            cb(*args)


def _bgr_to_hex(value):
    """Convert RapidP BGR integer to Tkinter hex color string."""
    if isinstance(value, int):
        r = value & 0xFF
        g = (value >> 8) & 0xFF
        b = (value >> 16) & 0xFF
        return f'#{r:02x}{g:02x}{b:02x}'
    return None


def MsgBox(prompt, title="Message", flags=0):
    """Display a message box.
    
    Args:
        prompt: Message text
        title: Window title
        flags: 0=OK only, 1=Yes/No, 2=Retry/Cancel
        
    Returns:
        1 for OK/Yes/Retry, 0 for No/Cancel
    """
    if flags == 1:
        result = messagebox.askyesno(title, prompt)
        return 1 if result else 0
    elif flags == 2:
        result = messagebox.askretrycancel(title, prompt)
        return 1 if result else 0
    else:
        messagebox.showinfo(title, prompt)
        return 1


import sys as _sys
_DEFAULT_FONT_FAMILY = "Segoe UI" if _sys.platform == "win32" else "Helvetica"
_DEFAULT_FONT_SIZE = 9


class PFont(PObject):
    """RapidP PFONT object – holds font attributes and applies them to a widget."""
    def __init__(self, owner=None):
        super().__init__()
        self._owner = owner
        self._name = _DEFAULT_FONT_FAMILY
        self._size = _DEFAULT_FONT_SIZE
        self._color = 0
        self._bold = 0
        self._italic = 0
        self._underline = 0
        self._strikeout = 0

    def _apply(self):
        """Push current settings to the owning widget (if any)."""
        if self._owner is not None:
            self._owner._apply_font()

    @property
    def name(self): return self._name
    @name.setter
    def name(self, value):
        self._name = str(value)
        self._apply()

    @property
    def size(self): return self._size
    @size.setter
    def size(self, value):
        self._size = int(value)
        self._apply()

    @property
    def color(self): return self._color
    @color.setter
    def color(self, value):
        self._color = int(value) if value else 0
        self._apply()

    @property
    def bold(self): return self._bold
    @bold.setter
    def bold(self, value):
        self._bold = int(value)
        self._apply()

    @property
    def italic(self): return self._italic
    @italic.setter
    def italic(self, value):
        self._italic = int(value)
        self._apply()

    @property
    def underline(self): return self._underline
    @underline.setter
    def underline(self, value):
        self._underline = int(value)
        self._apply()

    @property
    def strikeout(self): return self._strikeout
    @strikeout.setter
    def strikeout(self, value):
        self._strikeout = int(value)
        self._apply()

    def _tk_font_tuple(self):
        """Return a Tkinter font tuple."""
        style = ""
        if self._bold: style += " bold"
        if self._italic: style += " italic"
        if self._underline: style += " underline"
        if self._strikeout: style += " overstrike"
        return (self._name, self._size, style.strip() or "normal")


class PWidget(PObject):
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent
        self.widget = None
        
        self._left = 0
        self._top = 0
        self._width = 100
        self._height = 30
        self._caption = ""
        self._visible = True
        self._enabled = True
        self._color = None
        self._tag = 0
        self._font = PFont(owner=self)
        self._fontcolor = 0

    # ── Parent property (re-parent widget) ───────────────────────────
    @property
    def parent(self): return self._parent
    @parent.setter
    def parent(self, new_parent):
        if new_parent is self._parent:
            return
        self._parent = new_parent
        if self.widget:
            # Destroy old widget and recreate under new parent
            old_widget = self.widget
            p_widget = new_parent.widget if new_parent else get_root()
            # Determine widget type and recreate
            wtype = type(old_widget)
            try:
                if isinstance(old_widget, tk.Button):
                    self.widget = tk.Button(p_widget, text=self._caption)
                elif isinstance(old_widget, tk.Label):
                    self.widget = tk.Label(p_widget, text=self._caption)
                elif isinstance(old_widget, ttk.Combobox):
                    vals = old_widget['values']
                    self.widget = ttk.Combobox(p_widget)
                    self.widget['values'] = vals
                elif isinstance(old_widget, tk.Entry):
                    sv = getattr(self, '_sv', None)
                    self.widget = tk.Entry(p_widget)
                    if sv:
                        self.widget.config(textvariable=sv)
                elif isinstance(old_widget, ttk.Checkbutton):
                    var = getattr(self, '_var', None)
                    self.widget = ttk.Checkbutton(p_widget, text=self._caption)
                    if var:
                        self.widget.config(variable=var)
                elif isinstance(old_widget, tk.Frame):
                    self.widget = tk.Frame(p_widget)
                elif isinstance(old_widget, ttk.Radiobutton):
                    self.widget = ttk.Radiobutton(p_widget, text=self._caption)
                elif isinstance(old_widget, tk.Listbox):
                    self.widget = tk.Listbox(p_widget)
                else:
                    # Fallback: try generic
                    self.widget = wtype(p_widget)
                old_widget.destroy()
                self._place_widget()
            except Exception:
                pass  # Silently handle errors, keep old widget

    # ── Visible property ──────────────────────────────────────────────
    @property
    def visible(self):
        return 1 if self._visible else 0
    @visible.setter
    def visible(self, value):
        self._visible = bool(int(value))
        if self.widget:
            if self._visible:
                self.widget.place(x=self._left, y=self._top, width=self._width, height=self._height)
            else:
                self.widget.place_forget()

    def _place_widget(self):
        """Helper to place widget only if visible."""
        if self.widget and self._visible:
            self.widget.place(x=self._left, y=self._top, width=self._width, height=self._height)

    # ── Enabled property ─────────────────────────────────────────────
    @property
    def enabled(self):
        return 1 if self._enabled else 0
    @enabled.setter
    def enabled(self, value):
        self._enabled = bool(value) if isinstance(value, (int, float, bool)) else str(value).lower() not in ('0', 'false', '')
        if self.widget:
            try:
                self.widget.config(state='normal' if self._enabled else 'disabled')
            except tk.TclError:
                pass

    # ── Color property ───────────────────────────────────────────────
    @property
    def color(self):
        return self._color if self._color else 0
    @color.setter
    def color(self, value):
        self._color = value
        if self.widget:
            try:
                if isinstance(value, int):
                    # RapidP uses BGR format, Tkinter uses #RRGGBB
                    r = value & 0xFF
                    g = (value >> 8) & 0xFF
                    b = (value >> 16) & 0xFF
                    self.widget.config(bg=f'#{r:02x}{g:02x}{b:02x}')
                elif isinstance(value, str) and value:
                    self.widget.config(bg=value)
            except tk.TclError:
                pass

    # ── Tag property (integer store) ─────────────────────────────────
    @property
    def tag(self):
        return self._tag
    @tag.setter
    def tag(self, value):
        self._tag = int(value) if value else 0

    # ── Font property (returns PFont instance) ───────────────────────
    @property
    def font(self):
        return self._font
    @font.setter
    def font(self, value):
        if isinstance(value, PFont):
            self._font = value
            self._font._owner = self
            self._apply_font()

    # Shortcut properties: fontname, fontsize
    @property
    def fontname(self): return self._font.name
    @fontname.setter
    def fontname(self, value):
        self._font._name = str(value)
        self._apply_font()

    @property
    def fontsize(self): return self._font.size
    @fontsize.setter
    def fontsize(self, value):
        self._font._size = int(value)
        self._apply_font()

    # ── FontColor property (text foreground, BGR) ────────────────────
    @property
    def fontcolor(self): return self._fontcolor
    @fontcolor.setter
    def fontcolor(self, value):
        self._fontcolor = int(value) if isinstance(value, (int, float)) else value
        if self.widget:
            try:
                hex_c = _bgr_to_hex(self._fontcolor) if isinstance(self._fontcolor, int) else str(self._fontcolor)
                if hex_c:
                    self.widget.config(fg=hex_c)
            except tk.TclError:
                pass

    def _apply_font(self):
        """Apply the current PFont settings to the Tk widget."""
        if self.widget:
            try:
                self.widget.config(font=self._font._tk_font_tuple())
            except tk.TclError:
                pass
            # Also apply font color
            if self._font._color:
                hex_c = _bgr_to_hex(self._font._color)
                if hex_c:
                    try:
                        self.widget.config(fg=hex_c)
                    except tk.TclError:
                        pass

    # ── Bind standard events to a specific widget (for composites) ──
    def _bind_widget_events(self, target):
        """Eagerly bind standard mouse/key events to *target* widget.

        Used by composite widgets (e.g. PTreeView) whose interactive
        inner widget differs from self.widget (which is a frame).
        """
        target.bind('<ButtonPress-1>', lambda e: self.trigger_event('onclick'), add='+')
        target.bind('<Double-Button-1>', lambda e: self.trigger_event('ondblclick'), add='+')
        target.bind('<ButtonPress-1>',
                     lambda e: self.trigger_event('onmousedown', e.num if hasattr(e, 'num') else 1, e.x, e.y, 0), add='+')
        target.bind('<ButtonRelease-1>',
                     lambda e: self.trigger_event('onmouseup', e.num if hasattr(e, 'num') else 1, e.x, e.y, 0), add='+')
        target.bind('<B1-Motion>',
                     lambda e: self.trigger_event('onmousemove', e.x, e.y, 0), add='+')
        target.bind('<KeyPress>',
                     lambda e: self.trigger_event('onkeydown', e.keycode, 0), add='+')
        target.bind('<KeyRelease>',
                     lambda e: self.trigger_event('onkeyup', e.keycode, 0), add='+')

    # ── OnDblClick event ─────────────────────────────────────────────
    @property
    def ondblclick(self): return self._events.get('ondblclick')
    @ondblclick.setter
    def ondblclick(self, value):
        self._events['ondblclick'] = value
        if self.widget:
            self.widget.bind('<Double-Button-1>', lambda e: self.trigger_event('ondblclick'), add='+')

    # Common RapidP properties -> Python properties
    @property
    def left(self): return self._left
    @left.setter
    def left(self, value):
        self._left = int(value)
        self._place_widget()

    @property
    def top(self): return self._top
    @top.setter
    def top(self, value):
        self._top = int(value)
        self._place_widget()

    @property
    def width(self): return self._width
    @width.setter
    def width(self, value):
        self._width = int(value)
        self._place_widget()

    @property
    def height(self): return self._height
    @height.setter
    def height(self, value):
        self._height = int(value)
        self._place_widget()
        
    @property
    def caption(self): return self._caption
    @caption.setter
    def caption(self, value):
        self._caption = str(value)
        if self.widget:
             try:
                self.widget.config(text=self._caption)
             except tk.TclError:
                 pass # Some widgets might not have 'text'
                 
    # RapidP standard Event properties like `Button1.onclick = MySub`
    @property
    def onclick(self): return self._events.get('onclick')
    @onclick.setter
    def onclick(self, value):
        self.bind_event('onclick', value)
        if hasattr(self, '_bind_tk_click'):
            self._bind_tk_click()

    # ── Mouse events for ALL child widgets ────────────────────────────
    @property
    def onmousedown(self): return self._events.get('onmousedown')
    @onmousedown.setter
    def onmousedown(self, value):
        self._events['onmousedown'] = value
        if self.widget:
            def _md(e):
                btn = e.num if hasattr(e, 'num') else 1
                shift = 0
                if e.state & 0x1: shift = shift | 1  # Shift
                if e.state & 0x4: shift = shift | 2  # Ctrl
                self.trigger_event('onmousedown', btn, e.x, e.y, shift)
            self.widget.bind('<ButtonPress-1>', _md, add='+')

    @property
    def onmousemove(self): return self._events.get('onmousemove')
    @onmousemove.setter
    def onmousemove(self, value):
        self._events['onmousemove'] = value
        if self.widget:
            def _mm(e):
                shift = 0
                if e.state & 0x1: shift = shift | 1
                if e.state & 0x4: shift = shift | 2
                self.trigger_event('onmousemove', e.x, e.y, shift)
            self.widget.bind('<B1-Motion>', _mm, add='+')

    @property
    def onmouseup(self): return self._events.get('onmouseup')
    @onmouseup.setter
    def onmouseup(self, value):
        self._events['onmouseup'] = value
        if self.widget:
            def _mu(e):
                btn = e.num if hasattr(e, 'num') else 1
                shift = 0
                if e.state & 0x1: shift = shift | 1
                if e.state & 0x4: shift = shift | 2
                self.trigger_event('onmouseup', btn, e.x, e.y, shift)
            self.widget.bind('<ButtonRelease-1>', _mu, add='+')

    # ── Keyboard events for ALL widgets ───────────────────────────────
    @property
    def onkeydown(self): return self._events.get('onkeydown')
    @onkeydown.setter
    def onkeydown(self, value):
        self._events['onkeydown'] = value
        if self.widget:
            def _kd(e):
                shift = 0
                if e.state & 0x1: shift = shift | 1
                if e.state & 0x4: shift = shift | 2
                self.trigger_event('onkeydown', e.keycode, shift)
            self.widget.bind('<KeyPress>', _kd, add='+')

    @property
    def onkeypress(self): return self._events.get('onkeypress')
    @onkeypress.setter
    def onkeypress(self, value):
        self._events['onkeypress'] = value
        if self.widget:
            def _kp(e):
                if e.char:
                    self.trigger_event('onkeypress', ord(e.char[0]))
            self.widget.bind('<KeyPress>', _kp, add='+')

    @property
    def onkeyup(self): return self._events.get('onkeyup')
    @onkeyup.setter
    def onkeyup(self, value):
        self._events['onkeyup'] = value
        if self.widget:
            def _ku(e):
                shift = 0
                if e.state & 0x1: shift = shift | 1
                if e.state & 0x4: shift = shift | 2
                self.trigger_event('onkeyup', e.keycode, shift)
            self.widget.bind('<KeyRelease>', _ku, add='+')

class PForm(PWidget):
    def __init__(self):
        super().__init__()
        root = get_root()
        self.widget = tk.Toplevel(root)
        self.widget.withdraw() # Hidden until .Show() or .ShowModal()
        self.widget.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._width = 320
        self._height = 240
        self._caption = "Form1"
        self.widget.geometry(f"{self._width}x{self._height}")
        self.widget.title(self._caption)
        
        global _main_form
        if _main_form is None:
            _main_form = self
        
    @property
    def caption(self): return self._caption
    @caption.setter
    def caption(self, value):
        self._caption = str(value)
        self.widget.title(self._caption)
        
    @property
    def width(self): return self._width
    @width.setter
    def width(self, value):
        self._width = value
        self.widget.geometry(f"{self._width}x{self._height}+{self._left}+{self._top}")
        
    @property
    def height(self): return self._height
    @height.setter
    def height(self, value):
        self._height = value
        self.widget.geometry(f"{self._width}x{self._height}+{self._left}+{self._top}")

    @property
    def left(self): return self._left
    @left.setter
    def left(self, value):
        self._left = value
        self.widget.geometry(f"{self._width}x{self._height}+{self._left}+{self._top}")

    @property
    def top(self): return self._top
    @top.setter
    def top(self, value):
        self._top = value
        self.widget.geometry(f"{self._width}x{self._height}+{self._left}+{self._top}")

    @property
    def alwaysontop(self):
        return self.widget.attributes("-topmost")
    @alwaysontop.setter
    def alwaysontop(self, value):
        self.widget.attributes("-topmost", bool(value))

    # ── Grid support for design surface ───────────────────────────────
    @property
    def gridvisible(self): return getattr(self, '_gridvisible', 0)
    @gridvisible.setter
    def gridvisible(self, value):
        self._gridvisible = int(value)
        self._draw_grid()

    def _draw_grid(self):
        """Draw a dotted grid on the form background (like VB6 design surface)."""
        # Remove old grid canvas if any
        for child in self.widget.winfo_children():
            if getattr(child, '_is_grid_canvas', False):
                child.destroy()
        if not self._gridvisible:
            return
        c = tk.Canvas(self.widget, bg='#D4D0C8', highlightthickness=0)
        c._is_grid_canvas = True
        c.place(x=0, y=0, relwidth=1, relheight=1)
        # Lower the canvas behind all other widgets using Tk stacking
        c.tk.call('lower', c._w)
        w = self._width
        h = self._height
        spacing = 8
        for x in range(0, w, spacing):
            for y in range(0, h, spacing):
                c.create_oval(x, y, x+1, y+1, fill='#888', outline='#888')
        # Forward mouse events from canvas to form
        if self._events.get('onmousedown'):
            c.bind('<ButtonPress-1>', lambda e: self.trigger_event('onmousedown', e.x, e.y, 1))

    # PForm visible overrides PWidget (Toplevel uses withdraw/deiconify, not place)
    @property
    def visible(self):
        return 1 if self._visible else 0
    @visible.setter
    def visible(self, value):
        self._visible = bool(int(value))
        if self._visible:
            self.widget.deiconify()
        else:
            self.widget.withdraw()

    def show(self):
        self._visible = True
        self.widget.deiconify()
        self.trigger_event('onshow')

    # PForm overrides mouse events inherited from PWidget to bind on Toplevel
    @property
    def onmousedown(self): return self._events.get('onmousedown')
    @onmousedown.setter
    def onmousedown(self, value):
        self._events['onmousedown'] = value
        def _md(e):
            btn = e.num if hasattr(e, 'num') else 1
            shift = 0
            if e.state & 0x1: shift = shift | 1
            if e.state & 0x4: shift = shift | 2
            self.trigger_event('onmousedown', btn, e.x, e.y, shift)
        self.widget.bind('<ButtonPress-1>', _md, add='+')

    @property
    def onmousemove(self): return self._events.get('onmousemove')
    @onmousemove.setter
    def onmousemove(self, value):
        self._events['onmousemove'] = value
        def _mm(e):
            shift = 0
            if e.state & 0x1: shift = shift | 1
            if e.state & 0x4: shift = shift | 2
            self.trigger_event('onmousemove', e.x, e.y, shift)
        self.widget.bind('<B1-Motion>', _mm, add='+')

    @property
    def onmouseup(self): return self._events.get('onmouseup')
    @onmouseup.setter
    def onmouseup(self, value):
        self._events['onmouseup'] = value
        def _mu(e):
            btn = e.num if hasattr(e, 'num') else 1
            shift = 0
            if e.state & 0x1: shift = shift | 1
            if e.state & 0x4: shift = shift | 2
            self.trigger_event('onmouseup', btn, e.x, e.y, shift)
        self.widget.bind('<ButtonRelease-1>', _mu, add='+')

    def showmodal(self):
        self.show()
        # Make modal by running local loop or waiting window if multiple forms
        self.widget.focus_set()
        
        global _main_form
        if _main_form is self:
            get_root().mainloop()
        else:
            try:
                self.widget.grab_set()
                self.widget.wait_window()
            except tk.TclError:
                pass
    def center(self):
        self.widget.update_idletasks()
        w = self._width
        h = self._height
        ws = self.widget.winfo_screenwidth()
        hs = self.widget.winfo_screenheight()
        x = int(ws/2 - w/2)
        y = int(hs/2 - h/2)
        self.widget.geometry(f"+{x}+{y}")

    def close(self):
        global _main_form
        self._visible = False
        self.widget.destroy()
        if _main_form is self:
            get_root().quit()

    def _on_close(self):
        self.trigger_event('onclose')
        self.close()

    # ── OnResize event for PForm ──────────────────────────────────────
    @property
    def onresize(self): return self._events.get('onresize')
    @onresize.setter
    def onresize(self, value):
        self._events['onresize'] = value
        def _rs(e):
            if e.widget is self.widget:
                self._width = e.width
                self._height = e.height
                self.trigger_event('onresize')
        self.widget.bind('<Configure>', _rs, add='+')

    # ── OnKeyDown / OnKeyPress for PForm (override to bind on Toplevel focus) ──
    @property
    def onkeydown(self): return self._events.get('onkeydown')
    @onkeydown.setter
    def onkeydown(self, value):
        self._events['onkeydown'] = value
        def _kd(e):
            shift = 0
            if e.state & 0x1: shift = shift | 1
            if e.state & 0x4: shift = shift | 2
            self.trigger_event('onkeydown', e.keycode, shift)
        self.widget.bind('<KeyPress>', _kd, add='+')

    @property
    def onkeypress(self): return self._events.get('onkeypress')
    @onkeypress.setter
    def onkeypress(self, value):
        self._events['onkeypress'] = value
        def _kp(e):
            if e.char:
                self.trigger_event('onkeypress', ord(e.char[0]))
        self.widget.bind('<KeyPress>', _kp, add='+')

class PFormMDI(PForm):
    def __init__(self):
        super().__init__()
        # In RapidP, MDI child window behavior maps to OS child instances natively
        # Tkinter floating frames default correctly identically handling fsMDI configurations

class PButton(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self.widget = tk.Button(p_widget, text=self.caption)
        self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)
        
    @property
    def caption(self): return getattr(self, '_caption', '')
    @caption.setter
    def caption(self, value):
        self._caption = str(value).replace('&', '')
        self.widget.config(text=self._caption)

    def _bind_tk_click(self):
        self.widget.config(command=lambda: self.trigger_event('onclick'))

class PLabel(PWidget):
     def __init__(self, parent=None):
         super().__init__(parent)
         p_widget = parent.widget if parent else get_root()
         self._alignment = 0  # 0=left, 1=center, 2=right
         self._multiline = 0
         self.widget = tk.Label(p_widget, text=self.caption, anchor='w')
         self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)

     @property
     def caption(self): return getattr(self, '_caption', '')
     @caption.setter
     def caption(self, value):
         self._caption = str(value).replace('&', '')
         self.widget.config(text=self._caption)
     
     @property
     def alignment(self): return self._alignment
     @alignment.setter
     def alignment(self, value):
         self._alignment = int(value)
         anchors = ['w', 'center', 'e']
         if 0 <= self._alignment < len(anchors):
             self.widget.config(anchor=anchors[self._alignment])
     
     @property
     def multiline(self): return self._multiline
     @multiline.setter
     def multiline(self, value):
         self._multiline = int(value)
         if self._multiline:
             self.widget.config(wraplength=self.width - 5)

class PEdit(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self._sv = tk.StringVar()
        self.widget = ttk.Entry(p_widget, textvariable=self._sv)
        self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)

    @property
    def text(self):
         return self.widget.get()
    @text.setter
    def text(self, value):
         self.widget.delete(0, tk.END)
         self.widget.insert(0, str(value))

    # ── OnChange event for PEdit ──────────────────────────────────────
    @property
    def onchange(self): return self._events.get('onchange')
    @onchange.setter
    def onchange(self, value):
        self._events['onchange'] = value
        self._sv.trace_add('write', lambda *a: self.trigger_event('onchange'))
         
class PCanvas(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self.widget = tk.Canvas(p_widget, bg="white", highlightthickness=0)
        self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)

    def pset(self, x, y, color=0):
        c = self._int_to_hex(color)
        self.widget.create_oval(x, y, x+1, y+1, fill=c, outline=c)

    def line(self, x1, y1, x2, y2, color=0):
        c = self._int_to_hex(color)
        self.widget.create_line(x1, y1, x2, y2, fill=c)

    def fillrect(self, x1, y1, x2, y2, color=0):
        c = self._int_to_hex(color)
        self.widget.create_rectangle(x1, y1, x2, y2, fill=c, outline=c)

    def rectangle(self, x1, y1, x2, y2, color=0):
        c = self._int_to_hex(color)
        self.widget.create_rectangle(x1, y1, x2, y2, outline=c)

    def cls(self):
        self.widget.delete('all')

    def drawtext(self, x, y, text, color=0, fontsize=9):
        c = self._int_to_hex(color)
        self.widget.create_text(x, y, text=str(text), fill=c, anchor='nw',
                               font=('Helvetica', int(fontsize)))

    def circle(self, x, y, radius, color=0):
        c = self._int_to_hex(color)
        self.widget.create_oval(x - radius, y - radius, x + radius, y + radius, outline=c)

    def paint(self):
        self.widget.update_idletasks()

    @staticmethod
    def _int_to_hex(color):
        if isinstance(color, str) and color.startswith('#'): return color
        if isinstance(color, (int, float)):
            v = int(color)
            r, g, b = v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF
            return f'#{r:02x}{g:02x}{b:02x}'
        return '#000000'

class PPanel(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self.widget = tk.Frame(p_widget, relief="groove", bd=1)
        self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)

class PCodeEditor(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self._frame = tk.Frame(p_widget)
        self._frame.place(x=self.left, y=self.top, width=self.width, height=self.height)
        # Scrollbars
        self._vscroll = ttk.Scrollbar(self._frame, orient='vertical')
        self._hscroll = ttk.Scrollbar(self._frame, orient='horizontal')
        self.widget = tk.Text(self._frame, undo=True, wrap="none",
                             font=("Courier New", 11), bg="#1E1E1E", fg="#D4D4D4",
                             insertbackground="white", selectbackground="#264F78",
                             selectforeground="#D4D4D4", tabs="4c",
                             yscrollcommand=self._vscroll.set,
                             xscrollcommand=self._hscroll.set)
        self._vscroll.config(command=self.widget.yview)
        self._hscroll.config(command=self.widget.xview)
        self._hscroll.pack(side='bottom', fill='x')
        self._vscroll.pack(side='right', fill='y')
        self.widget.pack(side='left', fill='both', expand=True)
        # Line numbers
        self._linenums = tk.Canvas(self._frame, width=40, bg="#1E1E1E", highlightthickness=0)
        self._linenums.pack(side='left', fill='y', before=self.widget)
        
        self.widget.tag_configure("Keyword", foreground="#569CD6", font=("Courier New", 11, "bold"))
        self.widget.tag_configure("String", foreground="#CE9178")
        self.widget.tag_configure("Comment", foreground="#6A9955", font=("Courier New", 11, "italic"))
        self.widget.tag_configure("Number", foreground="#B5CEA8")
        self.widget.tag_configure("Type", foreground="#4EC9B0")
        self.widget.bind("<KeyRelease>", self._on_key)
        self.widget.bind("<<Modified>>", self._on_modified)
        self._highlight_scheduled = False
        
    def _place_widget(self):
        if self._frame and self._visible:
            self._frame.place(x=self._left, y=self._top, width=self._width, height=self._height)
            self._frame.tkraise()
        elif self._frame:
            self._frame.place_forget()

    @property
    def visible(self):
        return 1 if self._visible else 0
    @visible.setter
    def visible(self, value):
        self._visible = bool(int(value))
        self._place_widget()

    def _on_key(self, event=None):
        self._schedule_highlight()
        self._update_linenums()
    
    def _on_modified(self, event=None):
        if self.widget.edit_modified():
            self._schedule_highlight()
            self._update_linenums()
            self.widget.edit_modified(False)

    def _schedule_highlight(self):
        if not self._highlight_scheduled:
            self._highlight_scheduled = True
            self.widget.after(50, self._do_highlight)
    
    def _do_highlight(self):
        self._highlight_scheduled = False
        self._highlight()

    def _update_linenums(self):
        self._linenums.delete('all')
        i = self.widget.index("@0,0")
        while True:
            dline = self.widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self._linenums.create_text(36, y, anchor="ne", text=linenum,
                                      fill="#858585", font=("Courier", 10))
            i = self.widget.index(f"{i}+1line")
            if int(i.split('.')[0]) > int(self.widget.index('end').split('.')[0]):
                break

    def _highlight(self, event=None):
        import re
        self.widget.tag_remove("Keyword", "1.0", tk.END)
        self.widget.tag_remove("String", "1.0", tk.END)
        self.widget.tag_remove("Comment", "1.0", tk.END)
        self.widget.tag_remove("Number", "1.0", tk.END)
        self.widget.tag_remove("Type", "1.0", tk.END)
        
        text = self.widget.get("1.0", tk.END)
        tagged = set()
        
        for line_match in re.finditer(r'[^\n]*', text):
            line_text = line_match.group()
            line_start = line_match.start()
            if not line_text.strip():
                continue
            for m in re.finditer(r'"[^"]*"', line_text):
                a = line_start + m.start()
                b = line_start + m.end()
                self.widget.tag_add("String", f"1.0+{a}c", f"1.0+{b}c")
                for i in range(a, b):
                    tagged.add(i)
            in_str = False
            for ci, ch in enumerate(line_text):
                if ch == '"':
                    in_str = not in_str
                elif ch == "'" and not in_str:
                    a = line_start + ci
                    b = line_start + len(line_text)
                    self.widget.tag_add("Comment", f"1.0+{a}c", f"1.0+{b}c")
                    for i in range(a, b):
                        tagged.add(i)
                    break
        
        kw = r'\b(SUB|FUNCTION|END|CREATE|IF|THEN|ELSE|ELSEIF|DIM|AS|CONST|DECLARE|IMPORT|TYPE|WITH|SELECT|CASE|DO|LOOP|UNTIL|EXIT|NOT|AND|OR|XOR|MOD|FOR|NEXT|WHILE|WEND|TRUE|FALSE|TO|STEP|BYREF|BYVAL|RETURN|GOTO|GOSUB|STATIC|SHARED|DEFINT|DEFLNG|DEFSNG|DEFDBL|DEFSTR|DATA|READ|RESTORE|PRINT|INPUT|OPEN|CLOSE|WRITE|APPEND|OUTPUT|BINARY|RANDOM|LEN|GET|PUT|EOF|LOF|SEEK|LINE|CALL|CLASS|PROPERTY|METHOD|NEW|SET)\b'
        types_re = r'\b(INTEGER|STRING|SINGLE|DOUBLE|LONG|BYTE|SHORT|WORD|DWORD|PFORM|PBUTTON|PLABEL|PEDIT|PPANEL|PCANVAS|PCHECKBOX|PCOMBOBOX|PRADIOBUTTON|PLISTBOX|PGROUPBOX|PPROGRESSBAR|PTIMER|PRICHEDIT|PMENU|PMAINMENU|PMENUITEM|PTABCONTROL|PCODEEDITOR|PSTRINGGRID|PSAVEDIALOG|POPENDIALOG|PCOLORDIALOG|PFONTDIALOG|PFILEDIALOG|PFILESTREAM|PMYSQL|PSQLITE|PSCROLLBAR|PSTATUSBAR|PIMAGE|PBITMAP|PICON|PLINE|PHTML|PMIDI|PSCREEN|PFILELISTBOX|PLISTVIEW|PNOTIFYICONDATA|PTREEVIEW|PSPLITTER|PTRACKBAR|PSCROLLBOX|PPOPUPMENU|PNUMPY|PMATPLOTLIB|PPANDAS)\b'
        props_re = r'\b(ONCLICK|ONDBLCLICK|ONCHANGE|ONMOUSEDOWN|ONMOUSEMOVE|ONMOUSEUP|ONKEYDOWN|ONKEYPRESS|ONKEYUP|ONTIMER|ONSHOW|ONCLOSE|ONRESIZE|ONPAINT|CENTER|SHOWMODAL|SHOW|CAPTION|LEFT|TOP|WIDTH|HEIGHT|VISIBLE|ENABLED|TEXT|COLOR|FONT|PARENT|TABINDEX|ADDTABS|ADDITEMS|ADDROW|CLEAR)\b'
        
        for match in re.finditer(kw, text, re.IGNORECASE):
            if match.start() not in tagged:
                self.widget.tag_add("Keyword", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(types_re, text, re.IGNORECASE):
            if match.start() not in tagged:
                self.widget.tag_add("Type", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(props_re, text, re.IGNORECASE):
            if match.start() not in tagged:
                self.widget.tag_add("Keyword", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
            
        for match in re.finditer(r'\b\d+\b', text):
            if match.start() not in tagged:
                self.widget.tag_add("Number", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

    @property
    def text(self): return self.widget.get("1.0", tk.END)
    @text.setter
    def text(self, val):
        self.widget.delete("1.0", tk.END)
        self.widget.insert(tk.END, str(val))
        self._highlight()

    # ── Autocomplete support ──────────────────────────────────────────
    _AC_KEYWORDS = [
        "SUB", "FUNCTION", "END SUB", "END FUNCTION", "END IF", "END SELECT",
        "CREATE", "END CREATE", "IF", "THEN", "ELSE", "ELSEIF",
        "DIM", "AS", "CONST", "DECLARE", "FOR", "NEXT", "TO", "STEP",
        "DO", "LOOP", "UNTIL", "WHILE", "WEND", "EXIT SUB", "EXIT FUNCTION",
        "EXIT FOR", "EXIT DO", "SELECT CASE", "CASE", "WITH", "END WITH",
        "AND", "OR", "NOT", "XOR", "MOD", "TRUE", "FALSE",
        "PRINT", "INPUT", "OPEN", "CLOSE", "WRITE", "APPEND",
        "BYREF", "BYVAL", "RETURN", "GOTO", "GOSUB", "CALL",
        "INTEGER", "STRING", "SINGLE", "DOUBLE", "LONG", "BYTE", "SHORT",
        "PFORM", "PBUTTON", "PLABEL", "PEDIT", "PPANEL", "PCANVAS",
        "PCHECKBOX", "PCOMBOBOX", "PRADIOBUTTON", "PLISTBOX", "PGROUPBOX",
        "PPROGRESSBAR", "PTIMER", "PRICHEDIT", "PMENU", "PMAINMENU",
        "PTABCONTROL", "PCODEEDITOR", "PSTRINGGRID", "PFONT",
        "PSAVEDIALOG", "POPENDIALOG", "PCOLORDIALOG", "PFONTDIALOG",
        "PFILESTREAM", "PMYSQL", "PSQLITE", "PSCROLLBAR", "PSTATUSBAR",
        "Caption", "Left", "Top", "Width", "Height", "Visible", "Enabled",
        "Text", "Color", "Font", "FontColor", "Parent",
        "OnClick", "OnDblClick", "OnChange", "OnMouseDown", "OnMouseMove",
        "OnMouseUp", "OnKeyDown", "OnKeyPress", "OnKeyUp", "OnTimer",
        "OnShow", "OnClose", "OnResize", "OnPaint",
        "Center", "ShowModal", "Show", "Close", "AddItems", "AddRow", "Clear",
        "AddTabs", "TabIndex", "ItemIndex", "ItemCount",
        "Interval", "Position", "Max", "Checked", "Bold", "Italic",
        "Name", "Size", "Underline", "Strikeout",
    ]

    def _init_autocomplete(self):
        """Set up autocomplete popup (called lazily on first trigger)."""
        if hasattr(self, '_ac_popup'):
            return
        self._ac_popup = tk.Toplevel(self.widget)
        self._ac_popup.wm_overrideredirect(True)
        self._ac_popup.withdraw()
        self._ac_list = tk.Listbox(self._ac_popup, bg="#252526", fg="#D4D4D4",
                                   selectbackground="#264F78", selectforeground="#FFFFFF",
                                   font=("Courier New", 10), borderwidth=1, relief="solid",
                                   highlightthickness=0)
        self._ac_list.pack(fill='both', expand=True)
        self._ac_list.bind('<Double-Button-1>', self._ac_accept)
        self._ac_visible = False
        self._ac_prefix = ""
        # Bind keys for autocomplete interaction
        self.widget.bind('<Key>', self._ac_on_key, add='+')
        self.widget.bind('<FocusOut>', lambda e: self._ac_hide(), add='+')

    def _ac_on_key(self, event):
        """Handle key events for autocomplete triggering and navigation."""
        self._init_autocomplete()
        # If popup is visible, handle navigation
        if self._ac_visible:
            if event.keysym == 'Down':
                idx = self._ac_list.curselection()
                nxt = (idx[0] + 1) if idx else 0
                if nxt < self._ac_list.size():
                    self._ac_list.selection_clear(0, tk.END)
                    self._ac_list.selection_set(nxt)
                    self._ac_list.see(nxt)
                return "break"
            elif event.keysym == 'Up':
                idx = self._ac_list.curselection()
                nxt = (idx[0] - 1) if idx else 0
                if nxt >= 0:
                    self._ac_list.selection_clear(0, tk.END)
                    self._ac_list.selection_set(nxt)
                    self._ac_list.see(nxt)
                return "break"
            elif event.keysym in ('Return', 'Tab'):
                self._ac_accept()
                return "break"
            elif event.keysym == 'Escape':
                self._ac_hide()
                return None
        # Schedule autocomplete check after the key is processed
        self.widget.after(10, self._ac_check)
        return None

    def _ac_check(self):
        """Check if we should show/update autocomplete popup."""
        self._init_autocomplete()
        # Get current word being typed
        try:
            pos = self.widget.index(tk.INSERT)
            line = self.widget.get(f"{pos} linestart", pos)
        except tk.TclError:
            return
        # Extract the current word (letters, digits, underscore)
        import re
        m = re.search(r'[A-Za-z_]\w*$', line)
        if not m or len(m.group()) < 2:
            self._ac_hide()
            return
        prefix = m.group()
        self._ac_prefix = prefix
        prefix_upper = prefix.upper()
        matches = [kw for kw in self._AC_KEYWORDS if kw.upper().startswith(prefix_upper) and kw.upper() != prefix_upper]
        if not matches:
            self._ac_hide()
            return
        # Populate and show
        self._ac_list.delete(0, tk.END)
        for item in matches[:15]:
            self._ac_list.insert(tk.END, item)
        self._ac_list.selection_set(0)
        # Position popup near cursor
        try:
            bbox = self.widget.bbox(tk.INSERT)
            if bbox:
                x = bbox[0] + self.widget.winfo_rootx()
                y = bbox[1] + bbox[3] + self.widget.winfo_rooty()
                self._ac_popup.geometry(f"220x{min(len(matches), 15) * 18 + 4}+{x}+{y}")
                self._ac_popup.deiconify()
                self._ac_popup.lift()
                self._ac_visible = True
        except tk.TclError:
            pass

    def _ac_accept(self, event=None):
        """Accept the selected autocomplete item."""
        if not self._ac_visible:
            return
        sel = self._ac_list.curselection()
        if sel:
            chosen = self._ac_list.get(sel[0])
            # Replace the typed prefix with chosen word
            pos = self.widget.index(tk.INSERT)
            prefix_len = len(self._ac_prefix)
            start = f"{pos}-{prefix_len}c"
            self.widget.delete(start, pos)
            self.widget.insert(start, chosen)
        self._ac_hide()

    def _ac_hide(self):
        """Hide the autocomplete popup."""
        if hasattr(self, '_ac_popup') and self._ac_visible:
            self._ac_popup.withdraw()
            self._ac_visible = False

    def gotosub(self, name):
        """Scroll to SUB or FUNCTION matching name and place cursor at the body."""
        import re
        text = self.widget.get('1.0', 'end')
        target = str(name).strip().upper()
        for i, line in enumerate(text.split('\n'), 1):
            stripped = line.strip().upper()
            if re.match(r'(SUB|FUNCTION)\s+' + re.escape(target) + r'\b', stripped):
                self.widget.see(f'{i + 1}.0')
                self.widget.mark_set('insert', f'{i + 1}.4')
                self.widget.focus_set()
                return True
        return False

    def gotoline(self, line_num):
        """Scroll to a specific line number and place cursor there."""
        line_num = int(line_num)
        if line_num < 1:
            line_num = 1
        self.widget.see(f'{line_num}.0')
        self.widget.mark_set('insert', f'{line_num}.0')
        self.widget.focus_set()

    @property
    def getsublist(self):
        """Return comma-separated list of SUB and FUNCTION names found in the code."""
        import re
        text = self.widget.get('1.0', 'end')
        names = []
        for line in text.split('\n'):
            m = re.match(r'\s*(SUB|FUNCTION)\s+(\w+)', line, re.IGNORECASE)
            if m:
                names.append(m.group(2))
        return ','.join(names)

class PTabControl(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self.widget = ttk.Notebook(p_widget)
        self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)
        self._tabs = []

    def addtabs(self, *args):
        for name in args:
            frame = tk.Frame(self.widget)
            self.widget.add(frame, text=name)
            self._tabs.append(frame)

    def tab(self, index):
        """Return the tab frame at index so children can parent to it."""
        idx = int(index)
        if 0 <= idx < len(self._tabs):
            return self._tabs[idx]
        return None

    @property
    def tabindex(self):
        try: return self.widget.index(self.widget.select())
        except: return 0

    @tabindex.setter
    def tabindex(self, val):
        try: self.widget.select(self._tabs[int(val)])
        except: pass

    @property
    def onchange(self): return self._events.get('onchange')
    @onchange.setter
    def onchange(self, value):
        self._events['onchange'] = value
        self.widget.bind('<<NotebookTabChanged>>', lambda e: self.trigger_event('onchange'))

class PGroupBox(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self.widget = ttk.LabelFrame(p_widget, text=self.caption)
        self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)

class PCheckBox(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self.var = tk.BooleanVar()
        self.widget = ttk.Checkbutton(p_widget, text=self.caption, variable=self.var)
        self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)

    @property
    def checked(self): return self.var.get()
    @checked.setter
    def checked(self, val): self.var.set(bool(val))
    
    @property
    def onchange(self): return self._events.get('onchange')
    @onchange.setter
    def onchange(self, value):
        self._events['onchange'] = value
        self.widget.bind('<ButtonRelease-1>', lambda e: self.trigger_event('onchange'))

class PRadioButton(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self.widget = ttk.Radiobutton(p_widget, text=self.caption)
        self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)

class PComboBox(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self.widget = ttk.Combobox(p_widget)
        self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)

    def additems(self, *items):
        self.widget['values'] = tuple(list(self.widget['values']) + list(items))

    def clear(self):
        self.widget.set('')
        self.widget['values'] = ()

    @property
    def text(self): return self.widget.get()
    @text.setter
    def text(self, val): self.widget.set(str(val))

    @property
    def itemindex(self):
        try: return self.widget.current()
        except: return -1
    @itemindex.setter
    def itemindex(self, val):
        try: self.widget.current(int(val))
        except: pass

    @property
    def itemcount(self): return len(self.widget['values'])

    @property
    def onchange(self): return self._events.get('onchange')
    @onchange.setter
    def onchange(self, value):
        self._events['onchange'] = value
        self.widget.bind('<<ComboboxSelected>>', lambda e: self.trigger_event('onchange'))

class PListBox(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self.widget = tk.Listbox(p_widget, exportselection=False)
        self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)

    def additems(self, *items):
        for item in items:
            self.widget.insert(tk.END, item)
            
    def clear(self):
        self.widget.delete(0, tk.END)
        
    @property
    def itemcount(self): return self.widget.size()
    
    @property
    def itemindex(self):
        sel = self.widget.curselection()
        return sel[0] if sel else -1
        
    @property
    def onclick(self): return self._events.get('onclick')
    @onclick.setter
    def onclick(self, value):
        self._events['onclick'] = value
        self.widget.bind('<<ListboxSelect>>', lambda e: self.trigger_event('onclick'))

class PFileListBox(PListBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._directory = "."
        self._mask = "*.*"
        self.showicons = False
        self._items = []
        self._update_list()
        
    @property
    def directory(self): return self._directory
    @directory.setter
    def directory(self, val):
        self._directory = str(val)
        self._update_list()
        
    @property
    def mask(self): return self._mask
    @mask.setter
    def mask(self, val):
        self._mask = str(val)
        self._update_list()
        
    @property
    def filename(self):
        idx = self.itemindex
        if idx >= 0 and self._items and len(self._items) > idx:
            return os.path.join(self._directory, self._items[idx])
        return ""
        
    def addfiletypes(self, *types): pass
    def delfiletypes(self, *types): pass
    def update(self): self._update_list()
        
    def _update_list(self):
        self.clear()
        self._items = []
        if os.path.isdir(self._directory):
            try:
                files = os.listdir(self._directory)
                for f in fnmatch.filter(files, self._mask):
                    self.additems(f)
                    self._items.append(f)
            except:
                pass

class PMainMenu(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self.widget = tk.Menu(p_widget)
        if hasattr(p_widget, 'config'):
            p_widget.config(menu=self.widget)
            
class PMenuItem(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget = None
        self._caption = ""
        self._is_cascade = False
        self._parent_qitem = parent if isinstance(parent, PMenuItem) else None
        self._parent_menu = parent.widget if parent and hasattr(parent, 'widget') else None
        
        if isinstance(self._parent_menu, tk.Menu):
            self.widget = tk.Menu(self._parent_menu, tearoff=0)
            
            if self._parent_qitem and not self._parent_qitem._is_cascade:
                idx = self._parent_qitem._index
                p_p_menu = self._parent_qitem._parent_menu
                p_p_menu.delete(idx)
                p_p_menu.insert_cascade(index=idx, label=self._parent_qitem._caption, menu=self._parent_qitem.widget)
                self._parent_qitem._is_cascade = True
                
            self._parent_menu.add_command(label="", command=lambda: self.trigger_event('onclick'))
            self._index = self._parent_menu.index(tk.END)
            
    @property
    def caption(self): return self._caption
    @caption.setter
    def caption(self, value):
        self._caption = str(value).replace('&', '')
        if self._parent_menu:
            self._parent_menu.entryconfig(self._index, label=self._caption)

class PDesignSurface(PWidget):
    """Visual design surface for IDE – MDI form window with real Tk widgets,
    design-time selection, drag, resize, and double-click behaviour."""

    _DEFAULT_SIZES = {
        'PBUTTON': (80, 30), 'PLABEL': (100, 20), 'PEDIT': (120, 24),
        'PCHECKBOX': (100, 24), 'PCOMBOBOX': (120, 24), 'PPANEL': (200, 150),
        'PRADIOBUTTON': (100, 24), 'PLISTBOX': (120, 100), 'PGROUPBOX': (200, 150),
        'PPROGRESSBAR': (150, 20), 'PTIMER': (32, 32), 'PRICHEDIT': (200, 120),
        'PCANVAS': (200, 150), 'PMYSQL': (32, 32), 'PSQLITE': (32, 32),
        'PTREEVIEW': (150, 150), 'PIMAGE': (100, 100), 'PTRACKBAR': (150, 25),
        'PSPLITTER': (300, 200), 'PSTRINGGRID': (200, 120), 'PSCROLLBOX': (200, 150),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._form_caption = 'Form1'

        # Create a real Toplevel window for the design surface
        self._toplevel = tk.Toplevel(get_root())
        self._toplevel.title(self._form_caption)
        self._toplevel.geometry(f'{self._width}x{self._height}')
        self._toplevel.resizable(True, True)
        self._toplevel.protocol('WM_DELETE_WINDOW', self._on_wm_close)
        self._toplevel.bind('<Configure>', self._on_configure)

        # Design surface (content area)
        self.widget = tk.Frame(self._toplevel, bg='#D4D0C8')
        self.widget.pack(fill='both', expand=True)

        # Background canvas for grid dots
        self._grid = tk.Canvas(self.widget, bg='#D4D0C8', highlightthickness=0)
        self._grid.place(x=0, y=0, relwidth=1, relheight=1)

        # Selection handles (small Frames)
        self._handles = []
        self._handle_size = 6

        # Component storage
        self._comps = []  # [{type, name, widget, x, y, w, h, props:{}, events:{}}]
        self._selected = -1

        # Drag / resize state
        self._dragging = False
        self._resizing = -1
        self._drag_sx = 0
        self._drag_sy = 0
        self._drag_ox = 0
        self._drag_oy = 0
        self._drag_ow = 0
        self._drag_oh = 0

        # Callbacks
        self._on_select = None
        self._on_move = None
        self._on_dblclick = None
        self._on_bgclick = None

        self._grid.bind('<ButtonPress-1>', self._bg_press)
        self._draw_grid()

    def _on_wm_close(self):
        """Handle window close button - just hide, don't destroy."""
        self._toplevel.withdraw()
        self._visible = False

    def _on_configure(self, event):
        """Track Toplevel resize and redraw grid dots (debounced)."""
        if event.widget == self._toplevel:
            new_w, new_h = event.width, event.height
            if new_w != self._width or new_h != self._height:
                self._width = new_w
                self._height = new_h
                if hasattr(self, '_configure_after_id'):
                    self._toplevel.after_cancel(self._configure_after_id)
                self._configure_after_id = self._toplevel.after(100, self._draw_grid)

    # ── placement ─────────────────────────────────────────────────────
    def _place_widget(self):
        if self._visible:
            self._toplevel.deiconify()
        else:
            self._toplevel.withdraw()

    @property
    def visible(self):
        return 1 if self._visible else 0
    @visible.setter
    def visible(self, value):
        self._visible = bool(int(value))
        self._place_widget()

    # ── grid ──────────────────────────────────────────────────────────
    def _draw_grid(self):
        self._grid.delete('all')
        w, h = self._width, self._height
        for x in range(0, w, 8):
            for y in range(0, h, 8):
                self._grid.create_oval(x, y, x + 1, y + 1, fill='#999', outline='#999')

    # ── size overrides ────────────────────────────────────────────────
    @property
    def width(self): return self._width
    @width.setter
    def width(self, v):
        self._width = int(v)
        self._toplevel.geometry(f'{self._width}x{self._height}')
        self._draw_grid()

    @property
    def height(self): return self._height
    @height.setter
    def height(self, v):
        self._height = int(v)
        self._toplevel.geometry(f'{self._width}x{self._height}')
        self._draw_grid()

    # ── form caption ──────────────────────────────────────────────────
    @property
    def formcaption(self): return self._form_caption
    @formcaption.setter
    def formcaption(self, value):
        self._form_caption = str(value)
        self._toplevel.title(self._form_caption)

    def show(self):
        """Show the design surface Toplevel window."""
        self._visible = True
        self._toplevel.deiconify()
        self._toplevel.lift()

    def hide(self):
        """Hide the design surface Toplevel window."""
        self._visible = False
        self._toplevel.withdraw()

    # ── callbacks (event properties) ──────────────────────────────────
    @property
    def onselect(self): return self._on_select
    @onselect.setter
    def onselect(self, v): self._on_select = v

    @property
    def onmove(self): return self._on_move
    @onmove.setter
    def onmove(self, v): self._on_move = v

    @property
    def ondblclick(self): return self._on_dblclick
    @ondblclick.setter
    def ondblclick(self, v): self._on_dblclick = v

    @property
    def onbgclick(self): return self._on_bgclick
    @onbgclick.setter
    def onbgclick(self, v): self._on_bgclick = v

    @property
    def selected(self): return self._selected

    @property
    def compcount(self): return len(self._comps)

    # ── snap helper ───────────────────────────────────────────────────
    @staticmethod
    def _snap(v):
        return round(int(v) / 8) * 8

    # ── component creation ────────────────────────────────────────────
    def addcomponent(self, comp_type, name, x, y, w, h):
        """Create a real Tk widget on the surface. Returns the 0-based index."""
        ct = str(comp_type).upper()
        x, y, w, h = int(x), int(y), int(w), int(h)
        wid = self._make_widget(ct, str(name))
        wid.place(x=x, y=y, width=w, height=h)
        idx = len(self._comps)
        comp = {'type': ct, 'name': str(name), 'widget': wid,
                'x': x, 'y': y, 'w': w, 'h': h,
                'props': {'caption': str(name)}, 'events': {}}
        self._comps.append(comp)
        self._bind_design(wid, idx)
        return idx

    def _make_widget(self, ct, name):
        f = self.widget
        if ct == 'PBUTTON':
            b = tk.Button(f, text=name, relief='raised', overrelief='raised')
            try:
                b.config(activebackground=b.cget('bg'))
            except tk.TclError:
                pass
            return b
        elif ct == 'PLABEL':
            return tk.Label(f, text=name, anchor='w', bg='#D4D0C8')
        elif ct == 'PEDIT':
            e = tk.Entry(f)
            e.insert(0, name)
            return e
        elif ct == 'PCHECKBOX':
            return tk.Checkbutton(f, text=name)
        elif ct == 'PCOMBOBOX':
            cb = ttk.Combobox(f)
            cb.set(name)
            return cb
        elif ct == 'PPANEL':
            p = tk.Frame(f, relief='groove', bd=2, bg='#D4D0C8')
            tk.Label(p, text=name, bg='#D4D0C8', font=(_DEFAULT_FONT_FAMILY, 8)).place(x=2, y=2)
            return p
        elif ct == 'PRADIOBUTTON':
            return tk.Radiobutton(f, text=name)
        elif ct == 'PLISTBOX':
            lb = tk.Listbox(f, font=(_DEFAULT_FONT_FAMILY, 9))
            lb.insert('end', '(ListBox)')
            return lb
        elif ct == 'PGROUPBOX':
            return tk.LabelFrame(f, text=name)
        elif ct == 'PPROGRESSBAR':
            return ttk.Progressbar(f, value=50)
        elif ct == 'PTIMER':
            return tk.Label(f, text='\u23f1 ' + name, bg='#FFFFCC', relief='solid', bd=1,
                            font=(_DEFAULT_FONT_FAMILY, 8))
        elif ct == 'PRICHEDIT':
            t = tk.Text(f, font=(_DEFAULT_FONT_FAMILY, 9), relief='sunken', bd=2)
            t.insert('1.0', name)
            return t
        elif ct == 'PCANVAS':
            return tk.Canvas(f, bg='white', highlightthickness=1, highlightbackground='#999')
        elif ct == 'PMYSQL':
            return tk.Label(f, text='\U0001f5c4 MySQL\n' + name, bg='#E8E8FF',
                            relief='solid', bd=1, font=(_DEFAULT_FONT_FAMILY, 7), justify='center')
        elif ct == 'PSQLITE':
            return tk.Label(f, text='\U0001f5c4 SQLite\n' + name, bg='#E8FFE8',
                            relief='solid', bd=1, font=(_DEFAULT_FONT_FAMILY, 7), justify='center')
        elif ct == 'PTREEVIEW':
            tv = ttk.Treeview(f, show='tree', selectmode='browse')
            tv.insert('', 'end', text='(TreeView)')
            return tv
        elif ct == 'PIMAGE':
            c = tk.Canvas(f, bg='#F0F0F0', highlightthickness=1, highlightbackground='#999')
            c.create_text(50, 50, text='\U0001f5bc ' + name, font=(_DEFAULT_FONT_FAMILY, 8))
            return c
        elif ct == 'PTRACKBAR':
            return ttk.Scale(f, from_=0, to=100, orient='horizontal')
        elif ct == 'PSPLITTER':
            p = tk.Frame(f, bg='#E0E0E0', relief='groove', bd=2)
            tk.Label(p, text='\u2194 ' + name, bg='#E0E0E0', font=(_DEFAULT_FONT_FAMILY, 8)).place(x=2, y=2)
            return p
        elif ct == 'PSTRINGGRID':
            fr = tk.Frame(f, relief='sunken', bd=2, bg='white')
            tk.Label(fr, text='\u2637 ' + name, bg='white', font=(_DEFAULT_FONT_FAMILY, 8)).place(x=2, y=2)
            return fr
        elif ct == 'PSCROLLBOX':
            fr = tk.Frame(f, relief='sunken', bd=1, bg='#F8F8F8')
            tk.Label(fr, text='\u2195 ' + name, bg='#F8F8F8', font=(_DEFAULT_FONT_FAMILY, 8)).place(x=2, y=2)
            return fr
        else:
            return tk.Label(f, text=name, relief='solid', bd=1)

    # ── design-time bindings ──────────────────────────────────────────
    def _bind_design(self, wid, idx):
        def press(e):
            self._comp_press(e, idx)
        def motion(e):
            self._comp_motion(e, idx)
        def release(e):
            self._comp_release(e, idx)
        def dblclick(e):
            self._comp_dblclick(e, idx)
        for w in [wid] + list(wid.winfo_children()):
            w.bind('<ButtonPress-1>', press)
            w.bind('<B1-Motion>', motion)
            w.bind('<ButtonRelease-1>', release)
            w.bind('<Double-Button-1>', dblclick)

    # ── mouse handlers ────────────────────────────────────────────────
    def _bg_press(self, e):
        """Click on empty background area."""
        if self._on_bgclick:
            self._on_bgclick(e.x, e.y)
        else:
            self._selected = -1
            self._hide_handles()
            if self._on_select:
                self._on_select(-1)

    def _comp_press(self, e, idx):
        self._selected = idx
        comp = self._comps[idx]
        self._dragging = True
        self._resizing = -1
        self._drag_sx = e.x_root
        self._drag_sy = e.y_root
        self._drag_ox = comp['x']
        self._drag_oy = comp['y']
        self._drag_ow = comp['w']
        self._drag_oh = comp['h']
        self._show_handles(idx)
        if self._on_select:
            self._on_select(idx)

    def _comp_motion(self, e, idx):
        if not self._dragging or self._selected != idx:
            return
        dx = e.x_root - self._drag_sx
        dy = e.y_root - self._drag_sy
        comp = self._comps[idx]
        comp['x'] = self._snap(self._drag_ox + dx)
        comp['y'] = self._snap(self._drag_oy + dy)
        comp['widget'].place(x=comp['x'], y=comp['y'])
        self._move_handles(idx)

    def _comp_release(self, e, idx):
        if self._dragging:
            self._dragging = False
            if self._on_move:
                c = self._comps[idx]
                self._on_move(idx, c['x'], c['y'], c['w'], c['h'])

    def _comp_dblclick(self, e, idx):
        self._selected = idx
        self._show_handles(idx)
        if self._on_select:
            self._on_select(idx)
        if self._on_dblclick:
            self._on_dblclick(idx)

    # ── selection handles ─────────────────────────────────────────────
    def _handle_positions(self, idx):
        """Compute the 8 handle positions for the given component."""
        c = self._comps[idx]
        x, y, w, h = c['x'], c['y'], c['w'], c['h']
        hs = self._handle_size
        return [
            (x - hs // 2, y - hs // 2),                  # 0 TL
            (x + w // 2 - hs // 2, y - hs // 2),         # 1 T
            (x + w - hs // 2, y - hs // 2),              # 2 TR
            (x + w - hs // 2, y + h // 2 - hs // 2),    # 3 R
            (x + w - hs // 2, y + h - hs // 2),         # 4 BR
            (x + w // 2 - hs // 2, y + h - hs // 2),    # 5 B
            (x - hs // 2, y + h - hs // 2),             # 6 BL
            (x - hs // 2, y + h // 2 - hs // 2),        # 7 L
        ]

    def _show_handles(self, idx):
        self._hide_handles()
        if idx < 0 or idx >= len(self._comps):
            return
        positions = self._handle_positions(idx)
        cursors = ['top_left_corner', 'sb_v_double_arrow', 'top_right_corner',
                    'sb_h_double_arrow', 'bottom_right_corner', 'sb_v_double_arrow',
                    'bottom_left_corner', 'sb_h_double_arrow']
        hs = self._handle_size
        for hi, ((hx, hy), cur) in enumerate(zip(positions, cursors)):
            hf = tk.Frame(self.widget, bg='black', width=hs, height=hs, cursor=cur)
            hf.place(x=hx, y=hy, width=hs, height=hs)
            hf.lift()
            hf.bind('<ButtonPress-1>', lambda e, h=hi: self._hnd_press(e, h))
            hf.bind('<B1-Motion>', lambda e, h=hi: self._hnd_motion(e, h))
            hf.bind('<ButtonRelease-1>', lambda e, h=hi: self._hnd_release(e, h))
            self._handles.append(hf)

    def _hide_handles(self):
        for hf in self._handles:
            hf.destroy()
        self._handles.clear()

    def _move_handles(self, idx):
        """Update handle positions without destroying them (safe during drag/resize)."""
        if idx < 0 or idx >= len(self._comps) or len(self._handles) != 8:
            self._show_handles(idx)
            return
        positions = self._handle_positions(idx)
        for i, (hx, hy) in enumerate(positions):
            self._handles[i].place(x=hx, y=hy)

    def _hnd_press(self, e, hi):
        self._resizing = hi
        self._dragging = False
        self._drag_sx = e.x_root
        self._drag_sy = e.y_root
        c = self._comps[self._selected]
        self._drag_ox = c['x']
        self._drag_oy = c['y']
        self._drag_ow = c['w']
        self._drag_oh = c['h']

    def _hnd_motion(self, e, hi):
        if self._selected < 0:
            return
        dx = e.x_root - self._drag_sx
        dy = e.y_root - self._drag_sy
        ox, oy, ow, oh = self._drag_ox, self._drag_oy, self._drag_ow, self._drag_oh
        x, y, w, h = ox, oy, ow, oh
        if hi == 0:
            x = self._snap(ox + dx); y = self._snap(oy + dy)
            w = ow - (x - ox); h = oh - (y - oy)
        elif hi == 1:
            y = self._snap(oy + dy); h = oh - (y - oy)
        elif hi == 2:
            y = self._snap(oy + dy); w = self._snap(ow + dx); h = oh - (y - oy)
        elif hi == 3:
            w = self._snap(ow + dx)
        elif hi == 4:
            w = self._snap(ow + dx); h = self._snap(oh + dy)
        elif hi == 5:
            h = self._snap(oh + dy)
        elif hi == 6:
            x = self._snap(ox + dx); w = ow - (x - ox); h = self._snap(oh + dy)
        elif hi == 7:
            x = self._snap(ox + dx); w = ow - (x - ox)
        if w < 8:
            w = 8
        if h < 8:
            h = 8
        c = self._comps[self._selected]
        c['x'] = x; c['y'] = y; c['w'] = w; c['h'] = h
        c['widget'].place(x=x, y=y, width=w, height=h)
        self._move_handles(self._selected)

    def _hnd_release(self, e, hi):
        self._resizing = -1
        if self._on_move and self._selected >= 0:
            c = self._comps[self._selected]
            self._on_move(self._selected, c['x'], c['y'], c['w'], c['h'])

    # ── public API callable from RapidP ───────────────────────────────
    def selectcomp(self, index):
        self._selected = int(index)
        if 0 <= self._selected < len(self._comps):
            self._show_handles(self._selected)
        else:
            self._hide_handles()

    def getname(self, index):
        return self._comps[int(index)]['name'] if 0 <= int(index) < len(self._comps) else ''
    def setname(self, index, name):
        idx = int(index)
        if 0 <= idx < len(self._comps):
            self._comps[idx]['name'] = str(name)
    def gettype(self, index):
        return self._comps[int(index)]['type'] if 0 <= int(index) < len(self._comps) else ''

    def getcompx(self, index):
        return self._comps[int(index)]['x'] if 0 <= int(index) < len(self._comps) else 0
    def getcompy(self, index):
        return self._comps[int(index)]['y'] if 0 <= int(index) < len(self._comps) else 0
    def getcompw(self, index):
        return self._comps[int(index)]['w'] if 0 <= int(index) < len(self._comps) else 0
    def getcomph(self, index):
        return self._comps[int(index)]['h'] if 0 <= int(index) < len(self._comps) else 0

    def setcompbounds(self, index, x, y, w, h):
        idx = int(index)
        if 0 <= idx < len(self._comps):
            c = self._comps[idx]
            c['x'] = int(x); c['y'] = int(y); c['w'] = int(w); c['h'] = int(h)
            c['widget'].place(x=c['x'], y=c['y'], width=c['w'], height=c['h'])
            if self._selected == idx:
                self._show_handles(idx)

    def getprop(self, index, prop_name):
        idx = int(index)
        if 0 <= idx < len(self._comps):
            return self._comps[idx]['props'].get(str(prop_name).lower(), '')
        return ''

    def setprop(self, index, prop_name, value):
        idx = int(index)
        if idx < 0 or idx >= len(self._comps):
            return
        c = self._comps[idx]
        pn = str(prop_name).lower()
        c['props'][pn] = value
        wid = c['widget']
        try:
            if pn in ('caption', 'text'):
                c['name'] = str(value) if pn == 'caption' else c['name']
                try:
                    wid.config(text=str(value))
                except tk.TclError:
                    if isinstance(wid, (tk.Entry, ttk.Entry, ttk.Combobox)):
                        wid.delete(0, 'end'); wid.insert(0, str(value))
                    elif isinstance(wid, tk.Text):
                        wid.delete('1.0', 'end'); wid.insert('1.0', str(value))
            elif pn == 'color':
                hex_c = _bgr_to_hex(int(value)) if value != '' else None
                if hex_c:
                    try:
                        wid.config(bg=hex_c)
                        if isinstance(wid, tk.Button):
                            wid.config(activebackground=hex_c)
                    except tk.TclError:
                        pass
            elif pn == 'fontcolor':
                hex_c = _bgr_to_hex(int(value)) if value != '' else None
                if hex_c:
                    try:
                        wid.config(fg=hex_c)
                        if isinstance(wid, tk.Button):
                            wid.config(activeforeground=hex_c)
                    except tk.TclError:
                        pass
            elif pn in ('font.name', 'font.size', 'font.bold', 'font.italic'):
                self._apply_font(c)
            elif pn == 'enabled':
                st = 'normal' if str(value).lower() in ('1', 'true', '-1') else 'disabled'
                try:
                    wid.config(state=st)
                except tk.TclError:
                    pass
            elif pn == 'visible':
                vis = str(value).lower() in ('1', 'true', '-1')
                if vis:
                    wid.place(x=c['x'], y=c['y'], width=c['w'], height=c['h'])
                else:
                    wid.place_forget()
            elif pn == 'borderstyle':
                relief_map = {'0': 'flat', '1': 'solid', '2': 'raised', '3': 'ridge',
                              '4': 'groove', '5': 'sunken',
                              'bsnone': 'flat', 'bssingle': 'solid', 'bssizeable': 'raised',
                              'bsdialog': 'ridge', 'bstoolwindow': 'groove'}
                relief = relief_map.get(str(value).lower(), 'flat')
                try:
                    wid.config(relief=relief)
                except tk.TclError:
                    pass
            elif pn == 'alignment':
                anchor_map = {'0': 'w', '1': 'e', '2': 'center',
                              'taleftalign': 'w', 'tarightalign': 'e', 'tacenter': 'center'}
                anchor = anchor_map.get(str(value).lower(), 'w')
                try:
                    wid.config(anchor=anchor)
                except tk.TclError:
                    pass
            elif pn == 'checked':
                try:
                    if isinstance(wid, (tk.Checkbutton, ttk.Checkbutton)):
                        if str(value).lower() in ('1', 'true', '-1'):
                            wid.select()
                        else:
                            wid.deselect()
                except tk.TclError:
                    pass
            elif pn == 'readonly':
                try:
                    st = 'disabled' if str(value).lower() in ('1', 'true', '-1') else 'normal'
                    wid.config(state=st)
                except tk.TclError:
                    pass
            elif pn == 'wordwrap':
                try:
                    if isinstance(wid, tk.Text):
                        wrap = 'word' if str(value).lower() in ('1', 'true', '-1') else 'none'
                        wid.config(wrap=wrap)
                except tk.TclError:
                    pass
            elif pn == 'bevelinner':
                rm = {'0': 'flat', '1': 'sunken', '2': 'raised', 'bvnone': 'flat',
                      'bvlowered': 'sunken', 'bvraised': 'raised'}
                try:
                    if isinstance(wid, tk.Frame):
                        wid.config(relief=rm.get(str(value).lower(), 'flat'))
                except tk.TclError:
                    pass
            elif pn == 'bevelouter':
                rm = {'0': 'flat', '1': 'sunken', '2': 'raised', 'bvnone': 'flat',
                      'bvlowered': 'sunken', 'bvraised': 'raised'}
                try:
                    if isinstance(wid, tk.Frame):
                        wid.config(relief=rm.get(str(value).lower(), 'raised'))
                except tk.TclError:
                    pass
        except Exception:
            pass

    def _apply_font(self, c):
        """Apply font properties from the component's props dict to its widget."""
        wid = c['widget']
        font_name = c['props'].get('font.name', _DEFAULT_FONT_FAMILY)
        try:
            font_size = int(c['props'].get('font.size', _DEFAULT_FONT_SIZE))
        except (ValueError, TypeError):
            font_size = _DEFAULT_FONT_SIZE
        parts = []
        if str(c['props'].get('font.bold', '0')).lower() in ('1', '-1', 'true'):
            parts.append('bold')
        if str(c['props'].get('font.italic', '0')).lower() in ('1', '-1', 'true'):
            parts.append('italic')
        font_style = ' '.join(parts)
        try:
            wid.config(font=(font_name, font_size, font_style) if font_style else (font_name, font_size))
        except tk.TclError:
            pass

    def getevent(self, index, event_name):
        idx = int(index)
        if 0 <= idx < len(self._comps):
            return self._comps[idx]['events'].get(str(event_name).lower(), '')
        return ''

    def setevent(self, index, event_name, value):
        idx = int(index)
        if 0 <= idx < len(self._comps):
            self._comps[idx]['events'][str(event_name).lower()] = str(value)

    def removecomponent(self, index):
        idx = int(index)
        if 0 <= idx < len(self._comps):
            self._comps[idx]['widget'].destroy()
            self._comps.pop(idx)
            self._hide_handles()
            self._selected = -1
            for i in range(idx, len(self._comps)):
                self._bind_design(self._comps[i]['widget'], i)

    def clearall(self):
        for c in self._comps:
            c['widget'].destroy()
        self._comps.clear()
        self._hide_handles()
        self._selected = -1


class PStringGrid(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self._data = []  # list of lists
        self._cols = 2
        self._col_widths = [100, 150]
        self._row_height = 22
        self._edit_widget = None
        self._edit_row = -1
        self._edit_col = -1
        self._edit_window_id = None
        self._selected_row = -1
        self._selected_col = -1
        self._finishing_edit = False
        self._suggestions = []  # For event grid: list of existing SUB names
        # Container frame for canvas + scrollbar
        self._frame = tk.Frame(p_widget)
        self._frame.place(x=self.left, y=self.top, width=self.width, height=self.height)
        self.widget = tk.Canvas(self._frame, bg='white', highlightthickness=1, highlightbackground='#999')
        self._scrollbar = ttk.Scrollbar(self._frame, orient='vertical', command=self.widget.yview)
        self.widget.configure(yscrollcommand=self._scrollbar.set)
        self._scrollbar.pack(side='right', fill='y')
        self.widget.pack(side='left', fill='both', expand=True)
        self.widget.bind('<ButtonPress-1>', self._on_click)
        self.widget.bind('<Double-Button-1>', self._on_dblclick)
        self.widget.bind('<MouseWheel>', self._on_mousewheel)
        self.widget.bind('<Button-4>', lambda e: self.widget.yview_scroll(-3, 'units'))
        self.widget.bind('<Button-5>', lambda e: self.widget.yview_scroll(3, 'units'))
        self._use_pack = False

    @staticmethod
    def _int_to_hex(color):
        if isinstance(color, str) and color.startswith('#'): return color
        if isinstance(color, (int, float)):
            v = int(color)
            r, g, b = v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF
            return f'#{r:02x}{g:02x}{b:02x}'
        return '#000000'

    def _place_widget(self):
        if getattr(self, '_use_pack', False):
            return  # Using pack layout inside tab frame
        if self._frame and self._visible:
            self._frame.place(x=self._left, y=self._top, width=self._width, height=self._height)
            self._frame.tkraise()
        elif self._frame:
            self._frame.place_forget()

    @property
    def visible(self):
        return 1 if self._visible else 0
    @visible.setter
    def visible(self, value):
        self._visible = bool(int(value))
        self._place_widget()

    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, new_parent):
        """Reparent the grid into a new container (e.g., a tab frame)."""
        self._parent = new_parent
        if hasattr(new_parent, 'widget'):
            p = new_parent.widget
        else:
            p = new_parent  # Raw tk widget (e.g., from PTabControl.tab())
        # Save state
        old_data = list(self._data)
        old_suggestions = list(self._suggestions)
        old_events = dict(self._events)
        # Destroy old frame
        if self._frame:
            self._frame.destroy()
        # Recreate in new parent
        self._frame = tk.Frame(p)
        self.widget = tk.Canvas(self._frame, bg='white', highlightthickness=1, highlightbackground='#999')
        self._scrollbar = ttk.Scrollbar(self._frame, orient='vertical', command=self.widget.yview)
        self.widget.configure(yscrollcommand=self._scrollbar.set)
        self._scrollbar.pack(side='right', fill='y')
        self.widget.pack(side='left', fill='both', expand=True)
        self.widget.bind('<ButtonPress-1>', self._on_click)
        self.widget.bind('<Double-Button-1>', self._on_dblclick)
        self.widget.bind('<MouseWheel>', self._on_mousewheel)
        self.widget.bind('<Button-4>', lambda e: self.widget.yview_scroll(-3, 'units'))
        self.widget.bind('<Button-5>', lambda e: self.widget.yview_scroll(3, 'units'))
        # Restore state
        self._data = old_data
        self._suggestions = old_suggestions
        self._events = old_events
        # Use pack if parent is a raw tk widget (e.g., tab frame)
        if not hasattr(new_parent, '_left'):
            self._use_pack = True
            self._frame.pack(fill='both', expand=True)
        else:
            self._use_pack = False
            self._place_widget()
        self._redraw()

    @property
    def cols(self): return self._cols
    @cols.setter
    def cols(self, val): self._cols = max(1, int(val))

    @property
    def rows(self): return len(self._data)

    @property
    def colwidth(self): return self._col_widths[0] if self._col_widths else 100
    @colwidth.setter
    def colwidth(self, val):
        w = int(val)
        self._col_widths = [w] * self._cols

    def addrow(self, *values):
        row = list(values) + [''] * (self._cols - len(values))
        self._data.append(row[:self._cols])
        self._redraw()

    @property
    def row(self):
        return self._edit_row if self._edit_row >= 0 else self._selected_row
    @property
    def selectedrow(self):
        return self._selected_row
    @property
    def col(self):
        return self._edit_col if self._edit_col >= 0 else self._selected_col

    @property
    def ondblclick(self): return self._events.get('ondblclick')
    @ondblclick.setter
    def ondblclick(self, value):
        self._events['ondblclick'] = value

    @property
    def onclick(self): return self._events.get('onclick')
    @onclick.setter
    def onclick(self, value):
        self._events['onclick'] = value

    @property
    def onchange(self): return self._events.get('onchange')
    @onchange.setter
    def onchange(self, value):
        self._events['onchange'] = value

    def setsuggestions(self, text):
        """Set suggestion items (comma-separated string) for event-like property editing."""
        if text:
            self._suggestions = [s.strip() for s in str(text).replace('\n', ',').split(',') if s.strip()]
        else:
            self._suggestions = []

    def clear(self):
        self._data.clear()
        self._redraw()

    def cell(self, row, col):
        r, c = int(row), int(col)
        if 0 <= r < len(self._data) and 0 <= c < self._cols:
            return self._data[r][c]
        return ''

    def setcell(self, row, col, text):
        r, c = int(row), int(col)
        while len(self._data) <= r:
            self._data.append([''] * self._cols)
        if 0 <= c < self._cols:
            self._data[r][c] = str(text)
            self._redraw()

    def _redraw(self):
        self.widget.delete('all')
        rh = self._row_height
        y = 0
        sel_r = self._selected_row
        for ri, row in enumerate(self._data):
            x = 0
            for ci, val in enumerate(row):
                cw = self._col_widths[ci] if ci < len(self._col_widths) else 100
                if ri == sel_r and ci == 1:
                    bg = '#E8F0FE'
                elif ci == 0:
                    bg = '#F0F0F0'
                else:
                    bg = 'white'
                self.widget.create_rectangle(x, y, x+cw, y+rh, fill=bg, outline='#CCC')
                # Show color swatch for color properties
                prop_name = row[0].lower().strip() if len(row) > 0 else ''
                if ci == 1 and prop_name in ('color', 'bgcolor', 'fgcolor', 'fontcolor'):
                    try:
                        hex_c = self._int_to_hex(int(val)) if val and val != '0' else None
                        if hex_c:
                            sw = rh - 6
                            self.widget.create_rectangle(x+4, y+3, x+4+sw, y+3+sw,
                                                         fill=hex_c, outline='#666')
                            self.widget.create_text(x+4+sw+4, y+rh//2, text=str(val),
                                                   anchor='w', font=('Helvetica', 10), fill='#333')
                        else:
                            self.widget.create_text(x+4, y+rh//2, text=str(val), anchor='w',
                                                   font=('Helvetica', 10), fill='#333')
                    except (ValueError, TypeError):
                        self.widget.create_text(x+4, y+rh//2, text=str(val), anchor='w',
                                               font=('Helvetica', 10), fill='#333')
                else:
                    self.widget.create_text(x+4, y+rh//2, text=str(val), anchor='w',
                                           font=('Helvetica', 10), fill='#333')
                x += cw
            y += rh
        self.widget.configure(scrollregion=(0, 0, sum(self._col_widths[:self._cols]), max(y, 1)))

    def _on_mousewheel(self, e):
        self.widget.yview_scroll(int(-1 * (e.delta / 120)), 'units')

    def _hit_test(self, e):
        """Return (row, col) from a mouse event, accounting for canvas scroll."""
        cy = self.widget.canvasy(e.y)
        cx = self.widget.canvasx(e.x)
        rh = self._row_height
        row = int(cy // rh)
        x = 0
        col = 0
        for ci in range(self._cols):
            cw = self._col_widths[ci] if ci < len(self._col_widths) else 100
            if x <= cx < x + cw:
                col = ci
                break
            x += cw
        return row, col

    def _on_click(self, e):
        self._finish_edit()
        row, col = self._hit_test(e)
        if 0 <= row < len(self._data):
            self._selected_row = row
            self._selected_col = col
            self._redraw()
            self.trigger_event('onclick')
            if col == 1:
                self.widget.after(50, lambda: self._start_edit(row, col))

    def _on_dblclick(self, e):
        row, col = self._hit_test(e)
        if 0 <= row < len(self._data):
            self._selected_row = row
            self._selected_col = col
            self.trigger_event('ondblclick')

    def _start_edit(self, row, col):
        if col != 1 or row >= len(self._data): return
        prop_name = self._data[row][0].lower().strip()
        if not prop_name or prop_name.startswith('('): return

        rh = self._row_height
        x = sum(self._col_widths[:col])
        cw = self._col_widths[col] if col < len(self._col_widths) else 100
        # Convert canvas y to window y for widget placement
        canvas_y = row * rh
        self._edit_row = row
        self._edit_col = col
        val = self._data[row][col] if row < len(self._data) else ''

        if prop_name in ['enabled', 'visible', 'center', 'autosize', 'multiselect', 'showicons', 'checked', 'wordwrap', 'readonly', 'font.bold']:
            self._edit_widget = ttk.Combobox(self.widget, values=['True', 'False'], state='readonly', font=('Helvetica', 10))
            self._edit_widget.set(str(val))
            # Place in canvas coordinate space using a window item
            self._edit_window_id = self.widget.create_window(x, canvas_y, window=self._edit_widget, width=cw, height=rh, anchor='nw')
            self._edit_widget.focus_set()
            self._edit_widget.bind('<<ComboboxSelected>>', lambda e: self.widget.after(10, self._finish_edit))
            return

        if prop_name in ['color', 'bgcolor', 'fgcolor', 'fontcolor']:
            from tkinter import colorchooser
            try:
                init_c = self._int_to_hex(int(val)) if val else None
            except: init_c = None
            c = colorchooser.askcolor(initialcolor=init_c, title='Select Color')
            if c and c[1]:
                rgb = c[0]
                if rgb:
                    color_int = int(rgb[0]) | (int(rgb[1]) << 8) | (int(rgb[2]) << 16)
                    self._data[row][col] = str(color_int)
                    self._redraw()
                    self.trigger_event('onchange')
            self._edit_row = -1
            self._edit_col = -1
            return

        if prop_name in ['font', 'font.name']:
            dlg = PFontDialog()
            dlg.fontname = val if val else 'Helvetica'
            if dlg.execute():
                self._data[row][col] = dlg.fontname
                self._redraw()
                self.trigger_event('onchange')
            self._edit_row = -1
            self._edit_col = -1
            return

        # Event properties: show editable combobox with existing SUB suggestions
        if prop_name.startswith('on') and self._suggestions:
            self._edit_widget = ttk.Combobox(self.widget, values=self._suggestions,
                                             font=('Helvetica', 10))
            self._edit_widget.set(str(val))
            self._edit_window_id = self.widget.create_window(x, canvas_y, window=self._edit_widget,
                                                             width=cw, height=rh, anchor='nw')
            self._edit_widget.focus_set()
            self._edit_widget.bind('<<ComboboxSelected>>', lambda e: self.widget.after(10, self._finish_edit))
            self._edit_widget.bind('<Return>', lambda e: self._finish_edit())
            self._edit_widget.bind('<FocusOut>', lambda e: self.widget.after(10, self._finish_edit))
            return

        self._edit_widget = tk.Entry(self.widget, font=('Helvetica', 10), relief='solid', bd=1)
        self._edit_widget.insert(0, val)
        self._edit_widget.select_range(0, tk.END)
        self._edit_window_id = self.widget.create_window(x, canvas_y, window=self._edit_widget, width=cw, height=rh, anchor='nw')
        self._edit_widget.focus_set()
        self._edit_widget.bind('<Return>', lambda e: self._finish_edit())
        self._edit_widget.bind('<Escape>', lambda e: self._cancel_edit())
        self._edit_widget.bind('<FocusOut>', lambda e: self.widget.after(10, self._finish_edit))

    def _cancel_edit(self):
        if self._edit_widget:
            if self._edit_window_id:
                try: self.widget.delete(self._edit_window_id)
                except: pass
                self._edit_window_id = None
            self._edit_widget.destroy()
            self._edit_widget = None
            self._edit_row = -1
            self._edit_col = -1
            self._redraw()

    def _finish_edit(self):
        if self._finishing_edit:
            return
        self._finishing_edit = True
        try:
            if self._edit_widget and self._edit_row >= 0:
                val = self._edit_widget.get()
                if self._edit_row < len(self._data) and self._edit_col < self._cols:
                    self._data[self._edit_row][self._edit_col] = val
                if self._edit_window_id:
                    try: self.widget.delete(self._edit_window_id)
                    except: pass
                    self._edit_window_id = None
                self._edit_widget.destroy()
                self._edit_widget = None
                self._edit_row = -1
                self._edit_col = -1
                self._redraw()
                self.trigger_event('onchange')
        finally:
            self._finishing_edit = False

class PRichEdit(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self.widget = tk.Text(p_widget, font=(_DEFAULT_FONT_FAMILY, _DEFAULT_FONT_SIZE))
        self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)

    @property
    def text(self): return self.widget.get("1.0", tk.END)
    @text.setter
    def text(self, val): 
        self.widget.delete("1.0", tk.END)
        self.widget.insert("1.0", str(val))

    # ── OnChange event for PRichEdit ──────────────────────────────────
    @property
    def onchange(self): return self._events.get('onchange')
    @onchange.setter
    def onchange(self, value):
        self._events['onchange'] = value
        def _on_mod(e):
            self.trigger_event('onchange')
            self.widget.edit_modified(False)
        self.widget.bind('<<Modified>>', _on_mod, add='+')

class PTimer(PObject):
    def __init__(self, parent=None):
        super().__init__()
        self._interval = 1000
        self._enabled = True
        self._job = None
        self._root = get_root()

    @property
    def interval(self): return self._interval
    @interval.setter
    def interval(self, val): 
        self._interval = int(val)
        self._restart()

    @property
    def enabled(self): return self._enabled
    @enabled.setter
    def enabled(self, val):
        self._enabled = bool(val)
        if self._enabled: 
            self._restart()
        else:
            self._stop()

    @property
    def ontimer(self): return self._events.get('ontimer')
    @ontimer.setter
    def ontimer(self, val):
        self.bind_event('ontimer', val)
        self._restart()

    def _restart(self):
        self._stop()
        if self._enabled and self.ontimer:
            self._job = self._root.after(self._interval, self._tick)

    def _stop(self):
        if self._job:
            self._root.after_cancel(self._job)
            self._job = None

    def _tick(self):
        self.trigger_event('ontimer')
        if self._enabled:
             self._job = self._root.after(self._interval, self._tick)

class PProgressBar(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget = ttk.Progressbar(parent.widget if parent else get_root())
        self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)
        self._position = 0
        self._max = 100

    @property
    def position(self): return self._position
    @position.setter
    def position(self, val):
        self._position = val
        self.widget['value'] = val
        
    @property
    def max(self): return self._max
    @max.setter
    def max(self, val):
        self._max = val
        self.widget['maximum'] = val

class PListView(PWidget):
    """RapidP PListView — multi-column list view for displaying data (like database results).
    
    Supports both single-column (list) and multi-column (report/details) modes.
    Ideal for displaying database query results.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        
        # Create frame to hold treeview and scrollbars
        self._frame = tk.Frame(p_widget)
        self._frame.place(x=self.left, y=self.top, width=self.width, height=self.height)
        
        # Create Treeview with columns support
        self.widget = ttk.Treeview(self._frame, show='headings', selectmode='extended')
        
        # Add scrollbars
        self._vsb = ttk.Scrollbar(self._frame, orient='vertical', command=self.widget.yview)
        self._hsb = ttk.Scrollbar(self._frame, orient='horizontal', command=self.widget.xview)
        self.widget.configure(yscrollcommand=self._vsb.set, xscrollcommand=self._hsb.set)
        
        # Grid layout for treeview and scrollbars
        self.widget.grid(row=0, column=0, sticky='nsew')
        self._vsb.grid(row=0, column=1, sticky='ns')
        self._hsb.grid(row=1, column=0, sticky='ew')
        
        # Make the treeview expandable
        self._frame.grid_rowconfigure(0, weight=1)
        self._frame.grid_columnconfigure(0, weight=1)
        
        self._columns = []  # List of column identifiers
        self._column_widths = {}  # Map of column id -> width
        self._items = {}  # Map of iid -> item data
        self._item_count = 0
        
        # Default single column
        self.addcolumn('Item', 150)
        
        # Bind events
        self.widget.bind('<<TreeviewSelect>>', lambda e: self.trigger_event('onchange'))
        self.widget.bind('<Double-Button-1>', lambda e: self.trigger_event('ondblclick'))
        self.widget.bind('<ButtonPress-1>', lambda e: self.trigger_event('onclick'))
        
    def _place_widget(self):
        """Override to handle frame placement."""
        if self._frame and self._visible:
            self._frame.place(x=self._left, y=self._top, width=self._width, height=self._height)
        elif self._frame:
            self._frame.place_forget()
    
    @property
    def visible(self):
        return 1 if self._visible else 0
    @visible.setter
    def visible(self, value):
        self._visible = bool(int(value))
        self._place_widget()
    
    def addcolumn(self, header, width=100, anchor='w'):
        """Add a column to the listview.
        
        Args:
            header: Column header text
            width: Column width in pixels
            anchor: Text alignment ('w', 'e', 'c', 'n', 's')
        """
        col_id = f'col_{len(self._columns)}'
        self._columns.append(col_id)
        self._column_widths[col_id] = int(width)
        self.widget['columns'] = self._columns
        self.widget.heading(col_id, text=header)
        self.widget.column(col_id, width=int(width), anchor=anchor, minwidth=50)
        return len(self._columns) - 1
    
    def setcolumnwidth(self, index, width):
        """Set the width of a column by index."""
        idx = int(index)
        if 0 <= idx < len(self._columns):
            col_id = self._columns[idx]
            self._column_widths[col_id] = int(width)
            self.widget.column(col_id, width=int(width))
    
    def setcolumntext(self, index, text):
        """Set the header text of a column by index."""
        idx = int(index)
        if 0 <= idx < len(self._columns):
            col_id = self._columns[idx]
            self.widget.heading(col_id, text=str(text))
    
    def additem(self, *values):
        """Add an item (row) to the listview.
        
        Args:
            values: Variable number of column values
            
        Returns:
            Item index (0-based)
        """
        self._item_count += 1
        iid = f'item_{self._item_count}'
        
        # Pad values to match column count
        val_list = list(values)
        while len(val_list) < len(self._columns):
            val_list.append('')
        
        # Insert into treeview (first column value goes to first special column '#0' if exists, otherwise use first column)
        if len(self._columns) > 0:
            self.widget.insert('', 'end', iid=iid, values=val_list[:len(self._columns)])
        else:
            self.widget.insert('', 'end', iid=iid, text=str(values[0]) if values else '')
        
        self._items[iid] = val_list
        return self._item_count - 1
    
    def additems(self, *items):
        """Add multiple items. Each item can be a single value or tuple/list of values."""
        for item in items:
            if isinstance(item, (list, tuple)):
                self.additem(*item)
            else:
                self.additem(str(item))
    
    def addrow(self, *values):
        """Alias for additem - adds a row to the listview."""
        return self.additem(*values)
    
    def insertitem(self, index, *values):
        """Insert an item at a specific position."""
        idx = int(index)
        self._item_count += 1
        iid = f'item_{self._item_count}'
        
        val_list = list(values)
        while len(val_list) < len(self._columns):
            val_list.append('')
        
        # Get iid of item after insertion point
        children = self.widget.get_children()
        if idx < len(children):
            after_iid = children[idx]
            self.widget.insert(self.widget.parent(after_iid), idx, iid=iid, values=val_list[:len(self._columns)])
        else:
            self.widget.insert('', 'end', iid=iid, values=val_list[:len(self._columns)])
        
        self._items[iid] = val_list
        return idx
    
    def deleteitem(self, index):
        """Delete an item by index."""
        idx = int(index)
        children = self.widget.get_children()
        if 0 <= idx < len(children):
            iid = children[idx]
            self.widget.delete(iid)
            if iid in self._items:
                del self._items[iid]
    
    def clear(self):
        """Remove all items from the listview."""
        self.widget.delete(*self.widget.get_children())
        self._items.clear()
        self._item_count = 0
    
    def setitem(self, index, *values):
        """Update an existing item's values."""
        idx = int(index)
        children = self.widget.get_children()
        if 0 <= idx < len(children):
            iid = children[idx]
            val_list = list(values)
            while len(val_list) < len(self._columns):
                val_list.append('')
            self.widget.item(iid, values=val_list[:len(self._columns)])
            self._items[iid] = val_list
    
    def getitem(self, index):
        """Get an item's values as a tuple."""
        idx = int(index)
        children = self.widget.get_children()
        if 0 <= idx < len(children):
            iid = children[idx]
            return tuple(self.widget.item(iid, 'values'))
        return ()
    
    @property
    def itemcount(self):
        """Return the number of items in the listview."""
        return len(self.widget.get_children())
    
    @property
    def selectedindex(self):
        """Return the index of the first selected item, or -1 if none selected."""
        sel = self.widget.selection()
        if sel:
            children = self.widget.get_children()
            try:
                return children.index(sel[0])
            except ValueError:
                return -1
        return -1
    
    @property
    def selectedindices(self):
        """Return a list of all selected item indices."""
        sel = self.widget.selection()
        children = self.widget.get_children()
        return [children.index(iid) for iid in sel if iid in children]
    
    @selectedindex.setter
    def selectedindex(self, value):
        """Set the selected item by index."""
        idx = int(value)
        children = self.widget.get_children()
        if 0 <= idx < len(children):
            self.widget.selection_set(children[idx])
            self.widget.see(children[idx])
        else:
            self.widget.selection_remove(*children)
    
    @property
    def onclick(self): return self._events.get('onclick')
    @onclick.setter
    def onclick(self, value):
        self._events['onclick'] = value
    
    @property
    def ondblclick(self): return self._events.get('ondblclick')
    @ondblclick.setter
    def ondblclick(self, value):
        self._events['ondblclick'] = value
    
    @property
    def onchange(self): return self._events.get('onchange')
    @onchange.setter
    def onchange(self, value):
        self._events['onchange'] = value

class POpenDialog(PObject):
    def __init__(self):
        super().__init__()
        self.filename = ""
        self.filter = ""
    
    @property
    def execute(self):
        import tkinter.filedialog
        self.filename = tkinter.filedialog.askopenfilename()
        return 1 if self.filename else 0
        
    @execute.setter
    def execute(self, val): pass

class PSaveDialog(PObject):
    def __init__(self):
        super().__init__()
        self.filename = ""
        self.filter = ""
    
    @property
    def execute(self):
        import tkinter.filedialog
        self.filename = tkinter.filedialog.asksaveasfilename()
        return 1 if self.filename else 0
        
    @execute.setter
    def execute(self, val): pass

class PFileDialog(PObject):
    def __init__(self, parent=None):
        super().__init__()
        self.filename = ""
        self.initialdir = ""
        self.filter = "All Files|*.*"
        self.multiselect = False
        self.mode = 0 # 0=Open, 1=Save
        self.files = []
        
    @property
    def execute(self):
        if int(self.mode) == 0:
            if self.multiselect:
                res = filedialog.askopenfilenames(initialdir=self.initialdir)
                if res:
                    self.files = [os.path.dirname(res[0])] + list(res)
                    self.filename = res[0]
                    return 1
            else:
                res = filedialog.askopenfilename(initialdir=self.initialdir)
                if res:
                    self.filename = res
                    return 1
        elif int(self.mode) == 1:
            res = filedialog.asksaveasfilename(initialdir=self.initialdir)
            if res:
                self.filename = res
                return 1
        return 0
        
    @execute.setter
    def execute(self, val): pass
    
    @property
    def selcount(self): return len(self.files) - 1 if self.files else 0
         
    @property
    def filetitle(self):
         return os.path.basename(self.filename) if self.filename else ""

class PFileStream(PObject):
    def __init__(self):
        super().__init__()
        self.file = None
        
    def open(self, filename, mode):
        m = 'w' if int(mode) in (1, 65535) else 'r'
        self.file = __builtins__['open'](str(filename), m)
        return 1

    def writeline(self, text):
        if self.file:
            self.file.write(str(text) + '\n')
            
    def readline(self):
        if self.file:
            return self.file.readline().strip()
        return ""
        
    def eof(self):
        if self.file:
            pos = self.file.tell()
            char = self.file.read(1)
            if not char: return 1
            self.file.seek(pos)
            return 0
        return 1
        
    def close(self):
        if self.file:
            self.file.close()
            self.file = None

class PLine(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget = tk.Frame(parent.widget if parent else get_root(), bg="black", height=2)

class PIcon(PObject):
    pass

class PImageList(PObject):
    pass

class PHTML(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            from tkhtmlview import HTMLLabel
            self.widget = HTMLLabel(parent.widget if parent else get_root(), html="<h1>PHTML</h1>")
        except ImportError:
            self.widget = tk.Text(parent.widget if parent else get_root())
            self.widget.insert("1.0", "Please run: pip install tkhtmlview")
            self.widget.config(state=tk.DISABLED)
            
    def loadfromstring(self, html_str):
        try:
            from tkhtmlview import HTMLLabel
            if isinstance(self.widget, HTMLLabel):
                self.widget.set_html(html_str)
        except:
            pass

class Pmidi(PObject):
    def __init__(self):
        super().__init__()
        self._filename = ""
        try:
             import pygame
             pygame.mixer.init()
        except:
             pass

    @property
    def filename(self): return self._filename
    @filename.setter
    def filename(self, val):
        self._filename = str(val)

    def play(self):
        try:
             import pygame
             pygame.mixer.music.load(self._filename)
             pygame.mixer.music.play()
        except:
             pass

    def stop(self):
        try:
             import pygame
             pygame.mixer.music.stop()
        except:
             pass

class PStatusBar(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget = tk.Label(parent.widget if parent else get_root(), text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.widget.pack(side=tk.BOTTOM, fill=tk.X)
        
    @property
    def left(self): return 0
    @left.setter
    def left(self, val): pass
    @property
    def top(self): return 0
    @top.setter
    def top(self, val): pass
    @property
    def width(self): return 0
    @width.setter
    def width(self, val): pass
    @property
    def height(self): return 0
    @height.setter
    def height(self, val): pass
        
    @property
    def simpletext(self): return self.widget['text']
    @simpletext.setter
    def simpletext(self, val):
        self.widget.config(text=str(val))


# ── Dialog Components ─────────────────────────────────────────────────
class PColorDialog(PObject):
    """Wraps tkinter.colorchooser — RapidP-style color picker."""
    def __init__(self):
        super().__init__()
        self._color = 0
        self._hex = ''

    @property
    def color(self): return self._color
    @color.setter
    def color(self, val): self._color = int(val) if val else 0

    def execute(self):
        from tkinter import colorchooser
        result = colorchooser.askcolor(title='Choose Color')
        if result and result[1]:
            self._hex = result[1]
            rgb = result[0]
            if rgb:
                self._color = int(rgb[0]) | (int(rgb[1]) << 8) | (int(rgb[2]) << 16)
            return True
        return False


class PFontDialog(PObject):
    """Font selection dialog — RapidP-style."""
    def __init__(self):
        super().__init__()
        self._fontname = ''
        self._fontsize = 9
        self._result = False

    @property
    def fontname(self): return self._fontname
    @fontname.setter
    def fontname(self, val): self._fontname = str(val)

    @property
    def fontsize(self): return self._fontsize
    @fontsize.setter
    def fontsize(self, val): self._fontsize = int(val) if val else 9

    def execute(self):
        import tkinter.font as tkfont
        top = tk.Toplevel(get_root())
        top.title('Choose Font')
        top.geometry('320x420')
        top.grab_set()
        self._result = False

        tk.Label(top, text='Font:', font=('Helvetica', 10)).pack(anchor='w', padx=8, pady=4)
        lb = tk.Listbox(top, font=('Helvetica', 9))
        lb.pack(fill='both', expand=True, padx=8, pady=2)
        families = sorted(set(tkfont.families()))
        for f in families:
            lb.insert('end', f)

        sf = tk.Frame(top)
        sf.pack(fill='x', padx=8, pady=4)
        tk.Label(sf, text='Size:').pack(side='left')
        size_var = tk.StringVar(value=str(self._fontsize))
        tk.Entry(sf, textvariable=size_var, width=5).pack(side='left', padx=4)

        def ok():
            sel = lb.curselection()
            if sel:
                self._fontname = families[sel[0]]
            try:
                self._fontsize = int(size_var.get())
            except:
                pass
            self._result = True
            top.destroy()

        def cancel():
            top.destroy()

        bf = tk.Frame(top)
        bf.pack(pady=4)
        tk.Button(bf, text='OK', width=8, command=ok).pack(side='left', padx=4)
        tk.Button(bf, text='Cancel', width=8, command=cancel).pack(side='left', padx=4)

        top.wait_window()
        return self._result


class PScrollBar(PWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        p_widget = parent.widget if parent else get_root()
        self.widget = ttk.Scrollbar(p_widget, orient='vertical')
        self.widget.place(x=self.left, y=self.top, width=self.width, height=self.height)


# ── Phase 2: New Runtime Components ──

class PTreeView(PWidget):
    """RapidP PTreeView — wraps ttk.Treeview in tree mode."""
    def __init__(self, parent=None):
        super().__init__(parent)
        p = parent.widget if parent else get_root()
        frame = tk.Frame(p)
        frame.place(x=0, y=0, width=200, height=150)
        self.widget = frame
        self._tree = ttk.Treeview(frame, show='tree')
        vsb = ttk.Scrollbar(frame, orient='vertical', command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        self._items = {}
        self._item_count = 0
        self._bind_widget_events(self._tree)

    def additem(self, text, parent_key=''):
        self._item_count += 1
        key = f'item_{self._item_count}'
        iid = self._tree.insert(parent_key, 'end', iid=key, text=str(text))
        self._items[self._item_count] = iid
        return self._item_count

    def addchild(self, parent_index, text):
        parent_key = self._items.get(int(parent_index), '')
        return self.additem(text, parent_key)

    def clear(self):
        self._tree.delete(*self._tree.get_children())
        self._items.clear()
        self._item_count = 0

    def expandall(self):
        def _expand(item):
            self._tree.item(item, open=True)
            for child in self._tree.get_children(item):
                _expand(child)
        for item in self._tree.get_children():
            _expand(item)

    def collapseall(self):
        def _collapse(item):
            self._tree.item(item, open=False)
            for child in self._tree.get_children(item):
                _collapse(child)
        for item in self._tree.get_children():
            _collapse(item)

    @property
    def itemcount(self):
        return self._item_count


class PImage(PWidget):
    """RapidP PImage — image display widget using Canvas + optional PIL."""
    def __init__(self, parent=None):
        super().__init__(parent)
        p = parent.widget if parent else get_root()
        self.widget = tk.Canvas(p, bg='white', highlightthickness=0)
        self.widget.place(x=0, y=0, width=100, height=100)
        self._photo = None
        self._pil_image = None
        self._autosize = 0
        self._stretch = 0
        self._bind_widget_events(self.widget)

    def loadfromfile(self, filename):
        filename = str(filename)
        try:
            from PIL import Image, ImageTk
            self._pil_image = Image.open(filename)
            if self._stretch:
                self._pil_image = self._pil_image.resize(
                    (int(self.width), int(self.height)), Image.LANCZOS)
            elif self._autosize:
                self.width = self._pil_image.width
                self.height = self._pil_image.height
            self._photo = ImageTk.PhotoImage(self._pil_image)
            self.widget.delete('all')
            self.widget.create_image(0, 0, anchor='nw', image=self._photo)
        except ImportError:
            # Fallback: try Tk's built-in PhotoImage (GIF/PGM/PPM only)
            try:
                self._photo = tk.PhotoImage(file=filename)
                self.widget.delete('all')
                self.widget.create_image(0, 0, anchor='nw', image=self._photo)
            except Exception:
                pass

    def savetofile(self, filename):
        if self._pil_image:
            self._pil_image.save(str(filename))

    @property
    def autosize(self): return self._autosize
    @autosize.setter
    def autosize(self, val): self._autosize = int(val)

    @property
    def stretch(self): return self._stretch
    @stretch.setter
    def stretch(self, val): self._stretch = int(val)

    def cls(self):
        self.widget.delete('all')

    def pset(self, x, y, color=0):
        hex_color = _bgr_to_hex(int(color)) or '#000000'
        self.widget.create_rectangle(int(x), int(y), int(x)+1, int(y)+1, fill=hex_color, outline='')

    def line(self, x1, y1, x2, y2, color=0):
        hex_color = _bgr_to_hex(int(color)) or '#000000'
        self.widget.create_line(int(x1), int(y1), int(x2), int(y2), fill=hex_color)

    def circle(self, x, y, radius, color=0):
        hex_color = _bgr_to_hex(int(color)) or '#000000'
        r = int(radius)
        self.widget.create_oval(int(x)-r, int(y)-r, int(x)+r, int(y)+r, outline=hex_color)

    def textout(self, x, y, text, color=0):
        hex_color = _bgr_to_hex(int(color)) or '#000000'
        self.widget.create_text(int(x), int(y), text=str(text), anchor='nw', fill=hex_color)

    def fillrect(self, x1, y1, x2, y2, color=0):
        hex_color = _bgr_to_hex(int(color)) or '#000000'
        self.widget.create_rectangle(int(x1), int(y1), int(x2), int(y2), fill=hex_color, outline='')

    @property
    def image(self):
        return self._pil_image

    @image.setter
    def image(self, value):
        """Set image from a file path string."""
        if isinstance(value, str) and value:
            self.loadfromfile(value)

    def loadfromplot(self, pmatplotlib):
        """Load image from a PMatPlotLib plot buffer."""
        try:
            from PIL import Image, ImageTk
            buf = pmatplotlib.saveto_buffer()
            self._pil_image = Image.open(buf)
            if self._stretch:
                self._pil_image = self._pil_image.resize(
                    (int(self.width), int(self.height)), Image.LANCZOS)
            elif self._autosize:
                self.width = self._pil_image.width
                self.height = self._pil_image.height
            self._photo = ImageTk.PhotoImage(self._pil_image)
            self.widget.delete('all')
            self.widget.create_image(0, 0, anchor='nw', image=self._photo)
        except ImportError:
            pass

    @property
    def bmpwidth(self):
        if self._pil_image:
            return self._pil_image.width
        return 0

    @property
    def bmpheight(self):
        if self._pil_image:
            return self._pil_image.height
        return 0


class PSplitter(PWidget):
    """RapidP PSplitter — wraps tk.PanedWindow."""
    def __init__(self, parent=None):
        super().__init__(parent)
        p = parent.widget if parent else get_root()
        self._orientation = 'horizontal'
        self.widget = tk.PanedWindow(p, orient=tk.HORIZONTAL, sashwidth=5)
        self.widget.place(x=0, y=0, width=300, height=200)
        self._control1 = None
        self._control2 = None

    @property
    def orientation(self): return 0 if self._orientation == 'horizontal' else 1
    @orientation.setter
    def orientation(self, val):
        self._orientation = 'vertical' if int(val) else 'horizontal'
        self.widget.configure(orient=tk.VERTICAL if int(val) else tk.HORIZONTAL)

    @property
    def control1(self): return self._control1
    @control1.setter
    def control1(self, widget):
        self._control1 = widget
        if hasattr(widget, 'widget'):
            self.widget.add(widget.widget)

    @property
    def control2(self): return self._control2
    @control2.setter
    def control2(self, widget):
        self._control2 = widget
        if hasattr(widget, 'widget'):
            self.widget.add(widget.widget)


class PTrackBar(PWidget):
    """RapidP PTrackBar — wraps ttk.Scale."""
    def __init__(self, parent=None):
        super().__init__(parent)
        p = parent.widget if parent else get_root()
        self._var = tk.DoubleVar(value=0)
        self.widget = ttk.Scale(p, from_=0, to=100, variable=self._var,
                                orient='horizontal', command=self._on_change)
        self.widget.place(x=0, y=0, width=150, height=25)
        self._min = 0
        self._max = 100

    def _on_change(self, val):
        self.trigger_event('onchange')

    @property
    def position(self): return int(self._var.get())
    @position.setter
    def position(self, val): self._var.set(int(val))

    @property
    def min(self): return self._min
    @min.setter
    def min(self, val):
        self._min = int(val)
        self.widget.configure(from_=self._min)

    @property
    def max(self): return self._max
    @max.setter
    def max(self, val):
        self._max = int(val)
        self.widget.configure(to=self._max)

    @property
    def orientation(self): return 0 if str(self.widget.cget('orient')) == 'horizontal' else 1
    @orientation.setter
    def orientation(self, val):
        self.widget.configure(orient='vertical' if int(val) else 'horizontal')


class PScrollBox(PWidget):
    """RapidP PScrollBox — scrollable container using Canvas + Frame."""
    def __init__(self, parent=None):
        super().__init__(parent)
        p = parent.widget if parent else get_root()
        frame = tk.Frame(p)
        frame.place(x=0, y=0, width=200, height=150)
        self.widget = frame
        self._canvas = tk.Canvas(frame, highlightthickness=0)
        self._vsb = ttk.Scrollbar(frame, orient='vertical', command=self._canvas.yview)
        self._hsb = ttk.Scrollbar(frame, orient='horizontal', command=self._canvas.xview)
        self._canvas.configure(yscrollcommand=self._vsb.set, xscrollcommand=self._hsb.set)
        self._inner = tk.Frame(self._canvas)
        self._canvas.create_window((0, 0), window=self._inner, anchor='nw')
        self._inner.bind('<Configure>', lambda e: self._canvas.configure(scrollregion=self._canvas.bbox('all')))
        self._vsb.pack(side='right', fill='y')
        self._hsb.pack(side='bottom', fill='x')
        self._canvas.pack(side='left', fill='both', expand=True)


class PPopupMenu(PObject):
    """RapidP PPopupMenu — wraps tk.Menu(tearoff=0)."""
    def __init__(self, parent=None):
        super().__init__()
        root = parent.widget if parent and hasattr(parent, 'widget') else get_root()
        self.widget = tk.Menu(root, tearoff=0)
        self._items = []

    def additem(self, label, callback=None):
        if str(label) == '-':
            self.widget.add_separator()
        else:
            self.widget.add_command(label=str(label), command=callback)
        self._items.append(label)

    def additems(self, *labels):
        for label in labels:
            self.additem(label)

    def popup(self, x=None, y=None):
        try:
            root = get_root()
            if x is None:
                x = root.winfo_pointerx()
            if y is None:
                y = root.winfo_pointery()
            self.widget.tk_popup(int(x), int(y))
        except Exception:
            pass

    def clear(self):
        self.widget.delete(0, 'end')
        self._items.clear()


class PIni(PObject):
    """RapidP PIni — INI file reader/writer using configparser."""
    def __init__(self, parent=None):
        super().__init__()
        import configparser
        self._parser = configparser.ConfigParser()
        self._filename = ''
        self._section = 'DEFAULT'

    @property
    def filename(self): return self._filename
    @filename.setter
    def filename(self, val):
        self._filename = str(val)
        if os.path.isfile(self._filename):
            self._parser.read(self._filename)

    @property
    def section(self): return self._section
    @section.setter
    def section(self, val): self._section = str(val)

    def readstring(self, key, default=''):
        try:
            return self._parser.get(self._section, str(key))
        except Exception:
            return str(default)

    def writestring(self, key, value):
        if not self._parser.has_section(self._section) and self._section != 'DEFAULT':
            self._parser.add_section(self._section)
        self._parser.set(self._section, str(key), str(value))
        if self._filename:
            with open(self._filename, 'w') as f:
                self._parser.write(f)

    def readinteger(self, key, default=0):
        try:
            return int(self._parser.get(self._section, str(key)))
        except Exception:
            return int(default)

    def writeinteger(self, key, value):
        self.writestring(key, str(int(value)))

    def deletesection(self, section=None):
        section = section or self._section
        self._parser.remove_section(str(section))
        if self._filename:
            with open(self._filename, 'w') as f:
                self._parser.write(f)

    def deletekey(self, key, section=None):
        section = section or self._section
        self._parser.remove_option(str(section), str(key))
        if self._filename:
            with open(self._filename, 'w') as f:
                self._parser.write(f)


class PMemoryStream(PObject):
    """RapidP PMemoryStream — wraps io.BytesIO."""
    def __init__(self, parent=None):
        super().__init__()
        import io
        self._stream = io.BytesIO()

    @property
    def position(self): return self._stream.tell()
    @position.setter
    def position(self, val): self._stream.seek(int(val))

    @property
    def size(self): return len(self._stream.getvalue())

    def write(self, data):
        if isinstance(data, str):
            self._stream.write(data.encode('latin-1'))
        else:
            self._stream.write(bytes(data))

    def read(self, count=-1):
        if count < 0:
            return self._stream.read().decode('latin-1', errors='replace')
        return self._stream.read(int(count)).decode('latin-1', errors='replace')

    def readbyte(self):
        b = self._stream.read(1)
        return b[0] if b else 0

    def writebyte(self, val):
        self._stream.write(bytes([int(val) & 0xFF]))

    def savetofile(self, filename):
        with open(str(filename), 'wb') as f:
            f.write(self._stream.getvalue())

    def loadfromfile(self, filename):
        with open(str(filename), 'rb') as f:
            self._stream = __import__('io').BytesIO(f.read())

    def clear(self):
        self._stream = __import__('io').BytesIO()

    def copyto(self, dest_stream):
        if hasattr(dest_stream, '_stream'):
            dest_stream._stream.write(self._stream.getvalue())


class PStringList(PObject):
    """RapidP PStringList — list of strings with helper methods."""
    def __init__(self, parent=None):
        super().__init__()
        self._items = []

    @property
    def count(self): return len(self._items)

    @property
    def text(self):
        return '\n'.join(self._items)
    @text.setter
    def text(self, val):
        self._items = str(val).split('\n')

    def add(self, item):
        self._items.append(str(item))

    def delete(self, index):
        index = int(index)
        if 0 <= index < len(self._items):
            del self._items[index]

    def clear(self):
        self._items.clear()

    def sort(self):
        self._items.sort()

    def indexof(self, item):
        try:
            return self._items.index(str(item))
        except ValueError:
            return -1

    def insert(self, index, item):
        self._items.insert(int(index), str(item))

    def exchange(self, i, j):
        i, j = int(i), int(j)
        self._items[i], self._items[j] = self._items[j], self._items[i]

    def loadfromfile(self, filename):
        with open(str(filename), 'r', encoding='latin-1') as f:
            self._items = f.read().splitlines()

    def savetofile(self, filename):
        with open(str(filename), 'w', encoding='latin-1') as f:
            f.write('\n'.join(self._items))

    def item(self, index):
        index = int(index)
        if 0 <= index < len(self._items):
            return self._items[index]
        return ''

    def setitem(self, index, value):
        index = int(index)
        if 0 <= index < len(self._items):
            self._items[index] = str(value)


class PPrinter(PObject):
    """RapidP PPrinter — basic printing support."""
    def __init__(self, parent=None):
        super().__init__()
        self._lines = []
        self._current_page = []
        self._pages = []

    def begindoc(self):
        self._lines = []
        self._current_page = []
        self._pages = []

    def enddoc(self):
        if self._current_page:
            self._pages.append(self._current_page)
        # Attempt to print via platform default
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as f:
                for page in self._pages:
                    for line in page:
                        f.write(line + '\n')
                    f.write('\f')  # form feed
                tmp_path = f.name
            import platform
            if platform.system() == 'Darwin':
                os.system(f'lpr "{tmp_path}"')
            elif platform.system() == 'Windows':
                os.startfile(tmp_path, 'print')
            else:
                os.system(f'lpr "{tmp_path}"')
        except Exception:
            pass

    def newpage(self):
        self._pages.append(self._current_page)
        self._current_page = []

    def textout(self, x, y, text):
        self._current_page.append(str(text))

    def printline(self, text):
        self._current_page.append(str(text))
