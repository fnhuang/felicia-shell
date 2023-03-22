import re
from glob import glob


def eval(cmdline):
    raw_commands = []

    # find command that matches any character other than " ' ;
    # or any word surrounded by "", that is not "
    # or any word surrounded by '', that is not '
    # for each non-overlapping match
    # for m in re.finditer("([^\"';]+|\"[^\"]*\"|'[^']*')", cmdline):
    for m in re.finditer('.*(;)(?=(?:[^"\']|"\'[^"\']*")*$)|.*', cmdline):
        # if there is a match (each match is considered a command)
        if m.group(0):
            # get the match and append it to raw commands
            if m.group(0).endswith(";"):
                raw_commands.append(m.group(0)[:-1])
            else:
                raw_commands.append(m.group(0))

    print("raw_commands: ", raw_commands)

    # for each command
    for command in raw_commands:
        tokens = []
        # print("raw_command:", command)

        # find token that matches any character other than whitespace,' and "
        # or any word surrounded by "", that is not "
        # or any word surrounded by '', that is not '
        # for each non-overlapping match
        for m in re.finditer("[^\\s\"']+|\"([^\"]*)\"|'([^']*)'", command):
            # print("to be processed: ", m.group(0))
            # if there is a match for second or third condition
            # group(1) literally means the first parenthesized subgroup (thus, excluding the quotes)
            if m.group(1) or m.group(2):
                # print("--group 1/2")
                # group (0) means the entire match (thus, including quotes)
                quoted = m.group(0)
                # remove the quotes and add into the list of tokens
                tokens.append(quoted[1:-1])
            else:
                # print("--no group 1/2")
                # glob function is a module that searches for files where the filename matches a certain pattern
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

        print("app-args:", app, args)


cmdline = "find './themes/aa;fu' -name aafu*.txt;echo hello;jjj"
print(eval(cmdline))
