#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 11:17:22 2017

@author: selin
"""


import os
import re
import xml.etree.ElementTree as ET

def parse(config):
    # get package: from config.xml jmh bench root dir and traverse down until find file .Benchmark
    # get config -->
    # pass ip-config?
    root = ET.parse(config).getroot()
    rootdir = root.find('.//project/jmh_root').attrib['dir']
    # find <jmh-root-dir>
    # assign
    
    test_list = []
    #file_pat = re.compile('(.*Benchmark)\.java') # to distribute benchmark-files
    annot_pat = re.compile('@Benchmark$')
    unit_pat = re.compile('public void (test.*)\(')
    name_pat = re.compile('public .* (.*)\(')
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            #if re.search(file_pat, file):
             #   test_list.append(re.search(file_pat, file).group(1))
            # open files
            filepath = subdir + os.sep + file
            with open(filepath, 'r') as f:
                for line in f: 
                    # loop over each line of file and look for @Benchmark or @Test or test.*()
                    if re.search(annot_pat, line):
                        # get name                      
                        line = f.next()
                        test_name = re.search(name_pat, line)
                        test_list.append(test_name.group(1))
                    elif re.search(unit_pat, line):
                        test_name = re.search(name_pat, line)    
                        test_list.append(test_name.group(1)) # store name in list 
                        
    #for x in test_list:
     #   print x
    return test_list

if __name__ == '__main__':
  parse('../config.xml')

           