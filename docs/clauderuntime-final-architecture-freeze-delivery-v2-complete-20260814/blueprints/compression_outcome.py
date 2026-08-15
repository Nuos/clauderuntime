from dataclasses import dataclass

@dataclass(frozen=True)
class CompressionOutcome:
    changed: bool
    stage: str | None = None
    warnings: tuple[str, ...] = ()
    hard_limit_reached: bool = False
    artifacts: tuple[str, ...] = ()
    tokens_before: int | None = None
    tokens_after: int | None = None
