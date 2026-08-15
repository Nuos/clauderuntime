from dataclasses import dataclass
from enum import Enum
from typing import Sequence, Any

class CompletionStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INDETERMINATE = "indeterminate"

@dataclass(frozen=True)
class CompletionDecision:
    status: CompletionStatus
    reasons: tuple[str, ...]
    evidence_refs: tuple[str, ...] = ()

class CompletionVerifier:
    def verify(self, task_contract: Any, execution_trace: Any, evidence: Sequence[Any]) -> CompletionDecision:
        raise NotImplementedError
