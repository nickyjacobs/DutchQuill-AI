"""Kleine validator voor het deel van JSON Schema dat config/schema.json gebruikt.

Ondersteund: type, enum, properties, additionalProperties (bool of schema), propertyNames, items,
minItems, minimum, maximum, required en $ref (JSON-pointer binnen hetzelfde schema).
"""

from __future__ import annotations

from typing import Any

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
}


def _resolve(schema: dict, root: dict) -> dict:
    while "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            raise ValueError(f"Alleen interne $ref ondersteund: {ref}")
        node: Any = root
        for deel in ref[2:].split("/"):
            node = node[deel]
        schema = node
    return schema


def _past_type(waarde: Any, type_: str) -> bool:
    if type_ in ("integer", "number") and isinstance(waarde, bool):
        return False
    return isinstance(waarde, _TYPES[type_])


def valideer(waarde: Any, schema: dict, root: dict | None = None, pad: str = "") -> list[str]:
    """Geef een lijst met fouten terug (leeg = geldig). Paden in de vorm toon.niveau."""
    root = root or schema
    schema = _resolve(schema, root)
    fouten: list[str] = []
    plek = pad or "(hoofdniveau)"

    type_ = schema.get("type")
    if type_ and not _past_type(waarde, type_):
        return [f"{plek}: verwacht {type_}, kreeg {type(waarde).__name__}"]

    if "enum" in schema and waarde not in schema["enum"]:
        opties = ", ".join(str(o) for o in schema["enum"])
        fouten.append(f"{plek}: '{waarde}' is geen geldige keuze (kies uit: {opties})")

    if isinstance(waarde, (int, float)) and not isinstance(waarde, bool):
        if "minimum" in schema and waarde < schema["minimum"]:
            fouten.append(f"{plek}: minimaal {schema['minimum']}")
        if "maximum" in schema and waarde > schema["maximum"]:
            fouten.append(f"{plek}: maximaal {schema['maximum']}")

    if isinstance(waarde, list):
        if "minItems" in schema and len(waarde) < schema["minItems"]:
            fouten.append(f"{plek}: minstens {schema['minItems']} item(s)")
        if "items" in schema:
            for i, item in enumerate(waarde):
                fouten += valideer(item, schema["items"], root, f"{pad}[{i}]")

    if isinstance(waarde, dict):
        props = schema.get("properties", {})
        for sleutel in schema.get("required", []):
            if sleutel not in waarde:
                fouten.append(f"{plek}: '{sleutel}' ontbreekt")
        extra = schema.get("additionalProperties", True)
        namen = schema.get("propertyNames")
        for sleutel, sub in waarde.items():
            subpad = f"{pad}.{sleutel}" if pad else str(sleutel)
            if namen is not None:
                fouten += [f.replace(subpad, f"{subpad} (naam)", 1) for f in valideer(sleutel, namen, root, subpad)]
            if sleutel in props:
                fouten += valideer(sub, props[sleutel], root, subpad)
            elif extra is False:
                fouten.append(f"{subpad}: onbekende instelling")
            elif isinstance(extra, dict):
                fouten += valideer(sub, extra, root, subpad)
    return fouten


def standaardwaarden(schema: dict, root: dict | None = None) -> Any:
    """Bouw een dict met alle default-waarden uit het schema (geneste objecten inbegrepen)."""
    root = root or schema
    schema = _resolve(schema, root)
    if "default" in schema:
        return schema["default"]
    if schema.get("type") == "object" and "properties" in schema:
        uit = {}
        for sleutel, sub in schema["properties"].items():
            w = standaardwaarden(sub, root)
            if w is not None:
                uit[sleutel] = w
        return uit
    return None
