#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 11:17:22 2017

@author: selin
"""


import os
import re

def parse(project):
    # TODO: extend method for unit tests (@Test)
    test_list = []
    annot_pat = re.compile('@Benchmark$')
    unit_pat = re.compile('@Test$')
    name_pat = re.compile('public .* (.*)\(')

    for subdir, dirs, files in os.walk(project):
        for file in files:
            #if re.search(file_pat, file):
             #   test_list.append(re.search(file_pat, file).group(1))
            filepath = subdir + os.sep + file
            with open(filepath, 'r') as f:
                for line in f:
                    # loop over each line of file and look for @Benchmark or @Test or test.*()
                    if re.search(annot_pat, line):
                        # get name
                        line = f.next()
                        test_name = re.search(name_pat, line)
                        test_list.append(test_name.group(1))
            #elif re.search(unit_pat, line):
             #   test_name = re.search(name_pat, line)    
              #  test_list.append(test_name.group(1)) # store name in list
    return test_list
