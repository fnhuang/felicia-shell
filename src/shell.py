import re
import sys
import os
from os import listdir
from collections import deque
from glob import glob

"""class Command:
    def eval(self, input, output):
        pass

class Call(Command):
    def eval(self, input, output):
        pass

class Seq(Command):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self, input, output):
        self.left(input, output)
        self.right(None, output)

def eval(cmdline, input, output):
    command = parse_command(cmdline)
    command.eval(input, output)

def parse_command(cmline):
    pass"""


def eval(cmdline, out):
    raw_commands = []

    # find command that matches any character other than " ' ;
    # or any word surrounded by "", that is not "
    # or any word surrounded by '', that is not '
    # for each non-overlapping match
    for m in re.finditer("([^\"';]+|\"[^\"]*\"|'[^']*')", cmdline):
        # if there is a match (each match is considered a command)
        if m.group(0):
            # get the match and append it to raw commands
            raw_commands.append(m.group(0))

    # for each command
    for command in raw_commands:
        tokens = []

        # find token that matches any character other than whitespace and "
        # or any word surrounded by "", that is not "
        # or any word surrounded by '', that is not '
        # for each non-overlapping match
        for m in re.finditer("[^\\s\"']+|\"([^\"]*)\"|'([^']*)'", command):
            # if there is a match for second or third condition
            # group(1) literally means the first parenthesized subgroup (thus, excluding the quotes)
            if m.group(1) or m.group(2):
                # group (0) means the entire match (thus, including quotes)
                quoted = m.group(0)
                # remove the quotes and add into the list of tokens
                tokens.append(quoted[1:-1])
            else:
                # glob function is a module that search for a search for files where the filename matches a certain pattern
                # by using wildcard characters.
                globbing = glob(m.group(0))
                if globbing:
                    # globbing returns an array of file names that match
                    tokens.extend(globbing)
                else:
                    # add into tokens
                    tokens.append(m.group(0))

        # given no piping and IO redirection
        # the first word of a token must be an application
        app = tokens[0]
        args = tokens[1:]
        if app == "pwd":
            # get the current directory
            out.append(os.getcwd())
        elif app == "cd":
            if len(args) == 0 or len(args) > 1:
                raise ValueError("wrong number of command line arguments")
            # change directory to the ones specified in the argument
            os.chdir(args[0])
        elif app == "echo":
            # out is a deque
            out.append(" ".join(args) + "\n")
        elif app == "ls":
            if len(args) == 0:
                # get the current working directory
                ls_dir = os.getcwd()
            elif len(args) > 1:
                raise ValueError("wrong number of command line arguments")
            else:
                ls_dir = args[0]

            # list all the files inside lis_dir
            for f in listdir(ls_dir):
                if not f.startswith("."):
                    out.append(f + "\n")
        elif app == "cat":
            for a in args:
                with open(a) as f:
                    # calling file object to read the file and return string
                    out.append(f.read())
        elif app == "head":
            # head command only have 1 or 3 arguments
            if len(args) != 1 and len(args) != 3:
                raise ValueError("wrong number of command line arguments")
            if len(args) == 1:
                num_lines = 10
                file = args[0]
            if len(args) == 3:
                if args[0] != "-n":
                    raise ValueError("wrong flags")
                else:
                    num_lines = int(args[1])
                    file = args[2]
            with open(file) as f:
                lines = f.readlines()
                # print out the first x lines of a file where x is num_lines
                for i in range(0, min(len(lines), num_lines)):
                    out.append(lines[i])
        # this function is almost similar to head
        elif app == "tail":
            if len(args) != 1 and len(args) != 3:
                raise ValueError("wrong number of command line arguments")
            if len(args) == 1:
                num_lines = 10
                file = args[0]
            if len(args) == 3:
                if args[0] != "-n":
                    raise ValueError("wrong flags")
                else:
                    num_lines = int(args[1])
                    file = args[2]
            with open(file) as f:
                lines = f.readlines()
                display_length = min(len(lines), num_lines)
                for i in range(0, display_length):
                    out.append(lines[len(lines) - display_length + i])
        # grep needs to have at least 1 argument
        elif app == "grep":
            # minimum number of argument for grep is 2
            if len(args) < 3:
                raise ValueError("wrong number of command line arguments")
            # grep tries to find a pattern of each line in a file
            pattern = args[0]
            files = args[1:]
            for file in files:
                with open(file) as f:
                    lines = f.readlines()
                    for line in lines:
                        # if there is a match
                        if re.search(pattern, line):
                            # if more than one files
                            if len(files) > 1:
                                out.append(f"{file}:{line}")
                            else:
                                out.append(line)
        else:
            raise ValueError(f"unsupported application {app}")


if __name__ == "__main__":
    args_num = len(sys.argv) - 1
    if args_num > 0:
        if args_num != 2:
            raise ValueError("wrong number of command line arguments")
        if sys.argv[1] != "-c":
            raise ValueError(f"unexpected command line argument {sys.argv[1]}")

        # deque (double ended queue) provides a lower time complexity
        # for append and pop operations as compared to a list
        out = deque()
        eval(sys.argv[2], out)
        while len(out) > 0:
            print(out.popleft(), end="")
    else:
        while True:
            print(os.getcwd() + "> ", end="")
            cmdline = input()
            out = deque()
            eval(cmdline, out)
            while len(out) > 0:
                print(out.popleft(), end="")
