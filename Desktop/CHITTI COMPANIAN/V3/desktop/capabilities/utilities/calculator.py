import ast
import operator
from typing import List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.runtimes.presentation.models import PresentationModel, PresentationType, PresentationMetadata, PresentationCapability, PresentationLifetime


class CalculatorCapability(ICapability):
    """Provides safe mathematical evaluation using a restricted AST parser."""
    
    def __init__(self):
        self._state = ServiceState.STOPPED
        self._operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos
        }

    @property
    def name(self) -> str:
        return "CalculatorCapability"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> dict:
        return {"status": "healthy"}

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name="calculator",
            version="1.0",
            category="utilities",
            permissions=[],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="evaluate_expression", 
                description="Evaluate a mathematical expression (e.g. '2 + 3 * 5').", 
                parameters=[ToolParameter(name="expression", type="string", description="The math expression.", required=True)]
            )
        ]

    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name == "evaluate_expression" and "expression" in invocation.parameters

    def _eval_node(self, node):
        if isinstance(node, ast.Num): # <python3.8
            return node.n
        elif isinstance(node, ast.Constant): # >=python3.8
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant: {node.value}")
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op = self._operators.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op)}")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op = self._operators.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported unary operator: {type(node.op)}")
            return op(operand)
        else:
            raise ValueError(f"Unsupported syntax node: {type(node)}")

    def execute(self, *args, **kwargs) -> ExecutionResult:
        if args and hasattr(args[0], "tool_name"):
            invocation = args[0]
        else:
            action = kwargs.get("action")
            parameters = kwargs.get("parameters", {})
            invocation = ToolInvocation(tool_name=action, parameters=parameters)

        if not self.validate(invocation):
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Invalid tool or missing expression."])

        expression = invocation.parameters["expression"]
        
        try:
            tree = ast.parse(expression, mode='eval')
            result = self._eval_node(tree.body)
            # Format nicely
            if isinstance(result, float) and result.is_integer():
                result = int(result)
                
            model = PresentationModel(
                type=PresentationType.REPORT,
                title="Calculator",
                subtitle="Evaluation Result",
                icon="calculator",
                data={"expression": expression, "result": str(result)},
                actions=[],
                metadata=PresentationMetadata(
                    capabilities=[PresentationCapability.COPY],
                    lifetime=PresentationLifetime.TRANSIENT
                )
            )
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=str(result), presentation=model)
        except ZeroDivisionError:
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Division by zero."])
        except Exception as e:
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=[f"Invalid expression: {str(e)}"])

    def cancel(self, invocation_id: str) -> None:
        pass
