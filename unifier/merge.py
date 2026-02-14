"""Lattice merge engine -- Python equivalent of CUE lattice unification.

CUE computes the greatest lower bound (meet) of all source contributions
for each gene. This module implements the same semantics in pure Python.

Lattice rules:
  Defaulted booleans (*false | true):
    false + false -> false   (both at default)
    false + true  -> true    (true is more specific)
    true  + true  -> true    (idempotent)
    true  + false -> true    (commutative)

  Defaulted strings (*"" | string):
    "" + ""         -> ""        (both at default)
    "" + "value"    -> "value"   (value is more specific)
    "value" + ""    -> "value"   (commutative)
    "value" + "value" -> "value" (idempotent)
    "v1" + "v2"     -> ERROR     (conflict)

  Optional fields (field?: type):
    absent  + absent  -> absent
    absent  + present -> present
    present + absent  -> present
    present(v1) + present(v2) -> v1 if v1 == v2, else ERROR

  List fields follow the optional rule -- present values must be equal.
"""

from .schema import GENE_DEFAULTS, OPTIONAL_FIELDS, new_gene

# Sentinel for "field not present" (distinct from any real value)
_ABSENT = object()


class ConflictError(Exception):
    """Raised when two sources set conflicting values for the same field."""


def merge_field(field_name: str, existing, incoming, default):
    """Lattice meet of two values for a single defaulted field.

    Both existing and incoming are concrete values (not absent).
    The default is the lattice top for this field.
    """
    if incoming == default:
        return existing  # incoming is at top, keep existing
    if existing == default:
        return incoming  # existing is at top, take incoming
    if existing == incoming:
        return existing  # idempotent
    raise ConflictError(
        f"Conflict on {field_name}: {existing!r} vs {incoming!r}"
    )


def merge_optional(field_name: str, existing, incoming):
    """Lattice meet for optional fields (may be absent).

    Uses _ABSENT sentinel to represent "not present".
    """
    if incoming is _ABSENT:
        return existing
    if existing is _ABSENT:
        return incoming
    if existing == incoming:
        return existing
    raise ConflictError(
        f"Conflict on optional {field_name}: {existing!r} vs {incoming!r}"
    )


def merge_gene(base: dict, contribution: dict) -> dict:
    """Merge a source's contribution into the base gene dict.

    The contribution dict should contain only fields this source actually
    sets (non-default values). The base should be a full gene dict with
    all defaults.

    Returns a new dict -- does not mutate base.
    """
    result = dict(base)

    for field, value in contribution.items():
        if field == "symbol":
            continue  # key field, always matches

        if field in GENE_DEFAULTS:
            # Defaulted field -- use lattice merge
            result[field] = merge_field(
                field,
                result.get(field, GENE_DEFAULTS[field]),
                value,
                GENE_DEFAULTS[field],
            )
        elif field in OPTIONAL_FIELDS:
            # Optional field -- absent + present -> present
            existing = result.get(field, _ABSENT)
            merged = merge_optional(field, existing, value)
            if merged is not _ABSENT:
                result[field] = merged
        else:
            # Unknown field -- forward compatibility, just set it
            # If already present, must be equal
            if field in result and result[field] != value:
                raise ConflictError(
                    f"Conflict on unknown field {field}: "
                    f"{result[field]!r} vs {value!r}"
                )
            result[field] = value

    return result


def merge_all_sources(
    gene_list: list[str], sources: list[dict]
) -> dict[str, dict]:
    """Merge all source contributions into unified gene dicts.

    Args:
        gene_list: list of gene symbols
        sources: list of dicts, each is {symbol: {field: value, ...}}
                 for genes that source has data for

    Returns:
        {symbol: unified_gene_dict} for all genes

    Properties (proven by prove.py):
        - Associative: merge(merge(a,b), c) == merge(a, merge(b,c))
        - Commutative: merge(a,b) == merge(b,a)
        - Idempotent:  merge(a,a) == a
    """
    unified = {}
    for symbol in gene_list:
        unified[symbol] = new_gene(symbol)

    for source_data in sources:
        for symbol, contribution in source_data.items():
            if symbol not in unified:
                continue
            unified[symbol] = merge_gene(unified[symbol], contribution)

    return unified
