import sys
import argparse
import os
import traceback

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.codegen import CodeGenerator
from compiler.errors import RapidPError, ErrorCollector
from compiler.preprocessor import preprocess

def compile_code(source_code: str, file_path: str = None) -> tuple:
    """Takes RapidP source code and returns (Python source code, ErrorCollector).

    The ErrorCollector contains any semantic errors and warnings found during
    compilation. Syntax errors still raise RapidPSyntaxError immediately.
    """
    # 0. Preprocessing
    base_dir = os.path.dirname(os.path.abspath(file_path)) if file_path else os.getcwd()
    source_code = preprocess(source_code, base_dir, file_path=file_path)

    # 1. Lexical Analysis
    lexer = Lexer(source_code, file_path=file_path)
    tokens = lexer.tokenize()

    # 2. Syntax Analysis
    parser = Parser(tokens, file_path=file_path)
    ast = parser.parse()

    # 3. Code Generation (with semantic validation)
    codegen = CodeGenerator(file_path=file_path)
    py_code = codegen.generate(ast, file_path=file_path)

    return py_code, codegen.errors

def main():
    argparser = argparse.ArgumentParser(description="RapidP Transpiler (RapidP BASIC to Python)")
    argparser.add_argument("source", help="The source file (.rp)")
    argparser.add_argument("-o", "--output", help="The output Python file (.py)", default=None)
    argparser.add_argument("-r", "--run", action="store_true", help="Run the compiled Python code immediately")
    argparser.add_argument("-b", "--bytecode", action="store_true", help="Compile to Python bytecode (.pyc)")
    argparser.add_argument("-s", "--standalone", action="store_true", help="Build standalone executable via PyInstaller")
    argparser.add_argument("--wx", action="store_true", help="Generate wxPython version instead of tkinter")
    argparser.add_argument("--ww", action="store_true", help="Generate pywebview (serverless) version instead of tkinter")
    argparser.add_argument("--encoding", default="utf-8", help="Source file encoding (default: utf-8, use latin-1 for legacy files)")
    argparser.add_argument("--json-errors", action="store_true", help="Output errors as JSON array (for IDE integration)")

    args = argparser.parse_args()

    if args.wx and args.ww:
        if args.json_errors:
            import json
            print(json.dumps([{"type": "compile", "file": args.source, "line": 0, "col": 0, "message": "Options --wx and --ww are mutually exclusive."}]))
        else:
            print("Error: options --wx and --ww are mutually exclusive.")
        sys.exit(1)

    if not os.path.isfile(args.source):
        if args.json_errors:
            import json
            print(json.dumps([{"type": "compile", "file": args.source, "line": 0, "col": 0, "message": f"Source file '{args.source}' not found."}]))
        else:
            print(f"Error: Source file '{args.source}' not found.")
        sys.exit(1)

    try:
        with open(args.source, 'r', encoding=args.encoding, errors='replace') as f:
            source_code = f.read()

        py_code, errors = compile_code(source_code, file_path=args.source)
        
        # Inject wxPython import if --wx flag is set
        if args.wx:
            # Replace tkinter import with wxPython runtime
            py_code = py_code.replace('from rp_runtime.gui import', 'from rp_runtime.gui_wx import')
            # Ensure run_app is called correctly for wx
            if 'get_app().run()' in py_code:
                py_code = py_code.replace('get_app().run()', 'run_app()')
        elif args.ww:
            # Replace tkinter import with pywebview runtime (serverless mode utilities).
            py_code = py_code.replace('from rp_runtime.gui import', 'from rp_runtime.gui_webview import')

        # Handle semantic errors
        if errors.has_errors:
            if args.json_errors:
                print(errors.to_json())
            else:
                print(errors.format_text())
            sys.exit(1)

        # Print warnings (non-blocking) if not in JSON mode
        if errors.warnings and not args.json_errors:
            print(errors.format_text())

        output_file = args.output
        if not output_file:
            base, _ = os.path.splitext(args.source)
            suffix = "_wx" if args.wx else ""
            output_file = base + suffix + ".py"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(py_code)

        if not args.json_errors:
            backend = "wxPython" if args.wx else ("pywebview" if args.ww else "tkinter")
            print(f"Successfully compiled '{args.source}' to '{output_file}' ({backend} backend)")

        if args.bytecode:
            import py_compile
            pyc_file = py_compile.compile(output_file, doraise=True)
            if not args.json_errors:
                print(f"Bytecode compiled to '{pyc_file}'")

        if args.standalone:
            if not args.json_errors:
                print("Building standalone executable...")
            import subprocess as _sp
            current_dir = os.path.abspath(os.path.dirname(__file__))
            pyinstaller_args = [
                sys.executable, '-m', 'PyInstaller',
                '--onefile',
                '--name', os.path.splitext(os.path.basename(output_file))[0],
                '--add-data', f'{os.path.join(current_dir, "rp_runtime")}:rp_runtime',
                output_file
            ]
            result = _sp.run(pyinstaller_args, capture_output=True, text=True)
            if result.returncode == 0:
                if not args.json_errors:
                    print("Standalone build successful! Check the 'dist/' folder.")
            else:
                if not args.json_errors:
                    print(f"Standalone build failed:\n{result.stderr}")
                sys.exit(1)

        if args.run:
            if not args.json_errors:
                print(f"Running '{output_file}'...\n{'-'*40}")
            import subprocess

            env = os.environ.copy()
            current_dir = os.path.abspath(os.path.dirname(__file__))
            python_path = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = f"{current_dir}:{python_path}" if python_path else current_dir

            try:
                subprocess.run([sys.executable, output_file], env=env, check=True)
            except subprocess.CalledProcessError as e:
                if not args.json_errors:
                    print(f"\n{'-'*40}\nExecution failed with error code {e.returncode}")
                sys.exit(e.returncode)

    except RapidPError as e:
        if args.json_errors:
            import json
            err_dict = e.to_dict() if hasattr(e, 'to_dict') else {"type": "syntax", "file": args.source, "line": getattr(e, 'line', 0), "col": getattr(e, 'column', 0), "message": getattr(e, 'message', str(e))}
            print(json.dumps([err_dict]))
        else:
            print(e)
        sys.exit(1)
    except Exception as e:
        if args.json_errors:
            import json
            print(json.dumps([{"type": "internal", "file": args.source, "line": 0, "col": 0, "message": str(e)}]))
        else:
            print(f"An unexpected error occurred: {e}")
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
