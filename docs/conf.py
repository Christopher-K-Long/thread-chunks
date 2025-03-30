# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'thread-chunks'
copyright = '2025, Christopher K. Long'
author = 'Christopher K. Long'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.coverage',
              'sphinx.ext.napoleon',
              'sphinx.ext.autosummary',
              'sphinx.ext.viewcode',
              'sphinx.ext.duration',
              'myst_parser',
              'stubdoc']

autosummary_generate = True # Turn on sphinx.ext.autosummary
autosummary_imported_members = True
# autodoc_inherit_docstrings = True
autodoc_member_order = "groupwise"
napoleon_include_init_with_doc = True
napoleon_numpy_docstring = True
viewcode_line_numbers = True
myst_heading_anchors = 5
suppress_warnings = ["myst.header"]
module_names = ["thread_chunks._remote_actor"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join('..', 'src')))