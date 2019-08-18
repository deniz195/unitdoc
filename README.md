# Unitdoc

Unitdoc is a Python library for dealing with data objects which describe physical objects with units and easy serialization. Let's look at an example. First, import unitdoc and create the registry that you will use in your application:
```python
from unitdoc import UnitDocRegistry

udr = UnitDocRegistry()
```

Let's create a class that represents a battery
```python
import attr

@udr.serialize()   
@attr.s()
class Battery(object):
    name = attr.ib()

    weight = udr.attrib(default='45g', description ='Total weight')
    volume = udr.attrib(default='16ml', description ='Total volume')
    capacity = udr.attrib(default='3.0Ah', description ='Total capacity')
    voltage = udr.attrib(default='3.6V', description ='Average voltage')
```

We can create an instance of `Battery`, which will be a normal `attr` object, which features e.g. a nice `repr` function:
```python
a_battery = Battery(name = 'battery', weight='43g')
print(a_battery)
# outputs: Battery(name='battery', weight=&lt Quantity(43, 'gram')&gt, volume=&ltQuantity(16, 'milliliter')&gt, capacity=&ltQuantity(3.0, 'Ah')&gt, voltage=&ltQuantity(3.6, 'volt')&gt)
```

We can use the attributes of the battery in any operation that are allowed by the pint package:
```python
energy = (a_battery.capacity * a_battery.voltage).to('Wh')
energy_density = (energy / a_battery.weight).to('Wh/kg')
print(f'{energy} @  {energy_density}')
# outputs: 10.8 Wh @  251.2 Wh / kg
```

Now let's save and reload our battery object:
```python
# look at serialized form
print(a_battery.serialize())

# outputs:
name: battery
weight: !unit 43 g
volume: !unit 16 ml
capacity: !unit 3 Ah
voltage: !unit 3.6 V
```

This can be easily saved to a file and reloaded again:
```python
fn = 'a_battery.yaml'
# save to yaml file
with open(fn, 'w') as f:
    f.write(a_battery.serialize())

# load from yaml file
with open(fn, 'r') as f:
    a_loaded_battery = Battery.deserialize(f.read())

assert a_battery == a_loaded_battery    
```


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install unitdoc:

```bash
pip install unitdoc
```

Alternatively, install the latest version from git:
```bash
git clone https://github.com/deniz195/unitdoc
python unitdoc/setup.py install --user
```

## Related packages
Unitdoc is based on the following amazing packages:

- [pint](https://pint.readthedocs.io/) deals with the units
- [ruamel.yamls](https://yaml.readthedocs.io/en/latest/) deals with (de)serializing from semi-structured data (nested dictionaries)
- [attrs](https://github.com/python-attrs/attrs) deals with the boilerplate of data classes
- [cattr](https://github.com/Tinche/cattrs) deals with the unstructuring and restructuring of classes for (de)serialization

The UnitDocRegistry creates registries/converters/parsers for each package and aggregates them. You can leverage the features of each package:

Use unit registry from pint:
```python
q = udr.ureg('1000gram').to('kg')
print(q)
# outputs: 1 kg
```

Use yaml parser from ruaml.yaml:
```python
q_yaml = udr.yaml.dump(dict(weight=q))
print(q_yaml)
# outputs: weight: !unit 1 kg
```

Use cattr converter:
```python
@udr.serialize()   
@attr.s()
class Thing(object):
    weight = udr.attrib(default='45g', description ='Total weight')

a_thing = Thing()
a_thing_dict = udr.cattr.unstructure(a_thing)

assert type(a_thing_dict) == dict
print(a_thing_dict['weight'])
# output: 45 g
```


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
