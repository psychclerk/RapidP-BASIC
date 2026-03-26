import os
import re
import builtins
from compiler.errors import RapidPCompileError


def preprocess(source_code: str, base_dir: str, defines=None, include_stack=None, file_path=None) -> str:
    """
    RapidP Preprocessor
    Handles $INCLUDE, $DEFINE, $UNDEF, $IFDEF, $IFNDEF, $ELSE, $ENDIF
    Performs macro text-substitution for $DEFINEs.
    """
    if defines is None:
        defines = {}
    if include_stack is None:
        include_stack = []
    
    macros = {}  # name -> (params_list_or_None, body_text)
    lines = source_code.split('\n')
    output_lines = []
    
    skip_stack = [] # True if currently skipping lines
    line_num = 0
    
    for original_line in lines:
        line_num += 1
        line = original_line.strip()
        upper_line = line.upper()
        
        # Handle conditional compilation
        if upper_line.startswith('$IFDEF'):
            parts = line.split(maxsplit=1)
            if len(parts) > 1:
                # Remove inline comments via split("'")
                symbol = parts[1].split("'")[0].strip()
                should_skip = (symbol not in defines)
                if skip_stack and skip_stack[-1]:
                    skip_stack.append(True)
                else:
                    skip_stack.append(should_skip)
            output_lines.append("") # Preserve line numbers
            continue
            
        elif upper_line.startswith('$IFNDEF'):
            parts = line.split(maxsplit=1)
            if len(parts) > 1:
                symbol = parts[1].split("'")[0].strip()
                should_skip = (symbol in defines)
                if skip_stack and skip_stack[-1]:
                    skip_stack.append(True)
                else:
                    skip_stack.append(should_skip)
            output_lines.append("")
            continue
            
        elif upper_line.startswith('$ELSE'):
            if skip_stack:
                parent_skip = skip_stack[-2] if len(skip_stack) > 1 else False
                if not parent_skip:
                    skip_stack[-1] = not skip_stack[-1]
            output_lines.append("")
            continue
            
        elif upper_line.startswith('$ENDIF'):
            if skip_stack:
                skip_stack.pop()
            output_lines.append("")
            continue
            
        if skip_stack and skip_stack[-1]:
            output_lines.append("")
            continue
            
        # Handle Defines
        if upper_line.startswith('$DEFINE'):
            parts = line.split()
            if len(parts) >= 2:
                symbol = parts[1]
                val_part = " ".join(parts[2:]) if len(parts) > 2 else "1"
                val_part = val_part.split("'")[0].strip()
                defines[symbol] = val_part
            output_lines.append("")
            continue
            
        if upper_line.startswith('$UNDEF'):
            parts = line.split()
            if len(parts) >= 2:
                symbol = parts[1]
                defines.pop(symbol, None)
            output_lines.append("")
            continue

        # Handle $MACRO name[(params)] = body
        if upper_line.startswith('$MACRO'):
            macro_match = re.match(r'\$MACRO\s+(\w+)(?:\(([^)]*)\))?\s*=\s*(.*)', line, re.IGNORECASE)
            if macro_match:
                mname = macro_match.group(1)
                mparams = [p.strip() for p in macro_match.group(2).split(',')] if macro_match.group(2) else None
                mbody = macro_match.group(3).split("'")[0].strip()
                macros[mname] = (mparams, mbody)
            output_lines.append("")
            continue

        # Handle $APPTYPE, $OPTIMIZE, $ESCAPECHARS — pass through as directives for codegen
        if upper_line.startswith(('$APPTYPE', '$OPTIMIZE', '$ESCAPECHARS')):
            output_lines.append(original_line)
            continue
            
        # Handle Includes
        if upper_line.startswith('$INCLUDE'):
            match = re.search(r'["<](.*?)[">]', line)
            if match:
                inc_file = match.group(1)
                inc_path = os.path.join(base_dir, inc_file)
                if not os.path.exists(inc_path):
                    inc_path = os.path.join(os.getcwd(), inc_file)
                    
                if os.path.exists(inc_path):
                    if inc_path not in include_stack:
                        include_stack.append(inc_path)
                        try:
                            with open(inc_path, 'r', encoding='utf-8', errors='replace') as f:
                                inc_source = f.read()
                            inc_output = preprocess(inc_source, os.path.dirname(inc_path), defines, include_stack, file_path=inc_path)
                            output_lines.append(inc_output)
                        except RapidPCompileError:
                            raise
                        except Exception as e:
                            raise RapidPCompileError(
                                f"Failed to include '{inc_file}': {e}",
                                line=line_num, column=1, file_path=file_path
                            )
                        include_stack.pop()
                    else:
                        raise RapidPCompileError(
                            f"Recursive include detected: '{inc_file}'",
                            line=line_num, column=1, file_path=file_path
                        )
                else:
                    raise RapidPCompileError(
                        f"Include file not found: '{inc_file}'",
                        line=line_num, column=1, file_path=file_path
                    )
            else:
                raise RapidPCompileError(
                    f"Invalid $INCLUDE syntax: {line}",
                    line=line_num, column=1, file_path=file_path
                )
            continue
            
        # Text Macro Substitution
        processed_line = original_line
        
        # Expand $MACROs first
        if macros:
            for mname, (mparams, mbody) in macros.items():
                if mname in processed_line:
                    if mparams:
                        # Parameterized macro: NAME(arg1, arg2)
                        pattern = re.compile(r'\b' + re.escape(mname) + r'\(([^)]*)\)')
                        match = pattern.search(processed_line)
                        while match:
                            args = [a.strip() for a in match.group(1).split(',')]
                            expanded = mbody
                            for i, p in enumerate(mparams):
                                if i < builtins.len(args):
                                    expanded = expanded.replace(p, args[i])
                            processed_line = processed_line[:match.start()] + expanded + processed_line[match.end():]
                            match = pattern.search(processed_line)
                    else:
                        # Simple macro substitution
                        processed_line = re.sub(r'\b' + re.escape(mname) + r'\b', mbody, processed_line)

        # Extract quoted strings to avoid substituting inside strings
        # A simple approach: split by '"', only substitute in even indices (0, 2, 4...)
        if defines and '$' not in upper_line: # Tiny optimization since $DEFINE directives are handled
            parts = processed_line.split('"')
            sorted_defines = sorted(defines.items(), key=lambda x: len(x[0]), reverse=True)
            for i in range(0, len(parts), 2):
                seg = parts[i]
                for sym, val in sorted_defines:
                    if sym in seg:
                        # Only whole words
                        seg = re.sub(r'\b' + re.escape(sym) + r'\b', val, seg)
                parts[i] = seg
            processed_line = '"'.join(parts)
            
        output_lines.append(processed_line)
        
    return "\n".join(output_lines)
