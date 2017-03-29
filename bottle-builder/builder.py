"""
"""

################################################################################
##### Command Line Interface ###################################################
################################################################################

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from tempfile import gettempdir
import os

parser = ArgumentParser(
    formatter_class=ArgumentDefaultsHelpFormatter,
    description=__doc__ )
parser.add_argument("-p", "--path",
    type=str,
    help="the path to the desired location of the generated site")
parser.add_argument("-d", "--deploy",
    action="store_true",
    help="package site for movement to deployment server. Default path is the"
    "current working directory, but the path flag will override that value" )
parser.add_argument("-r", "--reuse",
    action="store_true",
    help="if an already built website exists at the targeted path, attempt to"
    "reuse already present resources (i.e. images, favicon elements and other"
    "static resources)" )
args = parser.parse_args()

if args.path is None:
    args.path = os.getcwd()
    # if args.deploy:
    #     args.path = os.getcwd()
    # else:
    #     args.path = gettempdir()
