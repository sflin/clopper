#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 22 16:37:10 2017

@author: selin
"""

import sys
import subprocess
import re
import os

def parse_unit(project):
    test_list = []
    annot_pat = re.compile('@Test$')
    name_pat = re.compile('public .* (.*)\(')
    
    for subdir, dirs, files in os.walk(project):
        for file in files:
            filepath = subdir + os.sep + file
            with open(filepath, 'r') as f:
                for line in f:
                    # loop over each line of file and look for @Test
                    if re.search(annot_pat, line):
                        # get name
                        searching = True
                        while searching:
                            line = f.next()
                            if re.search(name_pat, line):
                                test_name = re.search(name_pat, line)
                                test_list.append(test_name.group(1))
                                searching = False
    return test_list

def parse(data):
    project = data['project']
    if data['CL-params']['-t']=='unit':
        return parse_unit(project)
    for subdir, dirs, files in os.walk(project):
        for file in files:
            if file == 'benchmarks.jar':
                jar_path = subdir + os.sep + file
                break
    cmd = "java -jar " + jar_path + " -l"
    proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if err:
        sys.exit(err)
    tests = out.replace('Benchmarks: \n','').split('\n')[:-1]
    return tests