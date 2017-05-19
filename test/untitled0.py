#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 18 23:05:28 2017

@author: selin
"""
import json
import unittest
from src.Distributor import (Distributor, VersionDistributor, 
                                 TestDistributor, VersionTestDistributor, 
                                 RandomVersionDistributor, RandomDistributor)
from src.TestSuite import TestSuite
from src.GitRepoHandler import GitRepoHandler
import os
import re

def parse(data):
    project = data['project']
    type = data['CL-params']['-t']
    test_list = []
    annot_pat = re.compile('@Benchmark$') if type == 'benchmark' else re.compile('@Test$')
    name_pat = re.compile('public .* (.*)\(')

    for subdir, dirs, files in os.walk(project):
        for file in files:
            filepath = subdir + os.sep + file
            with open(filepath, 'r') as f:
                for line in f:
                    # loop over each line of file and look for @Benchmark or @Test or test.*()
                    if re.search(annot_pat, line):
                        # get name
                        searching = True
                        while searching:
                            line = f.next()
                            if re.search(name_pat, line):
                                test_name = re.search(name_pat, line)
                                test_list.append(test_name.group(1))
                                searching = False
    return list(set(test_list))

 
def test_get_target():
    print 'silverflash:'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/silverflash')
    #versions = gh.find_commits_between('10ecd2b','d4526d5', True)
    #print 'versions:' + str(len(versions))
    print 'versions: 46'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/silverflash', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    print '\nm3:'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/m3')
    #versions = gh.find_commits_between('f11d415','d552ea2', True)
    #print 'versions:' + str(len(versions))
    print 'versions: 15'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/m3', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    
    print '\nprotostuff'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/project/protostuff')
    #versions = gh.find_commits_between('70278ed','c31c7dd', True)
    #print 'versions:' + str(len(versions))
    print 'versions: 1041'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/project/benchmarks', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    
    print '\nlog4j'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/log4j/project/log4j')
    #versions = gh.find_commits_between('9b3631b','c5f4279', True)
    #print 'versions:' + str(len(versions))
    print 'versions: 10'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/log4j/project/benchmarks', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    
    print '\nChronicle-Wire'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/Chronicle-Wire')
    #versions = gh.find_commits_between('e96e16f','ad5adc9', True)
    #print 'versions:' + str(len(versions))
    print 'versions: 1354'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/Chronicle-Wire', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    
    print '\nJava-tdd-katas'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/java-tdd-katas')
    #versions = gh.find_commits_between('04cd3d7','7a89541', True)
    #print 'versions:' + str(len(versions))
    print 'versions: 77'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/java-tdd-katas', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    
    print '\nthread-local'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/threadlocal-benchmark')
    versions = gh.find_commits_between('d2e46d6','a23da7e', True)
    #print 'versions:' + str(len(versions))
    print 'versions: 25'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/threadlocal-benchmark', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    
    print '\nJCTOOLSproject'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/JCTOOLSproject')
    #versions = gh.find_commits_between('24b515b','39904a9', True)
    #print 'versions:' + str(len(versions))
    print 'versions: 49'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/JCTOOLSproject', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    
    print '\nrut'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/rut')
    versions = gh.find_commits_between('02416d4','4c14d2f', True)
    print 'versions:' + str(len(versions))
    #print 'versions: 25'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/rut', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    print '\ncqengine-query-jmh'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/cqengine-query-jmh')
    versions = gh.find_commits_between('16ddad3','5e00d98', True)
    print 'versions:' + str(len(versions))
    #print 'versions: 25'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/cqengine-query-jmh', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    
    print '\nhazelcast-jmh'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/hazelcast-jmh')
    #versions = gh.find_commits_between('ca69254','a809ec2', True)
    #print 'versions:' + str(len(versions))
    print 'versions: 17'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/hazelcast-jmh', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(list)
    print len(set(list))
    
    print '\njbrotli'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/jbrotli')
    #versions = gh.find_commits_between('7488a73','0c81163', True)
    #print 'versions:' + str(len(versions))
    print 'versions: 91'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/jbrotli', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    
    print '\nYANG-promotion'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/YANG-promotion')
    #versions = gh.find_commits_between('375157a','8e08bc6', True)
    #print 'versions:' + str(len(versions))
    print 'versions: 5'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/YANG-promotion', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    
    print '\nbrave'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/brave')
    #versions = gh.find_commits_between('61fc9b8','7f521a9', True)
    #print 'versions:' + str(len(versions))
    print 'versions: 416'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/brave', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    
    print '\nrdf4j'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/rdf4j')
    versions = gh.find_commits_between('0aa98bd','e1427f2', True)
    print 'versions:' + str(len(versions))
    #print 'versions: 25'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/rdf4j', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    
    print '\nexternal-okhttp'
    gh = GitRepoHandler('/home/selin/Documents/Uni/Bachelorthesis/eval-projects/external_okhttp')
    versions = gh.find_commits_between('c3f6f16','f38272f', True)
    print 'versions:' + str(len(versions))
    #print 'versions: 25'
    data={'project':'/home/selin/Documents/Uni/Bachelorthesis/eval-projects/external_okhttp', 'CL-params':{'-t':'benchmark'}}
    list = parse(data)
    print 'tests:'+ str(len(list))
    print len(set(list))
    
        
if __name__ == '__main__':
    test_get_target()