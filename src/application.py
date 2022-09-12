import io
import os

# TODO: apply factory pattern
# TODO: perform testing using pytest
# TODO: apply unsafe decorator
class Application:
    def execute(self, args=[], input=None, output=None):
        self.print_output(output)

    def print_output(self, output):
        print(output.getvalue())


class Pwd(Application):
    def execute(self, args=[], input=None, output=io.StringIO()):
        output.write(os.getcwd())
        self.print_output(output)


class Cd(Application):
    def execute(self, args=[], input=None, output=None):
        if len(args) == 0 or len(args) > 1:
            raise ValueError("wrong number of command line arguments")
        else:
            os.chdir(args[0])


class Ls(Application):
    def execute(self, args=[], input=None, output=io.StringIO()):
        if len(args) == 0:
            # get the current working directory
            ls_dir = os.getcwd()
        elif len(args) > 1:
            raise ValueError("wrong number of command line arguments")
        else:
            ls_dir = args[0]

        # list all the files inside lis_dir
        for f in os.listdir(ls_dir):
            if not f.startswith("."):
                output.write(f + "\n")

        self.print_output(output)


if __name__ == "__main__":
    cd = Cd()
    cd.execute(["C:\\github\\fnooi\\content\\tenang"])

    pwd = Pwd()
    pwd.execute()

    ls = Ls()
    ls.execute()
