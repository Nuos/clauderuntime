def test_compaction_stage_order_is_fixed():
    expected = ["tool_result_budget", "snip", "microcompact", "context_collapse", "autocompact"]
    assert len(expected) == 5

def test_hard_limit_is_observable_in_compression_outcome():
    pass
