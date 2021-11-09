
# Table of Contents

1.  [How to install](#org3b99b5e)
2.  [How to use `compare_inlists.py`](#org41ae0b6)
    1.  [Example](#org6e25608)
3.  [How to use `compare_all_work_dir_inlists.py`](#orgbec23b8)
4.  [How to use `merge_column_lists.py`](#orga9a863d)

While experimenting with [MESA](http://mesa.sourceforge.net/) and developing setups, I often compare
inlists (for single and/or binary stars) with each other. A simple
diff is often not informative because of the comments, non-matching
order of the entries, or missing entries in one file that are present
in the other file but have no real effect because they are set to the
defaults. For this reason, I've written the script `compare_inlists.py`
which can print an option-by-option diff of two inlists, ignoring
comments and empty lines, and checking the defaults from the
documentation when entries are missing. It **assumes you use the same
MESA version for both inlists** for this last task.

This can be used inside of scripts or notebooks, or from command line
(which is the usual way I do it), thanks to [click](https://github.com/pallets/click).


<a id="org3b99b5e"></a>

# How to install

    python3 -m pip install --index-url https://github.com/mathren/compare_workdir_MESA compare_inlist-mathren-0.0.1-py3-


<a id="org41ae0b6"></a>

# How to use `compare_inlists.py`

    python compare_inlists.py --help
    Usage: compare_inlists.py [OPTIONS] INLIST1 INLIST2
    
    Options:
      --pgstar TEXT    Show also diff of pgstar namelists.
      --mesa_dir TEXT  use customized location of $MESA_DIR. Will use environment
    		   variable if empty.
      --vb TEXT        Show also matching lines using green.
      --help           Show this message and exit.

It uses [termcolor](https://pypi.org/project/termcolor/) to print in red entries that differ between
two inlists, and, if invoked adding `--vb=True` (for verbose) from the command
line it will also print in green entries that are equal. If one entry
is in one inlist but not the other, but the inlist that contains it
has the default value, it is considered as a "green" entry.

This has been tested with MESA version 12778 or later, and works for inlists
for single stars and binaries (but will refuse to compare an
inlist<sub>binary</sub> with an inlist for a single star). It can take a
customized `$MESA_DIR` with the optional argument `--mesa_dir`. If not
provided it will use the `$MESA_DIR` environment variable currently
set.

By default the comparison between pgstar namelist is disabled because
I need it less, but it can be enabled using `--pgstar=True`.


<a id="org6e25608"></a>

## Example

A screenshot of an example with `--vb=True` and `$MESA_DIR` set as
environment variable:

<file:///examples/verbose.png?raw=true "verbose output">


<a id="orgbec23b8"></a>

# How to use `compare_all_work_dir_inlists.py`

MESA allows to nest namelists (i.e., star<sub>job</sub>, controls, and/or
pgstar, and their binary counterparts) using `read_extra_star_job_inlist*` and
`extra_star_job_inlist*_name` (and similar). The script `compare_all_work_dir_inlists.py` uses
the functions defined in `compare_inlists.py` to compare the entire MESA
setup of two work directories, taking care of nested inlist that might
over-write each others.

It will not work to compare a work directory for a single star with a
work directory for a binary. However, the functions in the
`compare_inlists.py` and `compare_all_work_dir_inlists.py` could be
used to create a comparison (e.g., of a single star with the donor of
a binary).

As `compare_inlists.py`, it can be used inside of scripts or notebooks, or from command line.

    python compare_all_work_dir_inlists.py --help
    Usage: compare_all_work_dir_inlists.py [OPTIONS] WORK_DIR1 WORK_DIR2
    
    Options:
      --pgstar TEXT    Show also diff of pgstar namelists.
      --mesa_dir TEXT  use customized location of $MESA_DIR. Will use environment
    		   variable if empty and return an error if empty.
      --vb TEXT        Show also matching lines using green.
      --help           Show this message and exit.

If called on a pair of folders both for single stars (or both for
binaries), it first builds a "main" dictionary with of all the
options MESA reads for each namelist, starting from `inlist` and
checking if it contains nested namelists. It then performs the
comparison of the "main" dictionaries of the two folders. If the
same `read_extra_star_job_inlist*` (i.e. same number instead of the
`*`) appears in multiple nested inlists the last read will over-write
the previous, which is the same behavior as in MESA. Same for controls
and pgstar and the corresponding binary namelists. In the case of
binary folders, it will also compare all the namelists for each of the
stars in the binary. The comparison between the pgstar namelists is
also disabled by default and can be done using `--pgstar=True` from
command line.

The output is similar to the example above for individual inlists.


<a id="orga9a863d"></a>

# How to use `merge_column_lists.py`

Sometimes I need to merge the `profiles_columns.list`,
`history_columns.list`, or `binary_history_columns.list` between two or
more runs. This script does that, once again removing all the comments
(so the merged file won't be very nice), and not caring about order of
the options. It will check that the lists you want to merge are
compatible and refuse to merge, e.g., a `profiles_columns.list` with a
`history_columns.list`.  The merged list is printed to a file `OUTLIST`
specified by the user.

As of now it does **not** check if the merged list is compatible with the
MESA version.

    python $RESEARCH/codes/mesa/compare_wordir_MESA/merge_column_lists.py --help
    Usage: merge_column_lists.py [OPTIONS] LIST1 LIST2 OUTLIST
    
    Options:
      --mesa_dir TEXT  use customized location of $MESA_DIR. Will use environment
    		   variable if empty and return an error if empty.
    
      --help           Show this message and exit.

