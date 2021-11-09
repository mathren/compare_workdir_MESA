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


# This has been tested with MESA version 15140

import os
import sys
from pathlib import Path

# pip install -U termcolor
from termcolor import colored

# pip install -U click
import click


# ----- some auxiliary functions ----------------------------------


def get_name_val(line: "str"):
    """
    read the line removing comments and white spaces
    and returns the name of the option and the associated value
    """
    optionName = line.split("=")[0].rstrip().lstrip()
    optionName = optionName.lower()  ## convert everything to lowercase
    value = line.split("=")[-1].split("!")[0].rstrip().lstrip()
    return optionName, value


def conver_bool(val: "str") -> "str":
    """ fix occasional typo in MESA docs, might not be needed """
    if (val == ".true.") or (val == ".true"):
        return ".true."
    elif (val == ".false.") or (val == ".false"):
        return ".false."
    else:
        return val


def convert_float(val: "str") -> "float":
    """
    convert inlists entries into python floats
    to avoid mismatch do to formatting issues
    """
    try:
        tmp = val.replace("d", "e")
        new_val = float(tmp)
        return new_val
    except:
        return val


def clean_val(val):
    """ clean values in inlists """
    val = convert_float(val)
    val = conver_bool(val)
    return val


def get_MESA_DIR() -> str:
    """
    Read the MESA_DIR in the environment variables if not provided,
    and returns it as a string.
    """
    try:
        MESA_DIR = os.environ["MESA_DIR"]
        return MESA_DIR
    except KeyError:
        print(colored("Maybe $MESA_DIR environment variabile is not set?", "yellow"))
        print(colored("I don't know what to do, bye!", "yellow"))
        sys.exit()


# ----------------------- read the defaults ----------------------------------


def get_defaults(namelist: str, MESA_DIR="") -> "dict":
    """
    read the namelists from the MESA_DIR folder.
    MESA_DIR will be read from the environment variables if it is an empty string

    namelist can be either star_job, binary_job, controls, binary_controls, eos, kap, or pgstar
    returns a dictionary with MESA options as keys and the values set in the default files
    """
    defaults = {}
    if MESA_DIR == "":
        MESA_DIR = get_MESA_DIR()
    if namelist.lower() == "star_job":
        defaultFname = Path(MESA_DIR + "/star/defaults/star_job.defaults")
    elif namelist.lower() == "binary_job":
        defaultFname = Path(MESA_DIR + "/binary/defaults/binary_job.defaults")
    elif namelist.lower() == "controls":
        defaultFname = Path(MESA_DIR + "/star/defaults/controls.defaults")
    elif namelist.lower() == "binary_controls":
        defaultFname = Path(MESA_DIR + "/binary/defaults/binary_controls.defaults")
    elif namelist.lower() == "eos":
        if Path(MESA_DIR + "/eos/defaults/eos.defaults").exists():
            defaultFname = Path(MESA_DIR + "/eos/defaults/eos.defaults")
        else:
            print(colored("***********************************", "yellow"))
            print(colored("eos namelist not found in " + MESA_DIR, "yellow"))
            print(colored("***********************************", "yellow"))
            sys.exit()
    elif namelist.lower() == "kap":
        if Path(MESA_DIR + "/kap/defaults/kap.defaults").exists():
            defaultFname = Path(MESA_DIR + "/kap/defaults/kap.defaults")
        else:
            print(colored("***********************************", "yellow"))
            print(colored("kap namelist not found in " + MESA_DIR, "yellow"))
            print(colored("***********************************", "yellow"))
            sys.exit()
    elif namelist.lower() == "pgstar":
        defaultFname = Path(MESA_DIR + "/star/defaults/pgstar.defaults")
    else:
        print(
            colored("Namelist: " + namelist + " not recognized, don't know what to do!", "yellow",)
        )
        return defaults
    # now if we did not exit already, load a dict
    # print(defaultFname)
    with open(defaultFname, "r") as f:
        for i, line in enumerate(f):
            l = line.strip("\n\r").strip()  # remove \n and white spaces
            if (l == "") or (l[0] == "!"):
                # empty line or comment, move on
                continue
            else:
                optionName, value = get_name_val(l)
                value = clean_val(value)
                defaults[optionName] = value
    # Note, the longest key is ~45 characters in length, hence the 45 further down in the string formatting
    return defaults


# --------------------- read namelist of the inlists -------------------------


def get_job_namelist(inlist: "str"):
    """
    returns a dictionary of the star_job or binary_job namelist entries
    inside inlist, and values and a flag for binaries
    """
    job = {}
    is_binary = False
    with open(inlist, "r") as i1:
        in_job_namelist = False
        for i, line in enumerate(i1):
            # print(line.strip('\n\r'))
            l = line.strip("\n\r").rstrip().lstrip()  # remove \n and white spaces
            if "&star_job" == l.lower():
                in_job_namelist = True
                is_binary = False
                continue  # to avoid adding the first line
            elif "&binary_job" == l.lower():
                in_job_namelist = True
                is_binary = True
                continue  # to avoid adding the first line
            if in_job_namelist:
                if (l == "") or (l[0] == "!"):
                    # skip empty lines
                    pass
                else:
                    if l[0] == "/":  # exit
                        in_job_namelist = False
                        break
                    else:
                        option_name, value = get_name_val(l)
                        value = clean_val(value)
                        job[option_name] = value
    return job, is_binary


def get_controls_namelist(inlist: "str") -> "dict":
    """
    returns a dictionary of the controls or binary_controls namelist entries and values
    and a flag for binaries
    """
    controls = {}
    is_binary = False
    with open(inlist, "r") as i1:
        in_controls_namelist = False
        for i, line in enumerate(i1):
            # print(line.strip('\n\r'))
            l = line.strip("\n\r").rstrip().lstrip()  # remove \n and white spaces
            if "&controls" == l.lower():
                in_controls_namelist = True
                is_binary = False
                continue  # to avoid adding the first line
            elif "&binary_controls" == l.lower():
                in_controls_namelist = True
                is_binary = True
                continue  # to avoid adding the first line
            if in_controls_namelist:
                if (l == "") or (l[0] == "!"):
                    # skip empty lines
                    pass
                else:
                    if l[0] == "/":  # exit
                        in_controls_namelist = False
                        break
                    else:
                        option_name, value = get_name_val(l)
                        value = clean_val(value)
                        controls[option_name] = value
    return controls, is_binary


def get_eos_namelist(inlist: "str") -> "dict":
    """
    returns a dictionary of the eos and values
    """
    eos = {}
    with open(inlist, "r") as i1:
        in_eos_namelist = False
        for i, line in enumerate(i1):
            # print(line.strip('\n\r'))
            l = line.strip("\n\r").rstrip().lstrip()  # remove \n and white spaces
            if "&eos" == l.lower():
                in_eos_namelist = True
                continue  # to avoid adding the first line
            if in_eos_namelist:
                if (l == "") or (l[0] == "!"):
                    # skip empty lines
                    pass
                else:
                    if l[0] == "/":  # exit
                        in_controls_namelist = False
                        break
                    else:
                        option_name, value = get_name_val(l)
                        value = clean_val(value)
                        eos[option_name] = value
    return eos


def get_kap_namelist(inlist: "str") -> "dict":
    """
    returns a dictionary of the kap and values
    """
    kap = {}
    with open(inlist, "r") as i1:
        in_kap_namelist = False
        for i, line in enumerate(i1):
            # print(line.strip('\n\r'))
            l = line.strip("\n\r").rstrip().lstrip()  # remove \n and white spaces
            if "&kap" == l.lower():
                in_kap_namelist = True
                continue  # to avoid adding the first line
            if in_kap_namelist:
                if (l == "") or (l[0] == "!"):
                    # skip empty lines
                    pass
                else:
                    if l[0] == "/":  # exit
                        in_controls_namelist = False
                        break
                    else:
                        option_name, value = get_name_val(l)
                        value = clean_val(value)
                        kap[option_name] = value
    return kap


def get_pgstar_namelist(inlist: "str") -> "dict":
    """
    returns a dictionary of the pgstar namelist entries and values
    """
    pgstar = {}
    with open(inlist, "r") as i1:
        in_pgstar_namelist = False
        for i, line in enumerate(i1):
            # print(line.strip('\n\r'))
            l = line.strip("\n\r").rstrip().lstrip()  # remove \n and white spaces
            if "&pgstar" == l.lower():
                in_pgstar_namelist = True
                continue  # to avoid adding the first line
            if in_pgstar_namelist:
                if (l == "") or (l[0] == "!"):
                    # skip empty lines
                    pass
                else:
                    if l[0] == "/":  # exit
                        in_pgstar_namelist = False
                        break
                    else:
                        option_name, value = get_name_val(l)
                        value = clean_val(value)
                        pgstar[option_name] = value
    return pgstar


# ---------- compare namelists entries between each other and defaults -------------------------


def compare_and_report(
    k: "str", dic1: "dict", dic2: "dict", string1: "str", string2: "str", vb=False
):
    """
    Given two dictionaries, compares their entry k.
    Assumes the inlist name is less than 30 characters.
    The longest MESA parameter is about 45 characters.
    """
    if dic1[k] != dic2[k]:
        print(colored(f"{string1:<30}\t{k}={str(dic1[k]):<45}", "red"))
        print(colored(f"{string2:<30}\t{k}={str(dic2[k]):<45}", "red"))
        print("")
    elif vb:
        print(colored(f"{string1:<30}\t{k}={str(dic1[k]):<45}", "green"))
        print(colored(f"{string2:<30}\t{k}={str(dic2[k]):<45}", "green"))
        print("")


def compare_defaults_and_report(
    k: "str", dic: "dict", dic_defaults: "dict", string: "str", string_other: "str", vb=False
):
    """
    Given two dictionaries, compares the entry with key k and prints if not default.
    Assumes the inlist name is less than 30 characters.
    The longest MESA parameter is about 45 characters.
    """
    default = "default"  # for fstring
    try:
        tmp = dic_defaults[k]
    except KeyError:
        print(colored(k + " not in defaults", "yellow"))
        # print(colored(dic_defaults.keys(),"yellow"))
        return
    if dic[k] != dic_defaults[k]:
        print(colored(f"{string:<30}\t{k}={str(dic[k]):<45}", "red"))
        print(colored(f"{string_other:<30}\tmissing", "red"))
        print(colored(f"{default:<30}\t{k}={str(dic_defaults[k]):<45}", "red"))
        print("")
    elif vb:
        print(colored(f"{string:<30}\t{k}={str(dic[k]):<45}", "green"))
        print(colored(f"{default:<30}\t{k}={str(dic_defaults[k]):<45}", "green"))
        print("")


# --------------do the diff individual namelists ---------------------------


def diff_starjob(job1: "dict", job2: "dict", string1: "str", string2: "str", MESA_DIR="", vb=False):
    # check the keys appearing in both
    for k in job1.keys() & job2.keys():
        compare_and_report(k, job1, job2, string1, string2, vb)
    # check keys that are not in both and check if they are different than defaults
    defaults = get_defaults("star_job", MESA_DIR)
    # keys in job1 but not job2
    k1 = set(job1.keys()).difference(set(job2.keys()))
    for k in k1:
        compare_defaults_and_report(k, job1, defaults, string1, string2, vb)
    # keys in job2 but not job1
    k2 = set(job2.keys()).difference(set(job1.keys()))
    for k in k2:
        compare_defaults_and_report(k, job2, defaults, string2, string1, vb)


def diff_eos(eos1: "dict", eos2: "dict", string1: "str", string2: "str", MESA_DIR="", vb=False):
    # check the keys appearing in both
    for k in eos1.keys() & eos2.keys():
        compare_and_report(k, eos1, eos2, string1, string2, vb)
    # check keys that are not in both and check if they are different than defaults
    defaults = get_defaults("eos", MESA_DIR)
    # keys in job1 but not job2
    k1 = set(eos1.keys()).difference(set(eos2.keys()))
    for k in k1:
        compare_defaults_and_report(k, eos1, defaults, string1, string2, vb)
    # keys in job2 but not job1
    k2 = set(eos2.keys()).difference(set(eos1.keys()))
    for k in k2:
        compare_defaults_and_report(k, eos2, defaults, string2, string1, vb)


def diff_kap(kap1: "dict", kap2: "dict", string1: "str", string2: "str", MESA_DIR="", vb=False):
    # check the keys appearing in both
    for k in kap1.keys() & kap2.keys():
        compare_and_report(k, kap1, kap2, string1, string2, vb)
    # check keys that are not in both and check if they are different than defaults
    defaults = get_defaults("kap", MESA_DIR)
    # keys in job1 but not job2
    k1 = set(kap1.keys()).difference(set(kap2.keys()))
    for k in k1:
        compare_defaults_and_report(k, kap1, defaults, string1, string2, vb)
    # keys in job2 but not job1
    k2 = set(kap2.keys()).difference(set(kap1.keys()))
    for k in k2:
        compare_defaults_and_report(k, kap2, defaults, string2, string1, vb)


def diff_controls(
    controls1: "dict", controls2: "dict", string1: "str", string2: "str", MESA_DIR="", vb=False
):
    # check the keys appearing in both
    for k in controls1.keys() & controls2.keys():
        compare_and_report(k, controls1, controls2, string1, string2, vb)
    # check keys that are not in both and check if they are different than defaults
    defaults = get_defaults("controls", MESA_DIR)
    # keys in controls1 but not controls2
    k1 = set(controls1.keys()).difference(set(controls2.keys()))
    for k in k1:
        compare_defaults_and_report(k, controls1, defaults, string1, string2, vb)
    # keys in controls2 but not controls1
    k2 = set(controls2.keys()).difference(set(controls1.keys()))
    for k in k2:
        compare_defaults_and_report(k, controls2, defaults, string2, string1, vb)


def diff_pgstar(
    pgstar1: "dict", pgstar2: "dict", string1: "str", string2: "str", MESA_DIR="", vb=False
):
    # check the keys appearing in both
    for k in pgstar1.keys() & pgstar2.keys():
        compare_and_report(k, pgstar1, pgstar2, string1, string2, vb)
    # check keys that are not in both and check if they are different than defaults
    defaults = get_defaults("pgstar", MESA_DIR)
    # keys in pgstar1 but not pgstar2
    k1 = set(pgstar1.keys()).difference(set(pgstar2.keys()))
    for k in k1:
        compare_defaults_and_report(k, pgstar1, defaults, string1, string2, vb)
    # keys in pgstar2 but not pgstar1
    k2 = set(pgstar2.keys()).difference(set(pgstar1.keys()))
    for k in k2:
        compare_defaults_and_report(k, pgstar2, defaults, string2, string1, vb)


def diff_binary_job(
    job1: "dict", job2: "dict", string1: "str", string2: "str", MESA_DIR="", vb=False
):
    # check the keys appearing in both
    for k in job1.keys() & job2.keys():
        compare_and_report(k, job1, job2, string1, string2, vb)
    # check keys that are not in both and check if they are different than defaults
    defaults = get_defaults("binary_job", MESA_DIR)
    # keys in job1 but not job2
    k1 = set(job1.keys()).difference(set(job2.keys()))
    for k in k1:
        compare_defaults_and_report(k, job1, defaults, string1, string2, vb)
    # keys in job2 but not job1
    k2 = set(job2.keys()).difference(set(job1.keys()))
    for k in k2:
        compare_defaults_and_report(k, job2, defaults, string2, string1, vb)


def diff_binary_controls(
    controls1: "dict", controls2: "dict", string1: "str", string2: "str", MESA_DIR="", vb=False
):
    # check the keys appearing in both
    for k in controls1.keys() & controls2.keys():
        compare_and_report(k, controls1, controls2, string1, string2, vb)
    # check keys that are not in both and check if they are different than defaults
    defaults = get_defaults("binary_controls", MESA_DIR)
    # keys in controls1 but not controls2
    k1 = set(controls1.keys()).difference(set(controls2.keys()))
    for k in k1:
        compare_defaults_and_report(k, controls1, defaults, string1, string2, vb)
    # keys in controls2 but not controls1
    k2 = set(controls2.keys()).difference(set(controls1.keys()))
    for k in k2:
        compare_defaults_and_report(k, controls2, defaults, string2, string1, vb)


# ----------- do the diff of the whole inlists ----------------------------


def diff_inlists(inlist1: "str", inlist2: "str", do_pgstar=False, MESA_DIR="", vb=False):
    """
    Takes the path of two inlists and compares them taking care of
    comments and missing entries set to default.
    Prints a pretty diff of the inlists, or nothing if they are the same (unless vb=True).
    Will ignore order, comments, and empty lines. Works for single stars and binaries.
    """
    if MESA_DIR == "":
        MESA_DIR = get_MESA_DIR()
        # print(MESA_DIR)
    name1 = "1: " + inlist1.split("/")[-1]
    name2 = "2: " + inlist2.split("/")[-1]
    ## check star_job
    job1, is_binary1 = get_job_namelist(inlist1)
    job2, is_binary2 = get_job_namelist(inlist2)
    if is_binary1 != is_binary2:
        print(colored("ERROR: comparing binary to single star!", "red"))
        return
    else:
        if is_binary1 == False:
            print("")
            print("&star_job")
            diff_starjob(job1, job2, name1, name2, MESA_DIR, vb)
            print("/ !end star_job namelist")
        else:
            print("")
            print("&binary_job")
            diff_binary_job(job1, job2, name1, name2, MESA_DIR, vb)
            print("/ !end binary_job namelist")
    ## check eos
    eos1 = get_eos_namelist(inlist1)
    eos2 = get_eos_namelist(inlist2)
    print("")
    print("&eos")
    diff_eos(eos1, eos2, name1, name2, MESA_DIR, vb)
    print("/ !end eos namelist")
    ## check kap
    kap1 = get_kap_namelist(inlist1)
    kap2 = get_kap_namelist(inlist2)
    print("")
    print("&kap")
    diff_kap(kap1, kap2, name1, name2, MESA_DIR, vb)
    print("/ !end kap namelist")
    ## check controls
    controls1, is_binary1 = get_controls_namelist(inlist1)
    controls2, is_binary2 = get_controls_namelist(inlist2)
    if is_binary1 != is_binary2:
        print(colored("ERROR: comparing binary to single star!", "red"))
        return
    else:
        if is_binary1 == False:
            print("")
            print("&controls")
            diff_controls(
                controls1, controls2, name1, name2, MESA_DIR, vb,
            )
        else:
            print("")
            print("&binary_controls")
            diff_binary_controls(
                controls1, controls2, name1, name2, MESA_DIR, vb,
            )
    print("/ !end controls namelist")
    if do_pgstar:
        # check pgstar
        # this will compare single pgstar namelists and binaries
        print("")
        print("&pgstar")
        pgstar1 = get_pgstar_namelist(inlist1)
        pgstar2 = get_pgstar_namelist(inlist2)
        diff_pgstar(pgstar1, pgstar2, name1, name2, MESA_DIR, vb)
        print("/ !end pgstar")


# # ----------------- for testing on the MESA test_suite -------------------------------


def test_diff_inlists(outfile="", MESA_DIR=""):
    """
    Run all possible pairs of inlists from the test_suite as a test
    """
    import time

    failed = 0
    go_on = input("Do you want to do this very long test? [Y/y]")
    if go_on == "Y" or go_on == "y":
        t_start = time.time()
        import glob
        import itertools

        if MESA_DIR == "":
            MESA_DIR = get_MESA_DIR()
        inlists_single = glob.glob(MESA_DIR + "/star/test_suite/*/inlist*")
        inlists_binary = glob.glob(MESA_DIR + "/binary/test_suite/*/inlist*")
        inlists = list(set().union(inlists_binary, inlists_single))
        print(inlists)
        input("go on?")
        # this below could be parallelized
        for pair in itertools.combinations_with_replacement(inlists, 2):
            inlist1 = pair[0]
            inlist2 = pair[1]
            try:
                diff_inlists(inlist1, inlist2, do_pgstar=True)
            except:
                print(colored("FAILED: " + inlist1 + " " + inlist2, "yellow"))
                if outfile != "":
                    with open(outfile, "a") as F:
                        F.writelines("FAILED: " + inlist1 + " " + inlist2 + "\n")
                failed += 1
        t_end = time.time()
    else:
        t_start = 0
        t_end = 0
        print("If you don't try nothing fails...that's perfect!")
    print("...test took", t_end - t_start, "seconds")
    return failed


# command line wrapper
@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("inlist1", nargs=1, type=click.Path(exists=True))
@click.argument("inlist2", nargs=1, type=click.Path(exists=True))
@click.option("--pgstar", default=False, help="Show also diff of pgstar namelists.")
@click.option(
    "--mesa_dir",
    default="",
    help="use customized location of $MESA_DIR. Will use environment variable if empty and return an error if empty.",
)
@click.option("--vb", default=False, help="Show also matching lines using green.")
def compare_inlists(inlist1: str, inlist2: str, pgstar: bool, mesa_dir: str, vb: bool):
    diff_inlists(inlist1, inlist2, do_pgstar=pgstar, MESA_DIR=mesa_dir, vb=vb)

if __name__ == "__main__":
    compare_inlists()
