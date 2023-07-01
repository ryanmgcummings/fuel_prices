#!/usr/bin/env python3
# vim: set ts=4 sw=4 ts=4 et :

import argparse
import csv
import datetime
import json
import logging
import os
import re
import time

from bs4 import BeautifulSoup
import requests

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


def parse_args():
    parser = argparse.ArgumentParser(description="Default")
    parser.add_argument("--debug", help="debug", action="store_true")
    return parser.parse_args()


def get_national_prices(soup):
    """
    all the national data is stored in the iwmparam[0].placestxt variable in the last script

    returns a list where each element is another list that describes a state's gas prices:
    [<USPS Abbreviation>, <State Name>, <Gas Price>, <Link to State Page>]
    """
    national_prices = []
    script = soup.find_all("script")[-1]
    for line in script:
        if "iwmparam[0].placestxt" in line:
            data = re.search(r"iwmparam\[0\].placestxt\s=\s\"(.*)\"", line)
            national_prices = [
                state.strip().split(",")[0:-1]
                for state in data.group(1).strip().split(";")[0:-1]
            ]
    return national_prices


def get_state_prices(national_prices):
    all_prices = []
    with requests.Session() as s:
        s.headers = {
            "User-Agent": "insomnia/2022.4.2",
        }
        for state in national_prices:
            if state[0] == "DC":
                continue
            # scrape state url to get the data url
            resp = s.get(state[3])
            soup = BeautifulSoup(resp.text, "html.parser")
            state_data_url = soup.find(
                "script", src=re.compile(r"premiumhtml5map_js_data")
            )["src"]

            # scrape the data out of the javascript
            map_data = {}
            resp = s.get(state_data_url)
            for line in resp.text.strip().split("\n"):
                if "map_data" in line:
                    map_data = json.loads(
                        re.search(r"map_data\s*:\s*({.*),\s*groups", line.strip())
                        .group(1)
                        .strip()
                    )

            # clean data
            for key, county in map_data.items():
                all_prices.append(
                    [state[0], state[1], county["name"], county["comment"]]
                )
    return all_prices

def generate_master_files():
    scopes = ["national", "states"]
    for scope in scopes:
        filenames = dict()
        for file in os.listdir(f"./prices/{scope}"):
            filename = os.fsdecode(file)
            if filename.endswith(".csv"):
                filenames[filename.split(" ")[0]] = filename

        with open(f"prices/{scope}_master.csv", "w") as mfd:
            sorted_filenames = list(filenames.values())
            sorted_filenames.sort()
            for filename in sorted_filenames:
                with open(f"./prices/{scope}/{filename}") as fd:
                    mfd.write(fd.read())

def main():
    args = parse_args()

    log.info("Running {}".format(__file__))
    if args.debug:
        log.setLevel(logging.DEBUG)
        log.debug("Debug mode enabled")

    # profiling
    s = time.perf_counter()

    base_page = "https://gasprices.aaa.com"
    headers = {
        "User-Agent": "insomnia/2022.4.2",
    }
    req = requests.get(base_page, headers=headers)
    soup = BeautifulSoup(req.text, "html.parser")
    national_prices = get_national_prices(soup)
    state_prices = get_state_prices(national_prices)
    timestamp = str(datetime.datetime.now(datetime.timezone.utc))
    date = str(datetime.datetime.now(datetime.timezone.utc).date())

    with open(f"prices/national/{timestamp}.csv", "w") as fd:
        writer = csv.writer(fd)
        writer.writerows([[date] + state for state in national_prices])

    with open(f"prices/states/{timestamp}.csv", "w") as fd:
        writer = csv.writer(fd)
        writer.writerows([[date] + county for county in state_prices])
        writer.writerows(state_prices)

    generate_master_files()

    elapsed = time.perf_counter() - s
    log.info(f"{__file__} executed in {elapsed:0.5f} seconds.")
    elapsed = time.perf_counter() - s
    log.info(f"{__file__} executed in {elapsed:0.5f} seconds.")


if __name__ == "__main__":
    main()
