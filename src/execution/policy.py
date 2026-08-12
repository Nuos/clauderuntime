from __future__ import annotations

from dataclasses import dataclass, field
from ipaddress import ip_address
from typing import Literal, Mapping, Protocol
from urllib.parse import urlparse

from src.utils.subprocess_env import SUBPROCESS_SECRET_ENV_KEYS

NetworkMode = Literal["none", "loopback", "allowlist", "full"]

DEFAULT_MINIMAL_ENV_KEYS = frozenset(
    {
        "PATH",
        "HOME",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "TERM",
        "TMPDIR",
        "TEMP",
        "TMP",
        "SystemRoot",
        "ComSpec",
        "PATHEXT",
        "CLAUDE_CODE_SUBPROCESS_ENV_SCRUB",
    }
)


@dataclass(frozen=True)
class MinimalEnvPolicy:
    """Minimum child environment policy for C5.

    The default ``DefaultEnvPolicy`` remains a compatibility pass-through.
    This policy is the explicit minimum execution profile: keep only an
    allowlist and always remove provider/tool secrets plus GitHub Action
    ``INPUT_`` twins.
    """

    allowed_keys: frozenset[str] = DEFAULT_MINIMAL_ENV_KEYS
    extra_allowed_keys: tuple[str, ...] = ()
    secret_keys: tuple[str, ...] = SUBPROCESS_SECRET_ENV_KEYS
    include_input_twins: bool = True

    def prepare_env(
        self,
        env: Mapping[str, str] | None = None,
    ) -> dict[str, str]:
        source = dict(env or {})
        allowed = set(self.allowed_keys)
        allowed.update(self.extra_allowed_keys)
        secret_keys = set(self.secret_keys)
        if self.include_input_twins:
            secret_keys.update(f"INPUT_{key}" for key in self.secret_keys)
        return {
            key: value
            for key, value in source.items()
            if key in allowed and key not in secret_keys
        }


@dataclass(frozen=True)
class NetworkDecision:
    allow: bool
    mode: NetworkMode
    url: str
    host: str | None
    reason: str


class NetworkPolicy(Protocol):
    def check_url(self, url: str, *, purpose: str = "network") -> NetworkDecision: ...


@dataclass(frozen=True)
class ConfigurableNetworkPolicy:
    """Execution-layer network policy without doing network I/O."""

    mode: NetworkMode = "full"
    allowed_hosts: frozenset[str] = field(default_factory=frozenset)

    def check_url(self, url: str, *, purpose: str = "network") -> NetworkDecision:
        parsed = urlparse(url)
        host = parsed.hostname.lower() if parsed.hostname else None
        if not host:
            return NetworkDecision(
                allow=False,
                mode=self.mode,
                url=url,
                host=None,
                reason=f"{purpose}: URL has no host",
            )
        if self.mode == "full":
            return NetworkDecision(
                allow=True,
                mode=self.mode,
                url=url,
                host=host,
                reason=f"{purpose}: full network access allowed",
            )
        if self.mode == "none":
            return NetworkDecision(
                allow=False,
                mode=self.mode,
                url=url,
                host=host,
                reason=f"{purpose}: network access disabled",
            )
        if self.mode == "loopback":
            if _is_loopback_host(host):
                return NetworkDecision(
                    allow=True,
                    mode=self.mode,
                    url=url,
                    host=host,
                    reason=f"{purpose}: loopback host allowed",
                )
            return NetworkDecision(
                allow=False,
                mode=self.mode,
                url=url,
                host=host,
                reason=f"{purpose}: host is outside loopback policy",
            )
        if self.mode == "allowlist":
            if host in {h.lower() for h in self.allowed_hosts}:
                return NetworkDecision(
                    allow=True,
                    mode=self.mode,
                    url=url,
                    host=host,
                    reason=f"{purpose}: host is allowlisted",
                )
            return NetworkDecision(
                allow=False,
                mode=self.mode,
                url=url,
                host=host,
                reason=f"{purpose}: host is not allowlisted",
            )
        return NetworkDecision(
            allow=False,
            mode=self.mode,
            url=url,
            host=host,
            reason=f"{purpose}: unknown network policy mode",
        )


def _is_loopback_host(host: str) -> bool:
    if host == "localhost" or host.endswith(".localhost"):
        return True
    try:
        return ip_address(host).is_loopback
    except ValueError:
        return False


def default_network_policy() -> NetworkPolicy:
    return ConfigurableNetworkPolicy(mode="full")
