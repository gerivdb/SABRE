#!/usr/bin/env python3
"""
SABRE TOPOS Snapshot Consumer v1.0
Consumes TOPOS snapshot YAML for security audit and backup.

Bridge: TOPOS-SABRE-SNAPSHOT (active - consumer side)
IntentHash: 0xTOPOS_SABRE_BRIDGE_20260603
"""

__version__ = "1.0.0"

import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ToposSnapshotConsumer:
    """Consumes TOPOS snapshot YAML files for SABRE security audit."""

    def __init__(self, snapshot_dir: str = "snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self._snapshots: List[Dict] = []
        self._audit_results: List[Dict] = []

    def consume_snapshot(self, snapshot_data: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = snapshot_data.get("snapshot_id", "unknown")
        timestamp = snapshot_data.get("timestamp", "")
        repos = snapshot_data.get("repos", [])
        security_flags = snapshot_data.get("security_flags", [])

        audit = self._audit_snapshot(snapshot_data)

        result = {
            "snapshot_id": snapshot_id,
            "timestamp": timestamp,
            "repos_count": len(repos),
            "security_flags": security_flags,
            "audit": audit,
            "status": "consumed"
        }

        self._snapshots.append(result)
        self._audit_results.append(audit)

        logger.info("SABRE consumed snapshot %s: %d repos, %d flags",
                     snapshot_id, len(repos), len(security_flags))
        return result

    def _audit_snapshot(self, snapshot: Dict) -> Dict[str, Any]:
        repos = snapshot.get("repos", [])
        flags = snapshot.get("security_flags", [])
        issues = []
        for repo in repos:
            if repo.get("status") == "deprecated" and repo.get("phi_cps", 0) > 0:
                issues.append({
                    "type": "deprecated_active",
                    "repo": repo.get("name"),
                    "severity": "medium"
                })
        return {
            "repos_audited": len(repos),
            "flags_found": len(flags),
            "issues": issues,
            "clean": len(issues) == 0
        }

    @property
    def snapshot_count(self) -> int:
        return len(self._snapshots)
