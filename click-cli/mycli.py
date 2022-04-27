#!/usr/bin/env python
"""
A sample CLI tool using python's logging and external libraries Click, Rich, rich-click, and tqdm
"""
import logging
import pathlib
import re
import sys
import time
import traceback
# rich_click - Format click help output nicely with Rich.
# https://github.com/ewels/rich-click
import rich_click as click
# Rich - writing rich text to the terminal
# https://rich.readthedocs.io/en/stable/index.html
#   Rich Pretty Printing
# https://rich.readthedocs.io/en/stable/pretty.html
from rich.pretty import pprint
# tqdm - https://tqdm.github.io/
from tqdm import tqdm

# https://docs.python.org/3/library/logging.html
logger = logging.getLogger(__name__)


def read_line_from_file(inputfile, current_line_num):
    """
    Takes a desired line number and returns the String line content and that line number
    """
    # Assumes CSV file has first line as header so always +1 to the current_line_num
    # current_line_num = current_line_num + 1
    try:
        # A common pythonic way of opening files is the 'with some_item open()' but
        # in this case, use the enumerate() to keep track of the line content and the line number
        # This would be harder to do with 'with some_item open()'
        infile = open(inputfile, 'r', encoding="utf-8")
        for line_num, line in enumerate(infile):
            if line_num == current_line_num:
                line_at_line_num = line.rstrip('\n')
        infile.close()
        return line_at_line_num, current_line_num
    except Exception:
        logger.exception(f'Error: unable to read input logfile  {inputfile}')
        sys.exit(2)


def file_len(inputfile):
    """
    quick and dirty function to get get file length
    """
    try:
        with open(inputfile, 'r', encoding="utf-8") as afile:
            for linenum, l in enumerate(afile):
                pass
        return linenum + 1
    except Exception:
        logger.exception(f'Error: unable to get file length of {inputfile}')
        sys.exit(2)


def load_line_as_list(line):
    """
    do some regex substitution to account for possible missing values and
    return a List of values.
    """
    line_cleaned = re.sub(r'^,', 'nosuppliedvalue,', line)
    line_cleaned = re.sub(r',,', ',nosuppliedvalue,', line_cleaned)
    values_list = re.sub(",", " ", line_cleaned).split()

    return values_list


def some_func_with_warning():
    """
    prints a useless warning string to WARNING log level
    """
    logger.warning("This is a warning just to show logging and rich output")


# https://click.palletsprojects.com/en/8.1.x/commands/
@click.group()
# https://click.palletsprojects.com/en/8.1.x/options/
@click.option('--loglevel', '-l', default='CRITICAL', help='Set logging output level. Defaults to \'critical\'', type=click.Choice(['critical', 'error', 'warning', 'info', 'debug', 'notset'], case_sensitive=False))
@click.option('--logstyle', '-s', default='PLAIN', help='Set logging output readable-style. Defaults to \'plain\' styled.', type=click.Choice(['rich', 'plain'], case_sensitive=False))
# https://click.palletsprojects.com/en/8.1.x/commands/#nested-handling-and-contexts
# Commands can also ask for the context to be passed by marking themselves with the pass_context() decorator.
# In that case, the context is passed as first argument.
@click.pass_context
def main(ctx, loglevel, logstyle):
    """
    A sample CLI tool using python's logging and external libraries Click, Rich, rich-click, and tqdm.
    By default, all logging to levels is set to CRITICAL.\n
    If any loglevel other than NOTSET is set, then by default the logging style is PLAIN. Rich-styled logging can be enabled by passing \"-s plain\".\n
    """
    # ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)
    ctx.obj['logstyle'] = str(logstyle).upper()
    ctx.obj['console'] = "None"
    # Set logger level & logger style
    # https://docs.python.org/3/library/logging.html
    if str(loglevel).upper() == "NOTSET":
        # this disables logging.getLogger of all logging of 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'
        logger.setLevel(logging.CRITICAL + 1)

    # Turn on Rich Tracebacks and Rich Logging
    if str(logstyle).upper() == "RICH" and str(loglevel).upper() != "NOTSET":
        # https://rich.readthedocs.io/en/stable/console.html
        from rich.console import Console
        ctx.obj['console'] = Console()

        # https://rich.readthedocs.io/en/stable/logging.html
        from rich.logging import RichHandler
        FORMAT = "%(name)s %(message)s"
        # https://docs.python.org/3/library/logging.html#logging.basicConfig
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        logging.basicConfig(level=str(loglevel).upper(), format=FORMAT, datefmt="%Y-%m-%d-%H-%M-%S-%f-%z]", handlers=[RichHandler()])

        # https://rich.readthedocs.io/en/stable/traceback.html
        from rich.traceback import install
        install(show_locals=True)

    # Use plain styled tracebacks and logging
    if str(logstyle).upper() == "PLAIN" and str(loglevel).upper() != "NOTSET":
        # https://docs.python.org/3/library/logging.html#logging.basicConfig
        logging.basicConfig(level=str(loglevel).upper(), format='%(asctime)s %(name)s %(levelname)-8s %(message)s',)


@main.command()
# https://click.palletsprojects.com/en/8.1.x/arguments/#file-arguments
@click.argument('csvfile', type=click.Path(exists=True))
# https://click.palletsprojects.com/en/8.1.x/commands/#nested-handling-and-contexts
# Commands can also ask for the context to be passed by marking themselves with the pass_context() decorator.
# In that case, the context is passed as first argument.
@click.pass_context
def csvstats(ctx, csvfile):
    """
    Loads a csvfile as input, prints some stats, then iterates with a tqdm progress bar wrapper (only the first line in the file) and pretty prints the line using Rich.
    """
    logger.debug(f"csvfile is {csvfile}")
    csvfile_path = pathlib.Path.cwd() / f"{csvfile}"
    csvfile_len = file_len(csvfile_path)
    print(f"csvfile {csvfile} length is {csvfile_len}")
    current_line_num = 0
    csvfile_len_datarows = csvfile_len - 1
    print(f"Number of data rows in {csvfile_path}: {csvfile_len_datarows}")
    print("a 3 second sleep so that we can see different timestamps in the logs")
    time.sleep(3)
    # In this example first we wrap the whole thing in a 'try' so we can enable exception handling
    # Next the 'for' loop contains a tqdm progress bar, which accepts the 'range()'
    # function. range() arg 'stop' is hard set to 1, so we can just have it run against
    # a single line: the header row. You could make it:
    # "for current_line_num in tqdm(range(current_line_num, csvfile_len, 1)):"
    # and it would walk the entire CSF file.
    # Lastly in the except block can turn on or off rich tracebacks
    print(f"The first line in csvfile {csvfile_path} is:")
    logger.info("In this example first we wrap the whole thing in a 'try' then 'for' loop which has a tqdm progress bar, which accepts the 'range()' function who's arg 'stop' is hard set to 1, so we can just have it run against a single line")
    print("This use of the tqdm progress bar is just to show how it can be used")

    try:
        # tqdm Objects https://tqdm.github.io/docs/tqdm/
        for current_line_num in tqdm(range(current_line_num, 1, 1)):
            line, current_line_num = read_line_from_file(csvfile_path, current_line_num)
            logger.debug(line)
            values = []
            values = load_line_as_list(line)
            logger.info("The pprint uses Rich to colorize the pprint")
            # https://rich.readthedocs.io/en/stable/pretty.html
            pprint(values)
            logger.debug(f"current_line_num is {current_line_num}")
        some_func_with_warning()
    except Exception:
        # https://click.palletsprojects.com/en/8.1.x/commands/#nested-handling-and-contexts
        if ctx.obj['logstyle'] == "RICH":
            ctx.obj['console'].print_exception(show_locals=True)
        else:
            # https://docs.python.org/3/library/traceback.html#traceback.format_exc
            print(traceback.format_exc())


if __name__ == "__main__":
    main()
