#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 11:17:22 2017

@author: selin
"""


import os
import re

def parse(data):
    project = data['project']
    type = data['CL-params']['-t']
    test_list = []
    annot_pat = re.compile('@Benchmark$') if type == 'benchmark' else re.compile('@Test$')
    name_pat = re.compile('public .* (.*)\(')

    for subdir, dirs, files in os.walk(project):
        for file in files:
            filepath = subdir + os.sep + file
            with open(filepath, 'r') as f:
                for line in f:
                    # loop over each line of file and look for @Benchmark or @Test or test.*()
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
