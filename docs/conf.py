import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "DataLens"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": True
}

html_theme = "furo"
