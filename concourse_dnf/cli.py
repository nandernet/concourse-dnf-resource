import argparse
import gzip
import json
import logging
import xml.etree.ElementTree as ET
from typing import Dict, List
from xml.etree.ElementTree import Element

import requests

log = logging.getLogger(__name__)


def fetch_primary(baseurl) -> str:
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
            return baseurl + entry.find("repo:location", repomd_ns).attrib.get("href")


def fetch_repodata(repos: List[str], package: str) -> List[Dict[str, str]]:
    primary_ns = {
        "common": "http://linux.duke.edu/metadata/common",
        "rpm": "http://linux.duke.edu/metadata/rpm",
    }
    packages = []

    for repo in repos:
        primary_path = fetch_primary(repo)

        primary_r = requests.get(primary_path)
        primary_xml = gzip.decompress(primary_r.content)
        root = ET.fromstring(primary_xml)

        for pkg in root.findall("common:package", primary_ns):
            pkg_name = pkg.find("common:name", primary_ns).text
            pkg_version = pkg.find("common:version", primary_ns).attrib
            if pkg_name == package:
                packages.append(
                    {
                        "ref": "{}:{}-{}-{}".format(
                            pkg_name,
                            pkg_version.get("epoch", 0),
                            pkg_version.get("ver"),
                            pkg_version.get("rel"),
                        )
                    }
                )
    return packages


def parse_args():
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


def check() -> None:
    args = parse_args()
    print(json.dumps(fetch_repodata(args.repo, args.package)))


if __name__ == "__main__":
    check()
