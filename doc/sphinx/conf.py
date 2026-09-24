"""Sphinx configuration."""

# -- Project information -----------------------------------------------------

project = "Repo Template"
author = "Sven Krummen"
copyright = "2026"

# -- General configuration ---------------------------------------------------

extensions = [
    'myst_parser',
    'sphinx.ext.intersphinx',
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

