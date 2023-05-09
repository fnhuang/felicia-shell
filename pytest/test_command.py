from command import Pipe, Call, Seq
from application import create_application
from collections import deque


def testCall():
    app = create_application("echo")
    c = Call(app, ["123"])
    inp = deque()
    out = deque()

    c.eval(inp, out)
    assert app.get_str_from_deque(out) == "123\n"


def testPipe():
    app1 = create_application("echo")
    c1 = Call(app1, ["123"])

    app2 = create_application("grep")
    c2 = Call(app2, ["1"])

    out = deque()
    p = Pipe(c1, c2)
    p.eval(deque(), out)
    assert app2.get_str_from_deque(out) == "123\n"


def testSeq():
    app1 = create_application("echo")
    c1 = Call(app1, ["123"])

    app2 = create_application("grep")
    c2 = Call(app2, ["1"])

    out = deque()
    s = Seq(c1, c2)
    s.eval(deque(), out)
    assert app2.get_str_from_deque(out) == "123\n"


def testPipeSeq():
    app1 = create_application("echo")
    c1 = Call(app1, ["123"])

    app2 = create_application("grep")
    c2 = Call(app2, ["1"])

    app3 = create_application("grep")
    c3 = Call(app3, ["4"])

    out = deque()
    p = Pipe(c1, Seq(c3, c2))
    p.eval(deque(), out)

    assert app2.get_str_from_deque(out) == ""


def testSeqPipe():
    app1 = create_application("echo")
    c1 = Call(app1, ["123"])

    app2 = create_application("grep")
    c2 = Call(app2, ["1"])

    app3 = create_application("grep")
    c3 = Call(app3, ["4"])

    out = deque()
    s = Seq(c3, Pipe(c1, c2))
    s.eval(deque(), out)

    assert app3.get_str_from_deque(out) == "123\n"
