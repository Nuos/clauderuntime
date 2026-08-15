from dataclasses import dataclass

@dataclass(frozen=True)
class ModelCapabilities:
    adaptive_thinking: bool = False
    prompt_cache: bool = False
    images: bool = False
    max_context_tokens: int | None = None

class ModelCapabilityResolver:
    def resolve(self, provider_id: str, model_id: str) -> ModelCapabilities:
        raise NotImplementedError
