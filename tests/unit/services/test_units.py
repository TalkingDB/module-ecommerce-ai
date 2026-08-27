from talkingdb_eai.services.units import apply_unit, apply_units


def test_apply_unit_appends_configured_unit():
    assert apply_unit("capacity", "250", {"capacity": "lbs"}) == "250 lbs"


def test_apply_unit_strips_whitespace_before_matching():
    assert apply_unit("capacity", " 250 ", {"capacity": "lbs"}) == "250 lbs"


def test_apply_unit_handles_decimal_values():
    assert apply_unit("weight", "12.5", {"weight": "kg"}) == "12.5 kg"


def test_apply_unit_passes_through_when_no_unit_configured():
    assert apply_unit("color", "red", {"capacity": "lbs"}) == "red"


def test_apply_unit_passes_through_non_numeric_value():
    assert apply_unit("capacity", "heavy-duty", {"capacity": "lbs"}) == "heavy-duty"


def test_apply_unit_does_not_double_append_existing_unit_text():
    # Legacy behavior: strip any prior unit text then re-append - this
    # function only extracts the leading number, so trailing unit text
    # (if any) is simply dropped, not duplicated.
    assert apply_unit("capacity", "250 lbs", {"capacity": "lbs"}) == "250 lbs"


def test_apply_units_applies_across_a_dict():
    result = apply_units(
        {"capacity": "250", "color": "red"}, {"capacity": "lbs", "color": "n/a"}
    )

    assert result == {"capacity": "250 lbs", "color": "red"}
