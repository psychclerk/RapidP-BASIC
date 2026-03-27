const vscode = require('vscode');
const { COMPONENT_REGISTRY, BUILTIN_FUNCTIONS, KEYWORDS, TYPE_KEYWORDS, DIRECTIVES } = require('./languageData');

class RapidPHoverProvider {
    provideHover(document, position) {
        const wordRange = document.getWordRangeAtPosition(position, /[A-Za-z_$][A-Za-z0-9_$]*/);
        if (!wordRange) return null;

        const word = document.getText(wordRange).toUpperCase();
        const line = document.lineAt(position.line).text;

        // Check if preceded by $ (directive)
        const charBefore = wordRange.start.character > 0
            ? line.charAt(wordRange.start.character - 1)
            : '';
        if (charBefore === '$') {
            return this._hoverDirective(word);
        }

        // Check if it's a dot-member: varName.MEMBER
        const beforeWord = line.substring(0, wordRange.start.character);
        const dotMatch = beforeWord.match(/([A-Za-z_]\w*)\.$/);
        if (dotMatch) {
            return this._hoverMember(document, dotMatch[1], word);
        }

        // Component type
        if (COMPONENT_REGISTRY[word]) {
            return this._hoverComponent(word);
        }

        // Builtin function
        const builtin = BUILTIN_FUNCTIONS.find(f => f.name === word || f.name === word + '$');
        if (builtin) {
            return this._hoverBuiltin(builtin);
        }

        // Type keyword
        const typeKw = TYPE_KEYWORDS.find(t => t.name === word);
        if (typeKw) {
            return new vscode.Hover(
                new vscode.MarkdownString(`**${typeKw.name}** — *type*\n\n${typeKw.description}`)
            );
        }

        // Language keyword
        if (KEYWORDS.includes(word)) {
            return this._hoverKeyword(word);
        }

        // User-defined component variable — show its type
        const compType = this._resolveComponentType(document, word);
        if (compType && COMPONENT_REGISTRY[compType]) {
            const md = new vscode.MarkdownString();
            md.appendMarkdown(`**${word}** — \`${compType}\`\n\n`);
            md.appendMarkdown(`*Created component. Hover the type name for details.*`);
            return new vscode.Hover(md);
        }

        return null;
    }

    _hoverDirective(name) {
        const dir = DIRECTIVES.find(d => d.name === name);
        if (!dir) return null;
        const md = new vscode.MarkdownString();
        md.appendMarkdown(`**\\$${dir.name}** — *compiler directive*\n\n`);
        md.appendMarkdown(dir.description);
        return new vscode.Hover(md);
    }

    _hoverMember(document, varName, member) {
        const compType = this._resolveComponentType(document, varName);
        if (!compType || !COMPONENT_REGISTRY[compType]) return null;
        const comp = COMPONENT_REGISTRY[compType];
        const memberLower = member.toLowerCase();

        if (comp.props.includes(memberLower)) {
            return new vscode.Hover(
                new vscode.MarkdownString(`**${member}** — *property* of \`${compType}\``)
            );
        }
        if (comp.methods.includes(memberLower)) {
            return new vscode.Hover(
                new vscode.MarkdownString(`**${member}** — *method* of \`${compType}\``)
            );
        }
        if (comp.events.includes(memberLower)) {
            return new vscode.Hover(
                new vscode.MarkdownString(`**${member}** — *event* of \`${compType}\`\n\nAssign a SUB name to handle this event.`)
            );
        }
        return null;
    }

    _hoverComponent(name) {
        const comp = COMPONENT_REGISTRY[name];
        const md = new vscode.MarkdownString();
        md.appendMarkdown(`**${name}** — *GUI component*\n\n`);

        if (comp.props.length) {
            md.appendMarkdown(`**Properties:** ${comp.props.join(', ')}\n\n`);
        }
        if (comp.methods.length) {
            md.appendMarkdown(`**Methods:** ${comp.methods.join(', ')}\n\n`);
        }
        if (comp.events.length) {
            md.appendMarkdown(`**Events:** ${comp.events.join(', ')}\n\n`);
        }
        return new vscode.Hover(md);
    }

    _hoverBuiltin(fn) {
        const md = new vscode.MarkdownString();
        md.appendCodeblock(fn.signature, 'rapidp');
        md.appendMarkdown(`\n${fn.description}`);
        return new vscode.Hover(md);
    }

    _hoverKeyword(word) {
        const desc = KEYWORD_DOCS[word];
        if (!desc) {
            return new vscode.Hover(
                new vscode.MarkdownString(`**${word}** — *keyword*`)
            );
        }
        return new vscode.Hover(
            new vscode.MarkdownString(`**${word}** — *keyword*\n\n${desc}`)
        );
    }

    _resolveComponentType(document, varName) {
        const upper = varName.toUpperCase();
        const text = document.getText();
        // CREATE varName AS PTYPE
        const createRe = new RegExp(`CREATE\\s+${upper}\\s+AS\\s+(P\\w+|Q\\w+)`, 'im');
        const m1 = text.match(createRe);
        if (m1) return m1[1].toUpperCase();
        // DIM varName AS PTYPE
        const dimRe = new RegExp(`DIM\\s+${upper}\\s+AS\\s+(P\\w+|Q\\w+)`, 'im');
        const m2 = text.match(dimRe);
        if (m2) return m2[1].toUpperCase();
        return null;
    }
}

const KEYWORD_DOCS = {
    'DIM': 'Declares a variable. Syntax: `DIM name AS type`',
    'CONST': 'Declares a constant. Syntax: `CONST name = value`',
    'AS': 'Specifies the type in a declaration.',
    'IF': 'Conditional branch. Use with THEN, ELSE, ELSEIF, END IF.',
    'THEN': 'Follows an IF condition.',
    'ELSE': 'Alternative branch in an IF block.',
    'ELSEIF': 'Additional conditional branch.',
    'FOR': 'Counted loop. Syntax: `FOR var = start TO end [STEP n] ... NEXT`',
    'TO': 'Specifies the upper bound in a FOR loop.',
    'STEP': 'Specifies the increment in a FOR loop.',
    'NEXT': 'Ends a FOR loop iteration.',
    'WHILE': 'Loop with pre-condition. Syntax: `WHILE condition ... WEND`',
    'WEND': 'Ends a WHILE loop.',
    'DO': 'Flexible loop. Use with LOOP, UNTIL, WHILE.',
    'LOOP': 'Ends a DO block. Optionally followed by WHILE or UNTIL.',
    'UNTIL': 'Post-condition: loop until condition is true.',
    'SELECT': 'Multi-branch switch. Syntax: `SELECT CASE expr ... END SELECT`',
    'CASE': 'A branch in a SELECT CASE block.',
    'SUB': 'Declares a subroutine. Syntax: `SUB Name(params) ... END SUB`',
    'FUNCTION': 'Declares a function. Syntax: `FUNCTION Name(params) AS type ... END FUNCTION`',
    'CALL': 'Explicitly calls a subroutine.',
    'RETURN': 'Returns from a SUB or FUNCTION. In FUNCTION, sets return value.',
    'EXIT': 'Exits the current block (FOR, WHILE, DO, SUB, FUNCTION).',
    'PRINT': 'Outputs text to console.',
    'INPUT': 'Reads user input from console.',
    'GOTO': 'Unconditional jump to a label.',
    'GOSUB': 'Calls a label as subroutine, returns with RETURN.',
    'IMPORT': 'Imports a Python module. Syntax: `IMPORT "module"`',
    'CREATE': 'Creates a GUI component. Syntax: `CREATE name AS type ... END CREATE`',
    'TYPE': 'Defines a user-defined type (struct). Syntax: `TYPE Name ... END TYPE`',
    'DECLARE': 'Declares an external function from a DLL/library.',
    'WITH': 'Sets a default object for property/method access.',
    'EXTENDS': 'Inherits from another TYPE.',
    'BIND': 'Binds an event to a subroutine.',
    'CONSTRUCTOR': 'Defines a constructor inside a TYPE.',
    'PROPERTY': 'Declares a property inside a TYPE.',
    'SET': 'Assigns an object reference.',
    'BYVAL': 'Pass parameter by value.',
    'BYREF': 'Pass parameter by reference.',
    'AND': 'Logical/bitwise AND operator.',
    'OR': 'Logical/bitwise OR operator.',
    'NOT': 'Logical/bitwise NOT operator.',
    'XOR': 'Logical/bitwise XOR operator.',
    'MOD': 'Modulo (remainder) operator.',
    'END': 'Terminates the program, or closes a block (END IF, END SUB, etc.).',
    'TRUE': 'Boolean constant: True.',
    'FALSE': 'Boolean constant: False.',
    'NOTHING': 'Null object reference.',
    'REM': 'Comment (entire line).',
    'LIB': 'Specifies a library in a DECLARE statement.',
    'ALIAS': 'Specifies an alias name in a DECLARE statement.',
    'PRIVATE': 'Private member access in a TYPE.',
    'PUBLIC': 'Public member access in a TYPE.',
};

module.exports = { RapidPHoverProvider };
