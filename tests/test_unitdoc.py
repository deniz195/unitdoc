import pytest
import os

import attr
import cattr

from pathlib import Path

from unitdoc import UnitDocRegistry



def test_unit_doc_registry():
    udr = UnitDocRegistry()

    assert(udr.yaml.dump([udr.unit('1m')]) == '- !unit 1 m\n')
    assert(udr.yaml.dump([None,]) == '- \n')

    q1 = udr.ureg.Quantity(float('nan'), 'm')
    q2 = udr.ureg.Quantity(42, 'm')
    q3 = q2.plus_minus(2)
    
    print([q1, q2, q3, None,])

    assert(udr.yaml.dump([q3]) == '- !unit 1 m\n')


    ystr = udr.yaml.dump([q1, q2, q3, None,])
    assert('- \n- !unit 42 m\n- !unit (42.0000 +/- 2.0000) m\n- \n' == ystr)

    uus = udr.yaml.load(ystr)

    assert(uus[0] is None)
    assert(uus[3] is None)
    assert(uus[1] == q2)
    assert(str(uus[2].m.nominal_value) == str(q3.m.nominal_value))
    assert(str(uus[2].m.std_dev) == str(q3.m.std_dev))


    # Test deserializing
    uu2 = udr.yaml.load('!unit 1m')
    assert(str(uu2.m) == '1')
    assert(str(uu2.u) == 'm')

    uu3 = udr.yaml.load('!unit 1+/-0.2m')
    assert((str(uu3.m.n), str(uu3.m.s), str(uu3.u)) == ('1.0', '0.2', 'm'))



    @udr.serialize()   
    @attr.s(frozen=True, kw_only=True, )
    class SomeDoc(object):
        region_name = attr.ib(default=None, converter=str)

        qarea_neg = udr.attrib(default='355mAh/cm**2', description ='Area specific reversible capacity')
        qarea_1st_neg = udr.attrib(default=None, default_unit='mAh/cm**2', description='Area specific first charge capacity')


    # test serialization
    sd = SomeDoc(region_name = 'A')
    sd_str = 'region_name: A\nqarea_neg: !unit 355 mAh / cm ** 2\nqarea_1st_neg:\n'

    assert(sd.serialize() == sd_str)

    # test deserialization
    sd2 = SomeDoc.deserialize(sd_str)
    assert(sd2.region_name == 'A')
    assert(str(sd2.qarea_neg) == '355 mAh / cm ** 2')
    assert(sd2.qarea_1st_neg is None)

    assert(cattr.unstructure(sd) is not None)






