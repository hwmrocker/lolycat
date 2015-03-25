#!/usr/bin/env python
"""
TODO:

  --force, right now this is always on
  --animate / duration / speed
  --help
"""

from __future__ import print_function, division
import re
import sys
import math
import random
from itertools import combinations


strip_ansi = re.compile(r'\e\[(\d+)(;\d+)?(;\d+)?[m|K]')
TAB_WIDTH = 8
ESC_FG = "\033[38{}m"
COLOR_NONE = "\033[0m"


class OptionNotValid(Exception): pass
class ArgumentRequired(Exception): pass


def rgb_value(red, green, blue):
    """
    returns a similar ansi color code for a given rgb rgb_value

    this function is inspired by function with the same name from the ruby_gem paint.
    https://github.com/janlelis/paint/blob/9c380b5d186fd116365c4fd26245cbc0410f07b7/lib/paint.rb#L229
    """
    sep = 42.5
    gray = all(map(lambda x: abs(x[0] - x[1]) < sep, combinations([red, green, blue], 2)))

    if gray:
        color_value = 232 + round((red + green + blue) / 33)
    else:
        def col_mod(x):
            col, mod = x
            return int(6 * col / 256) * mod
        color_value = 16 + sum(map(col_mod, [(red, 36), (green, 6), (blue, 1)]))
    return ";5;%d" % (color_value)


def rainbow(freq, i):
    """
    returns ansicode color for a given frequency and index.

    this function produces the same colors like lolcat, but returns the ansicode and not CSS hex values
    https://github.com/busyloop/lolcat/blob/9b6960095579a9871254828dc9144f5c5e878b00/lib/lolcat/lol.rb#L25
    """
    freqi = freq * i
    pi_3 = math.pi / 3
    red = int(math.sin(freqi + 0 * pi_3) * 127 + 128) % 255
    green = int(math.sin(freqi + 2 * pi_3) * 127 + 128) % 255
    blue = int(math.sin(freqi + 4 * pi_3) * 127 + 128) % 255
    return ESC_FG.format(rgb_value(red, green, blue))


def remove_tabs(line, tab_width=TAB_WIDTH):
    """
    replaces tabs with spaces and aligns them in columns with a width of tab_width
    """
    segments = line.split("\t")
    return "".join([segment +
        " " * ((tab_width - len(segment) % tab_width) if idx < (len(segments) - 1) else 0)
        for idx, segment in enumerate(segments)])


def println(line, args):
    """
    print a colorful cleared line

    we remove previous ansicodes and translate tabs to spaces
    """
    line = line.rstrip()
    line = strip_ansi.sub("", line)
    line = remove_tabs(line)
    # println_plain(line, args)
    for idx, char in enumerate(line):
        # print(rainbow(args["freq"], (args["linecounter"] + idx) / args["spread"]))
        print(rainbow(args["freq"], (args["linecounter"] + idx) / args["spread"]), char, COLOR_NONE, sep="", end="")
    print()


def main(args):
    for filenhandler in args["files"]:
        for line in filenhandler:
            args["linecounter"] += 1
            println(line, args)


if __name__ == "__main__":
    default_args_desc = {
            "spread": dict(default=3, type="float", short="p"),
            "freq": dict(default=0.1, type="float", short="F"),
            "seed": dict(default=None, type="int", short="S"),
            "animate": dict(default=False, type="bool", short="a"),
            "duration": dict(default=12, type="int", short="d"),
            "speed": dict(default=20, type="int", short="s"),
            "force": dict(default=False, type="bool", short="f"),
            "version": dict(default=False, type="bool", short="v"),
            "help": dict(default=False, type="bool", short="h"),
        }
    args = {"files": []}
    short_to_long_lookup = dict((d["short"], name) for name, d in default_args_desc.items())
    sysargs = sys.argv[1:]

    def apply_shortoptions(options):
        for idx, option in enumerate(options):
            is_last = (idx == (len(options) - 1))
            if option not in short_to_long_lookup:
                raise OptionNotValid
            apply_option(short_to_long_lookup[option], allow_next_arg=is_last)

    def apply_option(fullname, allow_next_arg=True):
        if fullname not in default_args_desc:
            raise OptionNotValid
        option_parameter = default_args_desc[fullname]
        option_type = option_parameter.get("type", "bool")
        if option_type == "bool":
            args[fullname] = True
        elif option_type == "int":
            if allow_next_arg and sysargs:
                args[fullname] == int(sysargs.pop(0))
            else:
                raise ArgumentRequired
        elif option_type == "float":
            if allow_next_arg and sysargs:
                args[fullname] == float(sysargs.pop(0))
            else:
                raise ArgumentRequired

    while sysargs:
        nextarg = sysargs.pop(0)
        if nextarg == "--":
            break
        elif nextarg == "-":
            sysargs.insert(0, nextarg)
            break
        elif nextarg.startswith("--"):
            apply_option(nextarg[2:])
        elif nextarg.startswith("-") and len(nextarg) > 1:
            apply_shortoptions(nextarg[1:])
        else:
            sysargs.insert(0, nextarg)
            break
    else:
        args["files"].append(sys.stdin)

    for filename in sysargs:
        if filename == "-":
            args["files"].append(sys.stdin)
        else:
            args["files"].append(open(filename))

    for fullname, parameter in default_args_desc.items():
        if fullname not in args:
            args[fullname] = parameter["default"]

    if args["version"]:
        print("lolycat 0.1")
        exit(0)
    if args["help"]:
        print("no")
        exit(0)
    args["linecounter"] = random.randint(0, 255) if args["seed"] is None else args["seed"]
    exit(main(args))
