#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 17:15:44 2017

@author: selin
"""
import json
import tarfile
import unittest
import os
import shutil
from src.Distributor import (Distributor, VersionDistributor, 
                                 TestDistributor, VersionTestDistributor, 
                                 RandomVersionDistributor, RandomDistributor,
                                 DefaultDistributor)
import re
from os.path import expanduser
from src.Writer import Writer
import xml.etree.ElementTree as ET

class WriterTest(unittest.TestCase):
    data = json.loads("""{
                          "mode": "ip",
                          "total": 1,
                          "ip-list": {
                            "instance-1": "130.211.94.53"
                          },
                          "CL-params": {
                            "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                            "-o": "/home/selin/output/output.csv",
                            "-t": "benchmark",
                            "-b": "versions"
                          },
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/Testing/project",
                          "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                          "distribution": "TestDistributor",
                          "status-mode": "ALL"
                        }""") 
    
    versions = ['8924a5f', 'a16e0bb', '5fa34fc', '01bc2b2', '4a5af86', 
                '5030820', '54af3bd', '8b83879', 'a0b38e6', '49ed34b', 
                '4671f16', '1a2bc6b', '4c9bb60', '66fcce2', '7197210', 
                'c07c69c', '3d28206', '9dbbb11', '55241d1', '96a6b52', 
                '0104f8b', '584f8ff', 'ba4ba7b', '5f06c8a', '919551b', 
                'd872285', 'd4f489e', 'a0a52c4', '015d763', '3942af5', 
                '9ba2008', '115d6bb', '106d277', '98e1f4e', '4623a7d', 
                '699d232', 'f26266f', 'fc5582d', 'f93d597', '18b4f1e', 
                '4c2ec16']
    
    benchmarks = ['baseline', 
                  'runtime_deserialize_1_int_field',
                  'runtime_serialize_1_int_field',
                  'runtime_deserialize_10_int_field',
                  'runtime_serialize_10_int_fields',
                  'runtime_sparse_deserialize_1_int_field',
                  'testBar',
                  'testBaz',
                  'testFoo']
    def test_configwriter_1inst(self):
        
        self.data['total'] = 1
        distributor = Distributor(self.data, strategy=VersionDistributor)
        suite = distributor.get_suite()
        writer = Writer(self.data, content=suite.content)
        config, param = writer.generate_input(suite[0])
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser('~/tmp/config.tar.gz'))
        tar.extractall(path=expanduser('~/tmp/test-config'))
        tar.close()
        os.chdir(expanduser('~/tmp/test-config'))
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        config = os.listdir('.')[0]
        
        tree = ET.parse(config)
        testTree = ET.parse(self.data['config'])
        self.assertNotEqual(tree, testTree)
        root = tree.getroot()
        # adapt start and end tag in config for each instance
        dir = root.find('.//project').attrib['dir'] 
        
        self.assertEqual(expanduser(dir), expanduser('~/tmp/project/protostuff'))
        jmh = root.find('.//project/jmh_root').attrib['dir']
        self.assertEqual(expanduser(jmh), expanduser('~/tmp/project/benchmarks'))
        v1 = root.find('.//project/versions/start').text
        v2 = root.find('.//project/versions/end').text
        self.assertIn(v1, self.versions[0])
        self.assertIn(v2, self.versions[-1])
        os.chdir('..')
        shutil.rmtree(expanduser('~/tmp/test-config'))
        self.assertEqual(param, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser('~/tmp/params.tar.gz'))
        tar.extractall(path=expanduser('~/tmp/test-param'))
        tar.close()
        os.chdir(expanduser('~/tmp/test-param'))
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        param = os.listdir('.')[0]
        with open(param, 'r') as f:
            buf = f.read()
            #print buf
        self.assertNotIn('--tests',buf)
        self.assertIn('-o ~/output/out-1.csv', buf)
        self.assertIn('-f ~/tmp/config/cloud-config-1.xml', buf)
        os.chdir('..')
        shutil.rmtree('./test-param')
    
    def test_configwriter_5inst(self):
        
        self.data['total'] = 5
        distributor = Distributor(self.data, strategy=VersionDistributor)
        versions = distributor.get_suite()
        writer = Writer(self.data, content=versions.content)
        config, param = writer.generate_input(versions[0]) # generate config + param for first instance
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser('./config.tar.gz'))
        tar.extractall(path=expanduser('./test-config'))
        tar.close()
        os.chdir('./test-config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        config = os.listdir('.')[0]
        tree = ET.parse(config)
        testTree = ET.parse(self.data['config'])
        self.assertNotEqual(tree, testTree)
        root = tree.getroot()
        # adapt start and end tag in config for each instance
        dir = root.find('.//project').attrib['dir'] 
        
        self.assertEqual(expanduser(dir), expanduser('~/tmp/project/protostuff'))
        jmh = root.find('.//project/jmh_root').attrib['dir']
        self.assertEqual(expanduser(jmh), expanduser('~/tmp/project/benchmarks'))
        v1 = root.find('.//project/versions/start').text
        v2 = root.find('.//project/versions/end').text
        self.assertIn(v1, [self.versions[0], self.versions[8], self.versions[16], 
                           self.versions[24], self.versions[32]])
        self.assertIn(v2, [self.versions[7], self.versions[15], self.versions[23],
                           self.versions[31], self.versions[-1]])
        os.chdir('..')
        shutil.rmtree(expanduser('~/tmp/test-config'))
        self.assertEqual(param, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser('~/tmp/params.tar.gz'))
        tar.extractall(path=expanduser('~/tmp/test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        param = os.listdir('.')[0]
        with open(param, 'r') as f:
            buf = f.read()
            #print buf
        self.assertNotIn('--tests',buf)
        self.assertIn('-o ~/output/out-1.csv', buf)
        self.assertIn('-f ~/tmp/config/cloud-config-1.xml', buf)
        os.chdir('..')
        shutil.rmtree('./test-param')
        
        
    def test_random_configwriter_5inst(self):
        
        self.data['total'] = 5
        distributor = Distributor(self.data, strategy=RandomVersionDistributor)
        versions = distributor.get_suite()
        writer = Writer(self.data, content=versions.content)
        config, param = writer.generate_input(versions[0]) # generate config + param for first instance
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser('./config.tar.gz'))
        tar.extractall(path=expanduser('./test-config'))
        tar.close()
        os.chdir('./test-config')
        num_files = len([name for name in os.listdir('.')])
        self.assertIn(num_files, [8, 9])
        #print os.listdir('.')
        config = os.listdir('.')[0]
        
        tree = ET.parse(config)
        testTree = ET.parse(self.data['config'])
        self.assertNotEqual(tree, testTree)
        root = tree.getroot()
        # adapt start and end tag in config for each instance
        dir = root.find('.//project').attrib['dir'] 
        
        self.assertEqual(expanduser(dir), expanduser('~/tmp/project/protostuff'))
        jmh = root.find('.//project/jmh_root').attrib['dir']
        self.assertEqual(expanduser(jmh), expanduser('~/tmp/project/benchmarks'))
        v11 = root.find('.//project/versions/start').text
        v12 = root.find('.//project/versions/end').text
        self.assertEqual(v11, v12)
        config = os.listdir('.')[1]
        
        tree = ET.parse(config)
        root = tree.getroot()
        v21 = root.find('.//project/versions/start').text
        v22 = root.find('.//project/versions/end').text
        self.assertEqual(v21, v22)
        self.assertNotEqual(v11, v21)
        self.assertNotEqual(v12, v22)
        os.chdir('..')
        shutil.rmtree('./test-config')
        self.assertEqual(param, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser('./params.tar.gz'))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertIn(num_files, [8,9])
        param = os.listdir('.')[0]
        with open('cl-params-1.txt', 'r') as f:
            buf = f.read()
            #print buf
        self.assertNotIn('--tests',buf)
        self.assertIn('-o ~/output/out-1.csv', buf)
        self.assertIn('-f ~/tmp/config/cloud-config-1.xml', buf)
        os.chdir('..')
        shutil.rmtree('./test-param')
        
    # TestDistributor
    def test_paramwriter(self):
        self.data['total'] = 1
        distributor = Distributor(self.data, strategy=TestDistributor)
        suite = distributor.get_suite()
        writer = Writer(self.data, content=suite.content)
        config, param = writer.generate_input(suite[0])
        
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser('./config.tar.gz'))
        tar.extractall(path=expanduser('./test-config'))
        tar.close()
        os.chdir('./test-config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        config = os.listdir('.')[0]
        
        tree = ET.parse(config)
        testTree = ET.parse(self.data['config'])
        self.assertNotEqual(tree, testTree)
        root = tree.getroot()
        # adapt start and end tag in config for each instance
        dir = root.find('.//project').attrib['dir'] 
        
        self.assertEqual(expanduser(dir), expanduser('~/tmp/project/protostuff'))
        jmh = root.find('.//project/jmh_root').attrib['dir']
        self.assertEqual(expanduser(jmh), expanduser('~/tmp/project/benchmarks'))
        v1 = root.find('.//project/versions/start').text
        v2 = root.find('.//project/versions/end').text
        self.assertIn(v1, self.versions[0])
        self.assertIn(v2, self.versions[-1])
        os.chdir('..')
        shutil.rmtree('./test-config')
        
        self.assertEqual(param, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser('./params.tar.gz'))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        param = os.listdir('.')[0]
        with open(param, 'r') as f:
            buf = f.read()
            print buf
        test_pattern = re.compile(".*--tests \'(\..*$|)*\..*$\'") # TODO: check regex
        match = re.search(test_pattern, buf)
        #print match.groups()
        self.assertIn('--tests',buf)
        #self.assertIsNotNone(match)
        self.assertIn('-o ~/output/out-1.csv', buf)
        self.assertIn('-f ~/tmp/config/cloud-config-1.xml', buf)
        os.chdir('..')
        shutil.rmtree('./test-param')

class RandomWriterTest(unittest.TestCase):
    data = json.loads("""{
                          "mode": "ip",
                          "total": 1,
                          "ip-list": {
                            "instance-1": "130.211.94.53"
                          },
                          "CL-params": {
                            "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                            "-o": "/home/selin/output/output.csv",
                            "-t": "benchmark",
                            "-b": "versions"
                          },
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/Testing/project",
                          "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                          "distribution": "TestDistributor",
                          "status-mode": "ALL"
                        }""") 
    
    versions = ['8924a5f', 'a16e0bb', '5fa34fc', '01bc2b2', '4a5af86', 
                '5030820', '54af3bd', '8b83879', 'a0b38e6', '49ed34b', 
                '4671f16', '1a2bc6b', '4c9bb60', '66fcce2', '7197210', 
                'c07c69c', '3d28206', '9dbbb11', '55241d1', '96a6b52', 
                '0104f8b', '584f8ff', 'ba4ba7b', '5f06c8a', '919551b', 
                'd872285', 'd4f489e', 'a0a52c4', '015d763', '3942af5', 
                '9ba2008', '115d6bb', '106d277', '98e1f4e', '4623a7d', 
                '699d232', 'f26266f', 'fc5582d', 'f93d597', '18b4f1e', 
                '4c2ec16']
    
    benchmarks = ['baseline', 
                  'runtime_deserialize_1_int_field',
                  'runtime_serialize_1_int_field',
                  'runtime_deserialize_10_int_field',
                  'runtime_serialize_10_int_fields',
                  'runtime_sparse_deserialize_1_int_field',
                  'testBar',
                  'testBaz',
                  'testFoo']
    
    # Version ranges, random tests
    def test_version_testwriter(self): 
        self.data['total'] = 2
        distributor = Distributor(self.data, strategy=VersionTestDistributor)
        suite = distributor.get_suite()
        writer = Writer(self.data, content=suite.content)
        config, param = writer.generate_input(suite[0])
        
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser('./config.tar.gz'))
        tar.extractall(path=expanduser('./test-config'))
        tar.close()
        os.chdir('./test-config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        config = os.listdir('.')[0]
        
        tree = ET.parse(config)
        testTree = ET.parse(self.data['config'])
        self.assertNotEqual(tree, testTree)
        root = tree.getroot()
        # adapt start and end tag in config for each instance
        dir = root.find('.//project').attrib['dir'] 
        
        self.assertEqual(expanduser(dir), expanduser('~/tmp/project/protostuff'))
        jmh = root.find('.//project/jmh_root').attrib['dir']
        self.assertEqual(expanduser(jmh), expanduser('~/tmp/project/benchmarks'))
        v1 = root.find('.//project/versions/start').text
        v2 = root.find('.//project/versions/end').text
        self.assertIn(v1, [self.versions[0], self.versions[20]])
        self.assertIn(v2, [self.versions[19], self.versions[-1]])
        os.chdir('..')
        shutil.rmtree('./test-config')
        
        self.assertEqual(param, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser('./params.tar.gz'))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        param = os.listdir('.')[0]
        with open(param, 'r') as f:
            buf = f.read()
        test_pattern = re.compile(".*--tests \'(\..*$|)*\..*$\'") # TODO: check regex
        match = re.search(test_pattern, buf)
        #print match.groups()
        self.assertIn('--tests',buf)
        #self.assertIsNotNone(match)
        self.assertIn('-o ~/output/out-1.csv', buf)
        self.assertIn('-f ~/tmp/config/cloud-config-1.xml', buf)
        os.chdir('..')
        shutil.rmtree('./test-param')
        
    # random versions, random tests
    def test_random_distributor_writer(self): 
        self.data['total'] = 2
        distributor = Distributor(self.data, strategy=RandomDistributor)
        suite = distributor.get_suite()
        writer = Writer(self.data, content=suite.content)
        config, param = writer.generate_input(suite[0])
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser('./config.tar.gz'))
        tar.extractall(path=expanduser('./test-config'))
        tar.close()
        os.chdir('./test-config')
        num_files = len([name for name in os.listdir('.')])
        self.assertIn(num_files, [20,21])
        config = os.listdir('.')[0]
        
        tree = ET.parse(config)
        testTree = ET.parse(self.data['config'])
        self.assertNotEqual(tree, testTree)
        root = tree.getroot()
        # adapt start and end tag in config for each instance
        dir = root.find('.//project').attrib['dir'] 
        
        self.assertEqual(expanduser(dir), expanduser('~/tmp/project/protostuff'))
        jmh = root.find('.//project/jmh_root').attrib['dir']
        self.assertEqual(expanduser(jmh), expanduser('~/tmp/project/benchmarks'))
        v11 = root.find('.//project/versions/start').text
        v12 = root.find('.//project/versions/end').text
        self.assertEqual(v11, v12)
        config = os.listdir('.')[1]
        
        tree = ET.parse(config)
        root = tree.getroot()
        v21 = root.find('.//project/versions/start').text
        v22 = root.find('.//project/versions/end').text
        self.assertEqual(v21, v22)
        self.assertNotEqual(v11, v21)
        self.assertNotEqual(v12, v22)
        os.chdir('..')
        shutil.rmtree('./test-config')
        
        self.assertEqual(param, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser('./params.tar.gz'))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertIn(num_files, [20, 21])
        with open('./cl-params-1.txt', 'r') as f:
            buf = f.read()
        test_pattern = re.compile(".*--tests \'(\..*$|)*\..*$\'") # TODO: check regex
        match = re.search(test_pattern, buf)
        #print match.groups()
        self.assertIn('--tests',buf)
        #self.assertIsNotNone(match)
        self.assertIn('-o ~/output/out-1.csv', buf)
        self.assertIn('-f ~/tmp/config/cloud-config-1.xml', buf)
        os.chdir('..')
        shutil.rmtree('./test-param')
        
    # whole version range (no randomization), all tests
    def test_default(self):
        self.data['total'] = 2
        distributor = Distributor(self.data, strategy=DefaultDistributor)
        suite = distributor.get_suite()
        writer = Writer(self.data, content=suite.content)
        config, param = writer.generate_input(suite[0])
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser('./config.tar.gz'))
        tar.extractall(path=expanduser('./test-config'))
        tar.close()
        os.chdir('./test-config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEqual(num_files, 1)
        tree = ET.parse(os.listdir('.')[0])
        testTree = ET.parse(self.data['config'])
        self.assertNotEqual(tree, testTree)
        root = tree.getroot()
        # adapt start and end tag in config for each instance
        dir = root.find('.//project').attrib['dir'] 
        
        self.assertEqual(expanduser(dir), expanduser('~/tmp/project/protostuff'))
        jmh = root.find('.//project/jmh_root').attrib['dir']
        self.assertEqual(expanduser(jmh), expanduser('~/tmp/project/benchmarks'))
        v1 = root.find('.//project/versions/start').text
        v2 = root.find('.//project/versions/end').text
        self.assertEqual(v1, self.versions[0])
        self.assertEqual(v2, self.versions[-1])
        os.chdir('..')
        shutil.rmtree('./test-config')
        tar = tarfile.open(expanduser('./params.tar.gz'))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        param = os.listdir('.')[0]
        with open(param, 'r') as f:
            buf = f.read()
            #print buf
        self.assertNotIn('--tests',buf)
        self.assertIn('-f ~/tmp/config/cloud-config-1.xml', buf)
        os.chdir('..')
        shutil.rmtree('./test-param')
        
        config, param = writer.generate_input(suite[1])
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser('./config.tar.gz'))
        tar.extractall(path=expanduser('./test-config'))
        tar.close()
        os.chdir('./test-config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEqual(num_files, 1)
        tree = ET.parse(os.listdir('.')[0])
        testTree = ET.parse(self.data['config'])
        self.assertNotEqual(tree, testTree)
        root = tree.getroot()
        # adapt start and end tag in config for each instance
        dir = root.find('.//project').attrib['dir'] 
        
        self.assertEqual(expanduser(dir), expanduser('~/tmp/project/protostuff'))
        jmh = root.find('.//project/jmh_root').attrib['dir']
        self.assertEqual(expanduser(jmh), expanduser('~/tmp/project/benchmarks'))
        v3 = root.find('.//project/versions/start').text
        v4 = root.find('.//project/versions/end').text
        self.assertEqual(v3, self.versions[0])
        self.assertEqual(v4, self.versions[-1])
        self.assertEqual(v1, v3)
        self.assertEqual(v2, v4)
        os.chdir('..')
        shutil.rmtree('./test-config')
        tar = tarfile.open(expanduser('./params.tar.gz'))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        param = os.listdir('.')[0]
        with open(param, 'r') as f:
            buf2 = f.read()
            #print buf2
        self.assertNotIn('--tests',buf2)
        self.assertIn('-f ~/tmp/config/cloud-config-1.xml', buf2)
        self.assertEqual(buf, buf2)
        os.chdir('..')
        shutil.rmtree('./test-param')

if __name__ == '__main__':
    try:
        os.mkdir(expanduser('~/tmp'))
    except OSError:
        pass
    suite = unittest.TestLoader().loadTestsFromTestCase(WriterTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(RandomWriterTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    shutil.rmtree(expanduser('~/tmp'))