#!/bin/env python3

import sys
import os
import re
from glob import glob
from collections import defaultdict
from pathlib import Path

html_reference_regexp = re.compile(r' (src|href)="([^"]+)"')
html_id_regexp = re.compile(r' id="([^"]+)"')

cwd = Path.cwd()
def canonical_path(p):
   return os.path.relpath(os.path.realpath(p), cwd)

rc = 0
html_files_to_be_parsed = set()
input_paths = sys.argv[1:]

for path in input_paths:
    if os.path.isdir(path):
        html_files_in_this_dir = set([canonical_path(y) for x in os.walk(path) for y in glob(os.path.join(x[0], '*.html'))])
        if len(html_files_in_this_dir) == 0:
            print("Error: no HTML file found in "+path)
            rc = 1
        else:
            html_files_to_be_parsed |= html_files_in_this_dir
    elif os.path.isfile(path):
        if path.endswith(".html"):
            html_files_to_be_parsed.add(canonical_path(path))
        else:
            print("Error: input file "+path+" is not a .html file")
            rc = 1
    else:
        print("Error: input argument "+path+" does not exist")
        rc = 1

if rc != 0:
    sys.exit(rc)

referred_files = defaultdict(lambda: defaultdict(set))
html_ids = defaultdict(set)

parsed_html_files = set()
while len(html_files_to_be_parsed) > 0:
    html_file = html_files_to_be_parsed.pop()
    parsed_html_files.add(html_file)
    with open(html_file, encoding="utf8") as f:
        for line in f:
            if not line.startswith("<!--"):
                for _, href in html_reference_regexp.findall(line):
                    protocol, _, _ = href.partition(":")
                    if protocol in [ "http", "https", "javascript", "data" ]:
                        pass
                    else:
                        referred_file, _, referred_id = href.partition("#")
                        if referred_file == "":
                            referred_file = html_file
                        else:
                            if '.' not in os.path.basename(referred_file):
                                referred_file = os.path.join(referred_file, "index.html")
                            referred_file = canonical_path(os.path.join(os.path.dirname(html_file), referred_file))
                            #if referred_file.endswith(".html") and referred_file not in parsed_html_files:
                            #    html_files_to_be_parsed.add(referred_file)
                        referred_files[referred_file][referred_id].add(html_file)
                for html_id in html_id_regexp.findall(line):
                    #print(html_id)
                    html_ids[html_file].add(html_id)

for referred_file, referred_file_ids in referred_files.items():
    if referred_file not in html_ids and not os.path.isfile(referred_file):
        referred_from = set([x for y in referred_file_ids.values() for x in y])
        if referred_file.find("/_/fonts/") >=0 or referred_file.find("index.html") >=0:
            print("File "+referred_file+" has been ignored")
            continue
        else:
            print('Error: file '+referred_file+' does not exist (referred from '+", ".join(referred_from)+')')
            rc = 1
            continue
    for referred_id, referred_from in referred_file_ids.items():
        if referred_id == "":
            continue
        if referred_id not in html_ids[referred_file]:
            print('Error: file '+referred_file+' has no id '+referred_id+' as referred from '+", ".join(referred_from))
            rc = 1

if rc == 0:
    print("We don't have any broken links in the site ")
#sys.exit(rc)

