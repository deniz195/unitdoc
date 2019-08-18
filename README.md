# Unitdoc

Unitdoc is a Python library for dealing with data objects which need units for their properties and provide (de-)serialization for these objects. Unitdoc uses attrs, cattr, pint and ruamel.yamls packages to achieve this.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install unitdoc
```

Install from git repository
```bash
git clone https://github.com/deniz195/unitdoc
python unitdoc/setup.py install --user
```

## Usage

```python
import foobar

foobar.pluralize('word') # returns 'words'
foobar.pluralize('goose') # returns 'geese'
foobar.singularize('phenomena') # returns 'phenomenon'
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
