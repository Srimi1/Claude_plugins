from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


STATUS_OK = "ok"
STATUS_WARN = "warn"
STATUS_ERROR = "error"


@dataclass
class OperationResult:
    status: str
    findings: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


REQUIRED_OUTPUT_FIELDS = {
    "status",
    "findings",
    "actions",
    "commands",
    "next_steps",
}


def validate_result_shape(payload: dict[str, Any]) -> list[str]:
    missing = sorted(REQUIRED_OUTPUT_FIELDS - set(payload))
    return [f"missing field: {item}" for item in missing]
