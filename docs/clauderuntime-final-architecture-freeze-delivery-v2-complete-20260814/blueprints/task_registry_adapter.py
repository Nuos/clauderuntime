class LegacyTaskProjection:
    """Read-only compatibility view over RuntimeTaskRegistry."""
    def __init__(self, registry): self._registry = registry
    def get(self, task_id): return self._registry.get(task_id)
    def list(self): return self._registry.list()
    def __setitem__(self, key, value):
        raise RuntimeError("legacy task projection is read-only; mutate RuntimeTaskRegistry")
