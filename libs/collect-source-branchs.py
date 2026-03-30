#!/usr/bin/env python3
import argparse

RELEASE_SUPPORT = "22.9"

def collect_releases(current_release: str ="") -> list:
    start_release = RELEASE_SUPPORT.split(".")
    if current_release in ["", None]:
        raise Exception
    releases = []
    current_release = current_release.split(".")
    major_versions = range(int(start_release[0]), int(current_release[0])+1)
    minor_versions = range(3, 13, 3)
    for major in major_versions:
        for minor in minor_versions:
            if major == int(start_release[0]) and minor < int(start_release[1]): continue
            if major == int(current_release[0]) and minor >= int(current_release[1]): break
            version = "%s.%s-release" % (major, minor)
            releases.append(version)
    return releases

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", '--release', help = "The current release")
    args = parser.parse_args()
    print(collect_releases(args.release))

