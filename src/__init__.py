#!/usr/bin/python3
__author__ = "Mathieu Renzo"
import os
from os.path import exists

if __name__ ==  "__main__":
    """
    The scripts are executable from command line, we just need to tell python where to find them.
    We will add the present folder to the PATH environment variable.
    """
    PATH = os.environ['PATH']
    paths = PATH.split(":")
    pwd = os.getcwd()
    if pwd not in paths:
        print(pwd+" is not in path!")
        print("PATH=", PATH)
        os.environ['PATH'] = pwd
        print(os.environ['PATH'])
        print("""you can now call
        compare_inlists.py, compare_all_work_dir_inlists.py, and merge_column_list.py
        from anywhere in your system!""")
        global_only = input("do you want to modify your bashrc or equivalent to remember this location? [Y/n]")
        if ((global_only == "Y") or (local_only == "y")):
            if exists("~/.zshrc"):
                outfile = "~/.zshrc"
            elif exists("~/.bashrc"):
                outfile = "~/.bashrc"
            elif exists("~/.bash_profile"):
                outfile = "~/.bashrc"
            else:
                outfile = input("Can't find initial file, please give path")
            with open(outfile, 'a') as of:
                of.writeline("export PATH=$PATH:"+pwd)
            os.system("source "+outfile)
        else:
            print("done!")
    else:
        print(pwd+" is already in PATH")
        print(PATH)
        print("done!")
