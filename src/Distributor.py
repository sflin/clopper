#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 10:14:33 2017

@author: selin
"""

import random
import json
import parser
import os
from impl.GitRepoHandler import GitRepoHandler
import xml.etree.ElementTree as ET
from TestSuite import TestSuite

class Distributor(object):
    """Generates test suite based on strategy defined in json. 
    
        Output of format:
        [
        [[version-inst1],[tests-inst1]],
        [[versions-inst2],[tests-inst3]],
         [[version-inst3],[tests-inst3]],
         ...,
         [[versions-instx],[tests-instx]]
         ]
        """
    
    def __init__(self, data, strategy=None):
        self.action = None
        self.data = data
        if strategy:
            self.action = strategy()
            
    def get_suite(self):
        
        if(self.action):
            return self.action.get_suite(self)
        else:
            #suite = [(None, None) for in range(self.data['total'])]
            #return suite
            raise UnboundLocalError('Exception raised, no such strategyClass!')
             
            
class VersionDistributor(object):
    """Version range, all tests
        for 3 instances, generates output of format 
            [[[v1],[None]],[[v2],[None]],[[v3],[None]]]"""
            
    def get_target(self, data):
        
        cwd = os.getcwd()
        tree = ET.parse(data['config'])
        root = tree.getroot()
        project = root.find('.//project').attrib['dir']
        start = root.find('.//project/versions/start').text
        end = root.find('.//project/versions/end').text
        repo = GitRepoHandler(project) # this must be a git project!
        target = repo.find_commits_between(start, end, False)
        os.chdir(cwd)
        return target
    
    def split(self, data):
        
        target = self.get_target(data)
        total_inst = data['total']
        x = len(target)/total_inst
        suite = TestSuite()
        for i in range(total_inst-1):
            if x < 1:
                randoms = random.sample(range(len(target)), len(target))
                rand_list = [target[i] for i in randoms]
                suite.append(rand_list)
            else:
                suite.append(target[i*x:(i+1)*x])
        suite.append(target[(total_inst-1)*x:]) # for last group and if odd number - assign last elements
        random.shuffle(suite)
        return suite
    
    def get_suite(self, instance):
        
        suite = TestSuite()
        total_inst = instance.data['total']
        suite = self.split(instance.data)
        result = TestSuite()
        result = result.nest(suite, total_inst*[[None]], total_inst)
        return result
    
class RandomVersionDistributor(object):
    """Random versions, all tests."""
    
    def get_target(self, data):
        
        cwd = os.getcwd()
        tree = ET.parse(data['config'])
        root = tree.getroot()
        project = root.find('.//project').attrib['dir']
        start = root.find('.//project/versions/start').text
        end = root.find('.//project/versions/end').text
        repo = GitRepoHandler(project) # this must be a git project!
        target = repo.find_commits_between(start, end, False)
        os.chdir(cwd)
        return target
    
    def split(self, data):
        
        target = self.get_target(data)
        random.shuffle(target)
        total_inst = data['total']
        x = len(target)/total_inst
        suite = TestSuite(content='random')
        
        for i in range(total_inst-1):
            if x < 1:
                randoms = random.sample(range(len(target)), len(target))
                rand_list = [target[i] for i in randoms]
                suite.append(rand_list)
            else:
                suite.append(target[i*x:(i+1)*x])
        suite.append(target[(total_inst-1)*x:])
        return suite
    
    def get_suite(self, instance):
        suite = TestSuite()
        total_inst = instance.data['total']
        suite = self.split(instance.data)
        result = TestSuite(content='random')
        result = result.nest(suite, total_inst*[[None]], total_inst)
        return result
        
class TestDistributor(object):
    """All versions, random tests
        for 3 instances, generates output of format 
            [[[None],[t1]],[[None],[t2]],[[None],[t3]]]"""
            
    def get_target(self, data):
        
        if data['CL-params']['--tests']:
            tests = data['CL-params']['--tests'].replace("'", "").replace('\.', '').replace('|', '').split('$')[:-1]
            return tests
        target = parser.parse(data['project']+'/benchmarks') # this must be the jmh root dir
        return target
    
    def split(self, data):
        
        target = self.get_target(data)
        #target = self.get_target(data['project']+'/benchmarks') 
        random.shuffle(target)
        total_inst = data['total']
        x = len(target)/total_inst
        suite = TestSuite()
        
        for i in range(total_inst-1):
            if x < 1:
                randoms = random.sample(range(len(target)), len(target))
                rand_list = [target[i] for i in randoms]
                suite.append(rand_list)
            else:
                suite.append(target[i*x:(i+1)*x])
        suite.append(target[(total_inst-1)*x:])
        return suite
    
    def get_suite(self, instance):
        suite = TestSuite()
        total_inst = instance.data['total']
        suite = self.split(instance.data)
        result = TestSuite()
        result = result.nest(total_inst*[[None]], suite, total_inst)
        return result

class VersionTestDistributor(object):
    """Version ranges, random tests"""
    
    def get_versions(self, data):
        
        cwd = os.getcwd()
        tree = ET.parse(data['config'])
        root = tree.getroot()
        project = root.find('.//project').attrib['dir']
        start = root.find('.//project/versions/start').text
        end = root.find('.//project/versions/end').text
        repo = GitRepoHandler(project) # this must be a git project!
        target = repo.find_commits_between(start, end, False)
        os.chdir(cwd)
        return target
    
    def get_tests(self, data):
        
        if data['CL-params']['--tests']:
            print data['CL-params']['--tests']
            tests = data['CL-params']['--tests'].replace("'", "").replace('\.', '').replace('|', '').split('$')[:-1]
            print tests
            return tests
        target = parser.parse(data['project']+'/benchmarks') # this must be the jmh root dir
        return target
    
    def split(self, data, target):
        
        total_inst = data['total']
        x = len(target)/total_inst
        suite = TestSuite()
        
        for i in range(total_inst-1):
            if x < 1:
                randoms = random.sample(range(len(target)), len(target))
                rand_list = [target[i] for i in randoms]
                suite.append(rand_list)
            else:
                suite.append(target[i*x:(i+1)*x])
        suite.append(target[(total_inst-1)*x:])
        return suite  
    
    def get_suite(self, instance):
        versions = self.get_versions(instance.data)
        versions = self.split(instance.data, versions)
        random.shuffle(versions)
        tests = self.get_tests(instance.data)
        random.shuffle(tests)
        tests = self.split(instance.data, tests)      
        suite = TestSuite()
        suite = suite.nest(versions, tests, instance.data['total'])
        return suite
        
class RandomDistributor(object):
    """Random versions, random tests."""
    def get_versions(self, data):
        
        cwd = os.getcwd()
        tree = ET.parse(data['config'])
        root = tree.getroot()
        project = root.find('.//project').attrib['dir']
        start = root.find('.//project/versions/start').text
        end = root.find('.//project/versions/end').text
        repo = GitRepoHandler(project) # this must be a git project!
        target = repo.find_commits_between(start, end, False)
        os.chdir(cwd)
        return target
    
    def get_tests(self, data):
        
        if data['CL-params']['--tests']:
            tests = data['CL-params']['--tests'].replace("'", "").replace('\.', '').replace('|', '').split('$')[:-1]
            return tests
        target = parser.parse(data['project']+'/benchmarks') # this must be the jmh root dir
        return target
    
    def split(self, data, target):
        
        random.shuffle(target)
        total_inst = data['total']
        x = len(target)/total_inst
        suite = TestSuite(content='random')
        
        for i in range(total_inst-1):
            if x < 1:
                randoms = random.sample(range(len(target)), len(target))
                rand_list = [target[i] for i in randoms]
                suite.append(rand_list)
            else:
                suite.append(target[i*x:(i+1)*x])
        suite.append(target[(total_inst-1)*x:])
        return suite  
    
    def get_suite(self, instance):
        versions = self.get_versions(instance.data)
        versions = self.split(instance.data, versions)
        random.shuffle(versions)
        
        tests = self.get_tests(instance.data)
        random.shuffle(tests)
        tests = self.split(instance.data, tests)      
        suite = TestSuite(content='random')
        suite = suite.nest(versions, tests, instance.data['total'])
        return suite
    
class DefaultDistributor(object):
    """Versions specified in config, all tests"""
    
    def get_versions(self, data):
        
        cwd = os.getcwd()
        tree = ET.parse(data['config'])
        root = tree.getroot()
        project = root.find('.//project').attrib['dir']
        start = root.find('.//project/versions/start').text
        end = root.find('.//project/versions/end').text
        repo = GitRepoHandler(project) # this must be a git project!
        target = repo.find_commits_between(start, end, False)
        os.chdir(cwd)
        suite = TestSuite()
        suite.append(target)
        return suite
    
    def get_suite(self, instance):
        
        total = instance.data['total']
        versions = self.get_versions(instance.data)
        suite = TestSuite()
        suite = suite.nest(total*versions, total*[[None]], total)
        return suite        
    
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
                          "distribution": "VersionTestDistributor",
                          "status-mode": "ALL"
                        }""")
    distributor = Distributor(data, strategy=eval(data['distribution']))
    test_data = distributor.get_suite()
    for item in test_data:
        print item
    
