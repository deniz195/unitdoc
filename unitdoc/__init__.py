import logging
import re 
import typing
import attr
import cattr
import os
import sys

from collections import OrderedDict

import math
from functools import reduce

import datetime
from dateutil import parser

import attr_descriptions
from attr_descriptions import get_attr_description

from pathlib import Path

# import ruamel.yaml
from ruamel.yaml import YAML, yaml_object
from ruamel.yaml.compat import StringIO

import pint_mtools

from pint_mtools import DimensionalityError

# create logger
module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.DEBUG)

# general useful module components
def _reload_module():
    import sys
    import importlib
    current_module = sys.modules[__name__]
    module_logger.info('Reloading module %s' % __name__)
    importlib.reload(current_module)

# defining YAML_EXTENDED
class YAML_extended(YAML):
    def dump(self, data, stream=None, **kw):
        ''' Dump with string output by default '''
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()

        YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()

    def set_unit_registry(self, unit_registry, default_serialization_format = '{:.6~g}'):
        self._unit_registry = unit_registry
        
        # quant_class = type(self._unit_registry(''))
        quant_classes = [self._unit_registry.Measurement,
                         self._unit_registry.Quantity,]
            
        def quant_to_yaml(cls, representer, node):
            # return yaml_ex.representer.represent(None)
            mag_val = node.magnitude
            try:
                mag_val = mag_val.nominal_value # try for measurement class
            except (TypeError, AttributeError):
                pass
                                                 
            if math.isnan(mag_val):
                return representer.represent_none(None)
            else:
                return representer.represent_scalar(cls.yaml_tag, default_serialization_format.format(node))
                                                         
        def yaml_to_quant(cls, constructor, node):
            return cls(node.value)
                                                                 
        for quant_class in quant_classes:
            setattr(quant_class, 'yaml_tag', '!unit')
            setattr(quant_class, 'to_yaml', classmethod(quant_to_yaml))
            setattr(quant_class, 'from_yaml', classmethod(yaml_to_quant))
                                                                     
            self.register_class(quant_class)




# new class containing UNIT_EXTENDED and YAML_EXTENDED 
class UnitDocRegistry(object):
    
    _yaml = None 
    _unit = None 
    _cattr_converter = None

    def __init__(self):
        self._unit = self._create_unit()
        self._yaml = self._create_yaml()
        self._cattr_converter = self._create_cattr_converter()


    # @property
    # def unit(self):
    #     return self._unit
    
    @property
    def ureg(self):
        return self._unit
    
    def unit(self, value):
        tmp = re.sub(' ','',value)
        pattern = '([0-9]+[.]?[0-9]*)([+][/][-])([0-9]+[.]?[0-9]*)(.+)'
        groups = re.search(pattern,tmp)

        if groups:
            val = groups.group(1) + groups.group(4)
            print('this is the val and metric:{}'.format(val))
            std = float(groups.group(3))
            print('this is the std:{}'.format(std))
            result = self._unit(val).plus_minus(std)
        else:
            result = self._unit(value)
        return result

    @property
    def yaml(self):
        return self._yaml

    @property
    def cattr(self):
        return self._cattr_converter

    @property
    def cattr_converter(self):
        module_logger.warning(f'UnitDocRegistry.cattr_converter is deprecated! Use UnitDocRegistry.cattr instead!')                                                    
        return self._cattr_converter

    def attrib(self, default=attr.NOTHING, default_unit=None, auto_convert_str=True, description=None, significant_digits=None, **kwds):    
        unit_registry = self.ureg

        unit_quantity_classes = (unit_registry.Quantity, unit_registry.Measurement)

        def is_quantity(u):
            return type(u) in unit_quantity_classes

        is_optional = False
        has_unit = False

        if default is attr.NOTHING:
            is_optional = False
            has_unit = default_unit is not None
            base_unit = default_unit
        elif default is None:
            is_optional = True
            has_unit = default_unit is not None
            base_unit = default_unit
        elif is_quantity(default):
            is_optional = False
            has_unit = True

            base_unit = str(default.u)
        elif auto_convert_str:
            # auto convert
            is_optional = False
            has_unit = True
            
            default = unit_registry.Quantity(default)        
            base_unit = str(default.u)
        else:
            raise RuntimeError('This case should never be reached!')

            
        
        metadata = kwds.get('metadata', {})
        metadata['__default_unit'] = default_unit
        metadata['__base_unit'] = base_unit
        metadata['__unit_registry'] = unit_registry
        metadata['__unit_quantity_classes'] = unit_quantity_classes
        # metadata['__description'] = description        
        kwds['metadata'] = metadata
        
        converters = [kwds['converter']] if 'converter' in kwds else []   
        if default_unit is not None:
            def do_default_unit(u):
                if u is None: return u
                return u.to(default_unit)

            converters += [do_default_unit]

        if auto_convert_str:
            def do_auto_convert_str(u):
                if u is None: return u
                if is_quantity(u): return u
                try:
                    if math.isnan(u):
                        return None
                except TypeError:
                    pass

                return unit_registry.Quantity(str(u))

            converters += [do_auto_convert_str]

        if converters:
            # nest functions in proper order
            kwds['converter'] = reduce(lambda fo, fi: (lambda x: fo(fi(x))) , converters)        



        validator = kwds.get('validator', [])    
        if has_unit is not None:
            def make_dimensionality_check(base_unit):
                base_dim = unit_registry(base_unit).dimensionality
                def dimensionality_check(self, attr, value):
                    if value is None: return is_optional
                    return value.dimensionality == base_dim  

                return dimensionality_check

            validate_unit = make_dimensionality_check(base_unit)
            validator = [validate_unit] + validator

        validator = [attr.validators.optional(\
                        attr.validators.instance_of(metadata['__unit_quantity_classes'])
                        )] + validator

        kwds['validator'] = validator
                    
        kwds['default'] = default

        attribute = attr_descriptions.describe(attr.ib(**kwds), description=description, significant_digits=significant_digits)

        return attribute

    def _create_unit(self):
        # initalize unit object
        unit = pint_mtools.UnitRegistry(autoconvert_offset_to_baseunit = True)
        unit.default_format = '.4~g'

        unit.define('mAh = milliampere hour')
        unit.define('Ah = ampere hour')
        unit.define('percent = 0.01*count')
        unit.define('permille = 0.001*count')
        unit.define('ppm = 1e-6*count')
        unit.define('ppb = 1e-9*count')
        unit.define('molal = mol / kg')

        _c_elchem = pint_mtools.Context('elchem')
        _c_elchem.add_transformation('[substance]', '[current] * [time]',
                        lambda unit, x: x* unit('avogadro_number elementary_charge'))
        _c_elchem.add_transformation('[current] * [time]', '[substance]',
                        lambda unit, x: x/ unit('avogadro_number elementary_charge'))
        unit.add_context(_c_elchem)
        unit.enable_contexts('elchem')

        return unit

    def _create_yaml(self):
        yaml = YAML_extended()
        yaml.set_unit_registry(self._unit)
        return yaml


    def _create_cattr_converter(self, *args, **kwds):
        ''' Create new cattr converter which is hooked up to all relevant (un-)structure hooks '''
        cattr_converter = cattr.Converter(*args, **kwds)
        cattr_converter = self._hook_cattr_converter(cattr_converter)
        return cattr_converter

    def _hook_cattr_converter(self, cattr_converter):
        cattr_converter.register_structure_hook(self._unit.Quantity, lambda d, t: t(d))
        cattr_converter.register_unstructure_hook(datetime.datetime, lambda dt: dt.isoformat())
        cattr_converter.register_structure_hook(datetime.datetime, lambda ts, _: parser.parse(ts))
        return cattr_converter

    def create_cattr_converter(self, *args, **kwds):
        ''' Create new cattr converter which is hooked up to all relevant (un-)structure hooks.
        Pass all arguments to this function to the constructor of the converter '''
        return self._create_cattr_converter(self, *args, **kwds)

    def serialize(self):
        cattr_converter = self.cattr
        def decorate_class(cls):
            def to_yaml(obj):
                return self.yaml.dump(cattr_converter.unstructure(obj))
        
            def from_yaml(raw_yaml):
                data = self.yaml.load(raw_yaml)

                try:
                    obj = cattr_converter.structure(data, cls)
                except BaseException as e:
                    if hasattr(cls, 'recover_deserialize'):
                        module_logger.debug(f'Deserialization failed, trying recovery of class {cls.__qualname__}) ({e})')                                            
                        data_recovered = cls.recover_deserialize(data)
                        obj = cattr_converter.structure(data_recovered, cls)
                        module_logger.debug(f'Recovery successful!')                                            
                    else:
                        module_logger.debug(f'Deserialization failed (no recovery available for class {cls.__qualname__}) ({e})')
                        raise

                return obj
            
            cls.serialize = to_yaml
            cls.deserialize = from_yaml
            return cls
        
        return decorate_class



