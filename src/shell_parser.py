"""
Transform 
another example of lark usage
https://github.com/lark-parser/lark/blob/master/examples/calc.py
"""

from lark import Lark, Transformer, v_args
from application import create_application
from collections import deque
from command import *
from collections import namedtuple
import re

Iredirect = namedtuple("Iredirect", "data")
Oredirect = namedtuple("Oredirect", "data")
Argument = namedtuple("Argument", "data")
App = namedtuple("App", "data")


shell_grammar = """
    ?start: seq
    ?seq: pipe
        | pipe ";"" "* seq      -> create_seq
    ?pipe: call
         | call "|" " "* pipe    -> create_pipe
    ?redirection: "<" " "* iredir 
                | ">" " "* oredir
    ?iredir: arg -> iredir
    ?oredir: arg -> oredir
    ?call: (redirection " "+)* app (" "+ (arg | redirection))* " "*    -> create_app
    ?app: DATA                   -> app
    ?arg: DOUBLE_QUOTED_DATA     -> qarg 
    | SINGLE_QUOTED_DATA         -> qarg
    | DATA                       -> arg
    SPACE: /( |\t)+/
    DATA : /[0-9A-Za-z\.\/\-\,*\"]+/
    SINGLE_QUOTED_DATA: /\'[0-9A-Za-z\.\/\-\,*\" ]+\'/
    DOUBLE_QUOTED_DATA: /\"[0-9A-Za-z\.\/\-\,*\' ]+\"/
"""


@v_args(inline=True)
class ShellTree(Transformer):
    def data(self, s):
        return str(s)

    def iredir(self, s):
        return Iredirect(s)

    def oredir(self, s):
        return Oredirect(s)

    def arg(self, s):
        # print("arg", s)
        return Argument(s)

    def app(self, s):
        return App(s)

    def qarg(self, s):
        # print("qarg", s)
        s = s[1 : len(s) - 1]
        return Argument(s)

    def create_app(self, *args):
        app = ""
        iredir = ""
        oredir = ""
        data = []

        for arg in args:
            if isinstance(arg, App):
                app = arg.data
            elif isinstance(arg, Iredirect):
                iredir = arg.data
            elif isinstance(arg, Oredirect):
                oredir = arg.data
            else:
                data.append(arg.data)

        input = deque()

        if iredir != "":
            iredir = iredir.data
            with open(iredir, "r") as f:
                for line in f.readlines():
                    input.append(line)
            iredir = input

        if oredir != "":
            oredir = oredir.data

        # calling Call class
        return Call(create_application(app), data, iredir, oredir)

    def create_pipe(self, call, pipe):
        return Pipe(call, pipe)

    def create_seq(self, pipe, seq):
        return Seq(pipe, seq)

    def create_redirect():
        pass


def parse(cmdline):
    calc_parser = Lark(shell_grammar, parser="lalr", transformer=ShellTree())
    return calc_parser.parse(cmdline)
