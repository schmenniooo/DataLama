import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "DataLens"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

html_theme = "furo"
