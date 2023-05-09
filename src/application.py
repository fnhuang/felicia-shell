import io
import os
from collections import deque
from tokenize import String
from typing import Type
import re
from glob import glob
import sys
import re


class Application:
    def execute(self, args, input, output):
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
    def get_files(cls, file_patterns):
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

    def execute(self, args, input, output):
        try:
            self._wrapped.execute(args, input, output)
        except ValueError as v:
            print(v, file=sys.stderr)


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

        return list(set(bytes2take))

    def get_outputstr_from_slicedbytes(self, input_str, arg_b2slice):
        b2slice = bytes(input_str, encoding="utf-8")
        bytes2take = self.getBytesToTake(arg_b2slice, len(b2slice))
        sliced = [b2slice[bytes2take[i]] for i in range(0, len(bytes2take))]
        bsliced = bytes(sliced)
        return bsliced.decode()

    def execute(self, args, input, output):
        if len(args) == 2:
            if args[0] != "-b":
                raise ValueError("wrong flags")
            else:
                for str2slice in input:
                    strsliced = self.get_outputstr_from_slicedbytes(
                        str2slice.strip(), args[1]
                    )

                    output.append(strsliced + "\n")
        elif len(args) == 3:
            if args[0] != "-b":
                raise ValueError("wrong flags")
            else:
                filepath = Globbing.get_files([args[2]])[0]
                with open(filepath) as reader:
                    lines = reader.readlines()
                    for line in lines:
                        strsliced = self.get_outputstr_from_slicedbytes(
                            line.strip(), args[1]
                        )

                        output.append(strsliced + "\n")

        else:
            raise ValueError("wrong number of command line arguments")


# uniq function detects and deletes adjacent duplicate lines from an input file/stdin
# and prints the result to stdout
class Uniq(Application):
    def execute(self, args, input, output):
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
            uniq_noi(input)
        elif len(args) == 1:
            if args[0] == "-i":
                uniq_wi(input)
            else:
                filepath = Globbing.get_files([args[0]])[0]
                with open(filepath, "r") as reader:
                    uniq_noi(reader.readlines())
        elif len(args) == 2:
            if args[0] != "-i":
                raise ValueError("wrong flags")
            else:
                filepath = Globbing.get_files([args[1]])[0]
                with open(filepath, "r") as reader:
                    uniq_wi(reader.readlines())
        else:
            raise ValueError("wrong number of command line arguments")


class Sort(Application):
    def execute(self, args, input, output):
        to_be_sorted = []
        is_reverse = False
        if len(args) == 0:
            to_be_sorted = input
            to_be_sorted = [word.strip() for word in to_be_sorted]
            # stdin with only whitespaces ignored
            to_be_sorted = [word for word in to_be_sorted if len(word) > 0]
        elif len(args) == 1:
            if (args[0]) == "-r":
                is_reverse = True
                to_be_sorted = input
                to_be_sorted = [word.strip() for word in to_be_sorted]
                # stdin with only whitespaces ignored
                to_be_sorted = [word for word in to_be_sorted if len(word) > 0]
            else:
                file = Globbing.get_files([args[0]])[0]
                with open(file) as f:
                    to_be_sorted = [word.strip() for word in f.readlines()]
        elif len(args) == 2:
            if args[0] == "-r":
                is_reverse = True
                file = Globbing.get_files([args[1]])[0]
                with open(file) as f:
                    to_be_sorted = [word.strip() for word in f.readlines()]
            else:
                raise ValueError("wrong flags")
        else:
            raise ValueError("wrong number of command line arguments")

        sorted_array = sorted(to_be_sorted, reverse=is_reverse)
        sorted_array = [f"{w}\n" for w in sorted_array]

        output.extend(deque(sorted_array))


class Grep(Application):
    def execute(self, args, input, output):
        # minimum number of argument for grep is 2
        if len(args) < 1:
            raise ValueError("wrong number of command line arguments")
        # grep tries to find a pattern of each line in a file
        pattern = args[0]

        if len(args) == 2:
            files = Globbing.get_files(args[1:])

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
        elif len(args) == 1:
            for line in input:
                if re.search(pattern, line):
                    output.append(line)


class Tail(Application):
    def execute(self, args, input, output):
        num_lines = 10
        if len(args) > 3 or len(args) == 2:
            raise ValueError("wrong number of command line arguments")
        if len(args) == 0:
            file = ""
        elif len(args) == 1:
            num_lines = 10
            files = Globbing.get_files([args[0]])
            if len(files) > 1:
                raise ValueError("too many files")
            else:
                file = files[0]
        elif len(args) == 3:
            if args[0] != "-n":
                raise ValueError("wrong flags")
            else:
                num_lines = int(args[1])
                files = Globbing.get_files([args[2]])
                if len(files) > 1:
                    raise ValueError("too many files")
                else:
                    file = files[0]
        if file == "":
            lines = input
        else:
            with open(file) as f:
                lines = f.readlines()

        display_length = min(len(lines), num_lines)
        for i in range(0, display_length):
            output.append(lines[len(lines) - display_length + i])


class Head(Application):
    def execute(self, args, input, output):
        # head command only have 1 or 3 arguments
        num_lines = 10
        if len(args) != 1 and len(args) != 3:
            raise ValueError("wrong number of command line arguments")
        if len(args) == 1:
            num_lines = 10
            files = Globbing.get_files([args[0]])
            if len(files) > 1:
                raise ValueError("too many files")
            else:
                file = files[0]
        if len(args) == 3:
            if args[0] != "-n":
                raise ValueError("wrong flags")
            else:
                num_lines = int(args[1])
                files = Globbing.get_files([args[2]])
                if len(files) > 1:
                    raise ValueError("too many files")
                else:
                    file = files[0]

        with open(file) as f:
            lines = f.readlines()
            # print out the first x lines of a file where x is num_lines
            for i in range(0, min(len(lines), num_lines)):
                output.append(lines[i])


# echo input stream
class Echo(Application):
    def execute(self, args, input, output):
        output.append(" ".join(args) + "\n")


class Cat(Application):
    def execute(self, args, input, output):
        if len(args) == 0:
            for i in input:
                output.append(i)

        files = Globbing.get_files(args)
        for file in files:
            with open(file) as f:
                # calling file object to read the file and return string
                output.append(f.read())


# get current working directory
class Pwd(Application):
    ok_args = ["-L", "-P"]

    def execute(self, args, input, output):
        flag_args = [a for a in args if "-" in a]
        wrong_flags = [a for a in flag_args if a not in self.ok_args]

        if len(flag_args) > 0:
            if len(wrong_flags) > 0:
                raise ValueError("wrong flags")
            else:
                raise ValueError("unimplemented flags")
        else:
            output.append(os.getcwd())


# change current working directory
class Cd(Application):
    def execute(self, args, input, output):
        if len(args) > 1:
            raise ValueError("too many arguments")
        else:
            os.chdir(args[0])

        # output.append(os.getcwd())


class Find(Application):
    def execute(self, args, input, output):
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

        for g in globbing:
            output.append("./" + os.path.relpath(g) + "\n")


class Ls(Application):
    def execute(self, args, input, output):
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
