from typing import List, Optional
from .lexer import Token, TokenType
from .ast_nodes import *
from .errors import RapidPSyntaxError

class Parser:
    """Recursive descent parser for RapidP Basic."""

    def __init__(self, tokens: List[Token], file_path: str = None):
        self.tokens = tokens
        self.pos = 0
        self.file_path = file_path
        self.with_stack: List[ExpressionNode] = []

    def parse(self) -> ProgramNode:
        statements = []
        while not self.is_at_end():
            if self.match(TokenType.NEWLINE, TokenType.COLON):
                continue
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return ProgramNode(line=1, column=1, statements=statements)

    # --- Helper Methods ---

    def peek(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]

    def previous(self) -> Token:
        return self.tokens[self.pos - 1]

    def is_at_end(self) -> bool:
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def match(self, *types: TokenType) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def advance(self) -> Token:
        if not self.is_at_end():
            self.pos += 1
        return self.previous()

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> RapidPSyntaxError:
        return RapidPSyntaxError(
            message=f"Unexpected '{token.value}': {message}",
            line=token.line,
            column=token.column,
            file_path=self.file_path
        )

    def skip_newlines(self):
        while self.match(TokenType.NEWLINE, TokenType.COLON):
            pass

    def require_newline_or_colon(self):
        if self.is_at_end(): return
        if not self.match(TokenType.NEWLINE, TokenType.COLON):
            raise self.error(self.peek(), "Expected newline or ':' after statement")

    # --- Statements ---

    def parse_statement(self) -> Optional[StatementNode]:
        if self.match(TokenType.DIM):
            return self.parse_dim_statement()
        if self.match(TokenType.PRINT):
            return self.parse_print_statement()
        if self.match(TokenType.IF):
            return self.parse_if_statement()
        if self.match(TokenType.FOR):
            return self.parse_for_statement()
        if self.match(TokenType.WHILE):
            return self.parse_while_statement()
        if self.match(TokenType.DO):
            return self.parse_do_statement()
        if self.match(TokenType.SELECT):
            return self.parse_select_statement()
        if self.match(TokenType.SUB):
            return self.parse_sub_statement()
        if self.match(TokenType.FUNCTION):
            return self.parse_function_statement()
        if self.match(TokenType.DECLARE):
            return self.parse_declare_statement()
        if self.match(TokenType.CALL):
            return self.parse_call_statement()
        if self.match(TokenType.RETURN):
            return self.parse_return_statement()
        if self.match(TokenType.EXIT):
            return self.parse_exit_statement()
        if self.match(TokenType.IMPORT):
            return self.parse_import_statement()
        if self.match(TokenType.CONST):
            return self.parse_const_statement()
        if self.match(TokenType.TYPE):
            return self.parse_type_def_statement()
        if self.match(TokenType.WITH):
            return self.parse_with_statement()
        if self.match(TokenType.CREATE):
            return self.parse_create_statement()
        # Directives
        if self.match(TokenType.DIRECTIVE):
            return DirectiveNode(
                line=self.previous().line, column=self.previous().column,
                name=self.previous().value, value="" # TODO extract directive values
            )
            
        # DEF inline declarations
        if self.match(TokenType.DEFSTR, TokenType.DEFINT, TokenType.DEFBYTE, TokenType.DEFWORD,
                      TokenType.DEFDWORD, TokenType.DEFLONG, TokenType.DEFSNG, TokenType.DEFDBL, TokenType.DEFCUR):
            self.consume(TokenType.IDENTIFIER, "Expected identifier after DEF type")
            return self.parse_assignment_or_call()
            
        if self.match(TokenType.BIND):
            return self.parse_bind_statement()
            
        # Assignments or Function/Sub calls
        if self.match(TokenType.IDENTIFIER, TokenType.DOT):
            return self.parse_assignment_or_call()

        # Unknown token, we skip or error out.
        # For now, we raise a generic syntax error for unresolved tokens
        raise self.error(self.peek(), "Expected a statement")

    def parse_dim_statement(self) -> DimStatementNode:
        line, col = self.previous().line, self.previous().column
        variables = []
        
        # DIM var1, var2 AS Type
        # OR DIM var1(10), var2(1 TO 10) AS Type
        while True:
            name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
            array_size = None
            if self.match(TokenType.LPAREN):
                # Simple parsing for array size: DIM A(10) or DIM A(1 TO 10). We just parse expression(s)
                # Actually RapidP accepts DIM A(10, 20) for 2D arrays.
                # Let's just store the size tuple.
                dims = [self.parse_expression()]
                # TO keyword if it's 1 TO 10
                if self.match(TokenType.TO):
                    to_expr = self.parse_expression()
                    dims.append(to_expr) # Store as (start, end)
                else:
                    while self.match(TokenType.COMMA):
                        dims.append(self.parse_expression())
                self.consume(TokenType.RPAREN, "Expected ')' after array dimensions")
                array_size = dims
                
            variables.append((name, array_size))
            if not self.match(TokenType.COMMA):
                break
                
        self.consume(TokenType.AS, "Expected 'AS' after variable list")
        
        var_type = self.parse_type()
            
        self.require_newline_or_colon()
        return DimStatementNode(line=line, column=col, variables=variables, var_type=var_type)

    def parse_bind_statement(self) -> BindStatementNode:
        line, col = self.previous().line, self.previous().column
        target = self.parse_expression()
        self.consume(TokenType.TO, "Expected 'TO' in BIND statement")
        function = self.parse_expression()
        self.require_newline_or_colon()
        return BindStatementNode(line=line, column=col, target=target, function=function)

    def parse_print_statement(self) -> PrintStatementNode:
        line, col = self.previous().line, self.previous().column
        items = []
        append_newline = True
        
        if not self.check(TokenType.NEWLINE) and not self.check(TokenType.COLON) and not self.check(TokenType.EOF):
            items.append(self.parse_expression())
            while self.match(TokenType.COMMA, TokenType.SEMI):
                if self.check(TokenType.NEWLINE) or self.check(TokenType.COLON) or self.check(TokenType.EOF):
                    append_newline = self.previous().type != TokenType.SEMI
                    break
                items.append(self.parse_expression())

        self.require_newline_or_colon()
        return PrintStatementNode(line=line, column=col, items=items, append_newline=append_newline)

    def parse_if_statement(self) -> IfStatementNode:
        line, col = self.previous().line, self.previous().column
        condition = self.parse_expression()
        self.consume(TokenType.THEN, "Expected 'THEN' after IF condition")
        
        # Depending on if there is a block or single line statement
        if self.match(TokenType.NEWLINE, TokenType.COLON):
            # Block IF
            then_branch = self.parse_block([TokenType.ELSE, TokenType.ELSEIF, TokenType.END])
            elseif_branches = []
            else_branch = None
            
            while self.match(TokenType.ELSEIF):
                ei_cond = self.parse_expression()
                self.consume(TokenType.THEN, "Expected 'THEN' after ELSEIF condition")
                self.skip_newlines()
                ei_branch = self.parse_block([TokenType.ELSE, TokenType.ELSEIF, TokenType.END])
                elseif_branches.append((ei_cond, ei_branch))
                
            if self.match(TokenType.ELSE):
                self.skip_newlines()
                else_branch = self.parse_block([TokenType.END])
                
            self.consume(TokenType.END, "Expected 'END IF' to terminate IF block")
            if self.match(TokenType.IF): # END IF
                pass 
            self.require_newline_or_colon()
                
        else:
            # Single line IF — parse all colon-separated statements until newline
            stmt = self.parse_statement()
            then_branch = [stmt] if stmt else []
            # parse_statement calls require_newline_or_colon() which consumes
            # either a NEWLINE or COLON. If a COLON was consumed, there are more
            # statements on this line that belong to the THEN branch.
            # Check previous() to see what was consumed:
            while not self.is_at_end() and self.previous().type == TokenType.COLON and not self.check(TokenType.ELSE):
                s = self.parse_statement()
                if s:
                    then_branch.append(s)
            elseif_branches = []
            else_branch = None
            if self.match(TokenType.ELSE):
                else_stmts = []
                es = self.parse_statement()
                if es:
                    else_stmts.append(es)
                while not self.is_at_end() and self.previous().type == TokenType.COLON:
                    s2 = self.parse_statement()
                    if s2:
                        else_stmts.append(s2)
                else_branch = else_stmts if else_stmts else None
            
        return IfStatementNode(line=line, column=col, condition=condition, then_branch=then_branch, elseif_branches=elseif_branches, else_branch=else_branch)

    def parse_for_statement(self) -> ForStatementNode:
        line, col = self.previous().line, self.previous().column
        var_name = self.consume(TokenType.IDENTIFIER, "Expected variable name in FOR loop").value
        self.consume(TokenType.EQ, "Expected '=' after variable in FOR loop")
        start_expr = self.parse_expression()
        self.consume(TokenType.TO, "Expected 'TO' in FOR loop")
        end_expr = self.parse_expression()
        
        step_expr = None
        if self.match(TokenType.STEP):
            step_expr = self.parse_expression()
            
        self.require_newline_or_colon()
        
        body = self.parse_block([TokenType.NEXT])
        self.consume(TokenType.NEXT, "Expected 'NEXT' to close FOR loop")
        self.match(TokenType.IDENTIFIER) # Optional variable name after NEXT
        
        self.require_newline_or_colon()
        return ForStatementNode(line=line, column=col, variable=var_name, start=start_expr, end=end_expr, step=step_expr, body=body)

    def parse_while_statement(self) -> WhileStatementNode:
        line, col = self.previous().line, self.previous().column
        condition = self.parse_expression()
        self.require_newline_or_colon()
        
        body = self.parse_block([TokenType.WEND])
        self.consume(TokenType.WEND, "Expected 'WEND' to close WHILE loop")
        
        self.require_newline_or_colon()
        return WhileStatementNode(line=line, column=col, condition=condition, body=body)

    def parse_do_statement(self) -> DoLoopStatementNode:
        line, col = self.previous().line, self.previous().column
        condition = None
        pre_condition = False
        is_until = False
        
        if self.match(TokenType.WHILE):
            condition = self.parse_expression()
            pre_condition = True
        elif self.match(TokenType.UNTIL):
            condition = self.parse_expression()
            pre_condition = True
            is_until = True
            
        self.require_newline_or_colon()
        
        body = self.parse_block([TokenType.LOOP])
        self.consume(TokenType.LOOP, "Expected 'LOOP' to close DO block")
        
        if not pre_condition:
            if self.match(TokenType.WHILE):
                condition = self.parse_expression()
            elif self.match(TokenType.UNTIL):
                condition = self.parse_expression()
                is_until = True
                
        self.require_newline_or_colon()
        return DoLoopStatementNode(line=line, column=col, condition=condition, pre_condition=pre_condition, is_until=is_until, body=body)

    def parse_select_statement(self) -> SelectCaseStatementNode:
        line, col = self.previous().line, self.previous().column
        self.consume(TokenType.CASE, "Expected 'CASE' after SELECT")
        expr = self.parse_expression()
        self.require_newline_or_colon()
        
        cases = []
        case_else = None
        
        self.skip_newlines()
        while self.match(TokenType.CASE):
            if self.match(TokenType.ELSE):
                self.require_newline_or_colon()
                case_else = self.parse_block([TokenType.END, TokenType.CASE])
                break
            else:
                values = [self.parse_expression()]
                while self.match(TokenType.COMMA):
                    values.append(self.parse_expression())
                self.require_newline_or_colon()
                branch = self.parse_block([TokenType.END, TokenType.CASE])
                cases.append((values, branch))
                
        if self.check(TokenType.END):
            self.consume(TokenType.END, "Expected 'END SELECT'")
            self.consume(TokenType.SELECT, "Expected 'END SELECT'")
            self.require_newline_or_colon()
            
        return SelectCaseStatementNode(line=line, column=col, expression=expr, cases=cases, case_else=case_else)

    def parse_sub_statement(self) -> SubroutineDefNode:
        line, col = self.previous().line, self.previous().column
        name = self.consume(TokenType.IDENTIFIER, "Expected subroutine name").value
        params = self.parse_parameters()
        self.require_newline_or_colon()
        
        body = self.parse_block([TokenType.END])
        self.consume(TokenType.END, "Expected 'END SUB'")
        self.consume(TokenType.SUB, "Expected 'END SUB'")
        self.require_newline_or_colon()
        return SubroutineDefNode(line=line, column=col, name=name, params=params, body=body)

    def parse_function_statement(self) -> FunctionDefNode:
        line, col = self.previous().line, self.previous().column
        name = self.consume(TokenType.IDENTIFIER, "Expected function name").value
        params = self.parse_parameters()
        
        return_type = 'VARIANT'
        if self.match(TokenType.AS):
            return_type = self.parse_type()
            
        self.require_newline_or_colon()
        
        body = self.parse_block([TokenType.END])
        self.consume(TokenType.END, "Expected 'END FUNCTION'")
        self.consume(TokenType.FUNCTION, "Expected 'END FUNCTION'")
        self.require_newline_or_colon()
        return FunctionDefNode(line=line, column=col, name=name, params=params, return_type=return_type, body=body)

    def parse_declare_statement(self) -> DeclareStatementNode:
        line, col = self.previous().line, self.previous().column
        # DECLARE SUB name LIB "lib" ALIAS "alias" (params)
        is_func = False
        if self.match(TokenType.SUB):
             is_func = False
        elif self.match(TokenType.FUNCTION):
             is_func = True
        else:
             raise self.error(self.peek(), "Expected SUB or FUNCTION in DECLARE statement")
             
        name = self.consume(TokenType.IDENTIFIER, "Expected function/sub name in DECLARE").value
        
        lib_name = ""
        if self.match(TokenType.LIB):
             lib_name = self.consume(TokenType.STRING_LIT, "Expected string literal for LIB").value
             
        alias_name = name
        if self.match(TokenType.ALIAS):
             alias_name = self.consume(TokenType.STRING_LIT, "Expected string literal for ALIAS").value
             
        params = []
        # RapidP params might be optional in DECLARE if there are empty parens
        if self.check(TokenType.LPAREN):
            params = self.parse_parameters()
            
        return_type = "VARIANT"
        if is_func and self.match(TokenType.AS):
             return_type = self.parse_type()
             
        self.require_newline_or_colon()
        return DeclareStatementNode(line=line, column=col, name=name, lib=lib_name, alias=alias_name, params=params, return_type=return_type)

    def parse_parameters(self) -> List[tuple[str, str]]:
        params = []
        if self.match(TokenType.LPAREN):
            if not self.check(TokenType.RPAREN):
                while True:
                    if self.match(TokenType.BYVAL, TokenType.BYREF):
                        pass # Ignore/skip the byval/byref keywords for python transpilation
                        
                    p_name = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
                    p_type = 'VARIANT'
                    if self.match(TokenType.AS):
                        p_type = self.parse_type()
                    params.append((p_name, p_type))
                    if not self.match(TokenType.COMMA): break
            self.consume(TokenType.RPAREN, "Expected ')' after parameters")
        return params

    def parse_type(self) -> str:
        types = [
            TokenType.INTEGER, TokenType.STRING, TokenType.DOUBLE, TokenType.SINGLE,
            TokenType.BYTE, TokenType.WORD, TokenType.DWORD, TokenType.LONG, 
            TokenType.INT64, TokenType.CURRENCY, TokenType.POBJECT, TokenType.IDENTIFIER
        ]
        if self.match(*types):
            type_name = self.previous().value.upper()
            if type_name == "EVENT":
                if self.match(TokenType.LPAREN):
                    self.consume(TokenType.IDENTIFIER, "Expected event template name")
                    self.consume(TokenType.RPAREN, "Expected ')'")
            return type_name
            
        raise self.error(self.peek(), "Expected a valid type")

    def parse_call_statement(self) -> CallStatementNode:
        line, col = self.previous().line, self.previous().column
        name = self.consume(TokenType.IDENTIFIER, "Expected subroutine name").value
        args = []
        if not self.check(TokenType.NEWLINE) and not self.check(TokenType.COLON) and not self.check(TokenType.EOF):
            args.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                args.append(self.parse_expression())
        self.require_newline_or_colon()
        return CallStatementNode(line=line, column=col, name=name, args=args)
        
    def parse_return_statement(self) -> ReturnStatementNode:
        line, col = self.previous().line, self.previous().column
        val = None
        if not self.check(TokenType.NEWLINE) and not self.check(TokenType.COLON) and not self.check(TokenType.EOF):
            val = self.parse_expression()
        self.require_newline_or_colon()
        return ReturnStatementNode(line=line, column=col, value=val)

    def parse_exit_statement(self) -> ExitStatementNode:
        line, col = self.previous().line, self.previous().column
        exit_type = ""
        if self.match(TokenType.FOR, TokenType.WHILE, TokenType.DO, TokenType.SUB, TokenType.FUNCTION):
            exit_type = self.previous().value.upper()
        self.require_newline_or_colon()
        return ExitStatementNode(line=line, column=col, exit_type=exit_type)
        
    def parse_const_statement(self) -> ConstStatementNode:
        line, col = self.previous().line, self.previous().column
        name = self.consume(TokenType.IDENTIFIER, "Expected constant name").value
        
        # Optional type definition `AS LONG` etc.
        if self.match(TokenType.AS):
            self.advance() # skip the type specifier (can be IDENTIFIER or keyword like LONG)
                
        self.consume(TokenType.EQ, "Expected '=' in CONST statement")
        value = self.parse_expression()
        self.require_newline_or_colon()
        return ConstStatementNode(line=line, column=col, name=name, value=value)

    def parse_type_def_statement(self) -> TypeStatementNode:
        line, col = self.previous().line, self.previous().column
        name = self.consume(TokenType.IDENTIFIER, "Expected type name").value
        
        extends_name = None
        if self.match(TokenType.EXTENDS):
            if self.match(TokenType.IDENTIFIER, TokenType.POBJECT):
                extends_name = self.previous().value
            else:
                self.error(self.peek(), "Expected base type name after EXTENDS")
                
        self.require_newline_or_colon()
        
        fields = []
        methods = []
        constructor_stmts = []
        while not self.is_at_end():
            if self.check(TokenType.END):
                break
            if self.match(TokenType.NEWLINE, TokenType.COLON):
                continue
                
            if self.match(TokenType.CONSTRUCTOR):
                self.require_newline_or_colon()
                constructor_stmts = self.parse_block([TokenType.END])
                self.consume(TokenType.END, "Expected 'END CONSTRUCTOR'")
                if self.match(TokenType.CONSTRUCTOR):
                    pass
                self.require_newline_or_colon()
                continue
                
            if self.match(TokenType.SUB):
                methods.append(self.parse_sub_statement())
                continue
                
            if self.match(TokenType.FUNCTION):
                methods.append(self.parse_function_statement())
                continue
                
            field_name = self.consume(TokenType.IDENTIFIER, "Expected field name in TYPE block").value
            
            if field_name.upper() in ["PRIVATE", "PUBLIC"]:
                self.match(TokenType.COLON)
                continue
                
            array_size = None
            if self.match(TokenType.LPAREN):
                 dims = [self.parse_expression()]
                 if self.match(TokenType.TO):
                     dims.append(self.parse_expression())
                 else:
                     while self.match(TokenType.COMMA):
                         dims.append(self.parse_expression())
                 self.consume(TokenType.RPAREN, "Expected ')' after array dimensions in TYPE")
                 array_size = dims
                 
            self.consume(TokenType.AS, "Expected 'AS' after field name")
            field_type = self.parse_type()
            
            # Optional property mutator: PROPERTY set <method_name>
            property_setter = None
            if self.match(TokenType.PROPERTY):
                self.consume(TokenType.SET, "Expected SET after PROPERTY")
                property_setter = self.consume(TokenType.IDENTIFIER, "Expected setter logic method name").value
                
            fields.append((field_name, field_type, array_size))
            self.require_newline_or_colon()
            
        self.consume(TokenType.END, "Expected 'END TYPE'")
        if self.match(TokenType.TYPE):
            pass
        self.require_newline_or_colon()
        return TypeStatementNode(line=line, column=col, name=name, fields=fields, methods=methods, constructor=constructor_stmts, extends=extends_name)
        
        return TypeStatementNode(line=line, column=col, name=name, fields=fields)

    def parse_with_statement(self) -> WithStatementNode:
        line, col = self.previous().line, self.previous().column
        obj = self.parse_expression()
        self.require_newline_or_colon()
        
        self.with_stack.append(obj)
        body = self.parse_block([TokenType.END])
        self.with_stack.pop()
        
        self.consume(TokenType.END, "Expected 'END WITH'")
        self.consume(TokenType.WITH, "Expected 'WITH' after 'END'")
        self.require_newline_or_colon()
        
        return WithStatementNode(line=line, column=col, obj=obj, body=body)

    def parse_create_statement(self) -> CreateStatementNode:
        line, col = self.previous().line, self.previous().column
        name = self.consume(TokenType.IDENTIFIER, "Expected object name in CREATE").value
        self.consume(TokenType.AS, "Expected 'AS' in CREATE statement")
        
        obj_type = self.consume(TokenType.IDENTIFIER, "Expected object type").value.upper()
        self.require_newline_or_colon()
        
        body = self.parse_block([TokenType.END])
        self.consume(TokenType.END, "Expected 'END CREATE'")
        self.consume(TokenType.CREATE, "Expected 'END CREATE'")
        self.require_newline_or_colon()
        
        return CreateStatementNode(line=line, column=col, name=name, obj_type=obj_type, body=body)

    def parse_import_statement(self) -> ImportStatementNode:
        # RapidP-Python bridge syntax: $IMPORT "numpy" AS np OR IMPORT numpy AS np
        line, col = self.previous().line, self.previous().column
        
        # We allow module as string or identifier
        if self.match(TokenType.STRING_LIT, TokenType.IDENTIFIER):
            module_name = self.previous().value
        else:
            raise self.error(self.peek(), "Expected module name to import")
            
        alias = None
        if self.match(TokenType.AS):
            alias = self.consume(TokenType.IDENTIFIER, "Expected alias after AS").value
            
        self.require_newline_or_colon()
        return ImportStatementNode(line=line, column=col, module_name=module_name, alias=alias)

    def parse_assignment_or_call(self) -> StatementNode:
        line, col = self.previous().line, self.previous().column
        
        if self.previous().type == TokenType.DOT:
            if not getattr(self, 'with_stack', None):
                raise self.error(self.previous(), "'.' without WITH context")
            name = self.consume(TokenType.IDENTIFIER, "Expected property name after '.'").value
            left_expr = MemberAccessNode(line=line, column=col, obj=self.with_stack[-1], member=name)
        else:
            name = self.previous().value
            left_expr = IdentifierNode(line=line, column=col, name=name)
            
            if self.match(TokenType.LPAREN):
                args = []
                if not self.check(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.parse_expression())
                self.consume(TokenType.RPAREN, "Expected ')' after Array indices")
                left_expr = ArrayAccessNode(line=line, column=col, array=left_expr, index=args[0] if len(args)==1 else args)
            
        while self.match(TokenType.DOT):
            member = self.consume(TokenType.IDENTIFIER, "Expected property name").value
            left_expr = MemberAccessNode(line=left_expr.line, column=left_expr.column, obj=left_expr, member=member)
            if self.match(TokenType.LPAREN):
                args = []
                if not self.check(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.parse_expression())
                self.consume(TokenType.RPAREN, "Expected ')' after Array indices")
                left_expr = ArrayAccessNode(line=left_expr.line, column=left_expr.column, array=left_expr, index=args[0] if len(args)==1 else args)
                
        if self.match(TokenType.EQ):
            value = self.parse_expression()
            self.require_newline_or_colon()
            return AssignmentNode(line=line, column=col, target=left_expr, value=value)
        else:
            args = []
            is_end = self.check(TokenType.NEWLINE) or self.check(TokenType.COLON) or self.is_at_end()
            if not is_end:
                if self.match(TokenType.LPAREN):
                    if not self.check(TokenType.RPAREN):
                        args.append(self.parse_expression())
                        while self.match(TokenType.COMMA):
                            args.append(self.parse_expression())
                    self.consume(TokenType.RPAREN, "Expected ')' after arguments")
                else:
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.parse_expression())
                        
            self.require_newline_or_colon()
            
            if isinstance(left_expr, MemberAccessNode):
                method_node = MethodCallNode(line=line, column=col, obj=left_expr.obj, method=left_expr.member, args=args)
                return MethodCallStatementNode(line=line, column=col, method_call=method_node)
            elif isinstance(left_expr, ArrayAccessNode) and isinstance(left_expr.array, MemberAccessNode):
                method_args = left_expr.index if isinstance(left_expr.index, list) else [left_expr.index]
                if not method_args or (len(method_args) == 1 and method_args[0] is None):
                     method_args = []
                method_node = MethodCallNode(line=line, column=col, obj=left_expr.array.obj, method=left_expr.array.member, args=method_args)
                return MethodCallStatementNode(line=line, column=col, method_call=method_node)
            elif isinstance(left_expr, ArrayAccessNode) and isinstance(left_expr.array, IdentifierNode):
                call_args = left_expr.index if isinstance(left_expr.index, list) else [left_expr.index]
                if not call_args or (len(call_args) == 1 and call_args[0] is None):
                     call_args = []
                return CallStatementNode(line=line, column=col, name=left_expr.array.name, args=call_args)
                
            return CallStatementNode(line=line, column=col, name=name, args=args)

    def parse_block(self, end_tokens: List[TokenType]) -> List[StatementNode]:
        statements = []
        while not self.is_at_end():
            # Check if we hit any of the end tokens
            if self.peek().type in end_tokens:
                break
            if self.match(TokenType.NEWLINE, TokenType.COLON):
                continue
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements

    # --- Expressions (Pratt-Style / Recursive Descent) ---

    def parse_expression(self) -> ExpressionNode:
        return self.parse_logical_or()

    def parse_logical_or(self) -> ExpressionNode:
        expr = self.parse_logical_and()
        while self.match(TokenType.OR, TokenType.XOR):
            op = self.previous()
            right = self.parse_logical_and()
            expr = BinaryOpNode(line=expr.line, column=expr.column, left=expr, op=op.value, right=right)
        return expr

    def parse_logical_and(self) -> ExpressionNode:
        expr = self.parse_equality()
        while self.match(TokenType.AND):
            op = self.previous()
            right = self.parse_equality()
            expr = BinaryOpNode(line=expr.line, column=expr.column, left=expr, op=op.value, right=right)
        return expr

    def parse_equality(self) -> ExpressionNode:
        expr = self.parse_comparison()
        while self.match(TokenType.EQ, TokenType.NEQ):
            op = self.previous()
            right = self.parse_comparison()
            expr = BinaryOpNode(line=expr.line, column=expr.column, left=expr, op=op.value, right=right)
        return expr

    def parse_comparison(self) -> ExpressionNode:
        expr = self.parse_term()
        while self.match(TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE):
            op = self.previous()
            right = self.parse_term()
            expr = BinaryOpNode(line=expr.line, column=expr.column, left=expr, op=op.value, right=right)
        return expr

    def parse_term(self) -> ExpressionNode:
        expr = self.parse_factor()
        while self.match(TokenType.PLUS, TokenType.MINUS, TokenType.AMPERSAND):
            op_token = self.previous()
            operator = op_token.value
            if op_token.type == TokenType.AMPERSAND:
                operator = '+' # map rapidp string concat right to python + operator
            right = self.parse_factor()
            expr = BinaryOpNode(line=expr.line, column=expr.column, left=expr, op=operator, right=right)
        return expr

    def parse_factor(self) -> ExpressionNode:
        expr = self.parse_power()
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.BACKSLASH, TokenType.MOD):
            op = self.previous()
            right = self.parse_power()
            expr = BinaryOpNode(line=expr.line, column=expr.column, left=expr, op=op.value, right=right)
        return expr

    def parse_power(self) -> ExpressionNode:
        expr = self.parse_unary()
        while self.match(TokenType.CARET):
            op = self.previous()
            right = self.parse_unary()
            expr = BinaryOpNode(line=expr.line, column=expr.column, left=expr, op=op.value, right=right)
        return expr

    def parse_unary(self) -> ExpressionNode:
        if self.match(TokenType.NOT, TokenType.MINUS, TokenType.PLUS):
            op = self.previous()
            right = self.parse_unary()
            return UnaryOpNode(line=op.line, column=op.column, op=op.value, operand=right)
        return self.parse_primary()

    def parse_primary(self) -> ExpressionNode:
        if self.match(TokenType.DOT):
            if not getattr(self, 'with_stack', None):
                raise self.error(self.previous(), "'.' without WITH context")
            expr = self.with_stack[-1]
            member = self.consume(TokenType.IDENTIFIER, "Expected property or method name").value
            
            if self.match(TokenType.LPAREN):
                args = []
                if not self.check(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.parse_expression())
                self.consume(TokenType.RPAREN, "Expected ')' after method arguments")
                expr = MethodCallNode(line=self.previous().line, column=self.previous().column, obj=expr, method=member, args=args)
            else:
                expr = MemberAccessNode(line=self.previous().line, column=self.previous().column, obj=expr, member=member)
                
            # Allow chaining
            while self.match(TokenType.DOT):
                member2 = self.consume(TokenType.IDENTIFIER, "Expected property or method name").value
                if self.match(TokenType.LPAREN):
                    args = []
                    if not self.check(TokenType.RPAREN):
                        args.append(self.parse_expression())
                        while self.match(TokenType.COMMA):
                            args.append(self.parse_expression())
                    self.consume(TokenType.RPAREN, "Expected ')' after method arguments")
                    expr = MethodCallNode(line=self.previous().line, column=self.previous().column, obj=expr, method=member2, args=args)
                else:
                    expr = MemberAccessNode(line=self.previous().line, column=self.previous().column, obj=expr, member=member2)
            return expr

        if self.match(TokenType.NUMBER):
            val = self.previous().value
            num_type = 'DOUBLE' if '.' in val or 'e' in val.lower() else 'INTEGER'
            # Convert to actual python types, fallback to string if fails
            try:
                if num_type == 'DOUBLE': py_val = float(val)
                else: py_val = int(val)
            except ValueError:
                py_val = val
            return LiteralNode(line=self.previous().line, column=self.previous().column, value=py_val, type_name=num_type)
            
        if self.match(TokenType.STRING_LIT):
            return LiteralNode(line=self.previous().line, column=self.previous().column, value=self.previous().value, type_name='STRING')
            
        if self.match(TokenType.IDENTIFIER):
            name = self.previous().value
            expr = IdentifierNode(line=self.previous().line, column=self.previous().column, name=name)
            
            # Subroutine or Function call or Array Access as part of expression: foo() or foo(1)
            if self.match(TokenType.LPAREN):
                args = []
                if not self.check(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.parse_expression())
                self.consume(TokenType.RPAREN, "Expected ')' after arguments or indices")
                # At parse time it's ambiguous if A(1) is an array access or a function call returning a value.
                # We will build a FunctionCallNode, and Codegen will handle the translation. Or we can just 
                # default it to FunctionCallNode in AST and rename it later if symbol table says it's an array.
                # RapidP is a 1-pass compiler usually. For us, let's keep it as FunctionCallNode here.
                expr = FunctionCallNode(line=expr.line, column=expr.column, name=name, args=args)
                
            # Method or property access
            while self.match(TokenType.DOT):
                member = self.consume(TokenType.IDENTIFIER, "Expected property or method name").value
                
                # Check method call vs property access
                if self.match(TokenType.LPAREN):
                    args = []
                    if not self.check(TokenType.RPAREN):
                        args.append(self.parse_expression())
                        while self.match(TokenType.COMMA):
                            args.append(self.parse_expression())
                    self.consume(TokenType.RPAREN, "Expected ')' after method arguments")
                    expr = MethodCallNode(line=expr.line, column=expr.column, obj=expr, method=member, args=args)
                else:
                    expr = MemberAccessNode(line=expr.line, column=expr.column, obj=expr, member=member)
                    
            return expr
            
        if self.match(TokenType.LPAREN):
            op = self.previous()
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
            
        raise self.error(self.peek(), "Expected expression")
