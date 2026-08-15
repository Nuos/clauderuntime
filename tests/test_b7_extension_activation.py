"""B7 W3 — extension activation gate (trust-before-activation) tests.

Covers the W3 exit conditions:
- project/user/mcp executable activation requires workspace trust;
- name collisions are deterministic (silent overwrite forbidden,
  exact-same-hash dedupes, project-over-managed denied by default);
- every outcome is auditable (provenance ledger, reasons);
- the plugin loader register action is wrapped behind the gate.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pytest

from src.plugins.loader import (
    clear_loaded_plugins,
    get_loaded_plugin,
    load_plugins_from_directories,
    register_plugin,
)
from src.plugins.types import LoadedPlugin, PluginError, PluginManifest
from src.runtime.extension_activation import (
    ActivationBehavior,
    ExtensionActivationGate,
    ExtensionDescriptor,
    content_hash,
    descriptor_from_loaded_plugin,
)


def _desc(
    name: str = "ext",
    kind: str = "plugin",
    source: str = "user",
    scope: str = "project",
    trust_level: str = "project",
    provenance: str | None = None,
) -> ExtensionDescriptor:
    return ExtensionDescriptor(
        kind=kind,
        name=name,
        source=source,
        scope=scope,
        trust_level=trust_level,
        provenance_hash=provenance or content_hash(name, "v1"),
    )


class TestInvalidDescriptors(unittest.TestCase):
    def test_missing_name_invalid(self) -> None:
        gate = ExtensionActivationGate()
        decision = gate.decide(_desc(name=""), workspace_trusted=True)
        self.assertEqual(decision.behavior, ActivationBehavior.INVALID)

    def test_missing_hash_invalid(self) -> None:
        gate = ExtensionActivationGate()
        decision = gate.decide(_desc(provenance="short"), workspace_trusted=True)
        self.assertEqual(decision.behavior, ActivationBehavior.INVALID)

    def test_unknown_scope_invalid(self) -> None:
        gate = ExtensionActivationGate()
        decision = gate.decide(_desc(scope="root"), workspace_trusted=True)
        self.assertEqual(decision.behavior, ActivationBehavior.INVALID)

    def test_unknown_trust_level_invalid(self) -> None:
        gate = ExtensionActivationGate()
        decision = gate.decide(_desc(trust_level="root"), workspace_trusted=True)
        self.assertEqual(decision.behavior, ActivationBehavior.INVALID)


class TestTrustBeforeActivation(unittest.TestCase):
    def test_project_scope_requires_trust(self) -> None:
        gate = ExtensionActivationGate()
        decision = gate.decide(_desc(), workspace_trusted=False)
        self.assertEqual(decision.behavior, ActivationBehavior.REQUIRE_TRUST)

    def test_project_scope_trusted_allows(self) -> None:
        gate = ExtensionActivationGate()
        decision = gate.decide(_desc(), workspace_trusted=True)
        self.assertEqual(decision.behavior, ActivationBehavior.ALLOW)

    def test_bundled_scope_does_not_require_trust(self) -> None:
        gate = ExtensionActivationGate()
        decision = gate.decide(
            _desc(scope="bundled", trust_level="bundled"), workspace_trusted=False
        )
        self.assertEqual(decision.behavior, ActivationBehavior.ALLOW)

    def test_managed_scope_does_not_require_trust(self) -> None:
        gate = ExtensionActivationGate()
        decision = gate.decide(
            _desc(scope="managed", trust_level="managed"), workspace_trusted=False
        )
        self.assertEqual(decision.behavior, ActivationBehavior.ALLOW)


class TestCollisionPolicy(unittest.TestCase):
    def test_same_hash_dedupes(self) -> None:
        gate = ExtensionActivationGate()
        d1 = _desc(provenance=content_hash("ext", "same"))
        gate.activate(d1, workspace_trusted=True)
        d2 = _desc(provenance=content_hash("ext", "same"))
        decision = gate.decide(d2, workspace_trusted=True)
        self.assertEqual(decision.behavior, ActivationBehavior.ALLOW)
        self.assertIn("dedupe", decision.reason)

    def test_different_content_collision_rejected(self) -> None:
        gate = ExtensionActivationGate()
        gate.activate(_desc(provenance=content_hash("ext", "v1")), workspace_trusted=True)
        decision = gate.decide(
            _desc(provenance=content_hash("ext", "v2")), workspace_trusted=True
        )
        self.assertEqual(decision.behavior, ActivationBehavior.COLLISION)
        self.assertIn("silent overwrite is forbidden", decision.reason)

    def test_project_over_managed_denied(self) -> None:
        gate = ExtensionActivationGate()
        gate.activate(
            _desc(scope="managed", trust_level="managed", provenance=content_hash("ext", "m")),
            workspace_trusted=True,
        )
        decision = gate.decide(
            _desc(scope="project", trust_level="project", provenance=content_hash("ext", "m")),
            workspace_trusted=True,
        )
        self.assertEqual(decision.behavior, ActivationBehavior.DENY)
        self.assertIn("project_over_managed", decision.reason)


class TestAudit(unittest.TestCase):
    def test_ledger_records_allowed_activations(self) -> None:
        gate = ExtensionActivationGate()
        gate.activate(_desc(name="audit-a", provenance=content_hash("audit-a")), workspace_trusted=True)
        gate.activate(_desc(name="audit-b", provenance=content_hash("audit-b")), workspace_trusted=True)
        entries = gate.ledger()
        self.assertEqual({e["name"] for e in entries}, {"audit-a", "audit-b"})
        self.assertTrue(gate.is_active("audit-a"))
        self.assertFalse(gate.is_active("nope"))


class TestPluginLoaderWiring(unittest.TestCase):
    def test_register_plugin_consults_gate(self) -> None:
        clear_loaded_plugins()
        plugin = LoadedPlugin(
            name="wired",
            manifest=PluginManifest(name="wired"),
            enabled=True,
            source="user",
        )
        # user scope + untrusted → REQUIRE_TRUST → activation raises + nothing registered
        with pytest.raises(PluginError):
            register_plugin(plugin, workspace_trusted=False)
        self.assertIsNone(get_loaded_plugin("wired"))

    def test_register_plugin_allows_when_trusted(self) -> None:
        clear_loaded_plugins()
        plugin = LoadedPlugin(
            name="wired2",
            manifest=PluginManifest(name="wired2"),
            enabled=True,
            source="user",
        )
        register_plugin(plugin, workspace_trusted=True)
        self.assertIsNotNone(get_loaded_plugin("wired2"))

    def test_collision_raises_instead_of_silent_overwrite(self) -> None:
        clear_loaded_plugins()
        from src.runtime.extension_activation import ExtensionActivationGate

        gate = ExtensionActivationGate()
        p1 = LoadedPlugin(
            name="collide", manifest=PluginManifest(name="collide"), path="/a", source="user"
        )
        p2 = LoadedPlugin(
            name="collide", manifest=PluginManifest(name="collide"), path="/b", source="user"
        )
        register_plugin(p1, workspace_trusted=True, gate=gate)
        with pytest.raises(PluginError):
            register_plugin(p2, workspace_trusted=True, gate=gate)

    def test_batch_loader_reports_collision_as_error(self) -> None:
        clear_loaded_plugins()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # loader layout: <root>/<plugin-name>/plugin.json
            for root in ("a", "b"):
                d = tmp_path / root / "batch-collide"
                d.mkdir(parents=True, exist_ok=True)
                (d / "plugin.json").write_text(
                    json.dumps(
                        {"name": "batch-collide", "description": "c", "version": "1.0.0"}
                    ),
                    encoding="utf-8",
                )
            result = load_plugins_from_directories(
                [tmp_path / "a", tmp_path / "b"], source="user"
            )
            self.assertEqual(len(result.plugins), 1)
            self.assertTrue(any("activation denied" in str(e) for e in result.errors))

    def test_descriptor_from_loaded_plugin(self) -> None:
        plugin = LoadedPlugin(
            name="d", manifest=PluginManifest(name="d"), path="/x/y", source="project"
        )
        descriptor = descriptor_from_loaded_plugin(plugin)
        self.assertEqual(descriptor.kind, "plugin")
        self.assertEqual(descriptor.scope, "project")
        self.assertGreaterEqual(len(descriptor.provenance_hash), 8)


if __name__ == "__main__":
    unittest.main()
