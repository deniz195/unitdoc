import pytest
import os
from pathlib import Path

#get path to file and construct the dependencies for the db, pint, mvc accordingly
path_fn = os.path.dirname(os.path.abspath(__file__))
path_fn = Path(path_fn)
pint = path_fn.joinpath('..','..','pint')
ud  = path_fn.joinpath('..','unitdoc')

import sys
sys.path.append('..')
sys.path.insert(0, os.fspath(pint))
sys.path.insert(0, os.fspath(ud))

