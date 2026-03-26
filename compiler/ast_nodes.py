from dataclasses import dataclass
from typing import List, Optional, Any, Union

@dataclass
class ASTNode:
    line: int
    column: int

# --- Program Structure ---

@dataclass
class ProgramNode(ASTNode):
    statements: List[ASTNode]

# --- Expressions ---

@dataclass
class ExpressionNode(ASTNode):
    pass

@dataclass
class IdentifierNode(ExpressionNode):
    name: str

@dataclass
class LiteralNode(ExpressionNode):
    value: Any
    type_name: str # e.g., 'INTEGER', 'STRING', 'DOUBLE'

@dataclass
class BinaryOpNode(ExpressionNode):
    left: ExpressionNode
    op: str # '+', '-', '*', '/', \', '^', '=', '<>', '<', '>', '<=', '>=', 'AND', 'OR', 'NOT'
    right: ExpressionNode

@dataclass
class UnaryOpNode(ExpressionNode):
    op: str # '+', '-', 'NOT'
    operand: ExpressionNode

@dataclass
class ArrayAccessNode(ExpressionNode):
    array: ExpressionNode
    index: ExpressionNode

@dataclass
class MemberAccessNode(ExpressionNode):
    obj: ExpressionNode
    member: str

@dataclass
class FunctionCallNode(ExpressionNode):
    name: str
    args: List[ExpressionNode]

@dataclass
class MethodCallNode(ExpressionNode):
    obj: ExpressionNode
    method: str
    args: List[ExpressionNode]

# --- Statements ---

@dataclass
class StatementNode(ASTNode):
    pass

@dataclass
class MethodCallStatementNode(StatementNode):
    method_call: MethodCallNode

@dataclass
class DimStatementNode(StatementNode):
    # Variables can now be tuples of (name, array_size) where array_size is an ExpressionNode or None
    variables: List[tuple]
    var_type: str

@dataclass
class AssignmentNode(StatementNode):
    target: ExpressionNode
    value: ExpressionNode

@dataclass
class IfStatementNode(StatementNode):
    condition: ExpressionNode
    then_branch: List[StatementNode]
    elseif_branches: List[tuple[ExpressionNode, List[StatementNode]]] # List of (condition, branch)
    else_branch: Optional[List[StatementNode]]

@dataclass
class ForStatementNode(StatementNode):
    variable: str
    start: ExpressionNode
    end: ExpressionNode
    step: Optional[ExpressionNode]
    body: List[StatementNode]

@dataclass
class WhileStatementNode(StatementNode):
    condition: ExpressionNode
    body: List[StatementNode]

@dataclass
class DoLoopStatementNode(StatementNode):
    condition: Optional[ExpressionNode]
    pre_condition: bool # True for DO WHILE ..., False for DO ... LOOP UNTIL
    is_until: bool # Uses UNTIL instead of WHILE
    body: List[StatementNode]

@dataclass
class SelectCaseStatementNode(StatementNode):
    expression: ExpressionNode
    cases: List[tuple[List[ExpressionNode], List[StatementNode]]] # List of (values, branch). e.g CASE 1, 2
    case_else: Optional[List[StatementNode]]

@dataclass
class PrintStatementNode(StatementNode):
    items: List[ExpressionNode]
    append_newline: bool

@dataclass
class SubroutineDefNode(StatementNode):
    name: str
    params: List[tuple[str, str]] # List of (name, type)
    body: List[StatementNode]

@dataclass
class FunctionDefNode(StatementNode):
    name: str
    params: List[tuple[str, str]]
    return_type: str
    body: List[StatementNode]

@dataclass
class CallStatementNode(StatementNode):
    name: str
    args: List[ExpressionNode]

@dataclass
class ImportStatementNode(StatementNode):
    module_name: str
    alias: Optional[str]

@dataclass
class WithStatementNode(StatementNode):
    obj: ExpressionNode
    body: List[StatementNode]

@dataclass
class ReturnStatementNode(StatementNode):
    value: Optional[ExpressionNode]

@dataclass
class ExitStatementNode(StatementNode):
    exit_type: str # 'SUB', 'FUNCTION', 'FOR', 'WHILE', 'DO'

@dataclass
class DirectiveNode(StatementNode):
    name: str
    value: str

@dataclass
class ConstStatementNode(StatementNode):
    name: str
    value: ExpressionNode

@dataclass
class DeclareStatementNode(StatementNode):
    name: str
    lib: str
    alias: str
    params: List[tuple]
    return_type: str = "VARIANT"

@dataclass
class TypeStatementNode(StatementNode):
    name: str
    fields: List[tuple] # (field_name, field_type, array_size)
    methods: List[StatementNode] = None # Actually we'll just initialize it as [] in parser
    constructor: List[StatementNode] = None
    extends: Optional[str] = None

@dataclass
class BindStatementNode(StatementNode):
    target: ExpressionNode
    function: ExpressionNode

@dataclass
class CreateStatementNode(StatementNode):
    name: str
    obj_type: str
    body: List[StatementNode]
