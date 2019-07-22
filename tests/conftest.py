import pytest
import os
from pathlib import Path

#get path to file and construct the dependencies for the db, pint, mvc accordingly
path_fn = os.path.dirname(os.path.abspath(__file__))
path_fn = Path(path_fn)
ud  = path_fn.joinpath('..','unitdoc')
pint_mt= path_fn.joinpath('..','..','pint-mtools')
attr_description_mt= path_fn.joinpath('..','..','attr-descriptions')

import sys
sys.path.append('..')
sys.path.insert(0, os.fspath(ud))
sys.path.insert(0, os.fspath(pint_mt))
sys.path.insert(0, os.fspath(attr_description_mt))