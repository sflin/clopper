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
    
    def __init__(self, data, strategy=None):
        self.action = None
        self.data = data
        if strategy:
            self.action = strategy()
            
    def split(self):
        pass
            
    def get_suite(self):
        
        if(self.action):
            return self.action.get_suite(self)
        else:
            #suite = [(None, None) for in range(self.data['total'])]
            #return suite
            raise UnboundLocalError('Exception raised, no such strategyClass!')
             
            
class VersionDistributor(object):
    """Version range, all tests"""
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
    
    def split(self, instance):
        
        target = self.get_target(instance.data)
        total_inst = instance.data['total']
        x = len(target)/total_inst
        suite = TestSuite(content = 'version')
        for i in range(total_inst-1):
            if x < 1:
                randoms = random.sample(range(len(target)), len(target))
                rand_list = [target[i] for i in randoms]
                suite.append(rand_list)
            else:
                suite.append(target[i*x:(i+1)*x])
        suite.append(target[(total_inst-1)*x:]) # for last group and if odd number - assign last elements
        suite.randomize()
        return suite
    
    def get_suite(self, instance):
        
        suite = TestSuite()
        total_inst = instance.data['total']
        suite = self.split()
        suite = suite.nest(suite, total_inst*[None], total_inst)
        return suite
        
class TestDistributor(object):
    """All versions, random tests"""
    def get_target(self, project):
        
        target = parser.parse(project)
        return target
    
    def split(self, instance):
        
        target = self.get_target(instance.data['project']+'/benchmarks') # this must be the jmh root dir
        random.shuffle(target)
        total_inst = instance.data['total']
        x = len(target)/total_inst
        suite = TestSuite(content='test')
        
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
        suite = self.split()
        suite = suite.nest(total_inst*[None], suite, total_inst)
        return suite

class VersionTestDistributor(object):
    """Version ranges, random tests"""
    
    def split(self, instance):
        
        versioner = Distributor(instance.data, strategy = VersionDistributor)
        versions = versioner.split()
        tester = Distributor(instance.data, strategy = TestDistributor)
        tests = tester.split()
        return versions, tests    
    
    def get_suite(self, instance):
        
        suite = TestSuite(content='versiontest')
        versions, tests = self.split()
        suite = suite.nest(versions, tests, instance.data['total'])
        return suite
        
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
    
    def split(self, instance):
        
        target = self.get_target(instance.data)
        random.shuffle(target)
        total_inst = instance.data['total']
        x = len(target)/total_inst
        suite = TestSuite(content='test')
        
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
        suite = self.split()
        suite = suite.nest(suite, total_inst*[None], total_inst)
        return suite        
    
class RandomDistributor(object):
    """Random versions, random tests."""
    
    def split(self, instance):
        
        versioner = Distributor(instance.data, strategy = RandomVersionDistributor)
        versions = versioner.split()
        tester = Distributor(instance.data, strategy = TestDistributor)
        tests = tester.split()
        return versions, tests    
    
    def get_suite(self, instance):
        
        suite = TestSuite(content='versiontest')
        versions, tests = self.split()
        suite = suite.nest(versions, tests, instance.data['total'])
        return suite
    
class DefaultDistributor(object):
    """Versions specified in config, all tests"""
    
    def split(self, instance):
        
        total = instance.data['total']
        suite = TestSuite(content='default')
        suite = suite.nest(total*[None], total*[None], total)
        return suite

    def get_suite(self, instance):
        total = instance.data['total']
        suite = TestSuite(content='default')
        suite = suite.nest(total*[None], total*[None], total)
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
                            "-b": "versions"
                          },
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/project",
                          "config": "/home/selin/Documents/Uni/Bachelorthesis/clopper/config.xml",
                          "distribution": "TestDistributor",
                          "status-mode": "ALL"
                        }""")
    distributor = Distributor(data, strategy=eval(data['distribution']))
    test_data = distributor.get_suite()
    for item in test_data:
        print item
    
