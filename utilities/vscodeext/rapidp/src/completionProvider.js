const vscode = require('vscode');
const { COMPONENT_REGISTRY, BUILTIN_FUNCTIONS, KEYWORDS, TYPE_KEYWORDS, DIRECTIVES } = require('./languageData');

class RapidPCompletionProvider {
    provideCompletionItems(document, position, token, context) {
        const lineText = document.lineAt(position).text;
        const linePrefix = lineText.substring(0, position.character);

        // Dot completion: component member access
        const dotMatch = linePrefix.match(/(\w+)\.\s*$/);
        if (dotMatch) {
            return this._getComponentMemberCompletions(document, dotMatch[1]);
        }

        // WITH block dot completion
        if (linePrefix.match(/^\s*\.\s*$/)) {
            return this._getWithBlockCompletions(document, position);
        }

        // Directive completion (after $)
        if (linePrefix.match(/\$\w*$/)) {
            return this._getDirectiveCompletions();
        }

        // AS type completion
        if (linePrefix.match(/\bAS\s+\w*$/i)) {
            return this._getTypeCompletions();
        }

        // CREATE ... AS component type completion
        if (linePrefix.match(/\bCREATE\s+\w+\s+AS\s+\w*$/i)) {
            return this._getComponentTypeCompletions();
        }

        // Inside CREATE block: property/method/event completions
        const createContext = this._getCreateContext(document, position);
        if (createContext) {
            return this._getCreateBlockCompletions(createContext);
        }

        // General completions
        return this._getGeneralCompletions(document);
    }

    _getComponentMemberCompletions(document, varName) {
        const items = [];
        const compType = this._resolveComponentType(document, varName);
        if (compType) {
            const registry = COMPONENT_REGISTRY[compType.toUpperCase()];
            if (registry) {
                // Properties
                for (const prop of registry.props) {
                    const item = new vscode.CompletionItem(prop, vscode.CompletionItemKind.Property);
                    item.detail = `(property) ${compType}.${prop}`;
                    item.sortText = '0' + prop;
                    items.push(item);
                }
                // Methods
                for (const method of registry.methods) {
                    const item = new vscode.CompletionItem(method, vscode.CompletionItemKind.Method);
                    item.detail = `(method) ${compType}.${method}()`;
                    item.insertText = new vscode.SnippetString(method + '($0)');
                    item.sortText = '1' + method;
                    items.push(item);
                }
                // Events
                for (const event of registry.events) {
                    const item = new vscode.CompletionItem(event, vscode.CompletionItemKind.Event);
                    item.detail = `(event) ${compType}.${event}`;
                    item.sortText = '2' + event;
                    items.push(item);
                }
            }
        }
        return items;
    }

    _getWithBlockCompletions(document, position) {
        // Walk backwards to find the WITH target and its type
        for (let i = position.line - 1; i >= 0; i--) {
            const line = document.lineAt(i).text.trim();
            const withMatch = line.match(/^WITH\s+(\w+)/i);
            if (withMatch) {
                return this._getComponentMemberCompletions(document, withMatch[1]);
            }
            if (/^END\s+WITH/i.test(line)) break;
        }
        return [];
    }

    _getCreateContext(document, position) {
        // Walk backwards to find if we're inside a CREATE block
        let depth = 0;
        for (let i = position.line - 1; i >= 0; i--) {
            const line = document.lineAt(i).text.trim().toUpperCase();
            if (line.startsWith('END CREATE')) {
                depth++;
            } else if (line.startsWith('CREATE ')) {
                if (depth === 0) {
                    const match = document.lineAt(i).text.trim().match(/CREATE\s+\w+\s+AS\s+(\w+)/i);
                    if (match) {
                        return match[1];
                    }
                    return null;
                }
                depth--;
            }
        }
        return null;
    }

    _getCreateBlockCompletions(componentType) {
        const items = [];
        const upper = componentType.toUpperCase();
        const registry = COMPONENT_REGISTRY[upper];
        if (registry) {
            for (const prop of registry.props) {
                const item = new vscode.CompletionItem(prop, vscode.CompletionItemKind.Property);
                item.detail = `(property) ${componentType}.${prop}`;
                item.insertText = new vscode.SnippetString(prop + ' = $0');
                item.sortText = '0' + prop;
                items.push(item);
            }
            for (const method of registry.methods) {
                const item = new vscode.CompletionItem(method, vscode.CompletionItemKind.Method);
                item.detail = `(method) ${componentType}.${method}()`;
                item.sortText = '1' + method;
                items.push(item);
            }
            for (const event of registry.events) {
                const item = new vscode.CompletionItem(event, vscode.CompletionItemKind.Event);
                item.detail = `(event) ${componentType}.${event}`;
                item.insertText = new vscode.SnippetString(event + ' = $0');
                item.sortText = '2' + event;
                items.push(item);
            }
        }
        return items;
    }

    _getDirectiveCompletions() {
        return DIRECTIVES.map(d => {
            const item = new vscode.CompletionItem('$' + d.name, vscode.CompletionItemKind.Keyword);
            item.detail = d.description;
            item.insertText = new vscode.SnippetString(d.snippet);
            return item;
        });
    }

    _getTypeCompletions() {
        const items = [];
        for (const t of TYPE_KEYWORDS) {
            const item = new vscode.CompletionItem(t.name, vscode.CompletionItemKind.TypeParameter);
            item.detail = t.description;
            items.push(item);
        }
        // Also suggest component types
        for (const compName of Object.keys(COMPONENT_REGISTRY)) {
            const displayName = compName.charAt(0) + compName.slice(1).toLowerCase();
            const item = new vscode.CompletionItem(displayName, vscode.CompletionItemKind.Class);
            item.detail = `GUI component type`;
            items.push(item);
        }
        return items;
    }

    _getComponentTypeCompletions() {
        const items = [];
        for (const compName of Object.keys(COMPONENT_REGISTRY)) {
            const displayName = this._formatComponentName(compName);
            const item = new vscode.CompletionItem(displayName, vscode.CompletionItemKind.Class);
            const registry = COMPONENT_REGISTRY[compName];
            const propCount = registry.props.length;
            const methodCount = registry.methods.length;
            const eventCount = registry.events.length;
            item.detail = `${propCount} props, ${methodCount} methods, ${eventCount} events`;
            items.push(item);
        }
        return items;
    }

    _getGeneralCompletions(document) {
        const items = [];

        // Keywords
        for (const kw of KEYWORDS) {
            const item = new vscode.CompletionItem(kw, vscode.CompletionItemKind.Keyword);
            item.sortText = '3' + kw;
            items.push(item);
        }

        // Builtin functions
        for (const fn of BUILTIN_FUNCTIONS) {
            const item = new vscode.CompletionItem(fn.name, vscode.CompletionItemKind.Function);
            item.detail = fn.description;
            if (fn.signature) {
                item.insertText = new vscode.SnippetString(fn.snippet || fn.name + '($0)');
            }
            item.sortText = '1' + fn.name;
            items.push(item);
        }

        // Component types (when you might use them in DIM or CREATE)
        for (const compName of Object.keys(COMPONENT_REGISTRY)) {
            const displayName = this._formatComponentName(compName);
            const item = new vscode.CompletionItem(displayName, vscode.CompletionItemKind.Class);
            item.sortText = '2' + displayName;
            items.push(item);
        }

        // Document symbols (user-defined variables, subs, functions)
        const text = document.getText();
        const seen = new Set();

        // Subs
        const subPattern = /\bSUB\s+(\w+)/gi;
        let m;
        while ((m = subPattern.exec(text)) !== null) {
            const name = m[1];
            if (!seen.has(name.toUpperCase())) {
                seen.add(name.toUpperCase());
                const item = new vscode.CompletionItem(name, vscode.CompletionItemKind.Function);
                item.detail = '(subroutine)';
                item.sortText = '0' + name;
                items.push(item);
            }
        }

        // Functions
        const funcPattern = /\bFUNCTION\s+(\w+)/gi;
        while ((m = funcPattern.exec(text)) !== null) {
            const name = m[1];
            if (!seen.has(name.toUpperCase())) {
                seen.add(name.toUpperCase());
                const item = new vscode.CompletionItem(name, vscode.CompletionItemKind.Function);
                item.detail = '(function)';
                item.sortText = '0' + name;
                items.push(item);
            }
        }

        // Variables from DIM
        const dimPattern = /\bDIM\s+(\w+)/gi;
        while ((m = dimPattern.exec(text)) !== null) {
            const name = m[1];
            if (!seen.has(name.toUpperCase())) {
                seen.add(name.toUpperCase());
                const item = new vscode.CompletionItem(name, vscode.CompletionItemKind.Variable);
                item.detail = '(variable)';
                item.sortText = '0' + name;
                items.push(item);
            }
        }

        // Constants
        const constPattern = /\bCONST\s+(\w+)/gi;
        while ((m = constPattern.exec(text)) !== null) {
            const name = m[1];
            if (!seen.has(name.toUpperCase())) {
                seen.add(name.toUpperCase());
                const item = new vscode.CompletionItem(name, vscode.CompletionItemKind.Constant);
                item.detail = '(constant)';
                item.sortText = '0' + name;
                items.push(item);
            }
        }

        // CREATE'd components
        const createPattern = /\bCREATE\s+(\w+)\s+AS\s+(\w+)/gi;
        while ((m = createPattern.exec(text)) !== null) {
            const name = m[1];
            const type = m[2];
            if (!seen.has(name.toUpperCase())) {
                seen.add(name.toUpperCase());
                const item = new vscode.CompletionItem(name, vscode.CompletionItemKind.Variable);
                item.detail = `(${type})`;
                item.sortText = '0' + name;
                items.push(item);
            }
        }

        return items;
    }

    _resolveComponentType(document, varName) {
        const text = document.getText();
        const upper = varName.toUpperCase();
        
        // Check CREATE statements
        const createPattern = new RegExp(`\\bCREATE\\s+${this._escapeRegex(varName)}\\s+AS\\s+(\\w+)`, 'i');
        const createMatch = text.match(createPattern);
        if (createMatch) return createMatch[1];

        // Check DIM statements
        const dimPattern = new RegExp(`\\bDIM\\s+${this._escapeRegex(varName)}\\s+AS\\s+(\\w+)`, 'i');
        const dimMatch = text.match(dimPattern);
        if (dimMatch) return dimMatch[1];

        return null;
    }

    _escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    _formatComponentName(upperName) {
        // PFORM -> PForm, PBUTTON -> PButton, PHTTP -> PHTTP, etc.
        const nameMap = {
            'PFORM': 'PForm', 'PBUTTON': 'PButton', 'PLABEL': 'PLabel', 'PEDIT': 'PEdit',
            'PCANVAS': 'PCanvas', 'PPANEL': 'PPanel', 'PTIMER': 'PTimer',
            'PMAINMENU': 'PMainMenu', 'PMENUITEM': 'PMenuItem', 'PCOMBOBOX': 'PComboBox',
            'PLISTBOX': 'PListBox', 'PCHECKBOX': 'PCheckBox', 'PRADIOBUTTON': 'PRadioButton',
            'PRICHEDIT': 'PRichEdit', 'PSTRINGGRID': 'PStringGrid', 'PIMAGE': 'PImage',
            'PSCROLLBAR': 'PScrollBar', 'PTABCONTROL': 'PTabControl',
            'PGROUPBOX': 'PGroupBox', 'PMYSQL': 'PMySQL', 'PSQLITE': 'PSQLite',
            'PPROGRESSBAR': 'PProgressBar', 'PLISTVIEW': 'PListView',
            'POPENDIALOG': 'POpenDialog', 'PSAVEDIALOG': 'PSaveDialog',
            'PFILESTREAM': 'PFileStream', 'PFILEDIALOG': 'PFileDialog',
            'PCODEEDITOR': 'PCodeEditor', 'PLINE': 'PLine', 'PICON': 'PIcon',
            'PIMAGELIST': 'PImageList', 'PSOCKET': 'PSocket',
            'PSERVERSOCKET': 'PServerSocket', 'PHTTP': 'PHTTP',
            'PSTATUSBAR': 'PStatusBar', 'PCOLORDIALOG': 'PColorDialog',
            'PFONTDIALOG': 'PFontDialog', 'PDESIGNSURFACE': 'PDesignSurface',
            'PTREEVIEW': 'PTreeView', 'PSPLITTER': 'PSplitter', 'PTRACKBAR': 'PTrackBar',
            'PSCROLLBOX': 'PScrollBox', 'PPOPUPMENU': 'PPopupMenu',
            'PINI': 'PIni', 'PMEMORYSTREAM': 'PMemoryStream', 'PSTRINGLIST': 'PStringList',
            'PPRINTER': 'PPrinter', 'PNUMPY': 'PNumPy', 'PMATPLOTLIB': 'PMatPlotLib',
            'PPANDAS': 'PPandas'
        };
        return nameMap[upperName] || upperName;
    }
}

module.exports = { RapidPCompletionProvider };
