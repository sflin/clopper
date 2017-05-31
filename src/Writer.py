#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 10:14:33 2017

@author: selin
"""
import os
from os.path import expanduser
import shutil
import logging
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
        self.num = 1
        
    def eval_input(self):
        
        options = defaultdict(lambda :  False,
                              {'random': True})
        return options[self.content]
    
    def get_current_params(self):
        
        cl_dict = self.data['CL-params']
        cloud_flag = "~/" + self.data['credentials'].split('/')[-1] + " " + self.data['bucket-name']
        param_dict = {'-f':cl_dict['-f'], '-o':'~/tmp/out.csv', '-t':cl_dict['-t'],
                      '--cloud': cloud_flag}
        mapping = ['-b', '-r','-i', '--tests', '--mode', '--skip-noncode','--build-type']
        if self.data['distribution'] == 'TestDistributor':
            [mapping.append(item) for item in ('--from', '--to', '--step')]
        for key in mapping:
            try:
                param_dict[key] = cl_dict[key]
            except KeyError:
                continue
        return param_dict 
    
    def get_parameters(self, suite):
        
        os.mkdir(expanduser('~/tmp/params'))
        os.chdir(expanduser('~/tmp/params'))
        params = self.get_current_params()
        number = self.num
        for x in range(number):
            with open('cl-params-' + str(x + 1) + '.txt', 'w') as cl_file:
                for p in params:
                    if p == '-f':
                        cl_file.write(p + ' ' + '~/tmp/config/cloud-config-' + str(x + 1) + '.xml ')
                    elif p == '--tests' and suite[0]:
                        continue
                    else:
                        cl_file.write(p + ' ' + str(params[p]) + ' ')
                if suite[0]: # if suite has elements, add --tests flag
                    tmp = "--tests '"
                    delimiter = "$|" if params['-t'] == 'benchmark' else ","
                    if self.data['distribution'] == 'RMIT':
                        tmp += suite[x] + "$'"
                    else:
                        for i in range(0, len(suite)-1):
                            tmp += suite[i] + delimiter
                        end = "$'" if params['-t'] == 'benchmark' else "'"
                        tmp += suite[-1] + end
                    cl_file.write(tmp)
        os.chdir('..')
        params = shutil.make_archive('params', 'gztar', root_dir=expanduser('~/tmp/params'))
        shutil.rmtree(expanduser('~/tmp/params'))
        return params
    
    def get_config(self, suite, number):
        tree = ET.parse(self.data['CL-params']['-f'])
        root = tree.getroot()
        dir = "/home/" + self.data['username'] + "/tmp/project/" + root.find('.//project').attrib['dir'].split('/')[-1]
        root.find('.//project').attrib['dir'] = dir
        root.find('.//project/jmh_root').attrib['dir'] = "/home/" + self.data['username'] + "/tmp/project/benchmarks"
        if suite[0]: # if suite has elements 
            root.find('.//project/versions/start').text = suite[0]
            root.find('.//project/versions/end').text = suite[-1]
        config = './cloud-config-' + str(number) + '.xml'
        tree.write(config, encoding='utf-8', xml_declaration=True)
    
    def get_version_config(self, suite):
        
        tree = ET.parse(self.data['CL-params']['-f'])
        root = tree.getroot()
        root.find('.//project/jmh_root').attrib['dir'] = "/home/" + self.data['username'] + "/tmp/project/benchmarks"
        parent = root.find('.//project/versions')
        iterator = root.getiterator('version')
        if suite[0] and parent is not None:
            [parent.remove(item) for item in iterator]
            for x in range(0, len(suite)):
                element = ET.Element('version')
                element.text = suite[x]
                parent.insert(x, element)
        config = './cloud-config-1.xml'
        tree.write(config, encoding='utf-8', xml_declaration=True)
        
    def get_multi_configs(self, suite):
        
        try:
            os.mkdir(expanduser('~/tmp/config'))
        except OSError:
            logging.info("Folder config exists.")
        os.chdir(expanduser('~/tmp/config'))
        if ('-b','versions') in self.data['CL-params'].viewitems():
            self.get_version_config(suite)
        elif self.eval_input():
            self.num = 0
            for s in suite:
                self.num += 1
                self.get_config([s], self.num)
        else:
            self.get_config(suite, 1)
        # create zip-file of configs
        os.chdir('..')
        config = shutil.make_archive('config','gztar',root_dir=expanduser('~/tmp/config'))
        shutil.rmtree(expanduser('~/tmp/config'))
        return config
    
    def generate_input(self, test_suite):
        
        config = self.get_multi_configs(test_suite[0])
        logging.info("Config-files generated.")
        param = self.get_parameters(test_suite[1])
        logging.info("Commandline parameters prepared.")
        return config, param