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
from TestSuite import TestSuite

class Distributor(object):
    
    def __init__(self, data, strategy=None):
        self.action = None
        self.data = data
        self.total = data['total']
        self.project = '/home/selin/Documents/Uni/Bachelorthesis/protostuff'
        if strategy:
            self.action = strategy()
            
    def split(self):
        if(self.action):
            return self.action.split(self)
        else: 
            raise UnboundLocalError('Exception raised, no such strategyClass!')
             
            
class VersionDistributor(object):
    
    def get_target(self, project):
        # TODO: fix method
        cwd = os.getcwd()
        repo = GitRepoHandler(project)
        target = repo.find_commits_between('8924a5f1279a8cfdd845b6012832cfd2cfe32879','4c2ec165c1ae8394188475cc35e83bcc80931745', False)
        os.chdir(cwd)
        return target
    
    def split(self, instance):
        target = self.get_target(instance.project) #instance.data['project']) # this must be a git-project
        
        total_inst = instance.total
        x = len(target)/total_inst
        suite = TestSuite(content = 'version')
        for i in range(total_inst-1):
            if x < 1:
                randoms = random.sample(range(len(target)), len(target))
                rand_list = [target[i] for i in randoms]
                suite.append(rand_list)
                #splitted_test_suite.append(rand_list)
            else:
                suite.append(target[i*x:(i+1)*x])
                #splitted_test_suite.append(target[i*x:(i+1)*x])
        suite.append(target[(total_inst-1)*x:])
        #splitted_test_suite.append(target[(total_inst-1)*x:]) # for last group and if odd number - assign last elements
        suite.randomize()
        #random.shuffle(splitted_test_suite)
        return suite
        #return splitted_test_suite
    
class TestDistributor(object):
    
    def get_target(self, project):
        
        target = parser.parse(project) # project or jmh-dir?
        return target
    
    def split(self, instance):
        
        target = self.get_target(instance.data['project']) # this must be a jmh-project
        random.shuffle(target)
        total_inst = instance.total
        x = len(target)/total_inst
        suite = TestSuite(content='test')
        #splitted_test_suite = []
        
        for i in range(total_inst-1):
            if x < 1:
                randoms = random.sample(range(len(target)), len(target))
                rand_list = [target[i] for i in randoms]
                suite.append(rand_list)
                #splitted_test_suite.append(rand_list)
            else:
                suite.append(target[i*x:(i+1)*x])
                #splitted_test_suite.append(target[i*x:(i+1)*x])
        suite.append(target[(total_inst-1)*x:])
        return suite
        #splitted_test_suite.append(target[(total_inst-1)*x:]) # for last group and if odd number - assign last elements
        #return splitted_test_suite

class VersionTestDistributor(object):
    
    def split(self, instance):
        
        versioner = Distributor(instance.data, strategy = VersionDistributor)
        versions = versioner.split()
        tester = Distributor(instance.data, strategy = TestDistributor)
        tests = tester.split()
        suite = TestSuite(content='versiontest')
        suite = suite.nest(versions, tests, instance.total)

        #tmp = [(v,t) for v,t in zip(versions,tests)]
        #suite.extend(tmp)
        #print type(suite)
        return suite

"""class RandomDistributor(object):
    
    def split(self, instance):
        distributor = Distributor()"""
    
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
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/tests",
                          "distribution": "VersionTestDistributor",
                          "status-mode": "ALL"
                        }""")
    distributor = Distributor(data, strategy=eval(data['distribution']))
    test_data = distributor.split()
    for item in test_data:
        print item
    
