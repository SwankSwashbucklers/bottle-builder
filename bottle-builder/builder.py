"""
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from tempfile import gettempdir
import os
import os.path
import shutil

from stylesheets import StylesheetGenerator
from favicon import FaviconGenerator
from routes import RouteGenerator
from head import HeadGenerator


################################################################################
##### Command Line Interface ###################################################
################################################################################

def parse_args():
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        "-p", "--path",
        type=str,
        help="the path to the desired location of the generated site"
    )
    parser.add_argument(
        "-d", "--deploy",
        action="store_true",
        help="package site for movement to deployment server. Default path is the"
        "current working directory, but the path flag will override that value"
    )
    parser.add_argument(
        "-r", "--reuse",
        action="store_true",
        help="if an already built website exists at the targeted path, attempt to"
        "reuse already present resources (i.e. images, favicon elements and other"
        "static resources)"
    )
    args = parser.parse_args()
    if args.path is None:
        args.path = os.getcwd()
        # if args.deploy:
        #     args.path = os.getcwd()
        # else:
        #     args.path = gettempdir()
    return args

def main():
    options = parse_args()
    print(options.path)
    # NOTE: don't change the working directory so that you can use the the templates in this package
    os.chdir(options.path)
    try:
        os.makedirs('www', exist_ok=False)
    except OSError as e:
        shutil.rmtree('www')
        os.makedirs('www')

    # resources and views
    # NOTE: this must happen first because static must be copied first, TODO: I hate this
    routes_generator = RouteGenerator('.', 'www')
    routes_generator.copy_resources()
    routes_generator.copy_views()

    # stylesheets
    styles_generator = StylesheetGenerator('dev/sass', 'www/static')
    styles_generator.generate()

    # favicons
    favicon_generator = FaviconGenerator('res/favicon.svg', 'www/static')
    favicon_generator.generate_resources()

    # head elements
    head_generator = HeadGenerator('www', favicon_generator)
    head_generator.set_head()

    # TODO: remove head from favicons before generating app.py
    # TODO: parse out critical CSS before generating app.py
    routes_generator.populate_app_file()


if __name__ == '__main__':
    main()
