from multiprocessing.sharedctypes import Value
from application import create_application  # need to set the environment to src folder
from application import UnsafeDecorator
import os
import pytest
import io
from glob import glob
from collections import deque

REQ_CONTENT = "nose2\ncoverage\nflake8-html\njunit2html\n"
ENV_CONTENT = "PYTHONPATH=src:test"
README_CONTENT = "COMP0010 Shell is a [shell](https://en.wikipedia.org/wiki/Shell_(computing)) created for educational purposes."


@pytest.fixture
def create_temp_files(tmpdir):
    # create a temp directory with a copy of requirements.txt inside
    temp_dir = tmpdir.mkdir("temp")

    # Create a file in the temporary directory
    temp_file = temp_dir.join("requirements.txt")
    temp_file.write(REQ_CONTENT)
    temp_file2 = temp_dir.join(".env")
    temp_file2.write(ENV_CONTENT)
    temp_file3 = temp_dir.join("README.md")
    temp_file3.write(README_CONTENT)

    return {
        "REQPATH": str(temp_file),
        "ENVPATH": str(temp_file2),
        "README": str(temp_file3),
    }


@pytest.fixture
def create_sample_file_4cut(tmpdir):
    # create a temp directory with a copy of requirements.txt inside
    temp_dir = tmpdir.mkdir("temp")

    # Create a file in the temporary directory
    temp_file = temp_dir.join("sample_file_4cut.txt")
    temp_file.write("hello word\nhome sweet home")

    return str(temp_file)


@pytest.fixture
def create_dup_textfiles(tmpdir):
    temp_dir = tmpdir.mkdir("temp")

    dup_file = temp_dir.join("dup.txt")

    dup_file.write(
        "Hello world\nFrogs in the rain\nFrogs in the rain\n"
        "Dog bites\nNew home\nHello World\nhello world\nWinter wonderland"
    )

    return str(dup_file)


@pytest.fixture
def create_fnooi_dir(tmpdir):
    temp_dir = tmpdir.mkdir("fnooi")
    archetype_dir = temp_dir.mkdir("archetypes")
    archidefault_file = temp_dir.join("default.md")
    archidefault_file.write("This is fnooi/archetypes/default.md")

    content_dir = temp_dir.mkdir("content")
    project_dir = content_dir.mkdir("projects")
    tenang_dir = content_dir.mkdir("tenang")

    project_index_file = project_dir.join("_index.md")
    project_index_file.write("This is fnooi/content/projects/_index.md")

    tenang_april_file = tenang_dir.join("april2021.md")
    tenang_july_file = tenang_dir.join("july2021.md")
    tenang_december_file = tenang_dir.join("december2021.md")
    tenang_april_file.write("This is April blog")
    tenang_july_file.write("This is July blog")
    tenang_december_file.write("This is December blog")

    return str(temp_dir)


class TestCat:
    # pytest skips test class if init is define -- so this is FORBIDDEN
    # def __init__(self, tmpdir) -> None:

    def test_read_1file(self, create_temp_files):
        app = create_application("cat")
        inp = deque()
        out = deque()
        app.execute([create_temp_files["REQPATH"]], inp, out)

        rq_content = "nose2\ncoverage\nflake8-html\njunit2html\n"
        assert app.get_str_from_deque(out) == rq_content

    def test_read_mt1file(self, create_temp_files):
        app = create_application("cat")
        inp = deque()
        out = deque()

        # str(temp_file) will give the full directory
        app.execute(
            [create_temp_files["REQPATH"], create_temp_files["ENVPATH"]], inp, out
        )

        rq_content = "nose2\ncoverage\nflake8-html\njunit2html\nPYTHONPATH=src:test"

        assert app.get_str_from_deque(out) == rq_content


class TestUnique:
    def test_wrong_argsno(self):
        app = create_application("uniq")
        inp = deque()
        out = deque()
        with pytest.raises(ValueError):
            app.execute(["args1", "args2", "args3"], inp, out)

    def test_wrong_flags(self):
        app = create_application("uniq")
        inp = deque()
        out = deque()
        with pytest.raises(ValueError):
            app.execute(["args1", "args2"], inp, out)

    def test_0arg(self):
        app = create_application("uniq")
        inp = deque()
        out = deque()

        inp = deque(
            [
                "mrs. dalloway\n",
                "brother karamazov\n",
                "BrothEr KaRamazov\n",
                "little house on the prairie\n",
                "little house on the prairie\n",
                "mrs.dalloway\n",
                "Anne of Green Gables\n",
            ]
        )

        app.execute([], inp, out)

        assert (
            app.get_str_from_deque(out) == "mrs. dalloway\nbrother karamazov\n"
            "BrothEr KaRamazov\nlittle house on the prairie"
            "\nmrs.dalloway"
            "\nAnne of Green Gables\n"
        )

    def test_1arg_inv(self):
        app = create_application("uniq")
        out = deque()
        inp = deque(
            [
                "mrs. dalloway\n",
                "brother karamazov\n",
                "BrothEr KaRamazov\n",
                "little house on the prairie\n",
                "little house on the prairie\n",
                "mrs.dalloway\n",
                "Anne of Green Gables\n",
            ]
        )

        app.execute(["-i"], inp, out)

        assert (
            app.get_str_from_deque(out) == "mrs. dalloway\nbrother karamazov\n"
            "little house on the prairie"
            "\nmrs.dalloway"
            "\nAnne of Green Gables\n"
        )

    def test_1arg(self, create_dup_textfiles):
        app = create_application("uniq")
        inp = deque()
        out = deque()
        app.execute([create_dup_textfiles], inp, out)
        assert (
            app.get_str_from_deque(out) == "Hello world\nFrogs in the rain\n"
            "Dog bites\nNew home\nHello World\nhello world\nWinter wonderland"
        )

    def test_2arg(self, create_dup_textfiles):
        app = create_application("uniq")
        inp = deque()
        out = deque()
        app.execute(["-i", create_dup_textfiles], inp, out)
        assert (
            app.get_str_from_deque(out) == "Hello world\nFrogs in the rain\n"
            "Dog bites\nNew home\nHello World\nWinter wonderland"
        )


class TestSort:
    def test_wrong_argsno(self):
        app = create_application("sort")
        inp = deque()
        out = deque()
        with pytest.raises(ValueError):
            app.execute(["args1", "args2", "args3"], inp, out)

    def test_wrong_flags(self):
        app = create_application("sort")
        inp = deque()
        out = deque()
        with pytest.raises(ValueError):
            app.execute(["args1", "args2"], inp, out)

    def test_stdinput(self):
        app = create_application("sort")
        inp = deque(["hello", "world", "affogato"])
        out = deque()
        app.execute([], inp, out)

        assert app.get_str_from_deque(out) == "affogato\nhello\nworld\n"

    def test_stdinput_reverse(self):
        app = create_application("sort")
        inp = deque(["hello", "world", "affogato"])
        out = deque()
        app.execute(["-r"], inp, out)

        assert app.get_str_from_deque(out) == "world\nhello\naffogato\n"

    def test_readfile(self, create_temp_files):
        app = create_application("sort")
        inp = deque()
        out = deque()
        app.execute([create_temp_files["REQPATH"]], inp, out)

        assert (
            app.get_str_from_deque(out) == "coverage\nflake8-html\njunit2html\nnose2\n"
        )

    def test_readfile_reverse(self, create_temp_files):
        app = create_application("sort")
        inp = deque()
        out = deque()
        app.execute(["-r", create_temp_files["REQPATH"]], inp, out)

        assert (
            app.get_str_from_deque(out) == "nose2\njunit2html\nflake8-html\ncoverage\n"
        )


class TestFind:
    def test_wrong_argsno(self):
        app = create_application("find")
        inp = deque()
        out = deque()
        with pytest.raises(ValueError):
            app.execute(["args1"], inp, out)

    def test_wrong_flags(self):
        app = create_application("find")
        inp = deque()
        out = deque()
        with pytest.raises(ValueError):
            app.execute(["args1", "args2"], inp, out)

    def test_found(self, create_fnooi_dir):
        app = create_application("find")
        inp = deque()
        out = deque()
        app.execute([create_fnooi_dir, "-name", "april2021*"], inp, out)

        globbing = glob(f"{create_fnooi_dir}/**/april2021*", recursive=True)
        assert app.get_str_from_deque(out) == "\n".join(globbing) + "\n"

    def test_not_found(self, create_fnooi_dir):
        app = create_application("find")
        inp = deque()
        out = deque()
        app.execute([create_fnooi_dir, "-name", "ril2021*"], inp, out)
        assert app.get_str_from_deque(out) == ""


class TestUnsafeDecorator:
    def test_no_exception_raised(self):
        app = UnsafeDecorator(create_application("grep"))
        inp = deque()
        out = deque()
        try:
            app.execute(["args1"], inp, out)
        except ValueError as ve:
            # assertion is false because an exception is raised
            assert False, "Exception is raised"


class TestCut:
    def test_wrongargsno(self):
        app = create_application("cut")
        inp = deque()
        out = deque()
        with pytest.raises(ValueError):
            app.execute(["args1"], inp, out)

    def test_1starg_notb(self):
        app = create_application("cut")
        inp = deque()
        out = deque()
        with pytest.raises(ValueError):
            app.execute(["args1", "args2"], inp, out)

    def test_stdin_comma_args(self):
        app = create_application("cut")
        inp = deque(["hello world\n", "home sweet home\n"])
        out = deque()
        app.execute(["-b", "1,2,3"], inp, out)
        assert app.get_str_from_deque(out) == "hel\nhom\n"

    def test_stdin_hyphen_2side_args(self):
        app = create_application("cut")
        inp = deque(["hello world\n", "home sweet home\n"])
        out = deque()
        app.execute(["-b", "1-3,7-9"], inp, out)
        assert app.get_str_from_deque(out) == "helwor\nhomwee\n"

    def test_stdin_hyphen_1side_args(self):
        app = create_application("cut")
        inp = deque(["hello world\n", "home sweet home\n"])
        out = deque()
        app.execute(["-b", "-3,7-"], inp, out)
        assert app.get_str_from_deque(out) == "helworld\nhomweet home\n"

    def test_filein(self, create_sample_file_4cut):
        app = create_application("cut")
        inp = deque()
        out = deque()
        app.execute(["-b", "1-3,7-9", create_sample_file_4cut], inp, out)

        assert app.get_str_from_deque(out) == "helwor\nhomwee\n"


class TestGrep:
    def test_wrong_argsno(self):
        app = create_application("grep")
        inp = deque()
        out = deque()
        with pytest.raises(ValueError):
            app.execute(["args1"], inp, out)

    def test_onefile(self, create_temp_files):
        app = create_application("grep")
        inp = deque()
        out = deque()
        app.execute(["html", create_temp_files["REQPATH"]], inp, out)

        right_answer = "flake8-html\njunit2html"

    def test_multiplefiles(self, create_temp_files):
        app = create_application("grep")
        inp = deque()
        out = deque()
        app.execute(
            ["ose", create_temp_files["REQPATH"], create_temp_files["README"]], inp, out
        )

        reqpath = create_temp_files["REQPATH"]
        readpath = create_temp_files["README"]
        right_answer = (
            f"{reqpath}:nose2\n{readpath}:COMP0010 Shell is "
            + f"a [shell](https://en.wikipedia.org/wiki/Shell_(computing)) created "
            + f"for educational purposes."
        )

        assert app.get_str_from_deque(out) == right_answer


class TestEcho:
    def test_echo(self):
        app = create_application("echo")
        inp = deque()
        out = deque()
        app.execute(["hello world"], inp, out)
        assert app.get_str_from_deque(out) == "hello world\n"


class TestHead:
    def test_head_wrong_args_no(self, create_temp_files):
        app = create_application("head")
        inp = deque()
        out = deque()
        with pytest.raises(ValueError):
            app.execute([create_temp_files["REQPATH"], "3"], inp, out)

    def test_head_wrong_flags(self, create_temp_files):
        app = create_application("head")
        inp = deque()
        out = deque()
        with pytest.raises(ValueError):
            app.execute([create_temp_files["REQPATH"], "3", "4"], inp, out)

    def test_with_flag(self, create_temp_files):
        app = create_application("head")
        inp = deque()
        out = deque()
        app.execute(["-n", 3, create_temp_files["REQPATH"]], inp, out)
        rq_content = "nose2\ncoverage\nflake8-html\n"

        assert app.get_str_from_deque(out) == rq_content

    def test_no_flag(self, create_temp_files):
        app = create_application("head")
        inp = deque()
        out = deque()
        app.execute([create_temp_files["REQPATH"]], inp, out)

        rq_content = "nose2\ncoverage\nflake8-html\njunit2html\n"
        assert app.get_str_from_deque(out) == rq_content


class TestTail:
    def test_tail_wrong_args_no(self):
        app = create_application("tail")
        inp = deque()
        out = deque()
        with pytest.raises(ValueError):
            app.execute(["../requirements.txt", "3"], inp, out)

    def test_tail_wrong_flags(self):
        app = create_application("tail")
        inp = deque()
        out = deque()
        with pytest.raises(ValueError):
            app.execute(["../requirements.txt", "3", "4"], inp, out)

    def test_with_flag(self, create_temp_files):
        app = create_application("tail")
        inp = deque()
        out = deque()
        app.execute(["-n", 2, create_temp_files["REQPATH"]], inp, out)
        rq_content = "flake8-html\njunit2html\n"

        assert app.get_str_from_deque(out) == rq_content

    def test_no_flag(self, create_temp_files):
        app = create_application("tail")
        inp = deque()
        out = deque()
        app.execute([create_temp_files["REQPATH"]], inp, out)

        rq_content = "nose2\ncoverage\nflake8-html\njunit2html\n"
        assert app.get_str_from_deque(out) == rq_content


class TestCd:
    def test_cd_argsno(self):
        app = create_application("cd")
        inp = deque()
        out = deque()

        with pytest.raises(ValueError):
            app.execute(["args1", "args2"], inp, out)

    def test_cd(self):
        app = create_application("cd")
        inp = deque()
        out = deque()
        cwd = os.getcwd()
        up1level = cwd[0 : cwd.rfind("\\")]

        app.execute([".."], inp, out)
        assert app.get_str_from_deque(out) == up1level


class TestLs:
    def test_ls_noargs(self):
        app = create_application("cd")
        inp = deque()
        out = deque()

        with pytest.raises(ValueError):
            app.execute(["args1", "args2"], inp, out)

    def test_ls_zeroargs(self):
        lsres = []
        # list all the files inside lis_dir
        for f in os.listdir(os.getcwd()):
            if not f.startswith("."):
                lsres.append(f + "\n")

        inp = deque()
        out = deque()
        app = create_application("ls")
        app.execute([], inp, out)

        assert app.get_str_from_deque(out) == "".join(lsres)

    def test_ls_wrongargs(self):
        app = create_application("ls")
        inp = deque()
        out = deque()
        with pytest.raises(FileNotFoundError):
            app.execute(["hello"], inp, out)

    def test_ls_rightargs(self):
        cwd = os.getcwd()
        up1level = cwd[0 : cwd.rfind("\\")]

        lsres = []
        # list all the files inside lis_dir
        for f in os.listdir(up1level):
            if not f.startswith("."):
                lsres.append(f + "\n")

        app = create_application("ls")
        inp = deque()
        out = deque()
        app.execute([up1level], inp, out)

        assert app.get_str_from_deque(out) == "".join(lsres)


class TestPwd:
    ok_opts = ["L", "P"]

    def test_pwd(self):
        app = create_application("pwd")
        inp = deque()
        out = deque()
        app.execute([], inp, out)

        assert app.get_str_from_deque(out) == os.getcwd()

    def test_pwd_args_noflags(self):
        app = create_application("pwd")
        inp = deque()
        out = deque()
        app.execute(["args1", "args", "arg3"], inp, out)

        # somehow new application is not created so the output is not empty. output contains things from previous test
        assert app.get_str_from_deque(out) == os.getcwd()

    def test_pwd_args_okflags(self):
        app = create_application("pwd")
        inp = deque()
        out = deque()

        with pytest.raises(ValueError):
            app.execute(["-L", "args2"], inp, out)

    def test_pwd_args_wrongflags(self):
        app = create_application("pwd")
        inp = deque()
        out = deque()

        with pytest.raises(ValueError):
            strout = app.execute(["args1", "-G"], inp, out)
