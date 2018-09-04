#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    CLI support for restretto
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""


import sys
from argparse import ArgumentParser, ArgumentTypeError
from . import load
from .errors import ExpectError


def options(encoded):
    """Returns dict parsed from encoded string in form key1=val1,key2=val2"""
    opts = {}
    try:
        parts = (p.strip().split("=") for p in encoded.split(",") if p.strip())
        for key, val in parts:
            if not key.strip():
                raise ValueError
            opts[key.strip()] = val.strip()
    except Exception:
        raise ArgumentTypeError(encoded)
    return opts


parser = ArgumentParser(description="REST resources/endpoints testing tool")
parser.add_argument("path", help="path to look for tests (file or directory)")
#parser.add_argument("--xunit", dest="xunit_dir", default=None,
#                    help="output xunit reports to this dir")
parser.add_argument("--print-passed", action="store_true", help="Print passed tests")
parser.add_argument("--print-response", action="store_true", help="Print responses")
parser.add_argument(
    "--vars", action="store", type=options,
    help="Context variables as var1=val1,var2=val2")
parser.add_argument(
    "--debug-errors", action="store_true",
    help="Open ipdb (should be isntalled) debugger on errors"
)


def main(args=sys.argv[1:]):
    arguments = parser.parse_args(args)

    sessions = load(arguments.path)
    if not sessions:
        print("No test sessions found, exiting")
        sys.exit(1)

    for test_session in sessions:
        hdr = "Test session: {}".format(test_session.title)
        print(hdr)
        print('-' * len(hdr))
        for resource in test_session.resources:
            try:
                test_session.test(resource, context=arguments.vars)
                if arguments.print_passed:
                    # TODO: print response status instead
                    print("[PASS] {}: Ok".format(resource.title))
                if arguments.print_response:
                    print(action.response.text)
            except ExpectError as failure:
                print("[FAILURE] {}: {}".format(resource.title, failure))
                if arguments.print_response:
                    print(resource.response.text)
            except Exception as error:
                print("[ERROR] {}: {}".format(resource.title, error))
                if arguments.debug_errors:
                    import ipdb
                    ipdb.set_trace()
        print("")
        print("")
