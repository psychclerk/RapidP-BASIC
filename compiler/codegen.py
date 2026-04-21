from compiler.ast_nodes import *
from compiler.errors import ErrorCollector, RapidPWarning

def _normalize_comp_type(name):
    """Normalize Q-prefixed component types to P-prefixed (in an intent to maintain backward compatibility with RapidQ source)."""
    if name and name.upper().startswith('Q') and len(name) > 1 and name[1:2].isalpha():
        return 'P' + name[1:]
    return name

# --- Property/Method Registry for Known Types ---
# Maps component type -> set of valid properties and methods
# This is used for semantic validation only (not code generation)
COMPONENT_REGISTRY = {
    'PFORM': {
        'props': {'caption', 'width', 'height', 'top', 'left', 'visible', 'color', 'borderstyle',
                  'windowstate', 'formstyle', 'center', 'autosize', 'font', 'fontsize', 'fontcolor',
                  'icon', 'alphaBlend', 'alphablendvalue', 'parent', 'tag', 'cursor', 'enabled',
                  'hint', 'showhint', 'popupmenu', 'helpfile', 'helpcontext'},
        'methods': {'show', 'showmodal', 'close', 'center', 'repaint', 'refresh', 'hide',
                    'setfocus', 'bringtofront', 'sendtoback', 'update'},
        'events': {'onclick', 'onclose', 'onresize', 'onshow', 'onhide', 'onactivate',
                   'ondeactivate', 'onpaint', 'onmousemove', 'onmousedown', 'onmouseup',
                   'onkeydown', 'onkeyup', 'onkeypress', 'ondblclick', 'ontimer', 'onload'}
    },
    'PBUTTON': {
        'props': {'caption', 'width', 'height', 'top', 'left', 'visible', 'enabled', 'font',
                  'fontsize', 'fontcolor', 'color', 'hint', 'showhint', 'cursor', 'tag', 'parent', 'taborder'},
        'methods': {'setfocus', 'repaint', 'refresh', 'bringtofront', 'sendtoback'},
        'events': {'onclick', 'onmousedown', 'onmouseup', 'onmousemove'}
    },
    'PLABEL': {
        'props': {'caption', 'width', 'height', 'top', 'left', 'visible', 'enabled', 'font',
                  'fontsize', 'fontcolor', 'color', 'alignment', 'autosize', 'wordwrap', 'transparent',
                  'hint', 'showhint', 'cursor', 'tag', 'parent', 'fontbold', 'fontitalic', 'fontunderline'},
        'methods': {'repaint', 'refresh'},
        'events': {'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmousemove'}
    },
    'PEDIT': {
        'props': {'text', 'width', 'height', 'top', 'left', 'visible', 'enabled', 'font',
                  'fontsize', 'fontcolor', 'color', 'maxlength', 'readonly', 'passwordchar',
                  'alignment', 'borderstyle', 'hint', 'showhint', 'cursor', 'tag', 'parent', 'taborder', 'selstart', 'sellength', 'seltext'},
        'methods': {'setfocus', 'clear', 'selectall', 'copytoclipboard', 'cuttoclipboard',
                    'pastefromclipboard', 'undo', 'repaint', 'refresh'},
        'events': {'onchange', 'onclick', 'ondblclick', 'onkeydown', 'onkeyup', 'onkeypress'}
    },
    'PCANVAS': {
        'props': {'width', 'height', 'top', 'left', 'visible', 'color', 'font', 'fontsize',
                  'fontcolor', 'pen', 'brush', 'tag', 'parent', 'cursor', 'autoredraw'},
        'methods': {'cls', 'paint', 'pset', 'line', 'circle', 'textout', 'textwidth', 'textheight',
                    'fillrect', 'rectangle', 'floodfill', 'draw', 'stretch', 'copyrect',
                    'loadfromfile', 'savetofile', 'repaint', 'refresh'},
        'events': {'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmousemove', 'onpaint', 'onkeydown', 'onkeyup'}
    },
    'PPANEL': {
        'props': {'caption', 'width', 'height', 'top', 'left', 'visible', 'color', 'alignment',
                  'bevelinner', 'bevelouter', 'borderstyle', 'font', 'fontsize', 'fontcolor',
                  'hint', 'showhint', 'cursor', 'tag', 'parent', 'enabled'},
        'methods': {'repaint', 'refresh', 'bringtofront', 'sendtoback'},
        'events': {'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmousemove', 'onresize'}
    },
    'PCHECKBOX': {
        'props': {'caption', 'checked', 'width', 'height', 'top', 'left', 'visible', 'enabled',
                  'font', 'fontsize', 'fontcolor', 'color', 'state', 'hint', 'showhint', 'cursor', 'tag', 'parent'},
        'methods': {'setfocus', 'repaint', 'refresh'},
        'events': {'onclick', 'onchange'}
    },
    'PRADIOBUTTON': {
        'props': {'caption', 'checked', 'width', 'height', 'top', 'left', 'visible', 'enabled',
                  'font', 'fontsize', 'fontcolor', 'color', 'hint', 'showhint', 'cursor', 'tag', 'parent'},
        'methods': {'setfocus', 'repaint', 'refresh'},
        'events': {'onclick'}
    },
    'PCOMBOBOX': {
        'props': {'text', 'itemindex', 'itemcount', 'width', 'height', 'top', 'left', 'visible',
                  'enabled', 'font', 'fontsize', 'fontcolor', 'color', 'sorted', 'style', 'hint',
                  'showhint', 'cursor', 'tag', 'parent', 'taborder'},
        'methods': {'additem', 'additems', 'clear', 'deleteitem', 'setfocus', 'repaint', 'refresh'},
        'events': {'onchange', 'onclick', 'ondblclick'}
    },
    'PLISTBOX': {
        'props': {'itemindex', 'itemcount', 'width', 'height', 'top', 'left', 'visible', 'enabled',
                  'font', 'fontsize', 'fontcolor', 'color', 'sorted', 'multiselect', 'hint',
                  'showhint', 'cursor', 'tag', 'parent', 'taborder'},
        'methods': {'additem', 'additems', 'clear', 'deleteitem', 'setfocus', 'repaint', 'refresh', 'item'},
        'events': {'onclick', 'ondblclick', 'onchange'}
    },
    'PGROUPBOX': {
        'props': {'caption', 'width', 'height', 'top', 'left', 'visible', 'color', 'font',
                  'fontsize', 'fontcolor', 'hint', 'showhint', 'cursor', 'tag', 'parent', 'enabled'},
        'methods': {'repaint', 'refresh'},
        'events': {'onclick'}
    },
    'PRICHEDIT': {
        'props': {'text', 'width', 'height', 'top', 'left', 'visible', 'enabled', 'readonly',
                  'font', 'fontsize', 'fontcolor', 'color', 'wordwrap', 'scrollbars', 'line',
                  'linecount', 'selstart', 'sellength', 'seltext', 'hint', 'showhint', 'cursor',
                  'tag', 'parent', 'taborder', 'borderstyle', 'alignment'},
        'methods': {'clear', 'setfocus', 'selectall', 'copytoclipboard', 'cuttoclipboard',
                    'pastefromclipboard', 'undo', 'loadfromfile', 'savetofile', 'addstrings', 'repaint', 'refresh'},
        'events': {'onchange', 'onclick', 'ondblclick', 'onkeydown', 'onkeyup', 'onkeypress'}
    },
    'PTIMER': {
        'props': {'interval', 'enabled', 'tag'},
        'methods': set(),
        'events': {'ontimer'}
    },
    'PPROGRESSBAR': {
        'props': {'min', 'max', 'position', 'width', 'height', 'top', 'left', 'visible',
                  'color', 'hint', 'showhint', 'tag', 'parent'},
        'methods': {'stepit', 'stepby', 'repaint', 'refresh'},
        'events': set()
    },
    'PSTRINGGRID': {
        'props': {'cols', 'rows', 'fixedcols', 'fixedrows', 'colcount', 'rowcount', 'colwidth',
                  'rowheight', 'gridlinewidth', 'defaultcolwidth', 'defaultrowheight', 'width',
                  'height', 'top', 'left', 'visible', 'enabled', 'color', 'font', 'fontsize',
                  'fontcolor', 'scrollbars', 'options', 'col', 'row', 'selectedrow', 'hint', 'showhint', 'cursor',
                  'tag', 'parent', 'editorenabled', 'borderstyle', 'flat', 'cell', 'cells', 'rowsel', 'colsel'},
        'methods': {'addrow', 'deleterow', 'insertrow', 'clear', 'setcell', 'getcell',
                    'setcolwidth', 'repaint', 'refresh', 'setfocus', 'setsuggestions'},
        'events': {'onclick', 'ondblclick', 'onselectcell', 'ondrawcell', 'onchange', 'onrowselect'}
    },
    'PTABCONTROL': {
        'props': {'tabindex', 'tabcount', 'width', 'height', 'top', 'left', 'visible', 'enabled',
                  'font', 'fontsize', 'fontcolor', 'color', 'hint', 'showhint', 'cursor', 'tag', 'parent'},
        'methods': {'addtab', 'addtabs', 'deletetab', 'repaint', 'refresh', 'tab'},
        'events': {'onchange', 'onclick'}
    },
    'PMAINMENU': {
        'props': {'tag'},
        'methods': set(),
        'events': set()
    },
    'PMENUITEM': {
        'props': {'caption', 'checked', 'enabled', 'visible', 'shortcut', 'tag'},
        'methods': {'clear'},
        'events': {'onclick'}
    },
    'PSCROLLBAR': {
        'props': {'min', 'max', 'position', 'smallchange', 'largechange', 'kind', 'width', 'height',
                  'top', 'left', 'visible', 'enabled', 'tag', 'parent'},
        'methods': {'repaint', 'refresh'},
        'events': {'onchange'}
    },
    'PCODEEDITOR': {
        'props': {'text', 'width', 'height', 'top', 'left', 'visible', 'enabled', 'font',
                  'fontsize', 'fontcolor', 'color', 'readonly', 'linenumbers', 'wordwrap',
                  'selstart', 'sellength', 'seltext', 'line', 'linecount', 'caretx', 'carety',
                  'hint', 'showhint', 'cursor', 'tag', 'parent', 'highlighttypes', 'autocompletelist',
                  'borderstyle'},
        'methods': {'clear', 'setfocus', 'selectall', 'copytoclipboard', 'cuttoclipboard',
                    'pastefromclipboard', 'undo', 'redo', 'loadfromfile', 'savetofile',
                    'addstrings', 'gotosub', 'gotoline', 'getsublist', 'repaint', 'refresh'},
        'events': {'onchange', 'onclick', 'ondblclick', 'onkeydown', 'onkeyup', 'onkeypress'}
    },
    'PIMAGE': {
        'props': {'width', 'height', 'top', 'left', 'visible', 'stretch', 'center', 'autosize',
                  'bmpwidth', 'bmpheight', 'transparent', 'hint', 'showhint', 'cursor', 'tag', 'parent'},
        'methods': {'loadfromfile', 'savetofile', 'draw', 'stretch', 'copyrect', 'pixel',
                    'circle', 'line', 'pset', 'cls', 'fillrect', 'textout', 'repaint', 'refresh'},
        'events': {'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmousemove', 'onpaint'}
    },
    'PLISTVIEW': {
        'props': {'width', 'height', 'top', 'left', 'visible', 'enabled', 'viewstyle', 'multiselect',
                  'gridlines', 'checkboxes', 'rowselect', 'sorttype', 'sortcolumn', 'itemcount',
                  'itemindex', 'font', 'fontsize', 'fontcolor', 'color', 'hint', 'showhint',
                  'cursor', 'tag', 'parent', 'smallimages', 'largeimages', 'columns', 'selectedindex'},
        'methods': {'addcolumn', 'additem', 'addrow', 'deleteitem', 'clear', 'setfocus', 'repaint', 'refresh',
                    'itemcheck', 'subitem', 'insertitem', 'setitem', 'getitem', 'setcolumnwidth', 'setcolumntext'},
        'events': {'onclick', 'ondblclick', 'oncolumnclick', 'onchange', 'onitemcheck'}
    },
    'PFILESTREAM': {
        'props': {'position', 'size', 'tag'},
        'methods': {'open', 'close', 'read', 'write', 'readline', 'writeline', 'readnum',
                    'writenum', 'eof', 'seek'},
        'events': set()
    },
    'POPENDIALOG': {
        'props': {'filename', 'filter', 'initialdir', 'title', 'filterindex', 'defaultext', 'tag'},
        'methods': {'execute'},
        'events': set()
    },
    'PSAVEDIALOG': {
        'props': {'filename', 'filter', 'initialdir', 'title', 'filterindex', 'defaultext', 'tag'},
        'methods': {'execute'},
        'events': set()
    },
    'PFILEDIALOG': {
        'props': {'filename', 'filter', 'initialdir', 'title', 'filterindex', 'defaultext', 'tag'},
        'methods': {'execute'},
        'events': set()
    },
    'PCOLORDIALOG': {
        'props': {'color', 'tag'},
        'methods': {'execute'},
        'events': set()
    },
    'PFONTDIALOG': {
        'props': {'fontname', 'fontsize', 'fontcolor', 'fontstyle', 'tag'},
        'methods': {'execute'},
        'events': set()
    },
    'PSTATUSBAR': {
        'props': {'caption', 'simpletext', 'simplepanel', 'panels', 'panelcount', 'font', 'fontsize', 'fontcolor',
                  'visible', 'tag', 'parent'},
        'methods': {'addpanel', 'repaint', 'refresh'},
        'events': {'onclick'}
    },
    'PLINE': {
        'props': {'x1', 'y1', 'x2', 'y2', 'color', 'width', 'visible', 'tag', 'parent'},
        'methods': set(),
        'events': set()
    },
    'PICON': {
        'props': {'filename', 'handle', 'tag'},
        'methods': {'loadfromfile'},
        'events': set()
    },
    'PIMAGELIST': {
        'props': {'count', 'width', 'height', 'tag'},
        'methods': {'addimage', 'addimages', 'clear'},
        'events': set()
    },
    'PMYSQL': {
        'props': {'host', 'user', 'password', 'database', 'port', 'connected', 'rowcount',
                  'colcount', 'fieldcount', 'fieldname', 'row', 'dbcount', 'db', 'tablecount',
                  'table', 'escapestring', 'tag'},
        'methods': {'connect', 'open', 'close', 'query', 'fetchrow', 'fetchfield', 'use',
                    'selectdb', 'rowseek', 'fieldseek', 'createdb', 'dropdb'},
        'events': {'onconnect', 'ondisconnect', 'onerror', 'onquerydone'}
    },
    'PSQLITE': {
        'props': {'database', 'db', 'connected', 'rowcount', 'colcount', 'fieldcount',
                  'fieldname', 'row', 'tablecount', 'table', 'dbcount', 'tag'},
        'methods': {'connect', 'close', 'query', 'fetchrow', 'fetchfield', 'rowseek', 'fieldseek'},
        'events': {'onconnect', 'ondisconnect', 'onerror', 'onquerydone'}
    },
    'PSOCKET': {
        'props': {'host', 'port', 'connected', 'timeout', 'tag'},
        'methods': {'connect', 'close', 'write', 'writeline', 'read', 'readline', 'bind', 'listen', 'accept'},
        'events': {'onconnect', 'ondisconnect', 'ondataready', 'onerror'}
    },
    'PSERVERSOCKET': {
        'props': {'host', 'port', 'clientcount', 'tag'},
        'methods': {'start', 'stop', 'broadcast'},
        'events': {'onclientconnect', 'onclientdisconnect', 'ondatareceived', 'onerror'}
    },
    'PHTTP': {
        'props': {'host', 'port', 'url', 'statuscode', 'responsetext', 'responseheaders', 'timeout', 'usessl', 'tag'},
        'methods': {'get', 'post'},
        'events': set()
    },
    'PDESIGNSURFACE': {
        'props': {'width', 'height', 'left', 'top', 'compcount', 'visible', 'formcaption', 'tag', 'parent'},
        'methods': {'addcomponent', 'removecomponent', 'clearall', 'selectcomp', 'getname', 'setname',
                    'gettype', 'getprop', 'setprop', 'getevent', 'setevent', 'setcompbounds', 'getcompx', 'getcompy',
                    'getcompw', 'getcomph', 'show', 'hide', 'repaint', 'refresh'},
        'events': {'onselect', 'ondblclick', 'onmove', 'onbgclick'}
    },
    'PCANVAS': {
        'props': {'width', 'height', 'top', 'left', 'visible', 'color', 'pencolor', 'penwidth',
                  'brushcolor', 'font', 'fontsize', 'fontcolor', 'hint', 'showhint', 'cursor',
                  'tag', 'parent'},
        'methods': {'cls', 'pset', 'line', 'circle', 'fillrect', 'rectangle', 'textout', 'drawtext',
                    'paint', 'repaint', 'refresh'},
        'events': {'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmousemove', 'onpaint'}
    },
    # Phase 2 new component types
    'PTREEVIEW': {
        'props': {'width', 'height', 'top', 'left', 'visible', 'enabled', 'font', 'fontsize',
                  'fontcolor', 'color', 'itemcount', 'tag', 'parent'},
        'methods': {'additem', 'addchild', 'clear', 'expandall', 'collapseall', 'repaint', 'refresh'},
        'events': {'onclick', 'ondblclick', 'onexpanded', 'oncollapsed', 'onchange'}
    },
    'PIMAGE': {
        'props': {'width', 'height', 'top', 'left', 'visible', 'autosize', 'stretch', 'image',
                  'bmpwidth', 'bmpheight', 'tag', 'parent'},
        'methods': {'loadfromfile', 'savetofile', 'loadfromplot', 'cls', 'pset', 'line', 'circle',
                    'textout', 'fillrect', 'repaint', 'refresh'},
        'events': {'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmousemove'}
    },
    'PSPLITTER': {
        'props': {'width', 'height', 'top', 'left', 'visible', 'orientation', 'control1', 'control2',
                  'tag', 'parent'},
        'methods': set(),
        'events': set()
    },
    'PTRACKBAR': {
        'props': {'width', 'height', 'top', 'left', 'visible', 'enabled', 'min', 'max', 'position',
                  'orientation', 'tickfrequency', 'tag', 'parent'},
        'methods': {'setfocus', 'repaint', 'refresh'},
        'events': {'onchange', 'onclick'}
    },
    'PSCROLLBOX': {
        'props': {'width', 'height', 'top', 'left', 'visible', 'color', 'tag', 'parent'},
        'methods': {'repaint', 'refresh'},
        'events': set()
    },
    'PPOPUPMENU': {
        'props': {'tag'},
        'methods': {'additem', 'additems', 'popup', 'clear'},
        'events': set()
    },
    'PINI': {
        'props': {'filename', 'section', 'tag'},
        'methods': {'readstring', 'writestring', 'readinteger', 'writeinteger', 'deletesection', 'deletekey'},
        'events': set()
    },
    'PMEMORYSTREAM': {
        'props': {'position', 'size', 'tag'},
        'methods': {'write', 'read', 'readbyte', 'writebyte', 'savetofile', 'loadfromfile', 'clear', 'copyto'},
        'events': set()
    },
    'PSTRINGLIST': {
        'props': {'count', 'text', 'tag'},
        'methods': {'add', 'delete', 'clear', 'sort', 'indexof', 'insert', 'exchange',
                    'loadfromfile', 'savetofile', 'item', 'setitem'},
        'events': set()
    },
    'PPRINTER': {
        'props': {'tag'},
        'methods': {'begindoc', 'enddoc', 'newpage', 'textout', 'printline'},
        'events': set()
    },
    # Python-specific components
    'PNUMPY': {
        'props': {'data', 'shape', 'size', 'dtype', 'tag'},
        'methods': {'zeros', 'ones', 'arange', 'linspace', 'reshape', 'sum', 'mean', 'std',
                    'min', 'max', 'dot', 'transpose', 'tolist', 'sort', 'savetofile', 'loadfromfile'},
        'events': set()
    },
    'PMATPLOTLIB': {
        'props': {'title', 'xlabel', 'ylabel', 'width', 'height', 'grid', 'tag'},
        'methods': {'plot', 'scatter', 'bar', 'hist', 'pie', 'legend', 'clear',
                    'savetofile', 'show', 'saveto_buffer'},
        'events': set()
    },
    'PPANDAS': {
        'props': {'data', 'rowcount', 'colcount', 'columns', 'tag'},
        'methods': {'loadfromcsv', 'savetocsv', 'loadfromjson', 'savetojson', 'head', 'tail',
                    'describe', 'sort', 'filter', 'groupby', 'addcolumn', 'deletecolumn',
                    'cell', 'setcell', 'query', 'tostring', 'tolist'},
        'events': set()
    },
}

# Build a flattened set of "all known members" per type for fast lookup
_COMPONENT_ALL_MEMBERS = {}
for _ctype, _cdata in COMPONENT_REGISTRY.items():
    _COMPONENT_ALL_MEMBERS[_ctype] = _cdata['props'] | _cdata['methods'] | _cdata['events']


class SymbolTable:
    """Tracks declared symbols with scoped lookups (global -> local)."""

    def __init__(self):
        self._scopes = [{}]  # Stack of scopes. Index 0 = global.
        self.sub_signatures = {}  # name -> param_count
        self.func_signatures = {}  # name -> param_count
        self.const_names = set()

    def push_scope(self):
        self._scopes.append({})

    def pop_scope(self):
        if len(self._scopes) > 1:
            self._scopes.pop()

    def declare(self, name, sym_type='DOUBLE', kind='variable', component_type=None):
        """Declare a symbol in the current (innermost) scope."""
        scope = self._scopes[-1]
        scope[name] = {'type': sym_type, 'kind': kind, 'component_type': component_type}

    def declare_global(self, name, sym_type='DOUBLE', kind='variable', component_type=None):
        """Declare a symbol in the global scope."""
        self._scopes[0][name] = {'type': sym_type, 'kind': kind, 'component_type': component_type}

    def lookup(self, name):
        """Look up a symbol from innermost to outermost scope. Returns info dict or None."""
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def is_declared(self, name):
        return self.lookup(name) is not None

    def is_declared_in_current_scope(self, name):
        return name in self._scopes[-1]

    def in_global_scope(self):
        return len(self._scopes) == 1


class CodeGenerator:
    """Visits the AST and emits Python 3 code."""
    
    def __init__(self, file_path=None):
        self.output = []
        self.indent_level = 0
        self.imported_modules = set()
        self.create_obj_stack = []
        self.global_vars = set()
        self.arrays = set()
        self.udts = {}
        self.udt_array_fields = set()
        self.file_path = file_path
        self.errors = ErrorCollector()
        self.symbols = SymbolTable()
        self.typecheck = False  # $TYPECHECK OFF by default (matches RapidP)
        self.default_dim_type = 'DOUBLE'  # $OPTION DIM type
        self.apptype = 'GUI'  # $APPTYPE (GUI, CONSOLE, CGI)
        self._create_type_stack = []  # Tracks the component TYPE of each CREATE block
        
    def generate(self, program: ProgramNode, file_path=None) -> str:
        self.output = []
        self.indent_level = 0
        self.imported_modules = set()
        self.create_obj_stack = []
        self.global_vars = set()
        self.arrays = set()
        self.udts = {}
        self.udt_array_fields = set()
        self._current_function_name = None
        self.errors = ErrorCollector()
        self.symbols = SymbolTable()
        self.typecheck = False
        self.default_dim_type = 'DOUBLE'
        self.apptype = 'GUI'
        self._create_type_stack = []
        if file_path:
            self.file_path = file_path
        
        # We will add runtime imports at the beginning after collecting them
        
        # Pre-pass to find global variables (DIM at top level), UDT types,
        # SUB/FUNCTION signatures, CONST declarations, and directives
        for stmt in program.statements:
             if isinstance(stmt, TypeStatementNode):
                  self.udts[stmt.name.upper()] = stmt.name
             
        def collect_globals(stmts):
            for s in stmts:
                if isinstance(s, DimStatementNode):
                    comp_type = _normalize_comp_type(s.var_type.upper()) if s.var_type else None
                    for var_data in s.variables:
                        v_n = var_data[0].lower().rstrip('$%#&!')
                        self.global_vars.add(v_n)
                        if var_data[1] is not None:
                            self.arrays.add(v_n)
                        # Register in symbol table
                        self.symbols.declare_global(
                            v_n, sym_type=s.var_type or self.default_dim_type,
                            kind='array' if var_data[1] else 'variable',
                            component_type=comp_type if comp_type and (comp_type.startswith('P') or comp_type.startswith('Q')) else None
                        )
                elif isinstance(s, CreateStatementNode):
                    v_n = s.name.lower().rstrip('$%#&!')
                    self.global_vars.add(v_n)
                    norm_type = _normalize_comp_type(s.obj_type.upper())
                    self.symbols.declare_global(
                        v_n, sym_type=norm_type,
                        kind='component',
                        component_type=norm_type
                    )
                    if hasattr(s, 'body') and s.body:
                        collect_globals(s.body)
                elif isinstance(s, ConstStatementNode):
                    c_n = s.name.lower().rstrip('$%#&!')
                    self.global_vars.add(c_n)
                    self.symbols.declare_global(c_n, sym_type='CONST', kind='constant')
                    self.symbols.const_names.add(c_n)
                        
        collect_globals(program.statements)
        
        # Pre-pass to collect SUB/FUNCTION signatures
        for stmt in program.statements:
            if isinstance(stmt, SubroutineDefNode):
                name = stmt.name.lower().rstrip('$%#&!')
                self.symbols.sub_signatures[name] = len(stmt.params)
                self.symbols.declare_global(name, sym_type='SUB', kind='sub')
            elif isinstance(stmt, FunctionDefNode):
                name = stmt.name.lower().rstrip('$%#&!')
                self.symbols.func_signatures[name] = len(stmt.params)
                self.symbols.declare_global(name, sym_type='FUNCTION', kind='function')
            elif isinstance(stmt, DeclareStatementNode):
                name = stmt.name.lower().rstrip('$%#&!')
                self.symbols.declare_global(name, sym_type='FUNCTION', kind='function')
            elif isinstance(stmt, ImportStatementNode):
                alias = (stmt.alias or stmt.module_name).lower().strip('"')
                self.symbols.declare_global(alias, sym_type='MODULE', kind='module')

        # Always-available imported modules (added by preamble)
        self.symbols.declare_global('math', sym_type='MODULE', kind='module')

        # Pre-pass to find directives ($TYPECHECK, $OPTION)
        for stmt in program.statements:
            if isinstance(stmt, DirectiveNode):
                self._process_directive(stmt)
                       
        decls = []
        execs = []
        for stmt in program.statements:
            if isinstance(stmt, (SubroutineDefNode, FunctionDefNode, TypeStatementNode, DeclareStatementNode, ImportStatementNode)):
                decls.append(self.visit(stmt))
            else:
                execs.append(self.visit(stmt))
            
        # Add basic runtime imports implicitly
        preamble = [
            "from rp_runtime.builtins import *",
        ]
        if self.apptype != 'CONSOLE':
            preamble.append("from rp_runtime.gui import *")
        preamble.extend([
            "from rp_runtime.database import *",
            "from rp_runtime.network import *",
            "from rp_runtime.pycomponents import *"
        ])
        
        if self.imported_modules:
            preamble.extend(list(self.imported_modules))
            
        return "\n".join(preamble + [d for d in decls if d] + [e for e in execs if e])

    def _process_directive(self, node):
        """Handle $TYPECHECK, $OPTION, $APPTYPE directives."""
        full = (node.name or '').strip().upper()
        if node.value:
            full = full + ' ' + node.value.strip().upper()
        
        # Remove leading $
        if full.startswith('$'):
            full = full[1:]
        
        parts = full.split(None, 1)
        directive = parts[0] if parts else ''
        rest = parts[1] if len(parts) > 1 else ''
        
        if directive == 'TYPECHECK':
            self.typecheck = (rest == 'ON')
        elif directive == 'OPTION':
            if rest == 'EXPLICIT':
                self.typecheck = True
            elif rest.startswith('DIM'):
                dim_parts = rest.split()
                if len(dim_parts) >= 2:
                    self.default_dim_type = dim_parts[1]
        elif directive == 'APPTYPE':
            self.apptype = rest.strip()  # GUI, CONSOLE, CGI
        elif directive in ('OPTIMIZE', 'ESCAPECHARS'):
            pass  # Recognized but no semantic effect in transpiler

    def _check_identifier_declared(self, name, node):
        """Check if an identifier is declared. If $TYPECHECK ON, report error for undeclared vars."""
        clean = name.lower().rstrip('$%#&!')
        # Skip well-known constants and keywords  
        _KNOWN_CONSTANTS = frozenset({
            'true', 'false', 'nothing', 'null', 'none', 'me', 'self',
            # RapidP variant type constants
            'vttrue', 'vtfalse', 'vtnull', 'vtstring', 'vtinteger', 'vtdouble',
            'vtboolean', 'vtobject', 'vtarray', 'vtempty',
            # Common style constants
            'bsstyle', 'bsclient', 'bsleft', 'bsright', 'bstop', 'bsbottom',
            'bsnone', 'bssingle', 'bsdialog', 'bsmodal',
            'ssnone', 'ssboth', 'ssvertical', 'sshorizontal',
            # Color constants
            'clred', 'clblue', 'clgreen', 'clblack', 'clwhite', 'clyellow',
            'clgray', 'clsilver', 'clnavy', 'clteal', 'clpurple', 'clmaroon',
            'claqua', 'clfuchsia', 'cllime', 'clolive', 'clwindow', 'clbtnface',
            'clscrollbar', 'clbackground', 'clactivecaption', 'clinactivecaption',
            'clmenu', 'clhighlight', 'clhighlighttext', 'clgraytext',
            # MessageBox constants
            'mbok', 'mbyes', 'mbno', 'mbcancel', 'mbabort', 'mbretry', 'mbignore',
            # Cursor constants
            'crdefault', 'crarrow', 'crcross', 'cribeam', 'crhourglass', 'crhandpoint',
            # Key constants
            'vk_return', 'vk_escape', 'vk_tab', 'vk_back', 'vk_delete', 'vk_insert',
            'vk_home', 'vk_end', 'vk_prior', 'vk_next', 'vk_left', 'vk_right',
            'vk_up', 'vk_down', 'vk_space', 'vk_f1', 'vk_f2', 'vk_f3', 'vk_f4',
            'vk_f5', 'vk_f6', 'vk_f7', 'vk_f8', 'vk_f9', 'vk_f10', 'vk_f11', 'vk_f12',
        })
        if clean in _KNOWN_CONSTANTS:
            return
        # Skip if it's a known builtin function
        if clean in self._all_known_builtins:
            return
        # Skip if declared
        if self.symbols.is_declared(clean):
            return
        # Skip if it's a known UDT type name
        if clean.upper() in self.udts:
            return
        # Only error if $TYPECHECK ON
        if self.typecheck:
            self.errors.add_error(
                f"Undeclared variable '{clean}'",
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None),
                file_path=self.file_path
            )

    def _check_call_exists(self, name, arg_count, node):
        """Validate that a SUB/FUNCTION call target exists and arg count matches."""
        clean = name.lower().rstrip('$%#&!')
        # Skip builtins — they're always available
        if clean in self._all_known_builtins:
            return
        # Skip if it looks like a method call on an object (contains '.')
        if '.' in clean:
            return
        # Check SUB signatures
        if clean in self.symbols.sub_signatures:
            expected = self.symbols.sub_signatures[clean]
            if arg_count != expected:
                self.errors.add_error(
                    f"SUB '{clean}' expects {expected} argument(s), got {arg_count}",
                    line=getattr(node, 'line', None),
                    column=getattr(node, 'column', None),
                    file_path=self.file_path
                )
            return
        # Check FUNCTION signatures
        if clean in self.symbols.func_signatures:
            expected = self.symbols.func_signatures[clean]
            if arg_count != expected:
                self.errors.add_error(
                    f"FUNCTION '{clean}' expects {expected} argument(s), got {arg_count}",
                    line=getattr(node, 'line', None),
                    column=getattr(node, 'column', None),
                    file_path=self.file_path
                )
            return
        # If it's a declared variable/component (maybe callable), skip
        if self.symbols.is_declared(clean):
            return
        # If $TYPECHECK ON, error on undeclared call targets
        if self.typecheck:
            self.errors.add_error(
                f"Undeclared SUB or FUNCTION '{clean}'",
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None),
                file_path=self.file_path
            )

    def _check_member_access(self, obj_name, member_name, node):
        """Validate that a property/method exists on a known component type."""
        clean_obj = obj_name.lower().rstrip('$%#&!')
        clean_member = member_name.lower().rstrip('$%#&!')
        
        info = self.symbols.lookup(clean_obj)
        if info is None:
            return  # Can't resolve object — skip validation
        
        comp_type = info.get('component_type')
        if comp_type is None:
            return  # Not a component type we know — skip
        comp_type = _normalize_comp_type(comp_type).upper()
        
        all_members = _COMPONENT_ALL_MEMBERS.get(comp_type)
        if all_members is None:
            return  # Unknown component type — skip
        
        if clean_member not in all_members:
            # This could be a user-added property or dynamic attribute — warn, don't error
            self.errors.add_warning(
                f"Unknown property or method '{clean_member}' on {comp_type} object '{clean_obj}'",
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None),
                file_path=self.file_path
            )

    # All known builtin function names (for skipping validation)
    _all_known_builtins = frozenset([
        'rp_print', 'chr', 'asc', 'left', 'right', 'mid', 'len', 'instr',
        'ucase', 'lcase', 'val', 'str_func', 'abs', 'atn', 'cos', 'sin',
        'exp', 'log', 'sqr', 'rnd', 'timer', 'input_func', 'int', 'float',
        'dir_func', 'direxists', 'chdir', 'ceil', 'acos', 'asin',
        'command_func', 'date_func', 'delete_func', 'format_func',
        'hextodec', 'callback', 'callfunc', 'varptr', 'varptr_str',
        'vartype', 'sound', 'sleep_func', 'shell', 'showmessage',
        'space', 'string', 'ltrim', 'rtrim', 'trim', 'hex_func', 'bin_func',
        'oct_func', 'environ', 'curdir', 'time_func',
        # Phase 3 new builtins
        'tan', 'floor_func', 'fix', 'frac', 'round_func', 'sgn', 'cint', 'clng',
        'iif', 'randomize', 'insert_func', 'replace_func', 'replacesubstr',
        'reverse_func', 'rinstr', 'field_func', 'tally', 'strf', 'convbase',
        'mkdir_func', 'rmdir_func', 'kill_func', 'rename_func',
        'lbound', 'ubound', 'quicksort', 'initarray',
        'doevents', 'playwav', 'rgb', 'messagebox_func', 'messagedlg',
        'run_func', 'end_func', 'fileexists', 'shellwait',
        # Also original RapidP names (before interception)
        'print', 'str', 'dir', 'command', 'date', 'delete', 'format', 'sleep',
        'open', 'close', 'input', 'hex', 'bin', 'oct',
        'chr', 'asc', 'left', 'right', 'mid', 'len', 'instr',
        'ucase', 'lcase', 'val', 'abs', 'atn', 'cos', 'sin', 'exp', 'log',
        'sqr', 'rnd', 'ceil', 'acos', 'asin', 'hextodec',
        'callback', 'callfunc', 'varptr', 'vartype', 'sound',
        'shell', 'showmessage', 'space', 'string', 'ltrim', 'rtrim', 'trim',
        'environ', 'curdir', 'direxists', 'chdir',
        # RapidP names for new builtins
        'tan', 'floor', 'fix', 'frac', 'round', 'sgn', 'cint', 'clng',
        'iif', 'randomize', 'insert', 'replace', 'replacesubstr',
        'reverse', 'rinstr', 'field', 'tally', 'strf', 'convbase',
        'mkdir', 'rmdir', 'kill', 'rename',
        'lbound', 'ubound', 'quicksort', 'initarray', 'swap', 'redim',
        'doevents', 'playwav', 'rgb', 'messagebox', 'messagedlg',
        'run', 'end', 'fileexists', 'shellwait',
        # Python-side names
        'open_func', 'close_func', 'print_hash',
        # MsgBox variants
        'MsgBox', 'msgbox',
    ])
        
    def _emit(self, code: str) -> str:
        return ("    " * self.indent_level) + code
        
    def visit(self, node: ASTNode) -> str:
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
        
    def generic_visit(self, node: ASTNode) -> str:
        raise Exception(f'No visit_{type(node).__name__} method')

    # --- Statements ---

    def visit_DimStatementNode(self, node: DimStatementNode) -> str:
        # In Python, we don't strictly need to declare variables unless we want to initialize them
        # Let's initialize them based on type: INTEGER -> 0, STRING -> "", DOUBLE -> 0.0, POBJECT -> None?
        init_val = "None"
        if node.var_type in ('INTEGER', 'SINGLE', 'DOUBLE', 'SHORT', 'LONG', 'BYTE', 'WORD', 'DWORD', 'INT64', 'CURRENCY'):
            init_val = "0"
        elif node.var_type == 'STRING':
            init_val = '""'

        # Register in symbol table for local scope tracking
        comp_type = _normalize_comp_type(node.var_type.upper()) if node.var_type else None
        for var_data in node.variables:
            v_n = var_data[0].lower().rstrip('$%#&!')
            is_arr = var_data[1] is not None
            if self.symbols.in_global_scope():
                # Already registered in pre-pass
                pass
            else:
                self.symbols.declare(
                    v_n, sym_type=node.var_type or self.default_dim_type,
                    kind='array' if is_arr else 'variable',
                    component_type=comp_type if comp_type and (comp_type.startswith('P') or comp_type.startswith('Q')) else None
                )

        # Normalize Q-prefix to P-prefix for backward compat
        norm_var_type = _normalize_comp_type(node.var_type)

        gui_types = {
            'PFORM': 'PForm', 'PBUTTON': 'PButton', 'PLABEL': 'PLabel', 
            'PEDIT': 'PEdit', 'PCANVAS': 'PCanvas', 'PPANEL': 'PPanel',
            'PTIMER': 'PTimer', 'PMAINMENU': 'PMainMenu', 'PMENUITEM': 'PMenuItem',
            'PCOMBOBOX': 'PComboBox', 'PLISTBOX': 'PListBox', 
            'PCHECKBOX': 'PCheckBox', 'PRADIOBUTTON': 'PRadioButton',
            'PRICHEDIT': 'PRichEdit', 'PSTRINGGRID': 'PStringGrid',
            'PIMAGE': 'PImage', 'PSCROLLBAR': 'PScrollBar', 'PTABCONTROL': 'PTabControl',
            'PGROUPBOX': 'PGroupBox', 'PMYSQL': 'PMySQL', 'PSQLITE': 'PSQLite',
            'PPROGRESSBAR': 'PProgressBar', 'PLISTVIEW': 'PListView',
            'POPENDIALOG': 'POpenDialog', 'PSAVEDIALOG': 'PSaveDialog', 'PFILESTREAM': 'PFileStream',
            'PFILELISTBOX': 'PFileListBox', 'PFILEDIALOG': 'PFileDialog', 'PFORMMDI': 'PFormMDI', 'PCODEEDITOR': 'PCodeEditor',
            'PLINE': 'PLine', 'PICON': 'PIcon', 'PIMAGELIST': 'PImageList',
            'PHTML': 'PHTML', 'PMIDI': 'Pmidi', 'PSOCKET': 'PSocket', 'RSOCKET': 'RSocket',
            'PSTATUSBAR': 'PStatusBar',
            'PCOLORDIALOG': 'PColorDialog', 'PFONTDIALOG': 'PFontDialog',
            'PSCROLLBAR': 'PScrollBar',
            'PDESIGNSURFACE': 'PDesignSurface',
            # Phase 2 new components
            'PTREEVIEW': 'PTreeView', 'PSPLITTER': 'PSplitter', 'PTRACKBAR': 'PTrackBar',
            'PSCROLLBOX': 'PScrollBox', 'PPOPUPMENU': 'PPopupMenu',
            'PINI': 'PIni', 'PMEMORYSTREAM': 'PMemoryStream', 'PSTRINGLIST': 'PStringList',
            'PPRINTER': 'PPrinter',
            # Networking
            'PSERVERSOCKET': 'PServerSocket', 'PHTTP': 'PHTTP',
            # Python-specific components
            'PNUMPY': 'PNumPy', 'PMATPLOTLIB': 'PMatPlotLib', 'PPANDAS': 'PPandas',
        }
            
        lines = []
        for var_data in node.variables:
            var_name, array_size = var_data
            var_name = var_name.lower().rstrip('$%#&!')
            if array_size:
                self.arrays.add(var_name)
                
            if norm_var_type.startswith('P'):
                # Handle GUI components like PForm, PButton: DIM form AS PForm -> form = PForm()
                py_type = gui_types.get(norm_var_type, norm_var_type)
                if array_size:
                    # Array of objects
                    if len(array_size) == 1:
                        sz = self.visit(array_size[0])
                        # Usually RapidP 0-indexes arrays so DIM A(10) is 11 elements
                        lines.append(self._emit(f"{var_name} = [{py_type}() for _ in range({sz} + 1)]"))
                    elif len(array_size) == 2:
                        # DIM A(1 TO 10)
                        start = self.visit(array_size[0])
                        end = self.visit(array_size[1])
                        # We allocate up to `end + 1` to accommodate 1-to-1 array mapping seamlessly
                        lines.append(self._emit(f"{var_name} = [{py_type}() for _ in range(({end}) + 1)]"))
                elif node.var_type in self.udts:
                    lines.append(self._emit(f"{var_name} = {self.udts[node.var_type]}()"))
                else:
                    # If this variable will be instantiated by a CREATE block later,
                    # skip the constructor call to avoid creating orphaned GUI objects
                    sym = self.symbols.lookup(var_name)
                    if sym and sym.get('kind') == 'component':
                        lines.append(self._emit(f"{var_name} = None"))
                    else:
                        lines.append(self._emit(f"{var_name} = {py_type}()"))
            elif node.var_type in self.udts:
                # Same logic as UI types but for generic UDTs
                orig_name = self.udts[node.var_type]
                if array_size:
                    if len(array_size) == 1:
                        sz = self.visit(array_size[0])
                        lines.append(self._emit(f"{var_name} = [{orig_name}() for _ in range({sz} + 1)]"))
                    elif len(array_size) == 2:
                        end = self.visit(array_size[1])
                        lines.append(self._emit(f"{var_name} = [{orig_name}() for _ in range(({end}) + 1)]"))
                else:
                    lines.append(self._emit(f"{var_name} = {orig_name}()"))
            else:
                if array_size:
                    if len(array_size) == 1:
                        sz = self.visit(array_size[0])
                        lines.append(self._emit(f"{var_name} = [{init_val}] * ({sz} + 1)"))
                    elif len(array_size) == 2:
                        start = self.visit(array_size[0])
                        end = self.visit(array_size[1])
                        # Pad with init val up to end + 1 to avoid shifting indices on read/write ASTs
                        lines.append(self._emit(f"{var_name} = [{init_val}] * (({end}) + 1)"))
                else:
                    lines.append(self._emit(f"{var_name} = {init_val}"))
                
        return "\n".join(lines)

    def visit_PrintStatementNode(self, node: PrintStatementNode) -> str:
        items = [self.visit(item) for item in node.items]
        args = ", ".join(items) if items else ""
        end_arg = "" if node.append_newline else ", end=''"
        sep_arg = "" if args else ""
        
        # If no items but no newline appended, do nothing basically
        if not items and not node.append_newline:
            return ""
            
        if items:
            return self._emit(f"rp_print({args}{end_arg})")
        else:
            return self._emit("rp_print()")

    def visit_AssignmentNode(self, node: AssignmentNode) -> str:
        # For simple identifiers being assigned, handle declaration BEFORE visiting
        # (to prevent visit_IdentifierNode from reporting undeclared for assignment targets)
        if isinstance(node.target, IdentifierNode) and not self.create_obj_stack:
            var_name = node.target.name.lower().rstrip('$%#&!')
            if not self.symbols.is_declared(var_name) and var_name not in ('true', 'false'):
                if self.typecheck:
                    self.errors.add_error(
                        f"Undeclared variable '{var_name}'",
                        line=getattr(node, 'line', None),
                        column=getattr(node, 'column', None),
                        file_path=self.file_path
                    )
                # Auto-declare in current scope (RapidP implicit behavior when $TYPECHECK OFF)
                self.symbols.declare(var_name, sym_type=self.default_dim_type)
        
        target = self.visit(node.target)
        
        # Implicit property assignment inside CREATE blocks
        if self.create_obj_stack and isinstance(node.target, IdentifierNode):
            # Validate property on the component type
            prop_name = node.target.name.lower().rstrip('$%#&!')
            if self._create_type_stack:
                self._check_member_access_by_type(self._create_type_stack[-1], prop_name, node)
            target = f"{self.create_obj_stack[-1]}.{target}"
        elif self.create_obj_stack and isinstance(node.target, MemberAccessNode):
            # Handle dot-property chains like Font.Size inside CREATE blocks
            # Find the root identifier of the chain
            root = node.target
            while isinstance(root, MemberAccessNode):
                root = root.obj
            if isinstance(root, IdentifierNode):
                root_name = root.name.lower().rstrip('$%#&!')
                # If root is not a declared variable, it's an implicit property of the CREATE object
                if not self.symbols.is_declared(root_name) and root_name != self.create_obj_stack[-1]:
                    target = f"{self.create_obj_stack[-1]}.{target}"
            
        value = self.visit(node.value)
        return self._emit(f"{target} = {value}")

    def visit_IfStatementNode(self, node: IfStatementNode) -> str:
        code = []
        cond = self.visit(node.condition)
        code.append(self._emit(f"if {cond}:"))
        self.indent_level += 1
        
        if not node.then_branch:
            code.append(self._emit("pass"))
        else:
            for s in node.then_branch:
                code.append(self.visit(s))
        self.indent_level -= 1
        
        for e_cond, e_branch in node.elseif_branches:
            code.append(self._emit(f"elif {self.visit(e_cond)}:"))
            self.indent_level += 1
            if not e_branch:
                code.append(self._emit("pass"))
            else:
                for s in e_branch:
                    code.append(self.visit(s))
            self.indent_level -= 1
            
        if node.else_branch is not None:
            code.append(self._emit("else:"))
            self.indent_level += 1
            if not node.else_branch:
                code.append(self._emit("pass"))
            else:
                for s in node.else_branch:
                    code.append(self.visit(s))
            self.indent_level -= 1
            
        return "\n".join(code)

    def visit_ForStatementNode(self, node: ForStatementNode) -> str:
        var_name = node.variable.lower().rstrip('$%#&!')
        
        # FOR loop variable is implicitly declared if not already
        if not self.symbols.is_declared(var_name):
            self.symbols.declare(var_name, sym_type='INTEGER', kind='variable')
        
        start = self.visit(node.start)
        end = self.visit(node.end)
        step = self.visit(node.step) if node.step else "1"
        
        code = []
        # RapidP FOR loops are inclusive: FOR I=1 TO 10
        code.append(self._emit(f"{var_name} = {start}"))
        
        # Detect if step is negative: handles -1, (-1), (- 1), etc.
        step_is_negative = False
        step_stripped = step.strip().lstrip('(').strip()
        if step_stripped.startswith('-'):
            step_is_negative = True
        
        if step_is_negative:
            dir_cond = f"{var_name} >= {end}"
        else:
            dir_cond = f"{var_name} <= {end}"
        
        code.append(self._emit(f"while {dir_cond}:")) # approximation, true basic might be more complex
        self.indent_level += 1
        for s in node.body:
            code.append(self.visit(s))
        code.append(self._emit(f"{var_name} += {step}"))
        self.indent_level -= 1
        
        return "\n".join(code)

    def visit_WhileStatementNode(self, node: WhileStatementNode) -> str:
        cond = self.visit(node.condition)
        code = [self._emit(f"while {cond}:")]
        self.indent_level += 1
        if not node.body:
             code.append(self._emit("pass"))
        else:
            for s in node.body:
                code.append(self.visit(s))
        self.indent_level -= 1
        return "\n".join(code)

    def visit_DoLoopStatementNode(self, node: DoLoopStatementNode) -> str:
        code = []
        if node.pre_condition:
            if node.condition:
                cond_str = self.visit(node.condition)
                if node.is_until:
                    cond_str = f"not ({cond_str})"
                code.append(self._emit(f"while {cond_str}:"))
            else:
                 code.append(self._emit("while True:"))
                 
            self.indent_level += 1
            if not node.body:
                code.append(self._emit("pass"))
            else:
                for s in node.body:
                    code.append(self.visit(s))
            self.indent_level -= 1
        else:
            # Post condition loop: DO ... LOOP UNTIL
            code.append(self._emit("while True:"))
            self.indent_level += 1
            for s in node.body:
                code.append(self.visit(s))
                
            if node.condition:
                cond_str = self.visit(node.condition)
                if node.is_until:
                     code.append(self._emit(f"if {cond_str}: break"))
                else:
                     code.append(self._emit(f"if not ({cond_str}): break"))
            self.indent_level -= 1
            
        return "\n".join(code)

    def visit_SubroutineDefNode(self, node: SubroutineDefNode) -> str:
        name = node.name.lower().rstrip('$%#&!')
        params = ", ".join([p[0].lower().rstrip('$%#&!') for p in node.params])
        code = [self._emit(f"def {name}({params}):")]
        self.indent_level += 1
        
        # Push a new scope for local variables
        self.symbols.push_scope()
        
        # Register parameters as local variables
        param_names = [p[0].lower().rstrip('$%#&!') for p in node.params]
        for i, p in enumerate(node.params):
            p_name = p[0].lower().rstrip('$%#&!')
            p_type = p[1] if len(p) > 1 and p[1] else self.default_dim_type
            self.symbols.declare(p_name, sym_type=p_type, kind='parameter')
        
        # Declare global variables
        globals_to_declare = [g for g in self.global_vars if g not in param_names]
        if globals_to_declare:
            code.append(self._emit(f"global {', '.join(globals_to_declare)}"))
            
        if not node.body:
            code.append(self._emit("pass"))
        else:
            for s in node.body:
                code.append(self.visit(s))
        
        self.symbols.pop_scope()
        self.indent_level -= 1
        return "\n".join(code)

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> str:
        name = node.name.lower().rstrip('$%#&!')
        params = ", ".join([p[0].lower().rstrip('$%#&!') for p in node.params])
        code = [self._emit(f"def {name}({params}):")]
        self.indent_level += 1
        
        # Push a new scope for local variables
        self.symbols.push_scope()
        
        # Register parameters as local variables
        param_names = [p[0].lower().rstrip('$%#&!') for p in node.params]
        for i, p in enumerate(node.params):
            p_name = p[0].lower().rstrip('$%#&!')
            p_type = p[1] if len(p) > 1 and p[1] else self.default_dim_type
            self.symbols.declare(p_name, sym_type=p_type, kind='parameter')
        
        # The function name itself is a local variable (used for return value)
        self.symbols.declare(name, sym_type=node.return_type or self.default_dim_type, kind='function_result')
        
        # Declare global variables
        globals_to_declare = [g for g in self.global_vars if g not in param_names and g != name]
        if globals_to_declare:
            code.append(self._emit(f"global {', '.join(globals_to_declare)}"))
            
        # RapidP functions return by assigning to the function name: MyFunc = 10
        # In Python, we have to return explicitly. We introduce a local variable returning the name
        code.append(self._emit(f"{name} = None"))
        prev_func = self._current_function_name
        self._current_function_name = name
        if not node.body:
            pass
        else:
            for s in node.body:
                code.append(self.visit(s))
        self._current_function_name = prev_func
        code.append(self._emit(f"return {name}"))
        self.symbols.pop_scope()
        self.indent_level -= 1
        return "\n".join(code)

    def visit_CallStatementNode(self, node: CallStatementNode) -> str:
        raw_name = node.name.lower()
        if raw_name == 'varptr$':
             name = 'varptr_str'
        else:
             name = raw_name.rstrip('$%#&!')
        
        intercepts = {'dir': 'dir_func', 'command': 'command_func', 'str': 'str_func', 'date': 'date_func', 'delete': 'delete_func', 'format': 'format_func', 'sleep': 'sleep_func', 'hex': 'hex_func', 'bin': 'bin_func', 'oct': 'oct_func', 'round': 'round_func', 'insert': 'insert_func', 'replace': 'replace_func', 'reverse': 'reverse_func', 'field': 'field_func', 'mkdir': 'mkdir_func', 'rmdir': 'rmdir_func', 'kill': 'kill_func', 'rename': 'rename_func', 'messagebox': 'messagebox_func', 'msgbox': 'MsgBox', 'run': 'run_func', 'end': 'end_func', 'input': 'input_func', 'floor': 'floor_func'}
        name = intercepts.get(name, name)
        
        if self.create_obj_stack:
            known_builtins = ['rp_print', 'chr', 'asc', 'left', 'right', 'mid', 'len', 'instr', 'ucase', 'lcase', 'val', 'str_func', 'abs', 'atn', 'cos', 'sin', 'exp', 'log', 'sqr', 'rnd', 'timer', 'input_func', 'int', 'float', 'dir_func', 'direxists', 'chdir', 'ceil', 'acos', 'asin', 'command_func', 'date_func', 'delete_func', 'format_func', 'hextodec', 'callback', 'callfunc', 'varptr', 'varptr_str', 'vartype', 'sound', 'sleep_func', 'shell', 'showmessage', 'space', 'string', 'ltrim', 'rtrim', 'trim', 'hex_func', 'bin_func', 'oct_func', 'environ', 'curdir', 'tan', 'floor_func', 'fix', 'frac', 'round_func', 'sgn', 'cint', 'clng', 'iif', 'randomize', 'insert_func', 'replace_func', 'replacesubstr', 'reverse_func', 'rinstr', 'field_func', 'tally', 'strf', 'convbase', 'mkdir_func', 'rmdir_func', 'kill_func', 'rename_func', 'lbound', 'ubound', 'quicksort', 'initarray', 'doevents', 'playwav', 'rgb', 'messagebox_func', 'messagedlg', 'MsgBox', 'run_func', 'end_func', 'fileexists', 'shellwait']
            if name not in known_builtins:
                # Inside CREATE block, this is a method call on the component — skip global call validation
                name = f"{self.create_obj_stack[-1]}.{name}"
            else:
                self._check_call_exists(name, len(node.args), node)
        else:
            # Validate SUB/FUNCTION call exists and argument count
            self._check_call_exists(name, len(node.args), node)
                
        args = ", ".join([self.visit(arg) for arg in node.args])
        return self._emit(f"{name}({args})")
        
    def visit_MethodCallStatementNode(self, node: MethodCallStatementNode) -> str:
        return self._emit(self.visit(node.method_call))
        
    def visit_SelectCaseStatementNode(self, node: SelectCaseStatementNode) -> str:
        # Translate to if / elif / else
        code = []
        expr = self.visit(node.expression)
        temp_var = f"_select_val_{node.line}"
        code.append(self._emit(f"{temp_var} = {expr}"))
        
        first = True
        for values, branch in node.cases:
            conds = " or ".join([f"{temp_var} == {self.visit(v)}" for v in values])
            if first:
                code.append(self._emit(f"if {conds}:"))
                first = False
            else:
                code.append(self._emit(f"elif {conds}:"))
                
            self.indent_level += 1
            if not branch: code.append(self._emit("pass"))
            for s in branch: code.append(self.visit(s))
            self.indent_level -= 1
            
        if node.case_else is not None:
             code.append(self._emit("else:"))
             self.indent_level += 1
             if not node.case_else: code.append(self._emit("pass"))
             for s in node.case_else: code.append(self.visit(s))
             self.indent_level -= 1
             
        return "\n".join(code)

    def visit_ReturnStatementNode(self, node: ReturnStatementNode) -> str:
         if node.value:
             return self._emit(f"return {self.visit(node.value)}")
         return self._emit("return")

    def visit_ExitStatementNode(self, node: ExitStatementNode) -> str:
        if node.exit_type in ('FOR', 'WHILE', 'DO'):
            return self._emit("break")
        elif node.exit_type == 'FUNCTION' and self._current_function_name:
             return self._emit(f"return {self._current_function_name}")
        elif node.exit_type in ('SUB', 'FUNCTION'):
             return self._emit("return")
        return ""

    def visit_ImportStatementNode(self, node: ImportStatementNode) -> str:
        # E.g IMPORT "numpy" AS np -> import numpy as np
        module_name = node.module_name
        if module_name.startswith('"') and module_name.endswith('"'):
            module_name = module_name[1:-1]
            
        if node.alias:
             return self._emit(f"import {module_name} as {node.alias}")
        return self._emit(f"import {module_name}")
        
    def visit_DirectiveNode(self, node: DirectiveNode) -> str:
         # Process compiler directives for semantic validation
         self._process_directive(node)
         # In Python we can just add comments or ignore them
         return self._emit(f"# Directive: {node.name} {node.value}")
         
    def visit_ConstStatementNode(self, node: ConstStatementNode) -> str:
        name = node.name.lower().rstrip('$%#&!')
        # Register constant in local scope if not global
        if not self.symbols.in_global_scope() and not self.symbols.is_declared(name):
            self.symbols.declare(name, sym_type='CONST', kind='constant')
            self.symbols.const_names.add(name)
        val_str = self.visit(node.value)
        return self._emit(f"{name} = {val_str}")
        
    def visit_TypeStatementNode(self, node: TypeStatementNode) -> str:
        self.imported_modules.add("from dataclasses import dataclass")
        
        extends_str = f"({node.extends})" if getattr(node, 'extends', None) else ""
        lines = [self._emit("@dataclass"), self._emit(f"class {node.name}{extends_str}:")]
        self.indent_level += 1
        
        # Determine appropriate default for types inside DataClasses or keep as Any (None defaults)
        for field in node.fields:
            fname, ftype, array_size = field
            fname = fname.lower().rstrip('$%#&!')
            if ftype in ('INTEGER', 'DOUBLE', 'SINGLE', 'BYTE', 'WORD', 'DWORD', 'LONG', 'INT64', 'CURRENCY'):
                default_val = "0"
            elif ftype == 'STRING':
                default_val = '""'
            else:
                default_val = "None"
                
            # For array fields in TYPE (e.g. A(10) AS INTEGER) - Python dataclasses need `field(default_factory=list)`
            if array_size:
                self.udt_array_fields.add(fname)
                self.imported_modules.add("from dataclasses import field")
                size = self.visit(array_size[0]) if len(array_size) == 1 else self.visit(array_size[1])
                lines.append(self._emit(f"{fname}: list = field(default_factory=lambda: [{default_val}] * ({size} + 1))"))
            else:
                lines.append(self._emit(f"{fname}: any = {default_val}"))
                
        if getattr(node, 'constructor', None):
            lines.append(self._emit("def __post_init__(self):"))
            self.indent_level += 1
            if not node.constructor:
                lines.append(self._emit("pass"))
            else:
                for c_stmt in node.constructor:
                     lines.append(self.visit(c_stmt))
            self.indent_level -= 1
            
        if getattr(node, 'methods', None):
            for method in node.methods:
                method_code = self.visit(method)
                # Quick hack: methods inside a class need 'self' injected!
                method_code = method_code.replace("def " + method.name.lower() + "(", "def " + method.name.lower() + "(self, ")
                method_code = method_code.replace("(self, )", "(self)")
                lines.append(method_code)
                
        if not node.fields and not getattr(node, 'methods', None) and not getattr(node, 'constructor', None):
             lines.append(self._emit("pass"))
             
        self.indent_level -= 1
        return "\n".join(lines)
        
    def visit_DeclareStatementNode(self, node: DeclareStatementNode) -> str:
        # Translating DLL wrappers to Python library imports
        # Example: DECLARE SUB MyFunc LIB "math" ALIAS "sqrt"
        # Becomes -> from math import sqrt as myfunc
        name = node.name.lower().rstrip('$%#&!')
        lib = node.lib
        alias = node.alias if node.alias else name
        
        # We strip extension if the user typed "math.dll" since Python uses module names
        if lib.lower().endswith(".dll") or lib.lower().endswith(".so"):
             lib = lib[:-4]
             
        if not lib:
             lib = "builtins" # arbitrary fallback for empty LIB string
             
        self.imported_modules.add(f"from {lib} import {alias} as {name}")
        return self._emit(f"# Re-routed DECLARE: from {lib} import {alias} as {name}")

    def visit_WithStatementNode(self, node: WithStatementNode) -> str:
        # Since parser fully expanded the object refs implicitly, we just linearly generate body without python `with`
        lines = []
        for stmt in node.body:
             body_codegen = self.visit(stmt)
             if body_codegen:
                 lines.append(body_codegen)
        return "\n".join(lines)

    def visit_CreateStatementNode(self, node: CreateStatementNode) -> str:
        gui_types = {
            'PFORM': 'PForm', 'PBUTTON': 'PButton', 'PLABEL': 'PLabel', 
            'PEDIT': 'PEdit', 'PCANVAS': 'PCanvas', 'PPANEL': 'PPanel',
            'PTIMER': 'PTimer', 'PMAINMENU': 'PMainMenu', 'PMENUITEM': 'PMenuItem',
            'PCOMBOBOX': 'PComboBox', 'PLISTBOX': 'PListBox', 
            'PCHECKBOX': 'PCheckBox', 'PRADIOBUTTON': 'PRadioButton',
            'PRICHEDIT': 'PRichEdit', 'PSTRINGGRID': 'PStringGrid',
            'PIMAGE': 'PImage', 'PSCROLLBAR': 'PScrollBar', 'PTABCONTROL': 'PTabControl',
            'PGROUPBOX': 'PGroupBox', 'PMYSQL': 'PMySQL', 'PSQLITE': 'PSQLite',
            'PPROGRESSBAR': 'PProgressBar', 'PLISTVIEW': 'PListView',
            'POPENDIALOG': 'POpenDialog', 'PSAVEDIALOG': 'PSaveDialog', 'PFILESTREAM': 'PFileStream',
            'PFILELISTBOX': 'PFileListBox', 'PFILEDIALOG': 'PFileDialog', 'PFORMMDI': 'PFormMDI', 'PCODEEDITOR': 'PCodeEditor',
            'PLINE': 'PLine', 'PICON': 'PIcon', 'PIMAGELIST': 'PImageList',
            'PHTML': 'PHTML', 'PMIDI': 'Pmidi', 'PSOCKET': 'PSocket', 'RSOCKET': 'RSocket',
            'PSTATUSBAR': 'PStatusBar',
            'PCOLORDIALOG': 'PColorDialog', 'PFONTDIALOG': 'PFontDialog',
            'PSCROLLBAR': 'PScrollBar',
            'PDESIGNSURFACE': 'PDesignSurface',
            # Phase 2 new components
            'PTREEVIEW': 'PTreeView', 'PSPLITTER': 'PSplitter', 'PTRACKBAR': 'PTrackBar',
            'PSCROLLBOX': 'PScrollBox', 'PPOPUPMENU': 'PPopupMenu',
            'PINI': 'PIni', 'PMEMORYSTREAM': 'PMemoryStream', 'PSTRINGLIST': 'PStringList',
            'PPRINTER': 'PPrinter',
            # Networking
            'PSERVERSOCKET': 'PServerSocket', 'PHTTP': 'PHTTP',
            # Python-specific components
            'PNUMPY': 'PNumPy', 'PMATPLOTLIB': 'PMatPlotLib', 'PPANDAS': 'PPandas',
        }
        
        obj_name = node.name.lower().rstrip('$%#&!')
        norm_obj_type = _normalize_comp_type(node.obj_type)
        py_type = gui_types.get(norm_obj_type, norm_obj_type)
        comp_type_upper = norm_obj_type.upper()
        
        code = []
        # Pass parent dynamically avoiding Tkinter's lack of reparenting
        if self.create_obj_stack:
            parent_name = self.create_obj_stack[-1]
            code.append(self._emit(f"{obj_name} = {py_type}(parent={parent_name})"))
        else:
            code.append(self._emit(f"{obj_name} = {py_type}()"))
            
        self.create_obj_stack.append(obj_name)
        self._create_type_stack.append(comp_type_upper)
        
        if not node.body:
             code.append(self._emit(f"# Empty CREATE block for {obj_name}"))
        else:
             for s in node.body:
                  code.append(self.visit(s))
                  
        self.create_obj_stack.pop()
        self._create_type_stack.pop()
        return "\n".join(code)

    def _check_member_access_by_type(self, comp_type, member_name, node):
        """Validate that a property/method exists on a component type (used inside CREATE blocks)."""
        norm_type = _normalize_comp_type(comp_type).upper()
        all_members = _COMPONENT_ALL_MEMBERS.get(norm_type)
        if all_members is None:
            return  # Unknown type
        clean = member_name.lower().rstrip('$%#&!')
        if clean not in all_members:
            self.errors.add_warning(
                f"Unknown property or method '{clean}' on {comp_type}",
                line=getattr(node, 'line', None),
                column=getattr(node, 'column', None),
                file_path=self.file_path
            )

    # --- Expressions ---

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        if node.type_name == 'STRING':
            # handle quotes escaping
            val = node.value.replace('"', '\\"')
            return f'"{val}"'
        return str(node.value)

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        raw = node.name.lower()
        raw_stripped = raw.rstrip('$%#&!')
        # Map RapidP boolean keywords to Python boolean literals
        if raw_stripped == 'true': return 'True'
        if raw_stripped == 'false': return 'False'
        if raw == 'date$' and raw_stripped not in self.global_vars: return 'date_func()'
        if raw == 'time$' and raw_stripped not in self.global_vars: return 'time_func()'
        if raw == 'timer' and raw_stripped not in self.global_vars: return 'timer()'
        if raw == 'command$' and raw_stripped not in self.global_vars: return 'command_func()'
        if raw == 'dir$' and raw_stripped not in self.global_vars: return 'dir_func()'
        if raw == 'varptr$' and raw_stripped not in self.global_vars: return 'varptr_str'
        
        # Semantic check: is this identifier declared?
        # Skip inside CREATE blocks (properties are validated separately)
        if not self.create_obj_stack:
            self._check_identifier_declared(raw_stripped, node)
        
        return raw_stripped

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op.lower()
        
        if op == '=': op = '=='
        elif op == '<>': op = '!='
        elif op == 'and': op = 'and'
        elif op == 'or': op = 'or'
        elif op == 'xor': op = '^' # Note: xor in python is bitwise, but booleans are ints.
        elif op == '\\': op = '//' # integer division
        elif op == '^': op = '**' # exponentiation
        elif op == 'mod': op = '%'
        
        return f"({left} {op} {right})"

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        op = node.op.lower()
        if op == 'not': op = 'not '
        return f"({op}{self.visit(node.operand)})"

    def visit_MemberAccessNode(self, node: MemberAccessNode) -> str:
        obj = self.visit(node.obj)
        member = node.member.lower().rstrip('$%#&!')
        
        # Semantic check: validate property/method on known component types
        if isinstance(node.obj, IdentifierNode):
            self._check_member_access(node.obj.name, member, node)
        
        # RapidP allows calling zero-argument methods without parentheses. We must append () in Python.
        if member in ('fetchrow', 'fetchfield', 'close', 'showmodal', 'clear', 'show', 'center', 'cls', 'paint', 'update', 'refresh'):
             return f"{obj}.{member}()"
             
        return f"{obj}.{member}"

    def visit_ArrayAccessNode(self, node: ArrayAccessNode) -> str:
        arr = self.visit(node.array)
        # Assuming 1D for now since our parser just grabs first arg if len==1 or list if more
        # Needs to handle multi-dim later if needed. For now just standard index
        if isinstance(node.index, list):
             idx = "][".join([self.visit(i) for i in node.index])
             return f"{arr}[{idx}]"
        else:
             idx = self.visit(node.index)
             return f"{arr}[{idx}]"

    def visit_FunctionCallNode(self, node: FunctionCallNode) -> str:
        raw_name = node.name.lower()
        if raw_name == 'varptr$':
             name = 'varptr_str'
        else:
             name = raw_name.rstrip('$%#&!')
        
        intercepts = {'dir': 'dir_func', 'command': 'command_func', 'str': 'str_func', 'date': 'date_func', 'delete': 'delete_func', 'format': 'format_func', 'sleep': 'sleep_func', 'hex': 'hex_func', 'bin': 'bin_func', 'oct': 'oct_func', 'round': 'round_func', 'insert': 'insert_func', 'replace': 'replace_func', 'reverse': 'reverse_func', 'field': 'field_func', 'mkdir': 'mkdir_func', 'rmdir': 'rmdir_func', 'kill': 'kill_func', 'rename': 'rename_func', 'messagebox': 'messagebox_func', 'msgbox': 'MsgBox', 'run': 'run_func', 'end': 'end_func', 'input': 'input_func', 'floor': 'floor_func'}
        name = intercepts.get(name, name)
        
        # Check if it's an array indexing call that fell through
        if name in self.arrays:
            idx = "][".join([self.visit(arg) for arg in node.args])
            return f"{name}[{idx}]"
        
        # Check if it's a known variable (not a function/sub/module) being indexed
        # In BASIC, array access and function calls both use parentheses: arr(i) vs func(i)
        # If a symbol is declared as a variable/array/component, emit bracket indexing
        sym = self.symbols.lookup(name)
        if sym and sym.get('kind') in ('variable', 'array', 'component') and node.args:
            idx = "][".join([self.visit(arg) for arg in node.args])
            return f"{name}[{idx}]"
        
        # Validate FUNCTION call exists and argument count
        self._check_call_exists(name, len(node.args), node)
            
        if self.create_obj_stack:
             known_builtins = ['rp_print', 'chr', 'asc', 'left', 'right', 'mid', 'len', 'instr', 'ucase', 'lcase', 'val', 'str_func', 'abs', 'atn', 'cos', 'sin', 'exp', 'log', 'sqr', 'rnd', 'timer', 'input_func', 'int', 'float', 'dir_func', 'direxists', 'chdir', 'ceil', 'acos', 'asin', 'command_func', 'date_func', 'delete_func', 'format_func', 'hextodec', 'callback', 'callfunc', 'varptr', 'varptr_str', 'vartype', 'sound', 'sleep_func', 'shell', 'showmessage', 'space', 'string', 'ltrim', 'rtrim', 'trim', 'hex_func', 'bin_func', 'oct_func', 'environ', 'curdir', 'tan', 'floor_func', 'fix', 'frac', 'round_func', 'sgn', 'cint', 'clng', 'iif', 'randomize', 'insert_func', 'replace_func', 'replacesubstr', 'reverse_func', 'rinstr', 'field_func', 'tally', 'strf', 'convbase', 'mkdir_func', 'rmdir_func', 'kill_func', 'rename_func', 'lbound', 'ubound', 'quicksort', 'initarray', 'doevents', 'playwav', 'rgb', 'messagebox_func', 'messagedlg', 'MsgBox', 'run_func', 'end_func', 'fileexists', 'shellwait']
             if name not in known_builtins:
                 target = f"{self.create_obj_stack[-1]}.{name}"
             else:
                 target = name
        else:
             target = name
             
        args = ", ".join([self.visit(arg) for arg in node.args])
        return f"{target}({args})"

    def visit_MethodCallNode(self, node: MethodCallNode) -> str:
        # Implicit property/method call inside CREATE blocks
        obj = self.visit(node.obj)
        if self.create_obj_stack and isinstance(node.obj, IdentifierNode):
             pass
        method_name = node.method.lower().rstrip('$%#&!')
        
        # Semantic check: validate method on known component types
        if isinstance(node.obj, IdentifierNode):
            self._check_member_access(node.obj.name, method_name, node)
        
        # If it's actually an array inside a UDT
        if method_name in self.udt_array_fields:
            idx = "][".join([self.visit(arg) for arg in node.args])
            return f"{obj}.{method_name}[{idx}]"
            
        args = ", ".join([self.visit(arg) for arg in node.args])
        return f"{obj}.{method_name}({args})"

    def visit_BindStatementNode(self, node: BindStatementNode) -> str:
         target = self.visit(node.target)
         function = self.visit(node.function)
         return self._emit(f"{target} = {function}")
