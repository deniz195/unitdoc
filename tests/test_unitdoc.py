import pytest
import typing

import attr
import cattr

# from pathlib import Path

from unitdoc import UnitDocRegistry


def get_roundtrip_quantities():
    correct_result = "(42.0 +/- 2.0) mg"

    roundtrip_quantity_map1 = {
        "42.000+/-2.0000 mg": correct_result,
        "42.000 +/- 2.0000 mg": correct_result,
        "42.000±2.0000 mg": correct_result,
        "42.000 ± 2.0000 mg": correct_result,
        "(42.000+/-2.0000) mg": correct_result,
        "(42.000 +/- 2.0000) mg": correct_result,
        "(42.000±2.0000) mg": correct_result,
        "(42.000 ± 2.0000) mg": correct_result,
    }

    roundtrip_quantity_map = {}
    roundtrip_quantity_map.update(roundtrip_quantity_map1)

    return roundtrip_quantity_map


def test_pint_modifications():
    # Validate that we are using a modified version of pint
    # with certain properties
    from pint_mtools import UnitRegistry

    ureg = UnitRegistry()
    ureg.default_format = UnitDocRegistry().ureg.default_format
    assert ureg.fmt_locale is None

    roundtrip_quantity_map = get_roundtrip_quantities()

    for i, o in roundtrip_quantity_map.items():
        assert str(ureg(i)) == o


def test_unit_doc_registry_roundtrip():
    udr = UnitDocRegistry()

    roundtrip_quantity_map = get_roundtrip_quantities()
    roundtrip_quantity_map2 = {
        "1kg": "1 kg",
        "0": "0",
        "1": "1",
        "42cm": "42 cm",
        "55 degC": "55 °C",
        "34 °C": "34 °C",
        "(33.00 +/- 5.00) °C": "(33 +/- 5) °C",
    }
    roundtrip_quantity_map.update(roundtrip_quantity_map2)

    for i, o in roundtrip_quantity_map.items():
        assert str(udr.ureg(i)) == o
        assert str(udr.unit(i)) == o
        assert str(udr.yaml.load(f"!unit {i}")) == o


def test_unit_doc_registry_basics():
    udr = UnitDocRegistry()

    assert udr.yaml.dump([udr.unit("1m")]) == "- !unit 1 m\n"
    assert udr.yaml.dump([None]) == "- \n"

    q1 = udr.ureg.Quantity(float("nan"), "m")
    q2 = udr.ureg.Quantity(42, "m")
    q3 = q2.plus_minus(2)

    ystr = udr.yaml.dump([q1, q2, q3, None])
    assert "- \n- !unit 42 m\n- !unit (42.0000 +/- 2.0000) m\n- \n" == ystr

    uus = udr.yaml.load(ystr)

    assert uus[0] is None
    assert uus[3] is None
    assert uus[1] == q2
    assert str(uus[2].m.nominal_value) == str(q3.m.nominal_value)
    assert str(uus[2].m.std_dev) == str(q3.m.std_dev)


def test_deserialization():
    udr = UnitDocRegistry()

    # Test deserializing
    uu2 = udr.yaml.load("!unit 1m")
    assert str(uu2.m) == "1"
    assert str(uu2.u) == "m"

    uu3 = udr.yaml.load("!unit 1+/-0.2m")
    assert (str(uu3.m.n), str(uu3.m.s), str(uu3.u)) == ("1.0", "0.2", "m")


def test_multiplication_temperature():
    udr = UnitDocRegistry()

    # Test correct multiplication of quantity object with unit degC with quantity object with unit dimensionless
    q4 = udr.ureg.Quantity(34.0)
    q5 = udr.ureg("degC")
    q6 = q4 * q5
    q7 = q5 * q4
    assert (str(q6), str(q7)) == ("34 °C", "34 °C")

    # Test correct multiplication of measurement object with quantity object with unit degC
    m1 = udr.ureg.Measurement(33.0, 5.0)
    m2 = m1 * q5
    m3 = q5 * m1
    assert (str(m2), str(m3)) == ("(33 +/- 5) °C", "(33 +/- 5) °C")
    assert type(m2) == type(m3) == type(m1)


def test_serialization():
    udr = UnitDocRegistry()

    @udr.serialize()
    @attr.s(
        frozen=True, kw_only=True,
    )
    class SomeDoc(object):
        region_name = attr.ib(default=None, converter=str)

        qarea_neg = udr.attrib(default="355mAh/cm**2", description="Area specific reversible capacity")
        qarea_1st_neg = udr.attrib(
            default=None, default_unit="mAh/cm**2", description="Area specific first charge capacity",
        )

    # test serialization
    sd = SomeDoc(region_name="A")
    sd_str = "region_name: A\nqarea_neg: !unit 355 mAh / cm ** 2\nqarea_1st_neg:\n"

    assert sd.serialize() == sd_str

    # test deserialization
    sd2 = SomeDoc.deserialize(sd_str)
    assert sd2.region_name == "A"
    assert str(sd2.qarea_neg) == "355 mAh / cm ** 2"
    assert sd2.qarea_1st_neg is None

    assert cattr.unstructure(sd) is not None


def test_recover():
    udr = UnitDocRegistry()

    @udr.serialize()
    @attr.s(
        frozen=True, kw_only=True,
    )
    class SomeDoc(object):
        region_name = attr.ib(default=None, converter=str)

        qarea_neg = udr.attrib(default="355mAh/cm**2", description="Area specific reversible capacity")
        qarea_1st_neg = udr.attrib(
            default=None, default_unit="mAh/cm**2", description="Area specific first charge capacity",
        )

    @udr.serialize()
    @attr.s(
        frozen=True, kw_only=True,
    )
    class SomeDocOld(object):
        name = attr.ib(default=None, converter=str)

        qarea_neg = udr.attrib(default="355mAh/cm**2", description="Area specific reversible capacity")
        qarea_1st_neg = udr.attrib(
            default=None, default_unit="mAh/cm**2", description="Area specific first charge capacity",
        )

    sd_old = SomeDocOld(name="A")
    sd_str = sd_old.serialize()

    # Test failing deserialization
    with pytest.raises(TypeError, match="got an unexpected keyword argument"):
        sd = SomeDoc.deserialize(sd_str)

    # Test recovery of deserialization
    @udr.serialize()
    @attr.s(
        frozen=True, kw_only=True,
    )
    class SomeDocSmart(SomeDoc):
        @classmethod
        def recover_deserialize(cls, d):
            if "name" in d:
                print(f"Trying to recover {cls.__qualname__}")
                d["region_name"] = d.pop("name")

            return d

    sd = SomeDocSmart.deserialize(sd_str)
    print(sd.serialize())
    assert sd.region_name == "A"

    # Test recovery of deserialization failing
    @udr.serialize()
    @attr.s(
        frozen=True, kw_only=True,
    )
    class SomeDocStupid(SomeDoc):
        @classmethod
        def recover_deserialize(cls, d):
            # doing nothing, so that recovery will fail
            return d

    with pytest.raises(TypeError, match="got an unexpected keyword argument"):
        sd = SomeDocStupid.deserialize(sd_str)

    # Test recovery of nested class
    @udr.serialize()
    @attr.s(
        frozen=True, kw_only=True,
    )
    class ListSomeDocSmart:
        docs = attr.ib(default=None, type=typing.List[SomeDocSmart])

    lsds_old = ListSomeDocSmart(docs=[sd_old])
    lsds_old_str = lsds_old.serialize()

    lsds = ListSomeDocSmart.deserialize(lsds_old_str)

    assert lsds_old_str != lsds.serialize()

    print(lsds_old_str)
    print(lsds.serialize())


def test_nan():
    udr = UnitDocRegistry()

    @udr.serialize()
    @attr.s(
        frozen=True, kw_only=True,
    )
    class SomeDoc(object):
        area = udr.attrib(default_unit="dimensionless", description="Area specific reversible capacity",)

    sd = SomeDoc(area="3")
    assert sd.area == 3

    sd = SomeDoc(area=None)
    assert sd.area is None

    sd = SomeDoc(area=float("nan"))
    assert sd.area is None
