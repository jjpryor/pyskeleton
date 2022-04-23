#!/usr/bin/env python
"""
A sample CLI tool using python's logging and external libraries Click, Rich, and TQDM
"""
import logging
import pathlib
import re
import sys
import time
import click
from rich.logging import RichHandler
from rich.pretty import pprint
from tqdm import tqdm

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


@click.group()
@click.option('--loglevel', '-ll', default='NOTSET', help='Set logging output level. Defaults to notset', type=click.Choice(['critical', 'error', 'warning', 'info', 'debug', 'notset'], case_sensitive=False))
@click.option('--logstyle', '-ls', default='RICH', help='Set logging output readable-style. Defaults to \'rich\' styled.', type=click.Choice(['rich', 'plain'], case_sensitive=False))
def main(loglevel, logstyle):
    """
    A sample CLI tool using python's logging and external libraries Click, Rich, and TQDM.
    By default, all logging to levels is disabled (set to NOTSET) for reduced output to STDOUT.
    If any loglevel other than NOTSET is set, then by default Rich is used to style the log output via log handler arg.
    Non-Rich aka plain-normal styled logging can be enabled by passing '-ls plain'
    """
    # print(f"{loglevel}")
    if str(loglevel).upper() == "NOTSET":
        # this disables logging.getLogger of all logging of 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'
        logger.setLevel(logging.CRITICAL + 1)
    if str(logstyle).upper() == "RICH" and str(loglevel).upper() != "NOTSET":
        FORMAT = "%(name)s %(message)s"
        logging.basicConfig(level=str(loglevel).upper(), format=FORMAT, datefmt="[%D%X]", handlers=[RichHandler()])
    if str(logstyle).upper() == "PLAIN" and str(loglevel).upper() != "NOTSET":
        logging.basicConfig(level=str(loglevel).upper(), format='%(asctime)s %(name)s %(levelname)-8s %(message)s',)


@main.command()
@click.argument('csvfile', type=click.Path(exists=True))
def csvstats(csvfile):
    """
    Loads a csvfile as input, prints some stats, then iterates with a TQDM progress bar wrapper (only the first line in the file) and pretty prints the line using Rich.
    """
    logger.debug(f"csvfile is {csvfile}")
    print("a 3 second sleep so that we can see different timestamps in the logs")
    time.sleep(3)
    csvfile_path = pathlib.Path.cwd() / f"{csvfile}"
    csvfile_len = file_len(csvfile_path)
    print(f"csvfile {csvfile} length is {csvfile_len}")
    current_line_num = 0
    csvfile_len_datarows = csvfile_len - 1
    print(f"Number of data rows in {csvfile_path}: {csvfile_len_datarows}")
    # In the for loop we wrap a tqdm progress bar around a range command
    # so that it will iterate across all the lines in the file
    # and output a progress bar with stats so we know it is working
    # In this example the range() function arg stop is hard set to 1
    # so we can just have it run against a single line, the header row
    # You could make it:
    #    "for current_line_num in tqdm(range(current_line_num, csvfile_len, 1)):"
    # and it would walk the entire CSF file
    print(f"The first line in csvfile {csvfile_path} is:")
    logger.info("""In this example the 'range()' function arg 'stop' is hard set to 1, so we can just have it run against a single line: the header row. You could make it: "for current_line_num in tqdm(range(current_line_num, csvfile_len, 1)):"  and it would walk the entire CSF file""")
    print("This use of the TQDM progress bar is just to show how it can be used")
    for current_line_num in tqdm(range(current_line_num, 1, 1)):
        line, current_line_num = read_line_from_file(csvfile_path, current_line_num)
        logger.debug(line)
        values = []
        values = load_line_as_list(line)
        logger.info("The pprint uses Rich to colorize the pprint")
        pprint(values)
        logger.debug(f"current_line_num is {current_line_num}")
    logger.info("a 3 second sleep so that we can see different timestamps in the logs")
    time.sleep(3)
    some_func_with_warning()


if __name__ == "__main__":
    main()
