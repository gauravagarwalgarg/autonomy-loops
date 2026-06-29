"""Provider factory creates LLM provider instances from config."""

from __future__ import annotations

from autonomy_loops.config import Config, ProviderConfig
from autonomy_loops.providers.base import LLMProvider


def create_provider(name: str, config: Config) -> LLMProvider:
    """Create a single LLM provider by name.

    Args:
        name: Provider name ("openai", "anthropic", "bedrock", "local").
        config: Application configuration.

    Returns:
        Configured LLMProvider instance.

    Raises:
        ValueError: Unknown provider name.
    """
    provider_config = config.providers.get(name, ProviderConfig())

    if name == "openai":
        from autonomy_loops.providers.openai_provider import OpenAIProvider

        return OpenAIProvider(provider_config)
    elif name == "anthropic":
        from autonomy_loops.providers.anthropic_provider import AnthropicProvider

        return AnthropicProvider(provider_config)
    elif name == "local":
        from autonomy_loops.providers.local_provider import LocalProvider

        return LocalProvider(provider_config)
    elif name == "bedrock":
        # Bedrock uses the OpenAI-compatible interface with different base URL
        from autonomy_loops.providers.openai_provider import OpenAIProvider

        return OpenAIProvider(provider_config)
    else:
        raise ValueError(f"Unknown provider: {name}. Available: openai, anthropic, bedrock, local")


def create_all_providers(config: Config) -> dict[str, LLMProvider]:
    """Create all configured providers.

    Returns:
        Dict mapping provider name to LLMProvider instance.
    """
    providers: dict[str, LLMProvider] = {}
    for name in config.providers:
        try:
            providers[name] = create_provider(name, config)
        except (ImportError, ValueError):
            pass  # Skip providers with missing dependencies
    return providers
