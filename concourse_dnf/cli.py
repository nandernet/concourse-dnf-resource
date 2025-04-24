import argparse
import gzip
import json
import logging
import re
import os
import sys
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, TypeVar

import requests
import zstandard

P = TypeVar("P")

# Read from the environment in MB
MAX_OUTPUT_SIZE = int(os.environ.get("MAX_OUTPUT_SIZE", "4000")) * 10**6

log = logging.getLogger(__name__)


# https://stackoverflow.com/a/54985647/877983
def rpm_sort(elements: List[str]) -> List[str]:
    """sort list elements using 'natural sorting': 1.10 > 1.9 etc...
    taking into account special characters for rpm (~)"""

    alphabet = "~0123456789abcdefghijklmnopqrstuvwxyz:-."

    def convert(text):
        return (
            [int(text)]
            if text.isdigit()
            else ([alphabet.index(letter) for letter in text.lower()] if text else [1])
        )

    def alphanum_key(key):
        return [convert(c) for c in re.split("([0-9]+)", key)]

    return sorted(elements, key=alphanum_key)


def fetch_primary(baseurl: str) -> str:
    repomd_ns = {
        "repo": "http://linux.duke.edu/metadata/repo",
        "rpm": "http://linux.duke.edu/metadata/rpm",
    }

    repomd_path = "repodata/repomd.xml"
    if not baseurl.endswith("/"):
        baseurl += "/"

    repomd_url = baseurl + repomd_path

    repomd_r = requests.get(repomd_url)
    tree = ET.fromstring(repomd_r.text)

    for entry in tree.findall("repo:data", repomd_ns):
        if entry.attrib.get("type") == "primary":
            repo_node = entry.find("repo:location", repomd_ns)
            if repo_node is not None:
                return baseurl + repo_node.attrib.get("href", "")

    raise RuntimeError("Could not find 'primary' metadata in repomd")


def ref_wrap(packages: List[P]) -> List[Dict[str, P]]:
    return [{"ref": pkg} for pkg in packages]


def fetch_repodata(repos: List[str], package: str) -> List[Dict[str, str]]:
    primary_ns = {
        "common": "http://linux.duke.edu/metadata/common",
        "rpm": "http://linux.duke.edu/metadata/rpm",
    }
    packages = []

    for repo in repos:
        sys.stderr.write(f"Searching for '{package}' in '{repo}'...\n")
        primary_path = fetch_primary(repo)

        primary_r = requests.get(primary_path)
        if primary_path.endswith(".xml.gz"):
            primary_xml = gzip.decompress(primary_r.content)
        elif primary_path.endswith(".xml.zst"):
            primary_xml = zstandard.decompress(primary_r.content, MAX_OUTPUT_SIZE)
        elif primary_path.endswith(".xml"):
            primary_xml = primary_r.content
        else:
            raise RuntimeError(f"Don't know how to handle file: '{primary_path}'")
        root = ET.fromstring(primary_xml)

        for pkg in root.findall("common:package", primary_ns):
            pkg_name_node = pkg.find("common:name", primary_ns)
            pkg_version_node = pkg.find("common:version", primary_ns)
            if pkg_name_node is None or pkg_version_node is None:
                raise RuntimeError(f"Invalid package name/version in repo '{repo}'")

            pkg_name = pkg_name_node.text
            pkg_version = pkg_version_node.attrib
            if pkg_name == package:
                nerva = "{}:{}-{}-{}".format(
                    pkg_name,
                    pkg_version.get("epoch", 0),
                    pkg_version.get("ver"),
                    pkg_version.get("rel"),
                )
                sys.stderr.write(f"-> Found NERVA: {nerva}\n")
                packages.append(nerva)
    return ref_wrap(rpm_sort(list(set(packages))))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="DnfResource",
        description="Concourse-compatible DNF resource checker",
    )
    parser.add_argument(
        "-r",
        "--repo",
        nargs="+",
        help="BaseURL of yum/dnf repository, can be specified multiple times",
    )
    parser.add_argument("-p", "--package", help="Package base name version to check")
    parser.add_argument("-v", "--verbose")

    return parser.parse_args()


def parse_stdin() -> Tuple[List[str], str]:
    config = json.load(sys.stdin)

    package = config.get("source", {}).get("package")
    if not package:
        sys.stderr.write("Mandatory argument 'package' not defined\n")
        sys.exit(1)

    repos = config.get("source", {}).get("repositories")
    if not repos or len(repos) == 0:
        sys.stderr.write("Mandatory argument 'repositories' not defined\n")
        sys.exit(1)

    return repos, package


def resource_check() -> None:
    repos, package = parse_stdin()

    sys.stdout.write(json.dumps(fetch_repodata(repos, package)))


def resource_in() -> None:
    repos, package = parse_stdin()
    sys.stdout.write(
        json.dumps({"version": fetch_repodata(repos, package)[-1], "metadata": []})
    )


def resource_out() -> None:
    # repos, packages = parse_stdin()
    sys.stderr.write("Unsupported action")
    sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    print(json.dumps(fetch_repodata(args.repo, args.package)))
