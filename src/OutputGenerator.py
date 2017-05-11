#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 14:36:33 2017

@author: selin
"""
from os.path import expanduser
import os
from MvnCommitWalker import MvnCommitWalker
from MvnVersionWalker import MvnVersionWalker
 
def get_versions(params):
    
    kwargs = {'mode':params['mode'],'skip-noncode':params['codeonly'], 
              'start':params['start'], 'end':params['to'], 'step':params['step']}
    if 'versions' in params['backend']:
        backend = MvnVersionWalker(params['config'])
    else:
        backend = MvnCommitWalker(params['config'])
    cwd = os.getcwd()
    versions = backend.generate_version_list(**kwargs)
    os.chdir(cwd)
    return versions

def get_header(data):
    
    param_dict = {'config':data['CL-params']['-f'], 'outfile':data['CL-params']['-o'], 
                  'type':data['CL-params']['-t'], 'backend':'commits', 
                  'runner':'mvn', 'start':None, 'to': None, 'step':None, 
                  'invert':False, 'tests':None, 'mode':'commit-mode', 
                  'codeonly':False, 'build-type':'clean', 'cloud':data['project-id']}
    
    mapping = {'backend':'-b', 'runner':'-r', 'start':'--from', 'to':'--to', 
               'step':'--step', 'invert':'-i', 'tests':'--tests', 
               'mode':'--mode', 'codeonly':'--skip-noncode', 'build-type':'--build-type'}
    
    for key in mapping.keys():
        try:
            param_dict[key] = data['CL-params'][mapping[key]]
        except KeyError:
            continue
    return param_dict

def concat(data, files):
    """Concatenate files, sorted by version."""
    
    params = get_header(data)
    versions = get_versions(params)
    to_merge = []
    for v in versions:
        [to_merge.append(fname) for fname in files if v in fname]
    with open(expanduser(params['outfile']), 'w') as outfile:
        for key, val in params.iteritems():
            outfile.write("# %s -> %s\n" % (key, val))
        outfile.write("Project;Version;SHA;Configuration;Test;RawVal\n")
        for fname in to_merge:
            with open(fname, 'r') as fin:
                fin.next() # skip header
                [outfile.write(line) for line in fin]            