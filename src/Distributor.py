#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 10:14:33 2017

@author: selin
"""

import random
import parser
from MvnCommitWalker import MvnCommitWalker
from MvnVersionWalker import MvnVersionWalker
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
            raise UnboundLocalError('Exception raised, no such strategyClass!')
             
            
class VersionDistributor(object):
    """Version ranges, all tests
        for 3 instances, generates output of format 
            [[[v1],[None]],[[v2],[None]],[[v3],[None]]]"""
            
    def get_target(self, data):
        
        kwargs = {'mode':'commit-mode','skip-noncode':False, 
                  'start':None, 'end':None, 'step':None}
        mapping = {'mode':'--mode', 'skip-noncode':'--skip-noncode',
                   'start':'--from', 'end':'--to', 'step':'--step'}
        for key in mapping.keys():
            try:
                kwargs[key] = data['CL-params'][mapping[key]]
            except KeyError:
                continue
        if data['CL-params'].has_key('-b') and data['CL-params']['-b'] == 'versions':
            backend = MvnVersionWalker(data['CL-params']['-f'])
        else:
            backend = MvnCommitWalker(data['CL-params']['-f'])
        target = backend.generate_version_list(**kwargs)
        return target
    
    def split(self, target, total):
        
        x = len(target)/total
        bigger = len(target)%total
        suite = TestSuite()
        [suite.append(target[i*(x+1):(i+1)*(x+1)]) for i in range(bigger)]
        [suite.append(target[(bigger*(x+1))+i*x:(bigger*(x+1))+(i+1)*x]) for i in range(total - bigger)]
        random.shuffle(suite)
        return suite
    
    def get_suite(self, instance):
        
        suite = TestSuite()
        result = TestSuite()
        total_inst = instance.data['total']
        target = self.get_target(instance.data)
        [target.append(None) for x in range(0, total_inst - len(target))]
        suite = self.split(target, total_inst) 
        result = result.nest(suite, total_inst*[[None]], total_inst)
        return result
    
class RandomVersionDistributor(object):
    """Random versions, all tests."""
    
    def get_target(self, data):
        
        kwargs = {'mode':'commit-mode','skip-noncode':False, 
                  'start':None, 'end':None, 'step':None}
        mapping = {'mode':'--mode', 'skip-noncode':'--skip-noncode',
                   'start':'--from', 'end':'--to', 'step':'--step'}
        for key in mapping.keys():
            try:
                kwargs[key] = data['CL-params'][mapping[key]]
            except KeyError:
                continue
        if data['CL-params'].has_key('-b') and data['CL-params']['-b'] == 'versions':
            backend = MvnVersionWalker(data['CL-params']['-f'])
        else:
            backend = MvnCommitWalker(data['CL-params']['-f'])
        target = backend.generate_version_list(**kwargs)
        return target
    
    def split(self, target, total):
        
        random.shuffle(target)
        x = len(target)/total
        bigger = len(target)%total
        suite = TestSuite()
        [suite.append(target[i*(x+1):(i+1)*(x+1)]) for i in range(bigger)]
        [suite.append(target[(bigger*(x+1))+i*x:(bigger*(x+1))+(i+1)*x]) for i in range(total - bigger)]
        return suite
    
    def get_suite(self, instance):
        suite = TestSuite()
        result = TestSuite(content='random')
        total_inst = instance.data['total']
        target = self.get_target(instance.data)
        [target.append(None) for x in range(0, total_inst - len(target))]
        suite = self.split(target, total_inst)
        result = result.nest(suite, total_inst*[[None]], total_inst)
        return result
        
class TestDistributor(object):
    """All versions, random tests
        for 3 instances, generates output of format 
            [[[None],[t1]],[[None],[t2]],[[None],[t3]]]"""
            
    def get_target(self, data):
        
        if '--tests' in data['CL-params']:
            if data['CL-params']['-t']=='benchmark':
                tests = data['CL-params']['--tests'].replace("$","").replace("'", "").split('|')
            else:
                tests = data['CL-params']['--tests'].replace("'", "").replace(" ","").split(',')
            return tests
        target = parser.parse(data) 
        return target
    
    def split(self, target, total):
        
        random.shuffle(target)
        x = len(target)/total
        bigger = len(target)%total
        suite = TestSuite()
        [suite.append(target[i*(x+1):(i+1)*(x+1)]) for i in range(bigger)]
        [suite.append(target[(bigger*(x+1))+i*x:(bigger*(x+1))+(i+1)*x]) for i in range(total - bigger)]
        return suite
    
    def get_suite(self, instance):
        suite = TestSuite()
        result = TestSuite()
        total_inst = instance.data['total']
        target = self.get_target(instance.data)
        [target.append(None) for x in range(0, total_inst - len(target))]   
        suite = self.split(target, total_inst)
        result = result.nest(total_inst*[[None]], suite, total_inst)
        return result

class RMIT(object):
    """Generate Testsuite according to the RMIT-principle."""
    
    def get_versions(self, data):
        
        kwargs = {'mode':'commit-mode','skip-noncode':False, 
                  'start':None, 'end':None, 'step':None}
        mapping = {'mode':'--mode', 'skip-noncode':'--skip-noncode',
                   'start':'--from', 'end':'--to', 'step':'--step'}
        for key in mapping.keys():
            try:
                kwargs[key] = data['CL-params'][mapping[key]]
            except KeyError:
                continue
        if data['CL-params'].has_key('-b') and data['CL-params']['-b'] == 'versions':
            backend = MvnVersionWalker(data['CL-params']['-f'])
        else:
            backend = MvnCommitWalker(data['CL-params']['-f'])
        target = backend.generate_version_list(**kwargs)
        return target
    
    def get_tests(self, data):
        
        if '--tests' in data['CL-params']:
            if data['CL-params']['-t']=='benchmark':
                tests = data['CL-params']['--tests'].replace("$","").replace("'", "").split('|')
            else:
                tests = data['CL-params']['--tests'].replace("'", "").replace(" ","").split(',')
            return tests
        target = parser.parse(data)
        return target
    
    def split(self, target, total):
        
        random.shuffle(target)
        x = len(target)/total
        bigger = len(target)%total
        suite = TestSuite()
        [suite.append(target[i*(x+1):(i+1)*(x+1)]) for i in range(bigger)]
        [suite.append(target[(bigger*(x+1))+i*x:(bigger*(x+1))+(i+1)*x]) for i in range(total - bigger)]
        return suite  
    
    def get_suite(self, instance):
        versions = self.get_versions(instance.data)
        tests = self.get_tests(instance.data)
        result = TestSuite(content='random')
        tuples = []
        for v in versions:
            [tuples.append([v, t]) for t in tests]
        random.shuffle(tuples)
        total_inst = instance.data['total']
        result = self.split(tuples, total_inst)
        suite = TestSuite(content='random')
        for element in result:
            v =  []
            t = []
            [v.append(item[0]) for item in element]
            [t.append(item[1]) for item in element]
            suite.append([v, t])
        return suite  