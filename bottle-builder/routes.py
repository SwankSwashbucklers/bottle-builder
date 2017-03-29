"""
"""

SCRIPT_DIR   = os.getcwd()
PROJECT_NAME = relpath(SCRIPT_DIR, "..")
STATIC_ROUTE = lambda p, f, r: \
    ( STATIC_ROUTE_TEMPLATE, { "path": p, "file": f, "root": r } )
MAIN_ROUTE   = lambda p, m, t: \
    ( MAIN_ROUTE_TEMPLATE, { "path": p, "method_name": m, "template": t } )


## TEMPLATES

MAIN_ROUTE_TEMPLATE = Template("""\
@route('/${path}')
def ${method_name}():
    return template('${template}', request=request, template='${template}')
""" )


STATIC_ROUTE_TEMPLATE = Template("""\
@get('/${path}')
def load_resource():
    return static_file('${file}', root='${root}')
""" )



def migrate_files(directory, destination):
    src_path = join(SCRIPT_DIR, directory)
    if not isdir(destination): os.makedirs(destination)
    for root, dirs, files in os.walk(src_path):
        for dirname in dirs:
            if dirname.startswith('!') or dirname in ['.DS_STORE']:
                dirs.remove(dirname)
        for filename in files:
            if not filename.startswith('!') and filename not in ['.DS_Store']:
                if not isfile(filename): #added for the reuse flag
                    copy(join(root, filename), join(destination, filename))
                if not filename.startswith('~'):
                    yield normpath(join(relpath(root, src_path),
                                        filename) ).replace('\\', '/')


def migrate_views():
    routes = [ MAIN_ROUTE("", "load_root", "index") ]
    for route in migrate_files("dev/views", "views"):
        tpl_name = splitext(route.split("/")[-1])[0]
        if tpl_name == "index":
            continue
        routes.append(MAIN_ROUTE(
            splitext(route)[0],
            "load_" + tpl_name.replace("-","_"),
            tpl_name
        ))
    return routes


def get_api_routes():
    with open( join(SCRIPT_DIR, "dev/py", "routes.py"), 'r') as f:
        return f.read()
