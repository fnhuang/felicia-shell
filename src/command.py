from application import UnsafeDecorator, Application, create_application
from collections import deque
from typing import List
from dataclasses import dataclass


# TODO: change applications (stdin)
# TODO: check pytest applications
# TODO: check pytest command


class Command:
    def eval(self, input, output):
        return output

# dataclass decorator allows the object to be printed in an understandable manner
# because it automatically generates the `__str__()` method 
@dataclass
class Call(Command):
    app: Application
    args: List[str]
    inp: deque
    out: str

    def __init__(self, app, args, inp, out):

        self.app = app
        self.args = args
        self.inp = inp
        self.out = out

    def eval(self, input, output):
        input.extend(self.inp)

        if len(self.out) > 0:
            newout = deque()
            self.app.execute(self.args, input, newout)
            with open(self.out, "w") as outfile:
                outfile.writelines(newout)
        else:
            self.app.execute(self.args, input, output)


@dataclass
class Pipe(Command):
    left_obj: Command
    right_obj: Command

    def __init__(self, left_obj, right_obj):
        self.left_obj = left_obj
        self.right_obj = right_obj

    def eval(self, input, output):
        inter = deque()
        self.left_obj.eval(input, inter)
        self.right_obj.eval(inter, output)


@dataclass
class Seq(Command):
    left_obj: Command
    right_obj: Command

    def __init__(self, left_obj, right_obj):
        self.left_obj = left_obj
        self.right_obj = right_obj

    def eval(self, input, output):
        self.left_obj.eval(input, output)
        self.right_obj.eval(deque(), output)


if __name__ == "__main__":
    c = Command()
    c.eval("cat 123.txt")
