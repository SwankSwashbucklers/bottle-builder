"""
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from tempfile import gettempdir
import os
import os.path
import shutil

from stylesheets import StylesheetGenerator
from favicon import FaviconGenerator


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
    os.chdir(options.path)
    try:
        os.makedirs('www', exist_ok=False)
    except OSError as e:
        shutil.rmtree('www')
        os.makedirs('www')

    # stylesheets
    styles_generator = StylesheetGenerator('dev/sass', 'www')
    styles_generator.generate()

    # favicons
    favicon_generator = FaviconGenerator('res/favicon.svg', 'www')
    favicon_generator.generate()


if __name__ == '__main__':
    main()
