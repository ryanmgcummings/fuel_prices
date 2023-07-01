#!/usr/bin/env python3
# vim: set ts=4 sw=4 ts=4 et :

import argparse
import csv
import os
import sys
import time

def parse_args():
    parser = argparse.ArgumentParser(description="Default")
    parser.add_argument("-i", "--input", help="input", default="input")
    return parser.parse_args()


def main():
    args = parse_args()

    for file in os.listdir(args.input):
        filename = os.fsdecode(file)
        if filename.endswith(".csv"):
            date = filename.split(" ")[0]
            new_data = list()
            with open(f"./{args.input}/{filename}") as fd:
                reader = csv.reader(fd)
                data = list(reader)
                new_data = [[date] + row for row in data]
            with open(f"./{args.input}/{filename}", "w") as fd:
                writer = csv.writer(fd)
                writer.writerows(new_data)

if __name__ == "__main__":
    main()

