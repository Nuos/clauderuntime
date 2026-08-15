import inspect

def test_tool_context_has_no_implicit_bypass_default():
    from src.tool_system.context import ToolContext
    sig = inspect.signature(ToolContext)
    p = sig.parameters["permission_context"]
    # Preferred invariant: required argument.
    assert p.default is inspect._empty, "permission_context must not silently default to bypass"
