#!/usr/bin/env python3
import argparse
import json
import subprocess


def get_last_build_tag(pipeline: str = "") -> str:
    response = subprocess.Popen(
        "curl -sk https://jenkins-fnms.int.net.nokia.com/job/Third-Party-Images/job/%s/lastSuccessfulBuild/artifact/descriptor.json | grep pipelineTags | head -1" % pipeline,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)


    data = str(response.stdout.read())
    first = data.find("{")
    second = data.find("}") + 1
    last_tag = json.loads(data[first:second])[pipeline]
    return last_tag


def check_file_exist(url: str) -> bool:
    try:
        cmd = 'curl -s -o /dev/null -I -w "%{http_code}" ' + url
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, error = process.communicate()
        http_code = out.decode("utf-8").split("\n")[0]
        return True if http_code in [200, "200"] else False

    except Exception as e:
        return False


def build_url(host: str = ""):
    try:
        last_tag = get_last_build_tag(args.pipeline)
        url = "http://%s/artifactory/libs_cr_local/com/nokia/fnms/cdoc-theme/cdoc-theme-package/%s/cdoc-theme-package-%s.zip" % (
            host, last_tag, last_tag)
        url = url if check_file_exist(url) else args.ui
        print(url)

    except Exception as e:
        print(args.ui)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", '--host', default='artifactory-espoo-fnms.int.net.nokia.com',
                                               help = "provide jenkins's domain")
    parser.add_argument("-z", '--ui', default='ui-bundle.zip',
                                              help = "path to default ui-bundle.zip ")
    parser.add_argument("-p", '--pipeline', default='Altiplano-Customer-Doc-Theme',
                                             help = "provide pipeline which we need find last tag")
    args = parser.parse_args()
    build_url(args.host)
