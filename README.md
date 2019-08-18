# Unitdoc

Unitdoc is a Python library for dealing with data objects which need units for their properties and provide (de-)serialization for these objects. Unitdoc uses attrs, cattr, pint and ruamel.yamls packages to achieve this.

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

## Usage

First, import unitdoc and create the registry that you will use in your application:
```python
import attr
from unitdoc import UnitDocRegistry

udr = UnitDocRegistry()
```

Let's create a class that represents a battery
```python
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
# outputs: Battery(name='battery', weight=<Quantity(43, 'gram')>, volume=<Quantity(16, 'milliliter')>, capacity=<Quantity(3.0, 'Ah')>, voltage=<Quantity(3.6, 'volt')>)
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





## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
