"""
    bottle-builder.routes
    ---------------------

    This module handles the copying of static resources and views, and the
    generations of routes and the app.py file.

    :copyright: (c) 2017 by Nick Balboni.
    :license: MIT.
"""

__all__ = [ 'RouteGenerator' ]

import os
import os.path
from os.path import normpath, abspath, join, relpath
import shutil

from overrides import Template


##### Constants ################################################################

IGNORED_FILES = [ '.DS_Store' ]

### Route Templates

MAIN_ROUTE_TEMPLATE = Template("""\
@route('/${path}')
def ${method_name}():
    return template('${template}', request=request, template='${template_name}')
""" )

STATIC_ROUTE_TEMPLATE = Template("""\
@get('/${path}')
def load_resource():
    return static_file('${file}', root='${root}')
""" )


##### Route Generator Class ####################################################

class RouteGenerator:

    def __init__(self, src_dir, dest_dir):
        self.src_path = lambda *p: normpath(abspath(join(src_dir, *p))) # root
        self.dest_path = lambda *p: normpath(abspath(join(dest_dir, *p))) # www

    def _copy_resource(self, src_folder, dest_folder):
        src = self.src_path('res', src_folder)
        if not os.path.isdir(src):
            print('Folder res/'+ src_folder, 'not found')
            return
        dest = self.dest_path('static', dest_folder)
        os.mkdir(dest)
        for root, dirs, files in os.walk(src):
            path = relpath(root, src)
            for dirname in dirs:
                print(dirname)
                os.mkdir(join(dest, path, dirname))
            for filename in files:
                if filename.startswith('~'):
                    continue
                if filename in IGNORED_FILES:
                    continue
                shutil.copy(
                    join(root, filename),
                    join(dest, path, filename)
                )

    def copy_resources(self):
        # NOTE: copy resources over and then generate the routes
        # NOTE: static must be copied first
        self._copy_resource('static', '')
        self._copy_resource('img', 'img')
        self._copy_resource('font', 'font')

    def copy_views(self):
        shutil.copytree(
            self.src_path('dev', 'views'),
            self.dest_path('views')
        )

    def _get_routes(self, folder):
        for root, _, files in os.walk(self.dest_path(folder)):
            for filename in files:
                if filename.startswith('~'):
                    # don't create routes for ~ prefixed files
                    continue
                yield normpath(join(
                    relpath(root, self.dest_path(folder)),
                    filename
                )).replace('\\', '/')

    def _get_static_routes(self, folder):
        ret_routes = []
        for route in self._get_routes(folder):
            ret_routes.append((
                STATIC_ROUTE_TEMPLATE,
                {
                    'path': route,
                    'file': route,
                    'root': folder,
                }
            ))
        return ret_routes

    def get_main_routes(self):
        # strip extensions from the routes
        routes = [ os.path.splitext(r)[0] for r in self._get_routes('views') ]
        ret_routes = []
        for route in routes:
            if route == 'index':
                # specific route for index
                ret_routes.append((
                    MAIN_ROUTE_TEMPLATE,
                    {
                        'path': '',
                        'method_name': 'load_route',
                        'template': 'index',
                        'template_name': 'index',
                    }
                ))
                continue
            method_name = route.replace("-","_").replace("/","__")
            ret_routes.append((
                MAIN_ROUTE_TEMPLATE,
                {
                    'path': route,
                    'method_name': 'load_' + method_name,
                    'template': route,
                    'template_name': os.path.split(route)[-1],
                }
            ))
        return ret_routes

    def get_api_routes(self):
        with open( self.src_path('dev', 'py', 'routes.py'), 'r') as f:
            return f.read()

    def get_static_routes(self):
        # TODO: support for custom static folders
        routes = []
        for filename in os.listdir(self.dest_path('static')):
            if not os.path.isfile(filename):
                continue
            routes.append((
                STATIC_ROUTE_TEMPLATE,
                {
                    'path': filename,
                    'file': filename,
                    'root': 'static',
                }
            ))
        return routes

    def get_favicon_routes(self):
        return self._get_static_routes('static/favicon')

    def get_image_routes(self):
        return self._get_static_routes('static/img')

    def get_font_routes(self):
        return self._get_static_routes('static/font')

    def get_css_routes(self):
        return self._get_static_routes('static/css')

    def get_js_routes(self):
        return self._get_static_routes('static/js')

    def populate_app_file(self):
        # Read template file into a string
        with open('./templates/app.py') as app_tpl:
            Template.populate(Template(app_tpl.read()), self.dest_path('app.py'),
                doc_string="",
                main_routes=self.get_main_routes(),
                api_routes=self.get_api_routes(),
                static_routes=self.get_static_routes(),
                favicon_routes=self.get_favicon_routes(),
                image_routes=self.get_image_routes(),
                font_routes=self.get_font_routes(),
                css_routes=self.get_css_routes(),
                js_routes=self.get_js_routes()
            )
