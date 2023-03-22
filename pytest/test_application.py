from multiprocessing.sharedctypes import Value
from application import create_application  # need to set the environment to src folder
from application import UnsafeDecorator
import os
import pytest
import io
from glob import glob

REQ_CONTENT = "nose2\ncoverage\nflake8-html\njunit2html\n"
ENV_CONTENT = "PYTHONPATH=src:test"


@pytest.fixture
def create_temp_files(tmpdir):
    # create a temp directory with a copy of requirements.txt inside
    temp_dir = tmpdir.mkdir("temp")

    # Create a file in the temporary directory
    temp_file = temp_dir.join("requirements.txt")
    temp_file.write(REQ_CONTENT)
    temp_file2 = temp_dir.join(".env")
    temp_file2.write(ENV_CONTENT)

    return {"REQPATH": str(temp_file), "ENVPATH": str(temp_file2)}


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
        output = app.execute([create_temp_files["REQPATH"]])

        rq_content = "nose2\ncoverage\nflake8-html\njunit2html\n"
        assert output == rq_content

    def test_read_mt1file(self, create_temp_files):
        app = create_application("cat")
        # str(temp_file) will give the full directory
        output = app.execute(
            [create_temp_files["REQPATH"], create_temp_files["ENVPATH"]]
        )

        rq_content = "nose2\ncoverage\nflake8-html\njunit2html\nPYTHONPATH=src:test"

        assert output == rq_content

    def test_read_stdin(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("seryozha gemes"))

        app = create_application("cat")
        output = app.execute()

        assert output == "seryozha gemes"


class TestUnique:
    def test_wrong_argsno(self):
        app = create_application("uniq")
        with pytest.raises(ValueError):
            app.execute(["args1", "args2", "args3"])

    def test_wrong_flags(self):
        app = create_application("uniq")
        with pytest.raises(ValueError):
            app.execute(["args1", "args2"])

    def test_0arg(self, monkeypatch):
        app = create_application("uniq")
        monkeypatch.setattr(
            "sys.stdin",
            io.StringIO(
                "mrs. dalloway\nbrother karamazov\n"
                "BrothEr KaRamazov\nlittle house on the prairie"
                "\nlittle house on the prairie\nmrs.dalloway"
                "\nAnne of Green Gables"
            ),
        )
        output = app.execute([])

        assert (
            output == "mrs. dalloway\nbrother karamazov\n"
            "BrothEr KaRamazov\nlittle house on the prairie"
            "\nmrs.dalloway"
            "\nAnne of Green Gables"
        )

    def test_1arg_inv(self, monkeypatch):
        app = create_application("uniq")
        monkeypatch.setattr(
            "sys.stdin",
            io.StringIO(
                "mrs. dalloway\nbrother karamazov\n"
                "BrothEr KaRamazov\nlittle house on the prairie"
                "\nlittle house on the prairie\nmrs.dalloway"
                "\nAnne of Green Gables"
            ),
        )
        output = app.execute(["-i"])

        assert (
            output == "mrs. dalloway\nbrother karamazov\n"
            "little house on the prairie"
            "\nmrs.dalloway"
            "\nAnne of Green Gables"
        )

    def test_1arg(self, create_dup_textfiles):
        app = create_application("uniq")
        output = app.execute([create_dup_textfiles])
        assert (
            output == "Hello world\nFrogs in the rain\n"
            "Dog bites\nNew home\nHello World\nhello world\nWinter wonderland"
        )

    def test_2arg(self, create_dup_textfiles):
        app = create_application("uniq")
        output = app.execute(["-i", create_dup_textfiles])
        assert (
            output == "Hello world\nFrogs in the rain\n"
            "Dog bites\nNew home\nHello World\nWinter wonderland"
        )


class TestSort:
    def test_wrong_argsno(self):
        app = create_application("sort")
        with pytest.raises(ValueError):
            app.execute(["args1", "args2", "args3"])

    def test_wrong_flags(self):
        app = create_application("sort")
        with pytest.raises(ValueError):
            app.execute(["args1", "args2"])

    def test_stdinput(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("hello\nworld\naffogato"))

        app = create_application("sort")
        output = app.execute([])

        assert output == "affogato\nhello\nworld\n"

    def test_stdinput_reverse(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("hello\nworld\naffogato"))

        app = create_application("sort")
        output = app.execute(["-r"])

        assert output == "world\nhello\naffogato\n"

    def test_readfile(self, create_temp_files):
        app = create_application("sort")
        output = app.execute([create_temp_files["REQPATH"]])

        assert output == "coverage\nflake8-html\njunit2html\nnose2\n"

    def test_readfile_reverse(self, create_temp_files):
        app = create_application("sort")
        output = app.execute(["-r", create_temp_files["REQPATH"]])

        assert output == "nose2\njunit2html\nflake8-html\ncoverage\n"


class TestFind:
    def test_wrong_argsno(self):
        app = create_application("find")
        with pytest.raises(ValueError):
            output = app.execute(["args1"])

    def test_wrong_flags(self):
        app = create_application("find")
        with pytest.raises(ValueError):
            output = app.execute(["args1", "args2"])

    def test_found(self, create_fnooi_dir):
        app = create_application("find")
        output = app.execute([create_fnooi_dir, "-name", "april2021*"])

        globbing = glob(f"{create_fnooi_dir}/**/april2021*", recursive=True)
        assert output == "\n".join(globbing)

    def test_not_found(self, create_fnooi_dir):
        app = create_application("find")
        output = app.execute([create_fnooi_dir, "-name", "ril2021*"])
        assert output == ""


class TestUnsafeDecorator:
    def test_no_exception_raised(self):
        app = UnsafeDecorator(create_application("grep"))
        try:
            output = app.execute(["args1"])
        except ValueError as ve:
            # assertion is false because an exception is raised
            assert False, "Exception is raised"


class TestCut:
    def test_wrongargsno(self):
        app = create_application("cut")
        with pytest.raises(ValueError):
            output = app.execute(["args1"])

    def test_1starg_notb(self):
        app = create_application("cut")
        with pytest.raises(ValueError):
            output = app.execute(["args1", "args2"])

    def test_stdin_comma_args(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("hello world\nhome sweet home"))

        app = create_application("cut")
        output = app.execute(["-b", "1,2,3"])
        assert output == "hel\nhom\n"

    def test_stdin_hyphen_2side_args(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("hello world\nhome sweet home"))

        app = create_application("cut")
        output = app.execute(["-b", "1-3,7-9"])
        assert output == "helwor\nhomwee\n"

    def test_stdin_hyphen_1side_args(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("hello world\nhome sweet home"))

        app = create_application("cut")
        output = app.execute(["-b", "-3,7-"])
        assert output == "helworld\nhomweet home\n"

    def test_filein(self, create_sample_file_4cut):
        app = create_application("cut")
        output = app.execute(["-b", "1-3,7-9", create_sample_file_4cut])

        assert output == "helwor\nhomwee\n"


class TestGrep:
    def test_wrong_argsno(self):
        app = create_application("grep")
        with pytest.raises(ValueError):
            output = app.execute(["args1"])

    def test_onefile(self):
        app = create_application("grep")
        output = app.execute(["html", "../requirements.txt"])

        right_answer = "flake8-html\njunit2html"

    def test_multiplefiles(self):
        app = create_application("grep")
        output = app.execute(["ose", "../requirements.txt", "../README.md"])
        right_answer = (
            "../requirements.txt:nose2\n../README.md:COMP0010 Shell is "
            + "a [shell](https://en.wikipedia.org/wiki/Shell_(computing)) created "
            + "for educational purposes. \n"
        )

        assert output == right_answer


class TestEcho:
    def test_echo(self):
        app = create_application("echo")
        output = app.execute(["hello world"])
        assert output == "hello world\n"


class TestHead:
    def test_head_wrong_args_no(self):
        app = create_application("head")
        with pytest.raises(ValueError):
            output = app.execute(["../requirements.txt", "3"])

    def test_head_wrong_flags(self):
        app = create_application("head")
        with pytest.raises(ValueError):
            output = app.execute(["../requirements.txt", "3", "4"])

    def test_with_flag(self):
        app = create_application("head")
        output = app.execute(["-n", 3, "../requirements.txt"])
        rq_content = "nose2\ncoverage\nflake8-html\n"

        assert output == rq_content

    def test_no_flag(self):
        app = create_application("head")
        output = app.execute(["../requirements.txt"])

        rq_content = "nose2\ncoverage\nflake8-html\njunit2html\n"
        assert output == rq_content


class TestTail:
    def test_tail_wrong_args_no(self):
        app = create_application("tail")
        with pytest.raises(ValueError):
            output = app.execute(["../requirements.txt", "3"])

    def test_tail_wrong_flags(self):
        app = create_application("tail")
        with pytest.raises(ValueError):
            output = app.execute(["../requirements.txt", "3", "4"])

    def test_with_flag(self):
        app = create_application("tail")
        output = app.execute(["-n", 2, "../requirements.txt"])
        rq_content = "flake8-html\njunit2html\n"

        assert output == rq_content

    def test_no_flag(self):
        app = create_application("tail")
        output = app.execute(["../requirements.txt"])

        rq_content = "nose2\ncoverage\nflake8-html\njunit2html\n"
        assert output == rq_content


class TestCd:
    def test_cd_argsno(self):
        app = create_application("cd")

        with pytest.raises(ValueError):
            strout = app.execute(["args1", "args2"])

    def test_cd(self):
        app = create_application("cd")
        cwd = os.getcwd()
        up1level = cwd[0 : cwd.rfind("\\")]

        strout = app.execute([".."])
        assert strout == up1level


class TestLs:
    def test_ls_noargs(self):
        app = create_application("cd")

        with pytest.raises(ValueError):
            strout = app.execute(["args1", "args2"])

    def test_ls_zeroargs(self):
        output = []
        # list all the files inside lis_dir
        for f in os.listdir(os.getcwd()):
            if not f.startswith("."):
                output.append(f + "\n")

        app = create_application("ls")
        strout = app.execute()

        assert strout == "".join(output)

    def test_ls_wrongargs(self):
        app = create_application("ls")
        with pytest.raises(FileNotFoundError):
            strout = app.execute(["hello"])

    def test_ls_rightargs(self):
        cwd = os.getcwd()
        up1level = cwd[0 : cwd.rfind("\\")]

        output = []
        # list all the files inside lis_dir
        for f in os.listdir(up1level):
            if not f.startswith("."):
                output.append(f + "\n")

        app = create_application("ls")
        strout = app.execute([up1level])

        assert strout == "".join(output)


class TestPwd:
    ok_opts = ["L", "P"]

    def test_pwd(self):
        app = create_application("pwd")
        strout = app.execute()

        assert strout == os.getcwd()

    def test_pwd_args_noflags(self):
        app = create_application("pwd")
        strout = app.execute(["args1", "args", "arg3"])

        # somehow new application is not created so the output is not empty. output contains things from previous test
        assert strout == os.getcwd()

    def test_pwd_args_okflags(self):
        app = create_application("pwd")

        with pytest.raises(ValueError):
            strout = app.execute(["-L", "args2"])

    def test_pwd_args_wrongflags(self):
        app = create_application("pwd")

        with pytest.raises(ValueError):
            strout = app.execute(["args1", "-G"])
