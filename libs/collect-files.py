#!/usr/bin/env python3
import subprocess
import argparse
import re
import os

RELEASE_SUPPORT="23.9"

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
            if major == int(current_release[0]) and minor > int(current_release[1]): break
            version = "%s.%s" % (major, minor)
            releases.append(version)
    print("releases are avaliable: %s" % releases)
    return releases 

def get_remote_path_playbook(pipeline: str = "") -> str:
    cmd_template = "curl -k https://jenkins-fnms.int.net.nokia.com/job/%s/lastSuccessfulBuild/artifact/descriptor.json 2>/dev/null \
                    | grep installation_playbooks \
                    | awk '{print $2}'  \
                    | tail -1" % (pipeline)
    
    response = subprocess.Popen(
        cmd_template,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)
    
    remote_path = str(response.stdout.read())
    pattern = r'"(\S*)".*'
    remote_path = re.findall(pattern, remote_path)
    print(remote_path)
    return remote_path[0]

def download_zip_file(release, url: str = None, remotePath: str = None, tag: str=None):
    if not tag == None:
        url = "http://%s/artifactory/artifactory_maven/com/nokia/installation/%s/installation_playbooks-%s.zip" %(args.host, tag, tag)
    elif not remotePath == None:
        url = "http://%s/artifactory/artifactory_maven/%s" % (args.host, remotePath)

    subprocess.Popen(
        "curl -o %s/playbook-%s.zip --create-dirs %s && unzip -o %s/playbook-%s.zip 'docs/*' -d %s" % (args.tmp,release, url, args.tmp, release,args.tmp),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    ).communicate()

def clear():
    print("cleared %s" % args.tmp)
    subprocess.Popen(
        "rm -rf %s" % args.tmp,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )

def run_main():
    clear()
    for release in collect_releases(args.current_release):
        retry = 0
        downloaded = False
        pipeline_name = "FNMS-Altiplano-VM" if release==args.current_release else "FNMS-Altiplano-VM-%s-release" % release
        remote_path = get_remote_path_playbook(pipeline_name)
        print("pipeline name: %s" %pipeline_name)
        download_zip_file(release=release,remotePath=remote_path)
        while retry < 3:
            download_zip_file(release=release,remotePath=remote_path)
            downloaded = os.path.isdir(args.tmp + "/playbook-%s.zip" %release)
            if downloaded:
                break
            retry += 1

        if downloaded == False:
            print("download %s failed" % remote_path, True)
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pipeline_name", default="FNMS-Altiplano-VM", help = "Pipeline to download files")
    parser.add_argument("-m", "--tmp", default="./tmp", help="Path to store tmp files")
    parser.add_argument("-a", "--host", default="artifactory-espoo-fnms.int.net.nokia.com",
                        help="Host name to download playbook lab")
    parser.add_argument("-t", "--playbook_tag",default="", help="Playbook tag to contain files which we need collect on Pipeline")
    parser.add_argument("-u", "--url", default="", help="Provide if you want to download zip file in other places")
    parser.add_argument("-r", "--current_release", default="23.12", help = "Get current release if parameter is empty")
    args = parser.parse_args()
    run_main()