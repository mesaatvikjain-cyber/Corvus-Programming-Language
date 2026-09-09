const vscode = require('vscode');
const { spawn } = require('child_process');
const path = require('path');

let diagnosticCollection;

function activate(context) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('corvus');
    context.subscriptions.push(diagnosticCollection);

    // Register active editor diagnostic listener
    if (vscode.window.activeTextEditor) {
        validateCorvusDocument(vscode.window.activeTextEditor.document);
    }

    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(doc => {
            if (doc.languageId === 'corvus') {
                validateCorvusDocument(doc);
            }
        })
    );

    // Register Status Bar Item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'corvus.runFile';
    statusBarItem.text = '$(play) Run Corvus';
    statusBarItem.tooltip = 'Execute active Corvus file';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Command: Run file in interpreter
    let runFileCmd = vscode.commands.registerCommand('corvus.runFile', function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active Corvus file selected.');
            return;
        }

        const filePath = editor.document.fileName;
        if (!filePath.endsWith('.crv')) {
            vscode.window.showWarningMessage('Active file is not a Corvus (.crv) source file.');
            return;
        }

        const terminal = vscode.window.createTerminal('Corvus Interpreter');
        terminal.show();
        terminal.sendText(`python "${path.join(__dirname, '..', '..', 'Interpreter', 'Corvus.py')}" "${filePath}"`);
    });

    // Command: Compile & Run Native Binary
    let compileCmd = vscode.commands.registerCommand('corvus.compileAndRun', function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active Corvus file selected.');
            return;
        }

        const filePath = editor.document.fileName;
        const terminal = vscode.window.createTerminal('Corvus Compiler');
        terminal.show();
        terminal.sendText(`python "${path.join(__dirname, '..', '..', 'Compiler_Windows', 'CorvusC.py')}" "${filePath}"`);
    });

    // Command: Start Interactive REPL
    let replCmd = vscode.commands.registerCommand('corvus.startRepl', function () {
        const terminal = vscode.window.createTerminal('Corvus REPL');
        terminal.show();
        terminal.sendText(`python "${path.join(__dirname, '..', '..', 'Interpreter', 'Corvus.py')}" --repl`);
    });

    context.subscriptions.push(runFileCmd, compileCmd, replCmd);
}

function validateCorvusDocument(document) {
    if (document.languageId !== 'corvus') return;

    const filePath = document.fileName;
    const interpreterPath = path.join(__dirname, '..', '..', 'Interpreter', 'Corvus.py');

    const pyProcess = spawn('python', [interpreterPath, '--check', filePath]);
    let stderrData = '';

    pyProcess.stderr.on('data', (data) => {
        stderrData += data.toString();
    });

    pyProcess.on('close', (code) => {
        const diagnostics = [];
        if (code !== 0 && stderrData) {
            // Parse error line from stderr output
            const match = stderrData.match(/Line (\d+):/i);
            const lineNum = match ? Math.max(0, parseInt(match[1]) - 1) : 0;
            const range = new vscode.Range(lineNum, 0, lineNum, 100);

            const diagnostic = new vscode.Diagnostic(
                range,
                stderrData.trim(),
                vscode.DiagnosticSeverity.Error
            );
            diagnostics.push(diagnostic);
        }
        diagnosticCollection.set(document.uri, diagnostics);
    });
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
