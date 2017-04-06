
"""
${doc_string}
"""
from bottle import run, route, get, post, error
from bottle import static_file, template, request
from bottle import HTTPError

$ph{Command Line Interface}
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from inspect import getframeinfo, currentframe
from os.path import dirname, abspath
import os

parser = ArgumentParser(
    formatter_class=ArgumentDefaultsHelpFormatter,
    description=__doc__ )
parser.add_argument('-d', '--deploy',
    action='store_true',
    help='Run server for deployment' )
parser.add_argument('-i', '--ip',
    type=str,
    default="127.0.0.1",
    help='ip to run the server against, default localhost' )
parser.add_argument('-p', '--port',
    type=str,
    default="8080",
    help='port to run server on' )
args = parser.parse_args()

# change working directory to script directory
os.chdir(dirname(abspath(getframeinfo(currentframe()).filename)))

$ph{Main Site Routes}
${main_routes}
$ph{API and Additional Site Routes}
${api_routes}

$ph{Static Routes}
${static_routes}
$sh{Favicon Routes}
${favicon_routes}
$sh{Image Routes}
${image_routes}
$sh{Font Routes}
${font_routes}
$sh{Stylesheet Routes}
${css_routes}
$sh{Javascript Routes}
${js_routes}
$ph{Error Routes}
@error(404)
def error404(error):
    return 'nothing to see here'

$ph{Run Server}
if args.deploy:
    run(host=args.ip, port=args.port, server='cherrypy') #deployment
else:
    run(host=args.ip, port=args.port, debug=True, reloader=True) #development
