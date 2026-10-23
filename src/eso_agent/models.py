from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

SourceTag = Literal["real", "rule", "inferred", "synthetic"]


class Tagged(BaseModel):
    value: Any
    source: SourceTag
    note: str = ""


class RequestForm(BaseModel):
    kw: float | None = None
    phases: int | None = None
    lat: float | None = None
    lon: float | None = None
    customer_type: str = "household"
    pending_kw: float | None = None
    existing_kw: float | None = None
    required_element: str | None = None
    text: str = ""
    object_name: str = "Naujas buitinis objektas"


class ParsedRequest(BaseModel):
    kw: float
    phases: Literal[1, 3]
    lat: float
    lon: float
    customer_type: str = "household"
    pending_kw: float = 0.0
    existing_kw: float = 0.0
    object_name: str = "Naujas buitinis objektas"
    first_time_connection: bool = True
    includes_generation: bool = False
    parse_mode: Literal["form", "offline", "llm"] = "offline"
    warnings: list[str] = Field(default_factory=list)
    source_tags: list[SourceTag] = Field(default_factory=list)
    source_text: str = ""
    extraction: dict[str, Any] = Field(default_factory=dict)
    highlights: list[dict[str, Any]] = Field(default_factory=list)
    missing: list[dict[str, Any]] = Field(default_factory=list)


class ToolEvent(BaseModel):
    type: str
    tool: str
    title: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    source_tags: list[SourceTag] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    elapsed_ms: int = 0
    llm: bool = False
    ok: bool = True
    ts: float = 0.0
