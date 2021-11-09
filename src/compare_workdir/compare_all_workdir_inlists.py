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
from .compare_inlists import (
    get_job_namelist,
    get_eos_namelist,
    get_kap_namelist,
    get_controls_namelist,
    get_defaults,
    diff_binary_controls,
    diff_binary_job,
    diff_controls,
    diff_eos,
    diff_kap,
    diff_pgstar,
    diff_starjob,
)

# ------------------------- some auxiliary functions ----------------------------------


def append_inlist_path(path_list: "list", path: "str", work_dir="./") -> "str":
    """
    takes the list of paths to inlists, and adds the path to a new inlist,
    taking care of absolute vs. relative paths
    """
    if Path(path).is_absolute():
        path_list.append(path)
    else:  # it's relative
        path_list.append(work_dir + "/" + path)
    return path_list


def get_first_inlist(work_dir: "str") -> "str":
    inlist = work_dir + "/inlist"
    if os.path.isfile(inlist):
        return inlist
    else:
        print(colored(work_dir + " has no inlist, too complex for me", "yellow"))
        sys.exit()


def is_folder_binary(work_dir: "str") -> "bool":
    """
    checks if the provided path is to a work directory for a MESA binary run
    (returns True) or single star (returns False)
    """
    inlist = get_first_inlist(work_dir)
    is_binary = get_job_namelist(inlist)[1]
    return is_binary


def get_top_binary_inlist(job1: "dict", job2: "dict", MESA_DIR=""):
    """
    reads the inlist for each individual star in a binary
    for both folders we are comparing. If not present, use the default
    """
    # primary first binary
    try:
        main_inlist_star1_b1 = job1["inlist_names(1)"]
    except KeyError:
        job_defaults = get_defaults("binary_job", MESA_DIR=MESA_DIR)
        main_inlist_star1_b1 = job_defaults["inlist_names(1)"]
    # either way you got it, clean it
    main_inlist_star1_b1 = main_inlist_star1_b1.strip("'").strip('"')
    # secondary first binary
    try:
        main_inlist_star2_b1 = job1["inlist_names(2)"]
    except KeyError:
        job_defaults = get_defaults("binary_job", MESA_DIR=MESA_DIR)
        main_inlist_star2_b1 = job_defaults["inlist_names(2)"]
    main_inlist_star2_b1 = main_inlist_star2_b1.strip("'").strip('"')
    # primary second binary
    try:
        main_inlist_star1_b2 = job2["inlist_names(1)"]
    except KeyError:
        job_defaults = get_defaults("binary_job", MESA_DIR=MESA_DIR)
        main_inlist_star1_b2 = job_defaults["inlist_names(1)"]
    main_inlist_star1_b2 = main_inlist_star1_b2.strip("'").strip('"')
    # secondary first binary
    try:
        main_inlist_star2_b2 = job2["inlist_names(2)"]
    except KeyError:
        job_defaults = get_defaults("binary_job", MESA_DIR=MESA_DIR)
        main_inlist_star2_b2 = job_defaults["inlist_names(2)"]
    main_inlist_star2_b2 = main_inlist_star2_b2.strip("'").strip('"')
    return (
        main_inlist_star1_b1,
        main_inlist_star2_b1,
        main_inlist_star1_b2,
        main_inlist_star2_b2,
    )


# ------------------ check if there are nested namelists -------------------------------


def check_if_more_star_job(job: "dict", work_dir="./") -> "list":
    """
    Check if there are more star_job namelists to be read and returns a
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if job.get("read_extra_star_job_inlist1") == ".true.":
        new_inlist = job.get("extra_star_job_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if job.get("read_extra_star_job_inlist2") == ".true.":
        new_inlist = job.get("extra_star_job_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if job.get("read_extra_star_job_inlist3") == ".true.":
        new_inlist = job.get("extra_star_job_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if job.get("read_extra_star_job_inlist4") == ".true.":
        new_inlist = job.get("extra_star_job_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if job.get("read_extra_star_job_inlist5") == ".true.":
        new_inlist = job.get("extra_star_job_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    return inlists_to_be_read


def check_if_more_eos(eos: "dict", work_dir="./") -> "list":
    """
    Check if there are more eos namelists to be read and returns a
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if eos.get("read_extra_eos_inlist1") == ".true.":
        new_inlist = eos.get("extra_eos_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if eos.get("read_extra_eos_inlist2") == ".true.":
        new_inlist = eos.get("extra_eos_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if eos.get("read_extra_eos_inlist3") == ".true.":
        new_inlist = eos.get("extra_eos_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if eos.get("read_extra_eos_inlist4") == ".true.":
        new_inlist = eos.get("extra_eos_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if eos.get("read_extra_eos_inlist5") == ".true.":
        new_inlist = eos.get("extra_eos_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    return inlists_to_be_read


def check_if_more_kap(kap: "dict", work_dir="./") -> "list":
    """
    Check if there are more kap namelists to be read and returns a
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if kap.get("read_extra_kap_inlist1") == ".true.":
        new_inlist = kap.get("extra_kap_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if kap.get("read_extra_kap_inlist2") == ".true.":
        new_inlist = kap.get("extra_kap_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if kap.get("read_extra_kap_inlist3") == ".true.":
        new_inlist = kap.get("extra_kap_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if kap.get("read_extra_kap_inlist4") == ".true.":
        new_inlist = kap.get("extra_kap_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if kap.get("read_extra_kap_inlist5") == ".true.":
        new_inlist = kap.get("extra_kap_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    return inlists_to_be_read


def check_if_more_binary_job(job: "dict", work_dir="./") -> "list":
    """
    Check if there are more binary_job namelists to be read and returns a
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if job.get("read_extra_binary_job_inlist1") == ".true.":
        new_inlist = job.get("extra_binary_job_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if job.get("read_extra_binary_job_inlist2") == ".true.":
        new_inlist = job.get("extra_binary_job_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if job.get("read_extra_binary_job_inlist3") == ".true.":
        new_inlist = job.get("extra_binary_job_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if job.get("read_extra_binary_job_inlist4") == ".true.":
        new_inlist = job.get("extra_binary_job_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if job.get("read_extra_binary_job_inlist5") == ".true.":
        new_inlist = job.get("extra_binary_job_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    return inlists_to_be_read


def check_if_more_controls(controls: "dict", work_dir="./") -> "inlist":
    """
    Check if there are more controls namelists to be read and returns a
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if controls.get("read_extra_controls_inlist1") == ".true.":
        new_inlist = controls.get("extra_controls_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if controls.get("read_extra_controls_inlist2") == ".true.":
        new_inlist = controls.get("extra_controls_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if controls.get("read_extra_controls_inlist3") == ".true.":
        new_inlist = controls.get("extra_controls_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if controls.get("read_extra_controls_inlist4") == ".true.":
        new_inlist = controls.get("extra_controls_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if controls.get("read_extra_controls_inlist5") == ".true.":
        new_inlist = controls.get("extra_controls_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    return inlists_to_be_read


def check_if_more_binary_controls(binary_controls: "dict", work_dir="./") -> "list":
    """
    Check if there are more binary_controls namelists to be read and returns a
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if binary_controls.get("read_extra_binary_controls_inlist1") == ".true.":
        new_inlist = binary_controls.get("extra_binary_controls_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if binary_controls.get("read_extra_binary_controls_inlist2") == ".true.":
        new_inlist = binary_controls.get("extra_binary_controls_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if binary_controls.get("read_extra_binary_controls_inlist3") == ".true.":
        new_inlist = binary_controls.get("extra_binary_controls_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if binary_controls.get("read_extra_binary_controls_inlist4") == ".true.":
        new_inlist = binary_controls.get("extra_binary_controls_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if binary_controls.get("read_extra_binary_controls_inlist5") == ".true.":
        new_inlist = binary_controls.get("extra_binary_controls_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    return inlists_to_be_read


def check_if_more_pgstar(pgstar: "dict", work_dir="./") -> "list":
    """
    Check if there are more pgstar namelists to be read and returns a
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if pgstar.get("read_extra_pgstar_inlist1") == ".true.":
        new_inlist = pgstar.get("extra_pgstar_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if pgstar.get("read_extra_pgstar_inlist2") == ".true.":
        new_inlist = pgstar.get("extra_pgstar_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if pgstar.get("read_extra_pgstar_inlist3") == ".true.":
        new_inlist = pgstar.get("extra_pgstar_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if pgstar.get("read_extra_pgstar_inlist4") == ".true.":
        new_inlist = pgstar.get("extra_pgstar_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if pgstar.get("read_extra_pgstar_inlist5") == ".true.":
        new_inlist = pgstar.get("extra_pgstar_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    return inlists_to_be_read


def check_if_more_binary_pgstar(binary_pgstar: "dict", work_dir="./") -> "list":
    """
    Check if there are more binary_pgstar namelists to be read and returns a
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if binary_pgstar.get("read_extra_binary_pgstar_inlist1") == ".true.":
        new_inlist = binary_pgstar.get("extra_binary_pgstar_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if binary_pgstar.get("read_extra_binary_pgstar_inlist2") == ".true.":
        new_inlist = binary_pgstar.get("extra_binary_pgstar_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if binary_pgstar.get("read_extra_binary_pgstar_inlist3") == ".true.":
        new_inlist = binary_pgstar.get("extra_binary_pgstar_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if binary_pgstar.get("read_extra_binary_pgstar_inlist4") == ".true.":
        new_inlist = binary_pgstar.get("extra_binary_pgstar_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    if binary_pgstar.get("read_extra_binary_pgstar_inlist5") == ".true.":
        new_inlist = binary_pgstar.get("extra_binary_pgstar_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = append_inlist_path(inlists_to_be_read, new_inlist, work_dir)
    return inlists_to_be_read


# ----------------- build the dictionary that MESA will use ------------------------------


def build_top_star_job(work_dir: "str", first_inlist="") -> "dict":
    """
    Builds the star_job namelist by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed.
    """
    if first_inlist == "":
        first_inlist = get_first_inlist(work_dir)
    job = get_job_namelist(first_inlist)[0]
    inlists_to_be_read = check_if_more_star_job(job, work_dir=work_dir)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " star_job namelist")
        job_to_add = get_job_namelist(current_inlist)[0]
        inlists_to_add = check_if_more_star_job(job_to_add, work_dir=work_dir)
        # merge dictionaries with over-write
        job = {**job, **job_to_add}
        ## note: if the same read_extra_star_job is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA works
        # print(job)
        ## remove inlist we are doing now from list
        inlists_to_be_read.remove(current_inlist)
        ## add possible new inlists
        if inlists_to_add:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                # but we still want to add stuff
                inlists_to_be_read = inlists_to_add
    return job


def build_top_binary_job(work_dir: "str", first_inlist="") -> "dict":
    """
    Builds the namelist binary_job by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed.
    """
    if first_inlist == "":
        first_inlist = get_first_inlist(work_dir)
    job = get_job_namelist(first_inlist)[0]
    inlists_to_be_read = check_if_more_binary_job(job, work_dir=work_dir)
    # print(inlists_to_be_read)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " binary_job namelist")
        job_to_add = get_job_namelist(current_inlist)[0]
        inlists_to_add = check_if_more_binary_job(job_to_add, work_dir=work_dir)
        job = {**job, **job_to_add}
        ## note: if the same read_extra_binary_job is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA works
        # print(job)
        ## remove inlist we are doing now from list
        inlists_to_be_read.remove(current_inlist)
        ## add possible new inlists
        if inlists_to_add:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                # but we still want to add stuff
                inlists_to_be_read = inlists_to_add
    return job


def build_top_eos(work_dir: "str", first_inlist="") -> "dict":
    """
    Builds the eos namelist by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed.
    """
    if first_inlist == "":
        first_inlist = get_first_inlist(work_dir)
    eos = get_eos_namelist(first_inlist)
    inlists_to_be_read = check_if_more_eos(eos, work_dir=work_dir)
    # print(inlists_to_be_read)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " eos namelist")
        eos_to_add = get_eos_namelist(current_inlist)
        inlists_to_add = check_if_more_eos(eos_to_add, work_dir=work_dir)
        eos = {**eos, **eos_to_add}
        ## note: if the same read_extra_eos is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA worksg
        # print(eos)
        ## remove inlist we are doing now from list
        inlists_to_be_read.remove(current_inlist)
        ## add possible new inlists
        if inlists_to_add:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                inlists_to_be_read = inlists_to_add
    return eos


def build_top_kap(work_dir: "str", first_inlist="") -> "dict":
    """
    Builds the kap namelist by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed.
    """
    if first_inlist == "":
        first_inlist = get_first_inlist(work_dir)
    kap = get_kap_namelist(first_inlist)
    inlists_to_be_read = check_if_more_kap(kap, work_dir=work_dir)
    # print(inlists_to_be_read)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " kap namelist")
        kap_to_add = get_kap_namelist(current_inlist)
        inlists_to_add = check_if_more_kap(kap_to_add, work_dir=work_dir)
        kap = {**kap, **kap_to_add}
        ## note: if the same read_extra_kap is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA works
        # print(kap)
        ## remove inlist we are doing now from list
        inlists_to_be_read.remove(current_inlist)
        ## add possible new inlists
        if not inlists_to_add:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                inlists_to_be_read = inlists_to_add
    return kap


def build_top_controls(work_dir: "str", first_inlist=""):
    """
    Builds the controls namelist by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed.
    """
    if first_inlist == "":
        first_inlist = get_first_inlist(work_dir)
    controls = get_controls_namelist(first_inlist)[0]
    inlists_to_be_read = check_if_more_controls(controls, work_dir=work_dir)
    # print(inlists_to_be_read)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " controls namelist")
        controls_to_add = get_controls_namelist(current_inlist)[0]
        controls = {**controls, **controls_to_add}
        ## note: if the same read_extra_star_controls is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA works
        # print(controls)
        ## remove inlist we are doing now from list
        inlists_to_be_read.remove(current_inlist)
        inlists_to_add = check_if_more_controls(controls_to_add, work_dir=work_dir)
        ## add possible new inlists
        if inlists_to_add:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                inlists_to_be_read = inlists_to_add
    return controls


def build_top_binary_controls(work_dir: "str", first_inlist=""):
    """
    Builds the binary_controls namelist by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed.
    """
    if first_inlist == "":
        first_inlist = get_first_inlist(work_dir)
    binary_controls = get_controls_namelist(first_inlist)[0]
    inlists_to_be_read = check_if_more_binary_controls(binary_controls, work_dir=work_dir)
    # print(inlists_to_be_read)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " binary_controls namelist")
        binary_controls_to_add = get_controls_namelist(current_inlist)[0]
        inlists_to_add = check_if_more_binary_controls(binary_controls_to_add, work_dir=work_dir)
        binary_controls = {**binary_controls, **binary_controls_to_add}
        ## note: if the same read_extra_star_binary_controls is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA works
        # print(binary_controls)
        ## remove inlist we are doing now from list
        inlists_to_be_read.remove(current_inlist)
        ## add possible new inlists
        if inlists_to_add != None:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                inlists_to_be_read = inlists_to_add
    return binary_controls


def build_top_pgstar(work_dir: "str", first_inlist=""):
    """
    Builds the pgstar namelist by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed.
    """
    if first_inlist == "":
        first_inlist = get_first_inlist(work_dir)
    pgstar = get_pgstar_namelist(first_inlist)
    inlists_to_be_read = check_if_more_pgstar(pgstar, work_dir=work_dir)
    # print(inlists_to_be_read)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " pgstar namelist")
        pgstar_to_add = get_pgstar_namelist(current_inlist)
        inlists_to_add = check_if_more_pgstar(pgstar_to_add, work_dir=work_dir)
        pgstar = {**pgstar, **pgstar_to_add}
        ## note: if the same read_extra_star_pgstar is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA works
        # print(pgstar)
        ## remove inlist we are doing now from list
        inlists_to_be_read.remove(current_inlist)
        ## add possible new inlists
        if inlists_to_add != None:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                inlists_to_be_read = inlists_to_add
    return pgstar


def build_top_binary_pgstar(work_dir: "str", first_inlist=""):
    """
    Builds the binary_pgstar namelist by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed.
    """
    if first_inlist == "":
        first_inlist = get_first_inlist(work_dir)
    binary_pgstar = get_pgstar_namelist(first_inlist)
    inlists_to_be_read = check_if_more_binary_pgstar(binary_pgstar, work_dir=work_dir)
    # print(inlists_to_be_read)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " binary_pgstar namelist")
        binary_pgstar_to_add = get_pgstar_namelist(current_inlist)
        inlists_to_add = check_if_more_binary_pgstar(binary_pgstar_to_add, work_dir=work_dir)
        binary_pgstar = {**binary_pgstar, **binary_pgstar_to_add}
        ## note: if the same read_extra_star_binary_pgstar is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA works
        # print(binary_pgstar)
        ## remove inlist we are doing now from list
        inlists_to_be_read.remove(current_inlist)
        ## add possible new inlists
        if inlists_to_add:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                inlists_to_be_read = inlists_to_add
    return binary_pgstar


# ----------------------------- do the comparison ----------------------------------


def compare_single_work_dirs(work1: "str", work2: "str", do_pgstar=False, MESA_DIR="", vb=False):
    """
    compare the MESA setup for single stars in two work directories
    allowing for multiple nested inlists
    """
    if work1.split("/")[-1]:
        name1 = "1: " + work1.split("/")[-1]
    else:
        name1 = "1: " + work1.split("/")[-2]
    if work2.split("/")[-1]:
        name2 = "2: " + work2.split("/")[-1]
    else:
        name2 = "2: " + work2.split("/")[-2]
    # star_job
    job1 = build_top_star_job(work1)
    job2 = build_top_star_job(work2)
    print("")
    print("&star_job")
    diff_starjob(job1, job2, name1, name2, MESA_DIR, vb)
    print("/ !end star_job namelist")
    # eos_job
    eos1 = build_top_eos(work1)
    eos2 = build_top_eos(work2)
    print("")
    print("&eos")
    diff_eos(eos1, eos2, name1, name2, MESA_DIR, vb)
    print("/ !end eos namelist")
    # kap_job
    kap1 = build_top_kap(work1)
    kap2 = build_top_kap(work2)
    print("")
    print("&kap")
    diff_kap(kap1, kap2, name1, name2, MESA_DIR, vb)
    print("/ !end kap namelist")
    # controls
    controls1 = build_top_controls(work1)
    controls2 = build_top_controls(work2)
    print("")
    print("&controls")
    diff_controls(controls1, controls2, name1, name2, MESA_DIR, vb)
    print("/ !end controls namelist")
    if do_pgstar:
        pgstar1 = build_top_pgstar(work1)
        pgstar2 = build_top_pgstar(work2)
        print("")
        print("&pgstar")
        diff_pgstar(pgstar1, pgstar2, name1, name2, MESA_DIR, vb)
        print("/ !end pgstar")


def compare_binary_work_dirs(work1: "str", work2: "str", do_pgstar=False, MESA_DIR="", vb=False):
    """
    compares the MESA setup for two binary runs
    """
    if work1.split("/")[-1]:
        name1 = "1: " + work1.split("/")[-1]
    else:
        name1 = "1: " + work1.split("/")[-2]
    if work2.split("/")[-1]:
        name2 = "2: " + work2.split("/")[-1]
    else:
        name2 = "2: " + work2.split("/")[-2]
    job1 = build_top_binary_job(work1)
    job2 = build_top_binary_job(work2)
    ## To compare namelist of each star in both folders later
    inlist1_b1, inlist2_b1, inlist1_b2, inlist2_b2 = get_top_binary_inlist(
        job1, job2, MESA_DIR=MESA_DIR
    )
    print("")
    print("&binary_job")
    diff_binary_job(job1, job2, name1, name2, MESA_DIR, vb)
    print("/ !end binary_job namelist")
    # binary_controls
    binary_controls1 = build_top_binary_controls(work1)
    binary_controls2 = build_top_binary_controls(work2)
    print("")
    print("&binary_controls")
    diff_binary_controls(binary_controls1, binary_controls2, name1, name2, MESA_DIR, vb)
    print("/ !end binary_controls namelist")
    if do_pgstar:
        binary_pgstar1 = build_top_binary_pgstar(work1)
        binary_pgstar2 = build_top_binary_pgstar(work2)
        print("")
        print("&binary_pgstar")
        diff_pgstar(binary_pgstar1, binary_pgstar2, name1, name2, MESA_DIR, vb)
        print("/ !end binary_pgstar")
    print("")
    print("------------------------------------")
    print(" Now compare the individual stars...")
    print("------------------------------------")
    print("")
    print("*************************")
    print("* Compare primary stars *")
    print("*************************")
    print("")
    star_job1 = build_top_star_job(work1, first_inlist=work1 + "/" + inlist1_b1)
    star_job2 = build_top_star_job(work2, first_inlist=work2 + "/" + inlist1_b2)
    print("")
    print("&star_job")
    diff_starjob(star_job1, star_job2, name1, name2, MESA_DIR, vb)
    print("/ !end star_job namelist")
    # eos_job
    eos1 = build_top_eos(work1)
    eos2 = build_top_eos(work2)
    print("")
    print("&eos")
    diff_eos(eos1, eos2, name1, name2, MESA_DIR, vb)
    print("/ !end eos namelist")
    # kap_job
    kap1 = build_top_kap(work1)
    kap2 = build_top_kap(work2)
    print("")
    print("&kap")
    diff_kap(kap1, kap2, name1, name2, MESA_DIR, vb)
    print("/ !end kap namelist")
    # controls
    controls1 = build_top_controls(work1, first_inlist=work1 + "/" + inlist1_b1)
    controls2 = build_top_controls(work2, first_inlist=work2 + "/" + inlist1_b2)
    print("")
    print("&controls")
    diff_controls(controls1, controls2, name1, name2, MESA_DIR, vb)
    print("/ !end controls namelist")
    if do_pgstar:
        pgstar1 = build_top_pgstar(work1, first_inlist=work1 + "/" + inlist1_b1)
        pgstar2 = build_top_pgstar(work2, first_inlist=work2 + "/" + inlist1_b2)
        print("")
        print("&pgstar")
        diff_pgstar(pgstar1, pgstar2, name1, name2, MESA_DIR, vb)
        print("/ !end pgstar")
    print("**************************")
    print("*  Done with primaries   *")
    print("**************************")
    print(" Compare secondaries now *")
    print("**************************")
    star_job1 = build_top_star_job(work1, first_inlist=work1 + "/" + inlist2_b1)
    star_job2 = build_top_star_job(work2, first_inlist=work2 + "/" + inlist2_b2)
    print("")
    print("&star_job")
    diff_starjob(star_job1, star_job2, name1, name2, MESA_DIR, vb)
    print("/ !end star_job namelist")
    # eos_job
    eos1 = build_top_eos(work1)
    eos2 = build_top_eos(work2)
    print("")
    print("&eos")
    diff_eos(eos1, eos2, name1, name2, MESA_DIR, vb)
    print("/ !end eos namelist")
    # kap_job
    kap1 = build_top_kap(work1)
    kap2 = build_top_kap(work2)
    print("")
    print("&kap")
    diff_kap(kap1, kap2, name1, name2, MESA_DIR, vb)
    print("/ !end kap namelist")
    # controls
    controls1 = build_top_controls(work1, first_inlist=work1 + "/" + inlist2_b1)
    controls2 = build_top_controls(work2, first_inlist=work2 + "/" + inlist2_b2)
    print("")
    print("&controls")
    diff_controls(controls1, controls2, name1, name2, MESA_DIR, vb)
    print("/ !end controls namelist")
    if do_pgstar:
        pgstar1 = build_top_pgstar(work1, first_inlist=work1 + "/" + inlist2_b1)
        pgstar2 = build_top_pgstar(work2, first_inlist=work2 + "/" + inlist2_b2)
        print("")
        print("&pgstar")
        diff_pgstar(pgstar1, pgstar2, name1, name2, MESA_DIR, vb)
        print("/ !end pgstar")
    print("**************************")
    print("* Done with secondaries  *")
    print("**************************")


def check_folders_consistency(
    work_dir1: str, work_dir2: str, do_pgstar=False, MESA_DIR="", vb=False
):
    """ checks if both folders are for single or binary stars and calls the right functions"""
    is_binary1 = is_folder_binary(work_dir1)
    is_binary2 = is_folder_binary(work_dir2)
    if is_binary1 and is_binary2:
        compare_binary_work_dirs(
            work_dir1, work_dir2, do_pgstar=do_pgstar, MESA_DIR=MESA_DIR, vb=vb
        )
    elif (not is_binary1) and (not is_binary2):
        compare_single_work_dirs(
            work_dir1, work_dir2, do_pgstar=do_pgstar, MESA_DIR=MESA_DIR, vb=vb
        )
    else:
        print(colored("You're asking to compare a single star directory with a binary.", "yellow",))
        print(colored("I politely decline to do so.", "yellow"))


# command line wrapper
@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("work_dir1", nargs=1, type=click.Path(exists=True))
@click.argument("work_dir2", nargs=1, type=click.Path(exists=True))
@click.option("--pgstar", default=False, help="Show also diff of pgstar namelists.")
@click.option(
    "--mesa_dir",
    default="",
    help="use customized location of $MESA_DIR. Will use environment variable if empty and return an error if empty.",
)
@click.option("--vb", default=False, help="Show also matching lines using green.")
def compare_all_workdir_inlists(work_dir1, work_dir2, pgstar, mesa_dir, vb):
    check_folders_consistency(work_dir1, work_dir2, do_pgstar=pgstar, MESA_DIR=mesa_dir, vb=vb)


if __name__ == "__main__":
    compare_all_workdir_inlists()
