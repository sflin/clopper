#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 10:14:33 2017

@author: selin
"""
import os
from os.path import expanduser
import shutil
import xml.etree.ElementTree as ET
from collections import defaultdict

class Writer(object):
    """Writer generates customized config files and command line parameters 
        for each instance. 
        Output is of format:
            config.tar.gz
            params.tar.gz
        If random versions are used, directories contain multiple files for each
        instance:
            config.tar.gz
                cloud-config-1.xml
                cloud-config-2.xml
                ...
                cloud-config-n.xml
            params.tar.gz
                cl-params-1.txt
                cl-params-2.txt
                ...
                cl-params-n.txt
        """
        
    def __init__(self, data, content):
        self.data = data
        self.content = content
        self.random = False
        self.num = 1
        
    def eval_input(self):
        
        """options = defaultdict(lambda: (None, None), 
                              {'version': (suite, None), 
                               'test': (None, suite), 
                               'versiontest': (suite[0], suite[-1])})"""
        options = defaultdict(lambda :  False,
                              {'random': True})
        return options[self.content]
        
    def get_parameters(self, suite, number):
        
        cl_params = self.data['CL-params']
        os.mkdir(expanduser('~/tmp/params'))
        os.chdir(expanduser('~/tmp/params'))
        for x in range(number):
            with open('cl-params-' + str(x + 1) + '.txt', 'w') as cl_file:
                for param in cl_params:
                    if param == '-f':
                        cl_file.write(param + ' ' + '~/tmp/config/cloud-config-' + str(x + 1) + '.xml ')
                    elif param == '-o':
                        cl_file.write(param + ' ' + '~/output/out-' + str(x+1) + '.csv ')
                    else:
                        cl_file.write(param + ' ' + cl_params[param] + ' ')
                if suite[0]: # if suite has elements, add --tests flag
                    tmp="--tests '\."
                    for i in range(0, len(suite)-1): 
                        tmp += suite[i] + "$|\."
                    tmp += suite[-1] + "$'"
                    cl_file.write(tmp)
        os.chdir('..')
        params = shutil.make_archive('params', 'gztar', root_dir=expanduser('~/tmp/params'))
        shutil.rmtree(expanduser('~/tmp/params'))
        return params
    
    def get_config(self, suite, number):
        
        tree = ET.parse(self.data['config'])
        root = tree.getroot()
        # adapt start and end tag in config for each instance
        root.find('.//project').attrib['dir'] = '/home/selin/tmp/project/' + root.find('.//project').attrib['dir'].split('/')[-1]
        root.find('.//project/jmh_root').attrib['dir'] = '/home/selin/tmp/project/benchmarks'
        if suite[0]: # if suite has elements 
            root.find('.//project/versions/start').text = suite[0] # only do this if VersionDistributor or TestVersionDistributor
            root.find('.//project/versions/end').text = suite[-1]
        config = './cloud-config-' + str(number) + '.xml'
        tree.write(config, encoding='utf-8', xml_declaration=True)
        return
    
    def get_multi_configs(self, suite):
        
        try:
            os.mkdir(expanduser('~/tmp/config'))
        except OSError:
            print 'Changing into folder ./config.'
            pass
        os.chdir(expanduser('~/tmp/config'))
        # make config-folder, cd into it
        if self.random:
            for s in suite:
                self.num = suite.index(s) + 1
                self.get_config([s], self.num)
        else:
            self.get_config(suite, self.num)
        # create zip-file of configs
        os.chdir('..')
        config = shutil.make_archive('config','gztar',root_dir=expanduser('~/tmp/config'))
        shutil.rmtree(expanduser('~/tmp/config'))
        return config
    
    def generate_input(self, test_suite):
        
        self.random = self.eval_input() # check whether to create multiple configs
        config = self.get_multi_configs(test_suite[0])
        param = self.get_parameters(test_suite[1], self.num)
        return config, param
    