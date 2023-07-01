#!/usr/bin/env python3
# vim: set ts=4 sw=4 ts=4 et :

import argparse
import csv
import os
import sys
import time

def main():
    scopes = ["national", "states"]
    for scope in scopes:
        filenames = dict()
        for file in os.listdir(f"./prices/{scope}"):
            filename = os.fsdecode(file)
            if filename.endswith(".csv"):
                filenames[filename.split(" ")[0]] = filename

        with open(f"./prices/{scope}_master.csv", "w") as mfd:
            sorted_filenames = list(filenames.values())
            sorted_filenames.sort()
            for filename in sorted_filenames:
                with open(f"./prices/{scope}/{filename}") as fd:
                    mfd.write(fd.read())


if __name__ == "__main__":
    main()

