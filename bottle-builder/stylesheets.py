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
from os.path import isfile, isdir, abspath, normpath, join, splitext
from shutil import rmtree


##### Helpers ##################################################################

def _is_sass(filepath, accept_partials=True):
    # TODO: implement accept_partials
    # NOTE: accepts an absolute path
    if not isfile(filepath):
        return False
    if not splitext(f)[-1].lower() in ['.scss', '.sass']:
        return False
    #if not accept_partials and  #split filename and check if it starts with _
    return True

def _get_imports(path, folder): # pass an absolute path
    imports = []
    import_tpl = lambda p: '@import "{}";'.format(p.replace('\\', '/'))
    for root, dirs, files in os.walk(folder):
        for f in files:
            if splitext(f)[-1].lower() in ['.scss', '.sass']:
                import_path = relpath(join(root, f), path)
                imports.append(import_tpl(import_path))
    return imports

# critical: _generate_all(self.src_dir, include_partials=False)
# non: _generate_all(join(self.src_dir, 'non-critical'))
def _generate_all(path, include_partials=True):
    # NOTE: mixins and global variables must be imported first
    imports = _get_imports(path, 'modules')
    if include_partials:
        imports += _get_imports(path, 'partials')
    with open(join(path, '_all.scss'), 'w') as f:
        f.write('\n'.join(imports))

def _generate_sass(src_fp, dest_fp, deploy=False):
    # TODO: watch.py (make this a global watch (views and js too))
    # TODO: make watch.py a part of this project and not a file that just gets dropped in
    output_style = "compressed" if deploy else "expanded"
    compiled_output = sass.compile(filename=src_path, output_style=output_style)
    with open(dest_fp, 'w') as f:
        f.write(compiled_output)

##### Stylesheet Generator Class ###############################################

class StylesheetGenerator:

    # assuming correct src structure
    # TODO: make the necessary directories? or at least gracefully handle if they dont exist
    def __init__(self, src_dir, dest_dir, deploy=False):
        self.src_dir = abspath(src_dir) # "dev/sass"
        self.dest_dir = abspath(join(dest_dir, 'css'))
        self.dest_path = lambda p: normpath(join(self.dest_dir, p))
        self.deploy = deploy

    ### HELPERS
    def _remove_artifacts():
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

    def _generate_non_critical():
        src_path = join(self.src_dir, 'non-critical')
        self._generate_all(src_path)
        # TODO: ignore .DS_Store files throughout this?
        for sass_file in os.listdir(src_path):
            # TODO: make _is_sass a helper function outside of this class
            # TODO: maybe a helper that lists the sass files in the directory,
            #       I think that's all I use this for anyway
            if _is_sass(abspath(join(src_path, sass_file))):
                self._generate_sass

    def _generate_critical():
        self._generate_all(self.src_dir, include_partials=False)

    def inline_critical_css():
        # take generated critical css, and the view file and inline in
        # TODO: raise exception if a css file exists with no view
        # NOTE: this is a combination of general and page specific
        pass

    ### MAIN
    def generate():
        # TODO: think about source maps
        # get the proper sass function

        # critical

        # non-critical
        if isdir('non-critical'):
            pass
        pass
