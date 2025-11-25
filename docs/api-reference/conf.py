# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import django

# -- Path setup --------------------------------------------------------------

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('../..'))
# Add the apps directory to sys.path
sys.path.insert(0, os.path.abspath('../../apps'))

# Setup Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'githubai.settings'
django.setup()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'GitHubAI'
copyright = '2025, GitHubAI Contributors'
author = 'GitHubAI Contributors'
release = '0.3.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    'sphinx_autodoc_typehints',
    'sphinxcontrib_django',
    'myst_parser',
]

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'

# Autosummary settings
autosummary_generate = True

# Django settings
django_settings = 'githubai.settings'

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'django': ('https://docs.djangoproject.com/en/5.1/', 'https://docs.djangoproject.com/en/5.1/_objects/'),
    'celery': ('https://docs.celeryq.dev/en/stable/', None),
}

# MyST Parser settings (for Markdown support)
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
    'display_version': True,
}

html_context = {
    'display_github': True,
    'github_user': 'bamr87',
    'github_repo': 'githubai',
    'github_version': 'main',
    'conf_py_path': '/docs/api-reference/',
}

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp',
}
