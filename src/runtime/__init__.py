"""B7 W2 — runtime spine owners package.

The runtime spine (``docs/clauderuntime-final-architecture-freeze-delivery-v2-complete-20260814/docs/06_RUNTIME_SPINE_SPEC.md``)
declares a single authority chain: Surface → RuntimeSession →
TurnPreparationService → PreparedTurn → canonical query(). This package hosts
the canonical owners introduced during the architecture closure (W2 turn
preparation first; W4 session lifecycle and W6 capability/completion owners
land in later waves).
"""
