#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 10:14:33 2017

@author: selin
"""

import json
import xml.etree.ElementTree as ET
from Distributor import Distributor, TestDistributor, VersionDistributor, VersionTestDistributor

class InputWriter(object):
    
    def __init__(self, data, strategy=None):
        self.action = None
        self.data = data
        if strategy:
            self.action = strategy()
                        
    def generate_input(self, splitted_test_suite):
        if(self.action):
            return self.action.generate_input(self, splitted_test_suite)
        else:
            raise UnboundLocalError('Exception raised, no strategyClass specified!')
            
class ConfigurationWriter(object):
    
    def generate_input(self, splitted_test_suite, instance):
        
        tree = ET.parse(instance.data['config'])
        root = tree.getroot()
        # adapt start and end tag in config for each instance
        # TODO: check path project-tag
        root.find('.//project').attrib['dir'] = '~/project' + data['project'].split('/')[-1]
        root.find('.//project/jmh_root').attrib['dir'] = '~/project' + data['project'].split('/')[-1]
        root.find('.//project/versions/start').text = splitted_test_suite[0]
        root.find('.//project/versions/end').text = splitted_test_suite[-1]
        config = 'config.xml'
        tree.write(config)
        return config
    
class ParameterWriter(object):
    
    def generate_input(self, splitted_test_suite, instance):
        cl_params = instance.data['CL-params']
        cl_params['-f'] = 'config.xml' # overwrite local config-specification
        # generate file containing individual command line arguments
        with open('./cl-params.txt', 'w') as cl_file:
            for param in cl_params:
                cl_file.write(param + ' ' + cl_params[param] + ' ')
        return cl_file
        
class UniversalWriter(object):
    
    def generate_input(self, splitted_test_suite, instance):
        conf_writer = InputWriter(instance.data, strategy=ConfigurationWriter)
        conf = conf_writer.generate_input(splitted_test_suite[0])
        para_writer = ParameterWriter(instance.data, strategy=ParameterWriter)
        param = para_writer.generate_input(splitted_test_suite[1])
        return conf, param
    
if __name__ == "__main__" :
    with open('./config-ip.json') as data_file:
        data = json.load(data_file)    
    # TODO: adapt data['distribution'] for InputWriter
    distributor = Distributor(data, strategy=TestDistributor)
    test_data = distributor.split()
    distributor = Distributor(data, strategy=VersionDistributor)
    versions = distributor.split()
    distributor = Distributor(data, strategy=VersionTestDistributor)
    mixed = distributor.split()
    writer = InputWriter(data, strategy=ConfigurationWriter)
    test_data = writer.generate_input(versions)
    writer = InputWriter(data, strategy=ParameterWriter)
    test_data = writer.generate_input(test_data)
    writer = InputWriter(data, strategy=UniversalWriter)
    test_data = writer.generate_input(mixed)    
    
