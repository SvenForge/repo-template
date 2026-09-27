"""Sphinx configuration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

# -- Project information -----------------------------------------------------

project = 'Repo Template'
author = 'Sven Krummen'
copyright = '2026'

# -- General configuration ---------------------------------------------------

extensions = [
    'myst_parser',
    'sphinx.ext.intersphinx',
    'sphinx.ext.apidoc',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]

root_doc = 'doc/sphinx/index'
needs_sphinx = '8.2'
exclude_patterns = [
    '.*',
    '**/.*',
    'AGENTS.md',
    'README.md',
    'doc/sphinx/_build',
    'template',
]
exclude_patterns.extend(
    f'doc/sphinx/_apidoc/{path.name}'
    for path in (Path(__file__).parent / '_apidoc').glob('*')
    if path.name not in ['test_template']
)

# -- Options for HTML output -------------------------------------------------

html_theme = 'furo'

html_context = {
    'body': '<meta http-equiv="refresh" content="0; url=doc/sphinx/index.html">',
}
html_additional_pages = {
    'index': 'page.html',
}

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
}

# -- Options for apidoc / autodoc extensions ---------------------------------

apidoc_modules = [
    {
        'path': '../../src/test_template',
        'destination': 'doc/sphinx/_apidoc/test_template',
    },
]
autodoc_default_options = {
    'members': True,
    'show-inheritance': True,
}
autodoc_typehints = 'description'

# -- Options for napoleon extension ------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = False
