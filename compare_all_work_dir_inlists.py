## author: Mathieu Renzo

## Author: Mathieu Renzo <mathren90@gmail.com>
## Keywords: files

## Copyright (C) 2019-2020 Mathieu Renzo

## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or (at
## your option) any later version.
##
## This program is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see http://www.gnu.org/licenses/.


## This has been tested with MESA version 12778

import os
import sys
from pathlib import Path
## pip install -U termcolor
from termcolor import colored

## pip install -U click
import click

# sys.path.append('path/to/folder/plotFunc/')
from compare_inlists import (
    getJobNamelist,
    getControlsNamelist,
    getDefaults,
    diffBinaryControls,
    diffBinaryJob,
    diffControls,
    diffPgstar,
    diffStarJob,
)

# ------------------------- some auxiliary functions ----------------------------------


def appendInlistPath(path_list: list, path: str, workDir="./"):
    """
    takes the list of paths to inlists, and adds the path to a new inlist,
    taking care of absolute vs. relative paths
    """
    if Path(path).is_absolute():
        path_list.append(path)
    else:  # it's relative
        path_list.append(workDir + "/" + path)
    return path_list


def getFirstInlist(workDir: str):
    inlist = workDir + "/inlist"
    if os.path.isfile(inlist):
        return inlist
    else:
        print(colored(workDir + " has no inlist, too complex for me", "yellow"))
        sys.exit()


def isFolderBinary(workDir: str):
    """
    checks if the provided path is to a work directory for a MESA binary run
    (returns True) or single star (returns False)
    """
    inlist = getFirstInlist(workDir)
    isBinary = getJobNamelist(inlist)[1]
    return isBinary


def getMasterInlistStarsInBinaries(job1: dict, job2: dict, MESA_DIR=""):
    """
    reads the inlist for each individual star in a binary 
    for both folders we are comparing. If not present, use the default
    """
    # primary first binary
    try:
        master_inlist_star1_b1 = job1["inlist_names(1)"]
    except KeyError:
        job_defaults = getDefaults("binary_job", MESA_DIR=MESA_DIR)
        master_inlist_star1_b1 = job_defaults["inlist_names(1)"]
    # either way you got it, clean it
    master_inlist_star1_b1 = master_inlist_star1_b1.strip("'").strip('"')
    # secondary first binary
    try:
        master_inlist_star2_b1 = job1["inlist_names(2)"]
    except KeyError:
        job_defaults = getDefaults("binary_job", MESA_DIR=MESA_DIR)
        master_inlist_star2_b1 = job_defaults["inlist_names(2)"]
    master_inlist_star2_b1 = master_inlist_star2_b1.strip("'").strip('"')
    # primary second binary
    try:
        master_inlist_star1_b2 = job2["inlist_names(1)"]
    except KeyError:
        job_defaults = getDefaults("binary_job", MESA_DIR=MESA_DIR)
        master_inlist_star1_b2 = job_defaults["inlist_names(1)"]
    master_inlist_star1_b2 = master_inlist_star1_b2.strip("'").strip('"')
    # secondary first binary
    try:
        master_inlist_star2_b2 = job2["inlist_names(2)"]
    except KeyError:
        job_defaults = getDefaults("binary_job", MESA_DIR=MESA_DIR)
        master_inlist_star2_b2 = job_defaults["inlist_names(2)"]
    master_inlist_star2_b2 = master_inlist_star2_b2.strip("'").strip('"')
    return (
        master_inlist_star1_b1,
        master_inlist_star2_b1,
        master_inlist_star1_b2,
        master_inlist_star2_b2,
    )


# ------------------ check if there are nested namelists -------------------------------


def checkIfMoreStarJob(job: dict, workDir="./"):
    """
    Check if there are more star_job namelists to be read and returns a 
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if job.get("read_extra_star_job_inlist1") == ".true.":
        new_inlist = job.get("extra_star_job_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if job.get("read_extra_star_job_inlist2") == ".true.":
        new_inlist = job.get("extra_star_job_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if job.get("read_extra_star_job_inlist3") == ".true.":
        new_inlist = job.get("extra_star_job_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if job.get("read_extra_star_job_inlist4") == ".true.":
        new_inlist = job.get("extra_star_job_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if job.get("read_extra_star_job_inlist5") == ".true.":
        new_inlist = job.get("extra_star_job_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    return inlists_to_be_read


def checkIfMoreBinaryJob(job: dict, workDir="./"):
    """
    Check if there are more binary_job namelists to be read and returns a
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if job.get("read_extra_binary_job_inlist1") == ".true.":
        new_inlist = job.get("extra_binary_job_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if job.get("read_extra_binary_job_inlist2") == ".true.":
        new_inlist = job.get("extra_binary_job_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if job.get("read_extra_binary_job_inlist3") == ".true.":
        new_inlist = job.get("extra_binary_job_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if job.get("read_extra_binary_job_inlist4") == ".true.":
        new_inlist = job.get("extra_binary_job_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if job.get("read_extra_binary_job_inlist5") == ".true.":
        new_inlist = job.get("extra_binary_job_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    return inlists_to_be_read


def checkIfMoreControls(controls: dict, workDir="./"):
    """
    Check if there are more controls namelists to be read and returns a 
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if controls.get("read_extra_controls_inlist1") == ".true.":
        new_inlist = controls.get("extra_controls_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if controls.get("read_extra_controls_inlist2") == ".true.":
        new_inlist = controls.get("extra_controls_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if controls.get("read_extra_controls_inlist3") == ".true.":
        new_inlist = controls.get("extra_controls_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if controls.get("read_extra_controls_inlist4") == ".true.":
        new_inlist = controls.get("extra_controls_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if controls.get("read_extra_controls_inlist5") == ".true.":
        new_inlist = controls.get("extra_controls_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    return inlists_to_be_read


def checkIfMoreBinaryControls(binary_controls: dict, workDir="./"):
    """
    Check if there are more binary_controls namelists to be read and returns a 
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if binary_controls.get("read_extra_binary_controls_inlist1") == ".true.":
        new_inlist = binary_controls.get("extra_binary_controls_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if binary_controls.get("read_extra_binary_controls_inlist2") == ".true.":
        new_inlist = binary_controls.get("extra_binary_controls_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if binary_controls.get("read_extra_binary_controls_inlist3") == ".true.":
        new_inlist = binary_controls.get("extra_binary_controls_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if binary_controls.get("read_extra_binary_controls_inlist4") == ".true.":
        new_inlist = binary_controls.get("extra_binary_controls_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if binary_controls.get("read_extra_binary_controls_inlist5") == ".true.":
        new_inlist = binary_controls.get("extra_binary_controls_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    return inlists_to_be_read


def checkIfMorePgstar(pgstar: dict, workDir="./"):
    """
    Check if there are more pgstar namelists to be read and returns a 
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if pgstar.get("read_extra_pgstar_inlist1") == ".true.":
        new_inlist = pgstar.get("extra_pgstar_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if pgstar.get("read_extra_pgstar_inlist2") == ".true.":
        new_inlist = pgstar.get("extra_pgstar_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if pgstar.get("read_extra_pgstar_inlist3") == ".true.":
        new_inlist = pgstar.get("extra_pgstar_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if pgstar.get("read_extra_pgstar_inlist4") == ".true.":
        new_inlist = pgstar.get("extra_pgstar_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if pgstar.get("read_extra_pgstar_inlist5") == ".true.":
        new_inlist = pgstar.get("extra_pgstar_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    return inlists_to_be_read


def checkIfMoreBinaryPgstar(binary_pgstar: dict, workDir="./"):
    """
    Check if there are more binary_pgstar namelists to be read and returns a 
    list of the paths to their inlists
    """
    inlists_to_be_read = []
    if binary_pgstar.get("read_extra_binary_pgstar_inlist1") == ".true.":
        new_inlist = binary_pgstar.get("extra_binary_pgstar_inlist1_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if binary_pgstar.get("read_extra_binary_pgstar_inlist2") == ".true.":
        new_inlist = binary_pgstar.get("extra_binary_pgstar_inlist2_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if binary_pgstar.get("read_extra_binary_pgstar_inlist3") == ".true.":
        new_inlist = binary_pgstar.get("extra_binary_pgstar_inlist3_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if binary_pgstar.get("read_extra_binary_pgstar_inlist4") == ".true.":
        new_inlist = binary_pgstar.get("extra_binary_pgstar_inlist4_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    if binary_pgstar.get("read_extra_binary_pgstar_inlist5") == ".true.":
        new_inlist = binary_pgstar.get("extra_binary_pgstar_inlist5_name").strip("'").strip('"')
        inlists_to_be_read = appendInlistPath(inlists_to_be_read, new_inlist, workDir)
    return inlists_to_be_read


# ----------------- build the dictionary that MESA will use ------------------------------


def buildMasterStarJob(workDir: str, first_inlist=""):
    """
    Builds the star_job namelist by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed. 
    """
    if first_inlist == "":
        first_inlist = getFirstInlist(workDir)
    job = getJobNamelist(first_inlist)[0]
    inlists_to_be_read = checkIfMoreStarJob(job, workDir=workDir)
    # print(inlists_to_be_read)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " star_job namelist")
        job_to_add = getJobNamelist(current_inlist)[0]
        inlists_to_add = checkIfMoreStarJob(job_to_add, workDir=workDir)
        # merge dictionaries with over-write
        job = {**job, **job_to_add}
        ## note: if the same read_extra_star_job is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA works
        # print(job)
        ## remove inlist we are doing now from list
        inlists_to_be_read = inlists_to_be_read.remove(current_inlist)
        ## add possible new inlists
        if inlists_to_add != None:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                # but we still want to add stuff
                inlists_to_be_read = inlists_to_add
    return job


def buildMasterBinaryJob(workDir: str, first_inlist=""):
    """
    Builds the namelist binary_job by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed.
    """
    if first_inlist == "":
        first_inlist = getFirstInlist(workDir)
    job = getJobNamelist(first_inlist)[0]
    inlists_to_be_read = checkIfMoreBinaryJob(job, workDir=workDir)
    # print(inlists_to_be_read)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " binary_job namelist")
        job_to_add = getJobNamelist(current_inlist)[0]
        inlists_to_add = checkIfMoreBinaryJob(job_to_add, workDir=workDir)
        job = {**job, **job_to_add}
        ## note: if the same read_extra_binary_job is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA works
        # print(job)
        ## remove inlist we are doing now from list
        inlists_to_be_read = inlists_to_be_read.remove(current_inlist)
        ## add possible new inlists
        if not inlists_to_add:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                # but we still want to add stuff
                inlists_to_be_read = inlists_to_add
    return job


def buildMasterControls(workDir: str, first_inlist=""):
    """
    Builds the controls namelist by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed.
    """
    if first_inlist == "":
        first_inlist = getFirstInlist(workDir)
    controls = getControlsNamelist(first_inlist)[0]
    inlists_to_be_read = checkIfMoreControls(controls, workDir=workDir)
    # print(inlists_to_be_read)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " controls namelist")
        controls_to_add = getControlsNamelist(current_inlist)[0]
        inlists_to_add = checkIfMoreControls(controls_to_add, workDir=workDir)
        controls = {**controls, **controls_to_add}
        ## note: if the same read_extra_star_controls is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA works
        # print(controls)
        ## remove inlist we are doing now from list
        inlists_to_be_read = inlists_to_be_read.remove(current_inlist)
        ## add possible new inlists
        if not inlists_to_add:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                inlists_to_be_read = inlists_to_add
    return controls


def buildMasterBinaryControls(workDir: str, first_inlist=""):
    """
    Builds the binary_controls namelist by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed.
    """
    if first_inlist == "":
        first_inlist = getFirstInlist(workDir)
    binary_controls = getControlsNamelist(first_inlist)[0]
    inlists_to_be_read = checkIfMoreBinaryControls(binary_controls, workDir=workDir)
    # print(inlists_to_be_read)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " binary_controls namelist")
        binary_controls_to_add = getControlsNamelist(current_inlist)[0]
        inlists_to_add = checkIfMoreBinaryControls(binary_controls_to_add, workDir=workDir)
        binary_controls = {**binary_controls, **binary_controls_to_add}
        ## note: if the same read_extra_star_binary_controls is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA works
        # print(binary_controls)
        ## remove inlist we are doing now from list
        inlists_to_be_read = inlists_to_be_read.remove(current_inlist)
        ## add possible new inlists
        if inlists_to_add != None:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                inlists_to_be_read = inlists_to_add
    return binary_controls


def buildMasterPgstar(workDir: str, first_inlist=""):
    """
    Builds the pgstar namelist by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed.
    """
    if first_inlist == "":
        first_inlist = getFirstInlist(workDir)
    pgstar = getPgstarNamelist(first_inlist)
    inlists_to_be_read = checkIfMorePgstar(pgstar, workDir=workDir)
    # print(inlists_to_be_read)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " pgstar namelist")
        pgstar_to_add = getPgstarNamelist(current_inlist)
        inlists_to_add = checkIfMorePgstar(pgstar_to_add, workDir=workDir)
        pgstar = {**pgstar, **pgstar_to_add}
        ## note: if the same read_extra_star_pgstar is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA works
        # print(pgstar)
        ## remove inlist we are doing now from list
        inlists_to_be_read = inlists_to_be_read.remove(current_inlist)
        ## add possible new inlists
        if inlists_to_add != None:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                inlists_to_be_read = inlists_to_add
    return pgstar


def buildMasterBinaryPgstar(workDir: str, first_inlist=""):
    """
    Builds the binary_pgstar namelist by reading the inlists starting from inlist, unless an
    optional different starting inlist is passed.
    """
    if first_inlist == "":
        first_inlist = getFirstInlist(workDir)
    binary_pgstar = getPgstarNamelist(first_inlist)
    inlists_to_be_read = checkIfMoreBinaryPgstar(binary_pgstar, workDir=workDir)
    # print(inlists_to_be_read)
    while inlists_to_be_read:
        current_inlist = inlists_to_be_read[0]
        print("...reading " + current_inlist + " binary_pgstar namelist")
        binary_pgstar_to_add = getPgstarNamelist(current_inlist)
        inlists_to_add = checkIfMoreBinaryPgstar(binary_pgstar_to_add, workDir=workDir)
        binary_pgstar = {**binary_pgstar, **binary_pgstar_to_add}
        ## note: if the same read_extra_star_binary_pgstar is used in multiple
        ## inlists, only the last one works because settings
        ## overwrites. That's also how MESA works
        # print(binary_pgstar)
        ## remove inlist we are doing now from list
        inlists_to_be_read = inlists_to_be_read.remove(current_inlist)
        ## add possible new inlists
        if inlists_to_add != None:
            try:
                inlists_to_be_read = inlists_to_be_read + inlists_to_add
            except TypeError:
                # could be that inlists_to_be_read is empty
                inlists_to_be_read = inlists_to_add
    return binary_pgstar


# ----------------------------- do the comparison ----------------------------------


def compareSingleWorkDirs(work1: str, work2: str, doPgstar=False, MESA_DIR="", vb=False):
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
    job1 = buildMasterStarJob(work1)
    job2 = buildMasterStarJob(work2)
    print("")
    print("&star_job")
    print("")
    diffStarJob(job1, job2, name1, name2, MESA_DIR, vb)
    print("/ !end star_job namelist")
    print("")
    # controls
    controls1 = buildMasterControls(work1)
    controls2 = buildMasterControls(work2)
    print("")
    print("&controls")
    print("")
    diffControls(controls1, controls2, name1, name2, MESA_DIR, vb)
    print("")
    print("/ !end controls namelist")
    print("")
    if doPgstar:
        pgstar1 = buildMasterPgstar(work1)
        pgstar2 = buildMasterPgstar(work2)
        print("")
        print("&pgstar")
        print("")
        diffPgstar(pgstar1, pgstar2, name1, name2, MESA_DIR, vb)
        print("")
        print("/ !end pgstar")


def compareBinaryWorkDirs(work1: str, work2: str, doPgstar=False, MESA_DIR="", vb=False):
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
    job1 = buildMasterBinaryJob(work1)
    job2 = buildMasterBinaryJob(work2)
    ## To compare namelist of each star in both folders later
    inlist1_b1, inlist2_b1, inlist1_b2, inlist2_b2 = getMasterInlistStarsInBinaries(
        job1, job2, MESA_DIR=MESA_DIR
    )
    print("")
    print("&binary_job")
    print("")
    diffBinaryJob(job1, job2, name1, name2, MESA_DIR, vb)
    print("/ !end binary_job namelist")
    print("")
    # binary_controls
    binary_controls1 = buildMasterBinaryControls(work1)
    binary_controls2 = buildMasterBinaryControls(work2)
    print("")
    print("&binary_controls")
    print("")
    diffBinaryControls(binary_controls1, binary_controls2, name1, name2, MESA_DIR, vb)
    print("")
    print("/ !end binary_controls namelist")
    print("")
    if doPgstar:
        binary_pgstar1 = buildMasterBinaryPgstar(work1)
        binary_pgstar2 = buildMasterBinaryPgstar(work2)
        print("")
        print("&binary_pgstar")
        print("")
        diffPgstar(binary_pgstar1, binary_pgstar2, name1, name2, MESA_DIR, vb)
        print("")
        print("/ !end binary_pgstar")
    print("")
    print("------------------------------------")
    print(" Now compare the individual stars...")
    print("------------------------------------")
    print("")
    print("*************************")
    print("* Compare primary stars *")
    print("*************************")
    star_job1 = buildMasterStarJob(work1, first_inlist=work1 + "/" + inlist1_b1)
    star_job2 = buildMasterStarJob(work2, first_inlist=work2 + "/" + inlist1_b2)
    print("")
    print("&star_job")
    print("")
    diffStarJob(star_job1, star_job2, name1, name2, MESA_DIR, vb)
    print("/ !end star_job namelist")
    print("")
    # controls
    controls1 = buildMasterControls(work1, first_inlist=work1 + "/" + inlist1_b1)
    controls2 = buildMasterControls(work2, first_inlist=work2 + "/" + inlist1_b2)
    print("")
    print("&controls")
    print("")
    diffControls(controls1, controls2, name1, name2, MESA_DIR, vb)
    print("")
    print("/ !end controls namelist")
    print("")
    if doPgstar:
        pgstar1 = buildMasterPgstar(work1, first_inlist=work1 + "/" + inlist1_b1)
        pgstar2 = buildMasterPgstar(work2, first_inlist=work2 + "/" + inlist1_b2)
        print("")
        print("&pgstar")
        print("")
        diffPgstar(pgstar1, pgstar2, name1, name2, MESA_DIR, vb)
        print("")
        print("/ !end pgstar")
        print("")
    print("**************************")
    print("*  Done with primaries   *")
    print("**************************")
    print(" Compare secondaries now *")
    print("**************************")
    star_job1 = buildMasterStarJob(work1, first_inlist=work1 + "/" + inlist2_b1)
    star_job2 = buildMasterStarJob(work2, first_inlist=work2 + "/" + inlist2_b2)
    print("")
    print("&star_job")
    print("")
    diffStarJob(star_job1, star_job2, name1, name2, MESA_DIR, vb)
    print("/ !end star_job namelist")
    print("")
    # controls
    controls1 = buildMasterControls(work1, first_inlist=work1 + "/" + inlist2_b1)
    controls2 = buildMasterControls(work2, first_inlist=work2 + "/" + inlist2_b2)
    print("")
    print("&controls")
    print("")
    diffControls(controls1, controls2, name1, name2, MESA_DIR, vb)
    print("")
    print("/ !end controls namelist")
    print("")
    if doPgstar:
        pgstar1 = buildMasterPgstar(work1, first_inlist=work1 + "/" + inlist2_b1)
        pgstar2 = buildMasterPgstar(work2, first_inlist=work2 + "/" + inlist2_b2)
        print("")
        print("&pgstar")
        print("")
        diffPgstar(pgstar1, pgstar2, name1, name2, MESA_DIR, vb)
        print("")
        print("/ !end pgstar")
        print("")
    print("**************************")
    print("* Done with secondaries  *")
    print("**************************")


def checkFoldersConsistency(work_dir1: str, work_dir2: str, doPgstar=False, MESA_DIR="", vb=False):
    """ checks if both folders are for single or binary stars and calls the right functions"""
    isBinary1 = isFolderBinary(work_dir1)
    isBinary2 = isFolderBinary(work_dir2)
    if isBinary1 and isBinary2:
        compareBinaryWorkDirs(work_dir1, work_dir2, doPgstar=doPgstar, MESA_DIR=MESA_DIR, vb=vb)
    elif (not isBinary1) and (not isBinary2):
        compareSingleWorkDirs(work_dir1, work_dir2, doPgstar=doPgstar, MESA_DIR=MESA_DIR, vb=vb)
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
def cli_wrapper_directories(work_dir1, work_dir2, pgstar, mesa_dir, vb):
    checkFoldersConsistency(work_dir1, work_dir2, doPgstar=pgstar, MESA_DIR=mesa_dir, vb=vb)
    print("")
    print("*********")
    print("* done! *")
    print("*********")


if __name__ == "__main__":
    cli_wrapper_directories()
