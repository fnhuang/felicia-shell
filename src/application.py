import io
import os
import pytest
from collections import deque
from tokenize import String
from typing import Type
import re
from glob import glob
import sys
import re


# TODO: implement commands


class Application:
    def execute(self, args=[], inp=None, output=None) -> String:
        return output

    def get_str_from_deque(self, dq):
        strout = ""
        while len(dq) > 0:
            strout += dq.popleft()

        return strout


# glob function is a module that searches for files where the filename matches a certain pattern
# by using wildcard characters.
class Globbing:
    @classmethod
    def get_dirs_or_files(cls, file_patterns):
        files = []
        for file_pattern in file_patterns:
            globbing = glob(file_pattern)
            if globbing:
                # globbing returns an array of file names that match
                files.extend(globbing)
            else:
                # no matches
                # if error is raised in the event of no matches
                raise FileNotFoundError

        return files


# skipping value error
class UnsafeDecorator(Application):
    def __init__(self, wrapped: Application):
        self._wrapped = wrapped

    def execute(self, args=[], inp=None, output=None):
        try:
            strout = self._wrapped.execute(args)
        except ValueError as v:
            print(v)
        else:
            return strout


class Cut(Application):
    def getBytesToTake(self, bytes2extract, totalbytes):
        bytes2take = []

        splitters = "[,-]"
        digits = re.split(splitters, bytes2extract)
        isdigits = [x.isdigit() or x == "" for x in digits]  # all needs to be True
        if False in isdigits:
            raise ValueError("wrong bytes arg")
        else:
            slicers = bytes2extract.split(",")

            for slicer in slicers:
                cdo = slicer.split("-")
                if len(cdo) == 1:
                    # -1 because in python index starts at 0 and not 1
                    bytes2take.append(int(cdo[0]) - 1)
                elif len(cdo) == 2:
                    if cdo[0].isdigit() and cdo[1].isdigit():
                        bytes2take.extend(
                            [i for i in range(int(cdo[0]) - 1, int(cdo[1]))]
                        )
                    elif cdo[0] == "" and cdo[1].isdigit():
                        bytes2take.extend([i for i in range(0, int(cdo[1]))])
                    elif cdo[1] == "" and cdo[0].isdigit():
                        bytes2take.extend(
                            [i for i in range(int(cdo[0]) - 1, totalbytes)]
                        )
                else:
                    raise ValueError("wrong bytes arg")

        return bytes2take

    def get_outputstr_from_slicedbytes(self, input_str, arg_b2slice):
        b2slice = bytes(input_str, encoding="utf-8")
        bytes2take = self.getBytesToTake(arg_b2slice, len(b2slice))

        # TODO: CONTINUE
        sliced = [b2slice[bytes2take[i]] for i in range(0, len(bytes2take))]
        bsliced = bytes(sliced)
        return bsliced.decode()

    def execute(self, args=[], inp=None, output=deque):
        output = deque([])

        if len(args) == 2:
            if args[0] != "-b":
                raise ValueError("wrong flags")
            else:
                for str2slice in sys.stdin.readlines():
                    strsliced = self.get_outputstr_from_slicedbytes(
                        str2slice.strip(), args[1]
                    )

                    output.append(strsliced + "\n")
        elif len(args) == 3:
            if args[0] != "-b":
                raise ValueError("wrong flags")
            else:
                print("this is args", args[2])
                filepath = Globbing.get_dirs_or_files([args[2]])[0]
                with open(filepath) as reader:
                    lines = reader.readlines()
                    for line in lines:
                        strsliced = self.get_outputstr_from_slicedbytes(
                            line.strip(), args[1]
                        )

                        output.append(strsliced + "\n")

        else:
            raise ValueError("wrong number of command line arguments")

        strout = self.get_str_from_deque(output)
        return strout


# uniq function detects and deletes adjacent duplicate lines from an input file/stdin
# and prints the result to stdout
class Uniq(Application):
    def execute(self, args=[], inp=None, output=deque):
        output = deque([])

        def uniq_noi(lines):
            prevline = ""
            for line in lines:
                if line != prevline:
                    output.append(line)
                    prevline = line

        def uniq_wi(lines):
            prevline = ""
            for line in lines:
                if line.lower() != prevline:
                    output.append(line)
                    prevline = line.lower()

        if len(args) == 0:
            uniq_noi(sys.stdin.readlines())
        elif len(args) == 1:
            if args[0] == "-i":
                uniq_wi(sys.stdin.readlines())
            else:
                filepath = Globbing.get_dirs_or_files([args[0]])[0]
                with open(filepath, "r") as reader:
                    uniq_noi(reader.readlines())
        elif len(args) == 2:
            if args[0] != "-i":
                raise ValueError("wrong flags")
            else:
                filepath = Globbing.get_dirs_or_files([args[1]])[0]
                with open(filepath, "r") as reader:
                    uniq_wi(reader.readlines())
        else:
            raise ValueError("wrong number of command line arguments")

        strout = self.get_str_from_deque(output)
        return strout


class Sort(Application):
    def execute(self, args=[], inp=None, output=deque):
        to_be_sorted = []
        is_reverse = False
        if len(args) == 0:
            to_be_sorted = sys.stdin.readlines()
            to_be_sorted = [word.strip() for word in to_be_sorted]
            # stdin with only whitespaces ignored
            to_be_sorted = [word for word in to_be_sorted if len(word) > 0]
        elif len(args) == 1:
            if (args[0]) == "-r":
                is_reverse = True
                to_be_sorted = sys.stdin.readlines()
                to_be_sorted = [word.strip() for word in to_be_sorted]
                # stdin with only whitespaces ignored
                to_be_sorted = [word for word in to_be_sorted if len(word) > 0]
            else:
                file = Globbing.get_dirs_or_files([args[0]])[0]
                with open(file) as f:
                    to_be_sorted = [word.strip() for word in f.readlines()]
        elif len(args) == 2:
            if args[0] == "-r":
                is_reverse = True
                file = Globbing.get_dirs_or_files([args[1]])[0]
                with open(file) as f:
                    to_be_sorted = [word.strip() for word in f.readlines()]
            else:
                raise ValueError("wrong flags")
        else:
            raise ValueError("wrong number of command line arguments")

        sorted_array = sorted(to_be_sorted, reverse=is_reverse)
        sorted_array = [f"{w}\n" for w in sorted_array]

        output = deque(sorted_array)

        strout = self.get_str_from_deque(output)
        return strout


class Grep(Application):
    def execute(self, args=[], inp=None, output=deque()):
        # minimum number of argument for grep is 2
        if len(args) < 2:
            raise ValueError("wrong number of command line arguments")
        # grep tries to find a pattern of each line in a file
        pattern = args[0]

        files = Globbing.get_dirs_or_files(args[1:])

        for file in files:
            with open(file) as f:
                lines = f.readlines()
                for line in lines:
                    # if there is a match
                    if re.search(pattern, line):
                        # if more than one files
                        if len(files) > 1:
                            output.append(f"{file}:{line}")
                        else:
                            output.append(line)
        strout = self.get_str_from_deque(output)
        return strout


class Tail(Application):
    def execute(self, args=[], inp=None, output=deque()):
        if len(args) != 1 and len(args) != 3:
            raise ValueError("wrong number of command line arguments")
        if len(args) == 1:
            num_lines = 10
            files = Globbing.get_dirs_or_files([args[0]])
            if len(files) > 1:
                raise ValueError("too many files")
            else:
                file = files[0]
        if len(args) == 3:
            if args[0] != "-n":
                raise ValueError("wrong flags")
            else:
                num_lines = int(args[1])
                files = Globbing.get_dirs_or_files([args[2]])
                if len(files) > 1:
                    raise ValueError("too many files")
                else:
                    file = files[0]
        with open(file) as f:
            lines = f.readlines()
            display_length = min(len(lines), num_lines)
            for i in range(0, display_length):
                output.append(lines[len(lines) - display_length + i])

        strout = self.get_str_from_deque(output)
        return strout


class Head(Application):
    def execute(self, args=[], inp=None, output=deque()):
        # head command only have 1 or 3 arguments
        if len(args) != 1 and len(args) != 3:
            raise ValueError("wrong number of command line arguments")
        if len(args) == 1:
            num_lines = 10
            files = Globbing.get_dirs_or_files([args[0]])
            if len(files) > 1:
                raise ValueError("too many files")
            else:
                file = files[0]
        if len(args) == 3:
            if args[0] != "-n":
                raise ValueError("wrong flags")
            else:
                num_lines = int(args[1])
                files = Globbing.get_dirs_or_files([args[2]])
                if len(files) > 1:
                    raise ValueError("too many files")
                else:
                    file = files[0]

        with open(file) as f:
            lines = f.readlines()
            # print out the first x lines of a file where x is num_lines
            for i in range(0, min(len(lines), num_lines)):
                output.append(lines[i])

        strout = self.get_str_from_deque(output)
        return strout


# echo input stream
class Echo(Application):
    def execute(self, args=[], inp=None, output=deque()):
        output.append(" ".join(args) + "\n")

        strout = self.get_str_from_deque(output)
        return strout


class Cat(Application):
    def execute(self, args=[], inp=None, output=deque()):
        if len(args) == 0:
            text = input("")
            output.append(text)

        files = Globbing.get_dirs_or_files(args)
        for file in files:
            with open(file) as f:
                # calling file object to read the file and return string
                output.append(f.read())

        strout = self.get_str_from_deque(output)

        return strout


# get current working directory
class Pwd(Application):
    ok_args = ["-L", "-P"]

    def execute(self, args=[], inp=None, output=deque()) -> String:
        flag_args = [a for a in args if "-" in a]
        wrong_flags = [a for a in flag_args if a not in self.ok_args]

        if len(flag_args) > 0:
            if len(wrong_flags) > 0:
                raise ValueError("wrong flags")
            else:
                raise ValueError("unimplemented flags")
        else:
            output.append(os.getcwd())

        strout = self.get_str_from_deque(output)

        return strout


# change current working directory
class Cd(Application):
    def execute(self, args=["."], inp=None, output=None) -> String:
        if len(args) > 1:
            raise ValueError("too many arguments")
        else:
            os.chdir(args[0])

        return os.getcwd()


class Find(Application):
    def execute(self, args=[], inp=None, output=None):
        if len(args) == 2:
            if args[0] != "-name":
                raise ValueError("wrong flags")
            else:
                # get the current working directory
                rootdir = os.getcwd()
                pattern = args[1]
        elif len(args) == 3:
            if args[1] != "-name":
                raise ValueError("wrong flags")
            else:
                rootdir = args[0]
                pattern = args[2]
        else:
            raise ValueError("wrong number of command line arguments")

        globbing = glob(f"{rootdir}/**/{pattern}", recursive=True)

        strout = "\n".join(globbing)
        return strout


class Ls(Application):
    def execute(self, args=[], inp=None, output=deque()) -> String:
        if len(args) == 0:
            # get the current working directory
            ls_dir = os.getcwd()
        elif len(args) > 1:
            raise ValueError("wrong number of command line arguments")
        else:
            ls_dir = args[0]

        # list all the files inside lis_dir
        files = os.listdir(ls_dir)

        for f in files:
            if not f.startswith("."):
                output.append(f + "\n")

        strout = self.get_str_from_deque(output)

        print(strout)
        return strout


# factory design pattern
def create_application(app_name: str = "application"):
    applications = {
        "application": Application,
        "cd": Cd,
        "ls": Ls,
        "pwd": Pwd,
        "cat": Cat,
        "echo": Echo,
        "head": Head,
        "tail": Tail,
        "grep": Grep,
        "find": Find,
        "sort": Sort,
        "uniq": Uniq,
        "cut": Cut,
    }

    return applications[app_name]()


if __name__ == "__main__":
    print("This is Sort Function")
    app = create_application("sort")
    app.execute()

    """print("This is Head function")
    app = create_application("head")
    print(app.execute(["-n", 3, "../reqe*.txt"]))

    print("This is Cat function")
    app = create_application("cat")
    app.execute()

    print("This is Cd function")
    app = create_application("cd")
    app.execute(["C:\\github\\fnooi\\content\\tenang"])

    print("\nThis is Pwd function")
    app = create_application("pwd")
    app.execute()

    print("\nThis is Unsafe decorator function. Program will continue after error.")
    app = UnsafeDecorator(create_application("ls"))
    app.execute(["args1", "args2"])

    print("\nThis is normal Ls function. Program will stop after error.")
    app = create_application("ls")
    app.execute(["args1", "args2"])"""
