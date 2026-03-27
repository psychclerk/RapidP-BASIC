const vscode = require('vscode');
const { RapidPCompletionProvider } = require('./completionProvider');
const { RapidPHoverProvider } = require('./hoverProvider');
const { RapidPSignatureHelpProvider } = require('./signatureProvider');
const { RapidPDocumentSymbolProvider } = require('./symbolProvider');

const RAPIDP_MODE = { language: 'rapidp', scheme: 'file' };

function activate(context) {
    // Register completion provider
    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider(
            RAPIDP_MODE,
            new RapidPCompletionProvider(),
            '.', '(', '$'
        )
    );

    // Register hover provider
    context.subscriptions.push(
        vscode.languages.registerHoverProvider(
            RAPIDP_MODE,
            new RapidPHoverProvider()
        )
    );

    // Register signature help provider
    context.subscriptions.push(
        vscode.languages.registerSignatureHelpProvider(
            RAPIDP_MODE,
            new RapidPSignatureHelpProvider(),
            '(', ','
        )
    );

    // Register document symbol provider (Outline view)
    context.subscriptions.push(
        vscode.languages.registerDocumentSymbolProvider(
            RAPIDP_MODE,
            new RapidPDocumentSymbolProvider()
        )
    );

    // Register compile command
    context.subscriptions.push(
        vscode.commands.registerCommand('rapidp.compile', () => compileFile(false))
    );

    // Register compile and run command
    context.subscriptions.push(
        vscode.commands.registerCommand('rapidp.compileAndRun', () => compileFile(true))
    );

    // Register compile to executable command
    context.subscriptions.push(
        vscode.commands.registerCommand('rapidp.compileToExe', () => compileToExe())
    );

    // Setup diagnostics
    const diagnostics = vscode.languages.createDiagnosticCollection('rapidp');
    context.subscriptions.push(diagnostics);

    // Validate on save
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(doc => {
            if (doc.languageId === 'rapidp') {
                validateDocument(doc, diagnostics);
            }
        })
    );

    // Validate on open
    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(doc => {
            if (doc.languageId === 'rapidp') {
                validateDocument(doc, diagnostics);
            }
        })
    );

    // Validate currently open document
    if (vscode.window.activeTextEditor && vscode.window.activeTextEditor.document.languageId === 'rapidp') {
        validateDocument(vscode.window.activeTextEditor.document, diagnostics);
    }

    // Status bar item
    const statusItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusItem.text = '$(play) RapidP';
    statusItem.tooltip = 'Compile and Run (F5)';
    statusItem.command = 'rapidp.compileAndRun';
    context.subscriptions.push(statusItem);

    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor(editor => {
            if (editor && editor.document.languageId === 'rapidp') {
                statusItem.show();
            } else {
                statusItem.hide();
            }
        })
    );

    if (vscode.window.activeTextEditor && vscode.window.activeTextEditor.document.languageId === 'rapidp') {
        statusItem.show();
    }

    console.log('RapidP extension activated');
}

function findCompilerPath() {
    const config = vscode.workspace.getConfiguration('rapidp');
    const configuredPath = config.get('compilerPath');
    if (configuredPath) {
        return configuredPath;
    }
    // Auto-detect: look for compile.py relative to the workspace
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders) {
        for (const folder of workspaceFolders) {
            const path = require('path');
            const fs = require('fs');
            // Check common locations
            const candidates = [
                path.join(folder.uri.fsPath, 'compile.py'),
                path.join(folder.uri.fsPath, '..', 'compile.py'),
                path.join(folder.uri.fsPath, '..', '..', 'compile.py'),
            ];
            for (const candidate of candidates) {
                try {
                    const resolved = fs.realpathSync(candidate);
                    if (fs.existsSync(resolved)) {
                        return resolved;
                    }
                } catch {
                    // keep searching
                }
            }
        }
    }
    return null;
}

function compileFile(run) {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'rapidp') {
        vscode.window.showWarningMessage('No RapidP file is open.');
        return;
    }
    editor.document.save().then(() => {
        const filePath = editor.document.uri.fsPath;
        const compilerPath = findCompilerPath();
        if (!compilerPath) {
            vscode.window.showErrorMessage('Could not find compile.py. Set rapidp.compilerPath in settings.');
            return;
        }
        const config = vscode.workspace.getConfiguration('rapidp');
        const pythonPath = config.get('pythonPath') || 'python3';
        const encoding = config.get('encoding') || 'utf-8';

        const args = [compilerPath, filePath, '--encoding', encoding, '--json-errors'];
        if (run || config.get('runAfterCompile')) {
            args.push('-r');
        }

        const terminal = vscode.window.createTerminal({
            name: 'RapidP',
            shellPath: pythonPath,
            shellArgs: args
        });
        terminal.show();
    });
}

function compileToExe() {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'rapidp') {
        vscode.window.showWarningMessage('No RapidP file is open.');
        return;
    }
    editor.document.save().then(() => {
        const filePath = editor.document.uri.fsPath;
        const compilerPath = findCompilerPath();
        if (!compilerPath) {
            vscode.window.showErrorMessage('Could not find compile.py. Set rapidp.compilerPath in settings.');
            return;
        }
        const config = vscode.workspace.getConfiguration('rapidp');
        const pythonPath = config.get('pythonPath') || 'python3';
        const encoding = config.get('encoding') || 'utf-8';

        const terminal = vscode.window.createTerminal({
            name: 'RapidP Build',
            shellPath: pythonPath,
            shellArgs: [compilerPath, filePath, '--encoding', encoding, '-s']
        });
        terminal.show();
    });
}

function validateDocument(document, diagnostics) {
    const text = document.getText();
    const lines = text.split('\n');
    const diags = [];
    const blockStack = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();
        const upper = trimmed.toUpperCase();

        // Skip comments and empty lines
        if (!trimmed || upper.startsWith("'") || upper.startsWith('REM ') || upper === 'REM') {
            continue;
        }
        // Skip directives
        if (trimmed.startsWith('$')) continue;

        // Track block structures for mismatched END detection
        if (/^(IF\b.*\bTHEN\s*$)/i.test(trimmed)) {
            blockStack.push({ type: 'IF', line: i });
        } else if (/^FOR\b/i.test(upper)) {
            blockStack.push({ type: 'FOR', line: i });
        } else if (/^WHILE\b/i.test(upper)) {
            blockStack.push({ type: 'WHILE', line: i });
        } else if (/^DO\b/i.test(upper)) {
            blockStack.push({ type: 'DO', line: i });
        } else if (/^SUB\b/i.test(upper)) {
            blockStack.push({ type: 'SUB', line: i });
        } else if (/^FUNCTION\b/i.test(upper)) {
            blockStack.push({ type: 'FUNCTION', line: i });
        } else if (/^SELECT\s+CASE\b/i.test(upper)) {
            blockStack.push({ type: 'SELECT', line: i });
        } else if (/^TYPE\b/i.test(upper)) {
            blockStack.push({ type: 'TYPE', line: i });
        } else if (/^CREATE\b/i.test(upper)) {
            blockStack.push({ type: 'CREATE', line: i });
        } else if (/^WITH\b/i.test(upper)) {
            blockStack.push({ type: 'WITH', line: i });
        }

        // Pop blocks
        if (/^END\s+IF\b/i.test(upper)) {
            if (blockStack.length > 0 && blockStack[blockStack.length - 1].type === 'IF') {
                blockStack.pop();
            }
        } else if (/^NEXT\b/i.test(upper)) {
            if (blockStack.length > 0 && blockStack[blockStack.length - 1].type === 'FOR') {
                blockStack.pop();
            }
        } else if (/^WEND\b/i.test(upper)) {
            if (blockStack.length > 0 && blockStack[blockStack.length - 1].type === 'WHILE') {
                blockStack.pop();
            }
        } else if (/^LOOP\b/i.test(upper)) {
            if (blockStack.length > 0 && blockStack[blockStack.length - 1].type === 'DO') {
                blockStack.pop();
            }
        } else if (/^END\s+SUB\b/i.test(upper)) {
            if (blockStack.length > 0 && blockStack[blockStack.length - 1].type === 'SUB') {
                blockStack.pop();
            }
        } else if (/^END\s+FUNCTION\b/i.test(upper)) {
            if (blockStack.length > 0 && blockStack[blockStack.length - 1].type === 'FUNCTION') {
                blockStack.pop();
            }
        } else if (/^END\s+SELECT\b/i.test(upper)) {
            if (blockStack.length > 0 && blockStack[blockStack.length - 1].type === 'SELECT') {
                blockStack.pop();
            }
        } else if (/^END\s+TYPE\b/i.test(upper)) {
            if (blockStack.length > 0 && blockStack[blockStack.length - 1].type === 'TYPE') {
                blockStack.pop();
            }
        } else if (/^END\s+CREATE\b/i.test(upper)) {
            if (blockStack.length > 0 && blockStack[blockStack.length - 1].type === 'CREATE') {
                blockStack.pop();
            }
        } else if (/^END\s+WITH\b/i.test(upper)) {
            if (blockStack.length > 0 && blockStack[blockStack.length - 1].type === 'WITH') {
                blockStack.pop();
            }
        }

        // Check for unclosed strings
        const inString = (trimmed.split('"').length - 1) % 2 !== 0;
        if (inString) {
            // Check it's not just in a comment
            const commentIdx = trimmed.indexOf("'");
            const firstQuote = trimmed.indexOf('"');
            if (commentIdx === -1 || firstQuote < commentIdx) {
                diags.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    'Unterminated string literal',
                    vscode.DiagnosticSeverity.Error
                ));
            }
        }
    }

    // Report unclosed blocks
    for (const block of blockStack) {
        const endKeyword = block.type === 'FOR' ? 'NEXT' : block.type === 'WHILE' ? 'WEND' : block.type === 'DO' ? 'LOOP' : `END ${block.type}`;
        diags.push(new vscode.Diagnostic(
            new vscode.Range(block.line, 0, block.line, lines[block.line].length),
            `Unclosed ${block.type} block — missing ${endKeyword}`,
            vscode.DiagnosticSeverity.Warning
        ));
    }

    diagnostics.set(document.uri, diags);
}

function deactivate() {}

module.exports = { activate, deactivate };
