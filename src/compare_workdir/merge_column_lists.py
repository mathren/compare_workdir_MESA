#!/usr/bin/python3
# author: Mathieu Renzo

# Author: Mathieu Renzo <mathren90@gmail.com>
# Keywords: files

# Copyright (C) 2019-2021 Mathieu Renzo

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

# pip install -U termcolor
from termcolor import colored

# pip install -U click
import click


def list_type(col_list):
    if "profile_columns.list" in col_list:
        return "profile_columns"
    # note the order
    elif "binary_history_columns.list" in col_list:
        return "binary_columns"
    elif "history_columns.list" in col_list:
        return "history_columns"
    else:
        return "unknown"


def read_col_list(col_list):
    """reads a file and returns a list of columns ignoring empty lines and comments"""
    col = []
    with open(col_list, "r") as F:
        for i, line in enumerate(F):
            l = line.strip("\n\r").rstrip().lstrip()  # remove \n and white spaces
            if (l == "") or (l[0] == "!"):
                # skip empty lines and comments
                pass
            else:
                # remove comments and add to list
                col.append(l.split('!')[0].rstrip())
    return col


def merge_columns(list1: "str", list2: "str", outlist="", MESA_DIR=""):
    """if outlist is given, returns a column list merging list1 and list2"""
    # check they are compatible
    if (list_type(list1) != list_type(list2)) or (list_type(list1) == "unknown") or (list_type(list2) == "unknown"):
        print(colored("list types incompatible!", "red"))
        print(colored("1: " + list_type(list1), "red"))
        print(colored("2: " + list_type(list2), "red"))
        return
    col1 = read_col_list(list1)
    col2 = read_col_list(list2)
    col_new = sorted(list(set(col1 + col2)))
    # print(col_new)
    # N.B: if columns have disappeared in between MESA versions this won't deal with it for your
    if outlist != "":
        with open(outlist, "a") as F:
            for c in col_new:
                F.write(c + "\n")
    else:
        print(col_new)


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("list1", nargs=1, type=click.Path(exists=True))
@click.argument("list2", nargs=1, type=click.Path(exists=True))
@click.argument("outlist", nargs=1)
@click.option(
    "--mesa_dir",
    default="",
    help="use customized location of $MESA_DIR. Will use environment variable if empty and return an error if empty.",
)
def merge_column_lists(list1: str, list2: str, mesa_dir: str, outlist: str):
    merge_columns(list1, list2, outlist=outlist, MESA_DIR=mesa_dir)

if __name__ == "__main__":
    merge_column_lists()
