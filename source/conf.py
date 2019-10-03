# -*- coding: utf-8 -*-
#
# Ledger documentation build configuration file.

def setup(app):
    app.add_stylesheet('theme_overrides.css') # Override wide tables in RTD theme

# General Configuration
# =====================

extensions = []

source_suffix = ['.rst']

master_doc = 'index'

project = u'Ledger Documentation Hub'
copyright = u'2019 - 2020, Ledger Team'
author = u'Ledger Team'

version = u'2'
release = u'2'

pygments_style = 'sphinx'

# Options for HTML Output
# =======================

html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']

# intersphinx
# ===========

extensions += ['sphinx.ext.intersphinx']

intersphinx_mapping = {
    'python-loader': ('https://ledger.readthedocs.io/projects/blue-loader-python/en/0.1.15/', None)
}
