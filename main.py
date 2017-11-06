#!/usr/bin/env pypy
import sys

from rngtests import Tests

if __name__ == "__main__":
    for c in sys.stdin.read():
        for test in Tests:
            test.process_byte(c)

    for test in Tests:
        test.result()

