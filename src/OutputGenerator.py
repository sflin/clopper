#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 14:36:33 2017

@author: selin
"""
import json
from os.path import expanduser
import subprocess

def write_configuration_header(data):
    
    param_dict = {'config':data['config'], 'outfile':data['CL-params']['-o'], 
                  'type':data['CL-params']['-t'], 'backend':'commits', 
                  'runner':'mvn', 'start':None, 'to': None, 'step':None, 
                  'invert':False, 'tests':None, 'mode':'commit-mode', 
                  'codeonly':False, 'build-type':'clean'}
    
    mapping = {'backend':'-b', 'runner':'-r', 'start':'--from', 'to':'--to', 
               'step':'--step', 'invert':'-i', 'tests':'--tests', 
               'mode':'--mode', 'codeonly':'--skip-noncode','build-type':'--build-type'}
    for key in mapping.keys():
        try:
            param_dict[key] = data['CL-params'][mapping[key]]
        except KeyError:
            continue
    return param_dict

def concat(data):
    params = write_configuration_header(data)
    with open(expanduser('~/output/instance-0-output.csv'), 'w') as file:
        for key, val in params.iteritems():
            file.write("# %s -> %s\n" % (key, val))
        file.write("Project;Version;SHA;Configuration;Test;RawVal\n") # write header
    cmd = 'cat ~/output/*.csv > ' + params['outfile']
    subprocess.call(cmd, shell=True)
    
if __name__ == "__main__" :
    data = json.loads("""{
                          "mode": "ip",
                          "total": 3,
                          "ip-list": {
                            "instance-1": "130.211.94.53"
                          },
                          "CL-params": {
                            "-f": "/home/selin/Documents/Uni/Bachelorthesis/clopper/config.xml",
                            "-o": "./output.csv",
                            "-t": "benchmark",
                            "-b": "versions",
                            "--tests": "'\\\.runtime_deserialize_1_int_field$|\\\.runtime_serialize_1_int_field$|\\\.testFoo$|\\\.baseline$'"
                          },
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/project",
                          "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                          "distribution": "RandomDistributor",
                          "status-mode": "ALL"
                        }""")   
    concat(data)