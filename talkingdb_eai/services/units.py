import re

_LEADING_NUMBER = re.compile(r"^-?\d+(\.\d+)?")


def apply_unit(attribute_name: str, value, unit_config: dict[str, str]):
    """Append a tenant-configured unit to a numeric attribute value, e.g.
    apply_unit("capacity", "250", {"capacity": "lbs"}) -> "250 lbs".

    An attribute with no configured unit, or a value that doesn't start
    with a number, passes through unchanged - this only formats known
    numeric attributes, it never invents units for attributes a tenant
    hasn't configured.
    """

    unit = unit_config.get(attribute_name)
    if not unit:
        return value

    text = str(value).strip()
    match = _LEADING_NUMBER.match(text)
    if not match:
        return value

    return f"{match.group(0)} {unit}"


def apply_units(
    attributes: dict[str, object], unit_config: dict[str, str]
) -> dict[str, object]:
    return {
        name: apply_unit(name, value, unit_config) for name, value in attributes.items()
    }
