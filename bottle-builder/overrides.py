"""
    Overrides of standard python classes and functions to provide customized
    behavior and windows/mac compatibility.
"""

__all__ = [ "Template", "sCall", "sPopen" ]


##### Template #################################################################

from string import Template
from re import compile

class TemplateWrapper:

    def __init__(self, cls):
        PYTHON_LL = 80
        HTML_LL   = 112

        self.cls = cls
        self.headers = [
            (   # Primary python file header template
                compile(r'\$ph{(.*?)}'),
                lambda x: "\n\n{1}\n##### {0} {2}\n{1}\n".format(
                    x.upper(), '#'*PYTHON_LL, '#'*(PYTHON_LL-len(x)-7) )
            ),
            (   # Secondary python file header template
                compile(r'\$sh{(.*?)}'),
                lambda x: "\n### {0} {1}".format(
                    x, '#'*(PYTHON_LL-len(x)-5) )
            ),
            (   # HTML file header template
                compile(r'\$wh{(.*?)}'),
                lambda x: "<!-- ***** {0} {1} -->".format(
                    x, '*'*(HTML_LL-len(x)-16) )
            )
        ]

    def __call__(self, template):
        for header in self.headers:
            ptn, tpl = header
            for match in ptn.finditer(template):
                replacements = ( match.group(0), tpl(match.group(1)) )
                template = template.replace(*replacements)
        template_obj = self.cls(template)
        template_obj.populate = self.populate
        return template_obj

    @staticmethod
    def populate(template, filepath, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, list):
                kwargs[key] = "\n".join(
                    [ t[0].safe_substitute(**t[1]) for t in value ]
                )
        try:
            with open(filepath, 'w') as f:
                f.write(template.safe_substitute(**kwargs))
        except Exception as exception:
            raise exception

Template = TemplateWrapper(Template)


##### System Calls #############################################################

from subprocess import Popen, call, DEVNULL, STDOUT, PIPE
from sys import executable
import os

def sPopen(*args):
    command, shell = list(args), True
    if command[0] == 'python':
        command[0] = executable
        shell = False
    if os.name == 'nt':
        from subprocess import CREATE_NEW_CONSOLE
        return Popen( command, shell=shell, creationflags=CREATE_NEW_CONSOLE )
    else:
        return Popen( command, shell=shell )

def sCall(*args):
    command, shell = list(args), True
    if command[0] == 'python':
        command[0] = executable
        shell = False
    if os.name != 'nt':
        shell = False
    call( command, shell=shell, stdout=DEVNULL, stderr=STDOUT )
