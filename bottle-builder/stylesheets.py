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


##### Constants ################################################################

### Templates

EMBEDED_CSS_BLOCK = """\
<%
embeded_css = \"""{}\"""
%>
"""

STYLE_SHEET_HEAD_EL = """\
<link rel="stylesheet" type="text/css" href="/{0}">
"""

DEFERRED_STYLES_FOOTER_BLOCK = """\
    <noscript id="deferred-styles">
        {0}
        % if defined('template') and template in {1}:
        <link rel="stylesheet" type="text/css" href="/{{{{template}}}}.css">
        % end
    </noscript>
    <script>
        var loadDeferredStyles = function() {{
            var addStylesNode = document.getElementById("deferred-styles");
            var replacement = document.createElement("div");
            replacement.innerHTML = addStylesNode.textContent;
            document.body.appendChild(replacement)
            addStylesNode.parentElement.removeChild(addStylesNode);
        }};
        var raf = requestAnimationFrame || mozRequestAnimationFrame ||
            webkitRequestAnimationFrame || msRequestAnimationFrame;
        if (raf) raf(function() {{ window.setTimeout(loadDeferredStyles, 0); }});
        else window.addEventListener('load', loadDeferredStyles);
    </script>
"""


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

def _is_css(filepath): # NOTE: accepts an absolute path
    if not isfile(filepath):
        return False
    f = os.path.split(filepath)[-1]
    if not os.path.splitext(f)[-1].lower() == '.css':
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

    def _get_general_critical_css(self):
        try:
            with open(self.dest_path('critical', 'styles.css'), 'r') as f:
                return f.read()
        except FileNotFoundError:
            pass
        except Exception as e:
            print('Error opening file', e)
        return ''

    def _get_critical_css(self, page):
        try:
            with open(self.dest_path('critical', page + '.css'), 'r') as f:
                return f.read()
        except FileNotFoundError:
            pass
        except Exception as e:
            print('Error opening file', e)
        return ''

    def _get_views(self):
        # TODO: doesn't return nested views
        # TODO: check if it ends with .tpl?
        views_files = os.listdir(self.dest_path('..', '..', 'views'))
        def is_view(x):
            return (not x.startswith('~')
                and not x.startswith('!')
                and isfile(self.dest_path('..', '..', 'views', x)))
        views = map(
            lambda x: os.path.splitext(os.path.split(x)[-1])[0],
            filter(is_view, views_files)
        )
        return list(views)

    def _inline_css(self, page, embeded_css):
        # add the embeded_css variable to the top of the template
        # if there is css to embed
        if not embeded_css:
            return
        fp = self.dest_path('..', '..', 'views', page + '.tpl')
        try:
            file_contents = ''
            with open(fp, 'r') as f:
                file_contents = f.read()
            with open(fp, 'w') as f:
                f.write(EMBEDED_CSS_BLOCK.format(embeded_css) + file_contents)
        except FileNotFoundError:
            pass
        except Exception as e:
            print('Error opening file', e)

    def _get_deferred_styles(self):
        styles_block = ''
        # TODO: inline critical before you get stylesheets
        stylesheets = []
        for sheet in os.listdir(self.dest_path()):
            if _is_css(self.dest_path(sheet)):
                stylesheets.append(os.path.splitext(sheet)[0])
        if 'styles' in stylesheets:
            stylesheets.remove('styles')
            styles_block = STYLE_SHEET_HEAD_EL.format('styles.css')
        return DEFERRED_STYLES_FOOTER_BLOCK.format(styles_block, stylesheets)

    def inline_critical_css(self):
        # take generated critical css, and the view file and inline in
        # TODO: raise exception if a css file exists with no view
        # NOTE: this is a combination of general and page specific
        general_inline_css = self._get_general_critical_css()
        for view in self._get_views():
            embeded_css = general_inline_css + self._get_critical_css(view)
            self._inline_css(view, embeded_css)
        rmtree(self.dest_path('critical'))

    def load_deferred_styles(self):
        try:
            fp = self.dest_path('..', '..', 'views', '~footer.tpl')
            with open(fp, 'a') as f:
                f.write(self._get_deferred_styles())
        except FileNotFoundError:
            pass
        except Exception as e:
            print('Error opening file', e)

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
