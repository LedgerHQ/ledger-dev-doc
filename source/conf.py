# -*- coding: utf-8 -*-
#
# Ledger documentation build configuration file.

# General Configuration
# =====================

extensions = []

source_suffix = ['.rst']

master_doc = 'index'

project = u'Ledger Documentation Hub'
copyright = u'2016 - 2017, Ledger Team'
author = u'Ledger Team'

version = u'1'
release = u'1'

pygments_style = 'sphinx'

# Options for HTML Output
# =======================

html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']

html_context = {
    'css_files': [
        '_static/theme_overrides.css', # Override wide tables in RTD theme
    ],
}

# intersphinx
# ===========

extensions += ['sphinx.ext.intersphinx']

intersphinx_mapping = {
    'python-loader': ('https://ledger.readthedocs.io/projects/blue-loader-python/en/0.1.14/', None)
}
