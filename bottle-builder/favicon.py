"""
    bottle-builder.favicon
    ----------------------

    The favicon module provides methods for generating favicon resources from a
    provided .svg file, and for generating the optimal <head> elements for
    dictating access to those resources.

    :copyright: (c) 2017 by Nick Balboni.
    :license: MIT.
"""

__all__ = []

import os
from os.path import isfile, isdir, abspath, normpath, join
from overrides import sCall
from argparse import ArgumentParser, RawDescriptionHelpFormatter


##### Exceptions ################################################################

##### Constants ################################################################

### Filename Templates
favicon_tpl  = lambda r: "favicon-{0}x{0}.png".format(r)
android_tpl  = lambda r: "touch-icon-{0}x{0}.png".format(r)
apple_tpl    = lambda r: "apple-touch-icon-{0}x{0}.png".format(r)
precomp_tpl  = lambda r: "apple-touch-icon-{0}x{0}-precomposed.png".format(r)

### Resolution Lists
ico_res     = [ "16", "24", "32", "48", "64", "128", "256" ]
favicon_res = [ "16", "32", "96", "160", "196", "300" ]
android_res = [ "192" ]
apple_res   = [ "57", "76", "120", "152", "180" ] # add to head backwards

##### Helpers ##################################################################

##### Classes ##################################################################

class FaviconGenerator: # TODO: routes and precomposed

    def __init__(self, template_fp, result_fp):
        self.template_fp = abspath(template_fp)
        self.result_fp = abspath(join(result_fp, 'favicon'))
        self.result_path = lambda p: normpath(join(self.result_fp, p)) # normpath for windows users TODO: preferably get rid of this

    def _generate_pngs(self, res, file_tpl):
        path = self.result_path(file_tpl(res))
        if isfile(path): # dont recreate pngs
            return
        if not isfile(self.template_fp): #TODO: make this more pythonic (try/except)
            raise FileNotFoundError
        sCall('inkscape', '-z', '-e', path, '-w', res, '-h', res, self.template_fp)

    def _generate_ico(self):
        args = [ favicon_tpl(res) for res in ico_res ]
        args.append('favicon.ico')
        sCall('convert', *[ self.result_path(p) for p in args ])

    def generate_resources(self):
        os.makedirs(self.result_fp) # throws OSError (FileExistsError)
        for res in ico_res + favicon_res:
            self._generate_pngs(res, favicon_tpl)
        for res in android_res:
            self._generate_pngs(res, android_tpl)
        for res in apple_res:
            self._generate_pngs(res, apple_tpl)
        self._generate_ico()
        # clean up unnecessary files
        for res in ico_res:
            if res not in favicon_res:
                os.remove(self.result_path(favicon_tpl(res)))

    def _get_head_element(self, attrs):
        return "".join([
            '    <link', *[ ' {}="{}"'.format(*attr) for attr in attrs ], '>'
        ])

    def get_head_elements(self): # TODO: cached property?
        fav_head = [[('rel', 'shortcut icon'), ('href', 'favicon.ico')]]  # start with ico
        #resources = [ f for f in os.listdir(self.result_fp) if f.endswith('png') ]
        android_res_copy = list(android_res) # copy the list
        android_res_copy.reverse() # reverse it # .sort().reverse() ?
        for res in android_res_copy:
            filename = android_tpl(res)
            fp = self.result_path(filename)
            if not isfile(fp):
                print(fp, 'does not exist')
                return
            fav_head.append([
                ('rel', 'icon'),
                ('sizes', '{0}x{0}'.format(res)),
                ('href', '/{}'.format(filename))
            ])
        apple_res_copy = list(apple_res) # copy the list
        apple_res_copy.reverse() # reverse it # .sort().reverse() ?
        for res in apple_res_copy:
            filename = apple_tpl(res)
            fp = self.result_path(filename)
            if not isfile(fp):
                print(fp, 'does not exist')
                return
            fav_head.append([
                ('rel', 'apple-touch-icon'),
                ('sizes', '{0}x{0}'.format(res)),
                ('href', '/{}'.format(filename))
            ])
        favicon_res_copy = list(favicon_res) # copy the list
        favicon_res_copy.reverse() # reverse it # .sort().reverse() ?
        for res in favicon_res_copy:
            filename = favicon_tpl(res)
            fp = self.result_path(filename)
            if not isfile(fp):
                print(fp, 'does not exist')
                return
            fav_head.append([
                ('rel', 'icon'),
                ('type', 'image/png'),
                ('sizes', '{0}x{0}'.format(res)),
                ('href', '/{}'.format(filename))
            ])
        return '\n'.join([ self._get_head_element(attrs) for attrs in fav_head ])

    def generate(self):
        self.generate_resources()
        with open(self.result_path('head.html'), 'w') as f:
            f.write(self.get_head_elements())


##### Command Line Interface ###################################################

def parse_args():
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        'template_filepath',
        metavar='TPL',
        type=str,
        nargs='?',
        default='./favicon.svg',
        help='the filepath to an .svg of the favicon. (default "./favicon.svg")'
    )
    parser.add_argument(
        'result_path',
        metavar='RES',
        type=str,
        nargs='?',
        default='.',
        help='the path to put the resulting resources. (default ".")'
    )
    return parser.parse_args()

def main():
    options = parse_args()
    generator = FaviconGenerator(options.template_filepath, options.result_path)
    generator.generate()


if __name__ == '__main__':
    main()
