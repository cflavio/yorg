# -*- coding: utf-8 -*-
'''This module contains Sphinx's configuration.'''

import sys
import os
import datetime

sys.path.insert(0, os.path.abspath('<src_path>'))

extensions = [
    'sphinx.ext.autodoc',
    #'sphinx.ext.viewcode'  # it crashes
    ]
source_suffix = '.rst'
master_doc = 'index'
project = u'<name>'
copyright = u'%s, Ya2' % datetime.datetime.now().year
version = '<version>'
release = '<version>'
pygments_style = 'sphinx'
html_theme = 'ya2'
html_theme_path = ['.']
html_theme_options = {'rightsidebar': 'true'}
html_sidebars = {'*': ['localtoc.html', 'relations.html', 'sourcelink.html',
                       'searchbox.html', 'ads.html']}
html_last_updated_fmt = '%b %d, %Y'
html_show_sphinx = False
html_show_copyright = False
htmlhelp_basename = '<name>doc'
