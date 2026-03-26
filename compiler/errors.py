import json


class RapidPError(Exception):
    """Base exception for all RapidP compiler errors."""
    pass

class RapidPSyntaxError(RapidPError):
    """Exception raised for errors in syntax during lexing or parsing."""
    def __init__(self, message, line=None, column=None, file_path=None):
        self.message = message
        self.line = line
        self.column = column
        self.file_path = file_path
        
        err_msg = ""
        if file_path:
            err_msg += f"File \"{file_path}\", "
        if line is not None:
            err_msg += f"line {line}"
            if column is not None:
                err_msg += f":{column}"
            err_msg += " - "
            
        err_msg += f"Syntax Error: {message}"
        super().__init__(err_msg)

    def to_dict(self):
        return {"type": "syntax", "file": self.file_path or "", "line": self.line, "col": self.column, "message": self.message}

class RapidPCompileError(RapidPError):
    """Exception raised for semantic errors during compilation."""
    def __init__(self, message, line=None, column=None, file_path=None):
        self.message = message
        self.line = line
        self.column = column
        self.file_path = file_path
        
        err_msg = ""
        if file_path:
            err_msg += f"File \"{file_path}\", "
        if line is not None:
            err_msg += f"line {line}"
            if column is not None:
                err_msg += f":{column}"
            err_msg += " - "
            
        err_msg += f"Compile Error: {message}"
        super().__init__(err_msg)

    def to_dict(self):
        return {"type": "compile", "file": self.file_path or "", "line": self.line, "col": self.column, "message": self.message}

class RapidPWarning:
    """Non-fatal warning during compilation."""
    def __init__(self, message, line=None, column=None, file_path=None):
        self.message = message
        self.line = line
        self.column = column
        self.file_path = file_path

    def __str__(self):
        err_msg = ""
        if self.file_path:
            err_msg += f"File \"{self.file_path}\", "
        if self.line is not None:
            err_msg += f"line {self.line}"
            if self.column is not None:
                err_msg += f":{self.column}"
            err_msg += " - "
        err_msg += f"Warning: {self.message}"
        return err_msg

    def to_dict(self):
        return {"type": "warning", "file": self.file_path or "", "line": self.line, "col": self.column, "message": self.message}


class ErrorCollector:
    """Collects compile errors and warnings instead of raising on first one."""
    def __init__(self):
        self.errors = []
        self.warnings = []

    def add_error(self, message, line=None, column=None, file_path=None):
        self.errors.append(RapidPCompileError(message, line, column, file_path))

    def add_warning(self, message, line=None, column=None, file_path=None):
        self.warnings.append(RapidPWarning(message, line, column, file_path))

    @property
    def has_errors(self):
        return len(self.errors) > 0

    def to_json(self):
        items = [e.to_dict() for e in self.errors] + [w.to_dict() for w in self.warnings]
        return json.dumps(items)

    def format_text(self):
        lines = []
        for e in self.errors:
            lines.append(str(e))
        for w in self.warnings:
            lines.append(str(w))
        return "\n".join(lines)
