"""
    bottle-builder.head
    -------------------

    This module handles the generation of the necessary <head> elements.  It
    then modifies the project's ~head.tpl file, replacing the following <meta>
    tags with their corresponding generated html snippets:

        <meta name="favicon_elements">
        <meta name="open_graph">
        <meta name="style_sheets">

    :copyright: (c) 2017 by Nick Balboni.
    :license: MIT.
"""

__all__ = [ 'HeadGenerator' ]

import os
import os.path
from os.path import normpath, abspath, join, isfile

from overrides import Template


##### Constants ################################################################

METAS = [ "Favicon_Resources", "Open_Graph", "Style_Sheets" ]

### Head Templates

OPENGRAPH_HEAD = """\
    % url = request.environ['HTTP_HOST']
    <meta property="og:url" content="http://{{url}}/">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{{title}}">
    <meta property="open_graph_image">
    <meta property="og:description" content="{{description}}">"""

OPENGRAPH_IMAGE_HEAD = """<meta property="og:image:type" content="image/png">
    <meta property="og:image:width" content="300">
    <meta property="og:image:height" content="300">
    <meta property="og:image:url" content="http://{{url}}/favicon-300x300.png">
    <meta property="og:image" content="http://{{url}}/favicon-300x300.png">"""

STYLE_SHEET_HEAD_EL = """\
    <link rel="stylesheet" type="text/css" href="/{0}">
"""

STYLE_SHEET_PAGES = """\
    % if template in {}:
    <link rel="stylesheet" type="text/css" href="/{{template}}.css">
    % end"""


##### Helpers ##################################################################

def _is_css(filepath): # NOTE: accepts an absolute path
    if not isfile(filepath):
        return False
    f = os.path.split(filepath)[-1]
    if not os.path.splitext(f)[-1].lower() == '.css':
        return False
    return True


##### Head Generator Class #####################################################

class HeadGenerator:

    def __init__(self, dest_dir, favicon_generator):
        self.dest_path = lambda *p: normpath(abspath(join(dest_dir, *p))) # www
        self.favicon_generator = favicon_generator

    def _get_favicon_head(self):
        return self.favicon_generator.get_head_elements()

    def _get_opengraph_head(self):
        if isfile(self.dest_path('static', 'favicon', 'favicon-300x300.png')):
            return OPENGRAPH_HEAD.replace(
                '<meta property="open_graph_image">',
                OPENGRAPH_IMAGE_HEAD
            )
        return OPENGRAPH_HEAD

    def _get_style_sheet_head(self):
        styles_head = ''
        # TODO: inline critical before you get head elements
        stylesheets = []
        for sheet in os.listdir(self.dest_path('static', 'css')):
            if _is_css(self.dest_path('static', 'css', sheet)):
                stylesheets.append(os.path.splitext(sheet)[0])
        if 'styles' in stylesheets:
            stylesheets.remove('styles')
            styles_head += STYLE_SHEET_HEAD_EL.format('styles.css')
        return styles_head + STYLE_SHEET_PAGES.format(stylesheets)

    def set_head(self):
        head_tpl = ''
        fp = self.dest_path('views', '~head.tpl')
        with open(fp, 'r') as f:
            head_tpl = f.read()
        for meta in METAS:
            head_tpl = head_tpl.replace(
                '<meta name="'+meta.lower()+'">',
                '\n$wh{'+meta.replace('_', ' ')+'}\n${'+meta.lower()+'}'
            )
        Template.populate(Template(head_tpl), fp,
            favicon_resources=self._get_favicon_head(),
            open_graph=self._get_opengraph_head(),
            style_sheets=self._get_style_sheet_head()
        )
