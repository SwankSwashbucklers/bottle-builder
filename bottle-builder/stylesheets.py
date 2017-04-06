"""
    bottle-builder.stylesheets
    --------------------------

    The stylesheets module provides methods for generating the CSS files from
    the SCSS source files.  It also provides generation of bottle code to be
    inserted in the <head> which allows for specific stylesheets to be loaded
    for specific pages.  And defers non-render-blocking CSS to be loaded further
    on down the chain.

    Requirements:
    * libsass

    :copyright: (c) 2017 by Nick Balboni.
    :license: MIT.
"""

__all__ = [ 'StylesheetGenerator' ]

import sass
import os
import os.path
from os.path import isfile, isdir, abspath, normpath, join, relpath
from shutil import rmtree


##### Helpers ##################################################################

def _is_sass(filepath, accept_partials=True): # NOTE: accepts an absolute path
    if not isfile(filepath):
        return False
    f = os.path.split(filepath)[-1]
    if not os.path.splitext(f)[-1].lower() in ['.scss', '.sass']:
        return False
    if not accept_partials and f.startswith('_'):
        return False
    return True

def _get_imports(path, folder): # pass an absolute path
    imports = []
    import_tpl = lambda p: '@import "{}";'.format(p.replace('\\', '/'))
    for root, dirs, files in os.walk(join(path, folder)):
        for f in files:
            if _is_sass(abspath(join(root, f))):
                # TODO: remove leading _ for partials and split extension?
                import_path = relpath(join(root, f), path)
                imports.append(import_tpl(import_path))
    return imports

def _generate_all(path, include_partials=True):
    # NOTE: mixins and global variables must be imported first
    imports = _get_imports(path, 'modules')
    if include_partials:
        imports += _get_imports(path, 'partials')
    with open(join(path, '_all.scss'), 'w') as f:
        f.write('\n'.join(imports))

##### Stylesheet Generator Class ###############################################

class StylesheetGenerator:

    # assuming correct src structure
    # TODO: make the necessary directories? or at least gracefully handle if they dont exist
    def __init__(self, src_dir, dest_dir, deploy=False):
        self.src_dir = abspath(src_dir) # "dev/sass"
        self.dest_dir = abspath(join(dest_dir, 'css'))
        self.dest_path = lambda *p: normpath(join(self.dest_dir, *p))
        self.deploy = deploy

    ### HELPERS
    def _remove_artifacts(self):
        # TODO: delete the `critical` folder in `css` with this method?
        files_to_remove = [ '_all.scss' ]
        directories_to_remove = [ '.sass-cache' ]
        for root, dirs, files in os.walk(self.src_dir):
            for d in dirs:
                if d in directories_to_remove:
                    rmtree(join(root, d))
            for f in files:
                if f in files_to_remove:
                    os.remove(join(root, f))

    def _generate_sass(self, src_fp, dest_fp):
        # TODO: watch.py (make this a global watch (views and js too))
        # TODO: make watch.py a part of this project and not a file that just gets dropped in
        output_style = "compressed" if self.deploy else "expanded"
        compiled_output = sass.compile(filename=src_fp, output_style=output_style)
        with open(dest_fp, 'w') as f:
            f.write(compiled_output)

    def _generate_non_critical(self):
        src_path = join(self.src_dir, 'non-critical')
        _generate_all(src_path)
        # TODO: ignore .DS_Store files throughout this? (not relevent cause of _is_sass)
        for sass_file in os.listdir(src_path):
            # TODO: make _is_sass a helper function outside of this class
            # TODO: maybe a helper that lists the sass files in the directory,
            #       I think that's all I use this for anyway
            fp = join(src_path, sass_file)
            if _is_sass(fp, accept_partials=False):
                dest_file = os.path.splitext(sass_file)[0] + '.css' # TODO: min if deploy
                self._generate_sass(fp, self.dest_path(dest_file))

    def _generate_critical(self):
        _generate_all(self.src_dir, include_partials=False)
        for sass_file in os.listdir(self.src_dir):
            fp = join(self.src_dir, sass_file)
            if _is_sass(fp, accept_partials=False):
                dest_file = os.path.splitext(sass_file)[0] + '.css' # TODO: min if deploy
                self._generate_sass(fp, self.dest_path('critical', dest_file))

    def inline_critical_css(self):
        # take generated critical css, and the view file and inline in
        # TODO: raise exception if a css file exists with no view
        # NOTE: this is a combination of general and page specific
        pass

    ### MAIN
    def generate(self):
        # TODO: think about source maps
        try: # create destination path
            os.makedirs(self.dest_dir, exist_ok=False)
        except OSError as e:
            rmtree(self.dest_dir)
            os.makedirs(self.dest_dir)

        # critical
        os.makedirs(self.dest_path('critical'))
        self._generate_critical()

        # non-critical
        if isdir(join(self.src_dir, 'non-critical')):
            self._generate_non_critical()
