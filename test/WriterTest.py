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
from os.path import expanduser
from src.Writer import Writer
import xml.etree.ElementTree as ET

class WriterTest(unittest.TestCase):
    data = """{"CL-params": {
                            "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                            "-o": "/home/selin/output/output.csv",
                            "-t": "benchmark",
                            "--cloud": "/home/selin/storage-credentials.json clopper-storage"
                          },
                "credentials": "/home/selin/storage-credentials.json",
                "bucket-name": "clopper-storage",
                "distribution":"TestDistributor"
                }"""
    mapping = ['-b', '-r','--from','--to', '--step','-i', '--tests', 
                   '--mode', '--skip-noncode','--build-type'] 
    def test_eval_input(self):
        data = json.loads(self.data)
        writer = Writer(data, content = 'random')
        answer = writer.eval_input()
        self.assertTrue(answer)
        writer = Writer(data, content = '')
        answer = writer.eval_input()
        self.assertFalse(answer)
        
    def test_get_current_params_simple(self):
        data = json.loads(self.data)
        writer = Writer(data, content = '')
        test_dict = writer.get_current_params()
        self.assertEqual(test_dict['-t'], data['CL-params']['-t'])
        self.assertEqual(test_dict['-o'], '~/tmp/out.csv')
        self.assertEqual(test_dict['-f'], data['CL-params']['-f'])
        self.assertEqual(test_dict['--cloud'], "~/storage-credentials.json clopper-storage")
        [self.assertNotIn(item, test_dict) for item in self.mapping]
        
    def test_get_current_params_extended(self):
        data = json.loads(self.data)
        for item in self.mapping:
            data['CL-params'][item] = 'foo'
        writer = Writer(data, content = '')
        test_dict = writer.get_current_params()
        self.assertEqual(test_dict['-t'], data['CL-params']['-t'])
        self.assertEqual(test_dict['-o'], '~/tmp/out.csv')
        self.assertEqual(test_dict['-f'], data['CL-params']['-f'])
        [self.assertEqual(test_dict[item], 'foo') for item in self.mapping]
        
class ParamWriterTest(unittest.TestCase):
    data = """{"CL-params": {
                            "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                            "-o": "/home/selin/output/output.csv",
                            "-t": "benchmark",
                            "--cloud": "/home/selin/storage-credentials.json clopper-storage"
                          },
                "credentials": "/home/selin/storage-credentials.json",
                "bucket-name": "clopper-storage",
                "distribution":"VersionDistributor"
                }"""

    def setUp(self):
        try:
            os.mkdir(expanduser('~/tmp'))
        except OSError:
            pass
        
    def tearDown(self):
        shutil.rmtree(expanduser('~/tmp'))
    def test_get_parameters(self):
        data = json.loads(self.data)
        writer = Writer(data, content = '')
        suite = [None]
        test_params = writer.get_parameters(suite)
        self.assertEqual(test_params, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser(test_params))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        param = os.listdir('.')[0]
        self.assertEqual(param, 'cl-params-1.txt')
        with open(param, 'r') as f:
            buf = f.read()
        self.assertNotIn('--tests', buf)
        self.assertIn('-o ~/tmp/out.csv', buf)
        self.assertIn('-f ~/tmp/config/cloud-config-1.xml', buf)
        self.assertIn('--cloud ~/storage-credentials.json clopper-storage', buf)
        self.assertNotEqual(data['CL-params']['-f'], '~/tmp/config/cloud-config-1.xml')
        
    def test_get_parameters2(self):
        data = json.loads(self.data)
        data['CL-params']['--tests'] = 'foo'
        writer = Writer(data, content = '')
        test_params = writer.get_parameters([None])
        self.assertEqual(test_params, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser(test_params))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        param = os.listdir('.')[0]
        self.assertEqual(param, 'cl-params-1.txt')
        with open(param, 'r') as f:
            buf = f.read()
        self.assertIn('--tests foo', buf)
        self.assertIn('-o ~/tmp/out.csv', buf)
        self.assertIn('-f ~/tmp/config/cloud-config-1.xml', buf)
        self.assertIn('--cloud ~/storage-credentials.json clopper-storage', buf)

    def test_get_parameters3(self):
        data = json.loads(self.data)
        data['CL-params']['--tests'] = 'duck'
        writer = Writer(data, content = '')
        test_params = writer.get_parameters(['foo','bar','baz'])
        self.assertEqual(test_params, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser(test_params))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        param = os.listdir('.')[0]
        self.assertEqual(param, 'cl-params-1.txt')
        with open(param, 'r') as f:
            buf = f.read()
        self.assertIn("--tests 'foo$|bar$|baz$'", buf)
        self.assertIn('-o ~/tmp/out.csv', buf)
        self.assertIn('-f ~/tmp/config/cloud-config-1.xml', buf)
        self.assertIn('--cloud ~/storage-credentials.json clopper-storage', buf)
        self.assertNotIn("--tests duck", buf)
        
    def test_get_parameters4(self):
        data = json.loads(self.data)
        writer = Writer(data, content = '')
        test_params = writer.get_parameters(['foo','bar','baz'])
        self.assertEqual(test_params, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser(test_params))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        param = os.listdir('.')[0]
        self.assertEqual(param, 'cl-params-1.txt')
        with open(param, 'r') as f:
            buf = f.read()
        self.assertIn("--tests 'foo$|bar$|baz$'", buf)
        self.assertIn('-o ~/tmp/out.csv', buf)
        self.assertIn('-f ~/tmp/config/cloud-config-1.xml', buf)
        self.assertIn('--cloud ~/storage-credentials.json clopper-storage', buf)
    
    def test_get_parameters5(self):
        data = json.loads(self.data)
        writer = Writer(data, content = '')
        writer.num = 3
        test_params = writer.get_parameters([None])
        self.assertEqual(test_params, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser(test_params))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        files = os.listdir('.')
        self.assertItemsEqual(files, ['cl-params-1.txt','cl-params-2.txt','cl-params-3.txt'])
         
class MvnCommitsWriterTest(unittest.TestCase):
    data = json.loads("""{
                          "CL-params": {
                            "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                            "-t": "benchmark",
                            "--cloud": "/home/selin/storage-credentials.json clopper-storage"
                          },
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/Testing/project",
                          "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                          "username":"selin",
                            "credentials": "/home/selin/storage-credentials.json",
                            "bucket-name": "clopper-storage",
                "distribution":"VersionDistributor"
                        }""") 
    
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <historian type="MvnCommitWalker">
            <project name="Protostuff" dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/protostuff">
                    <jmh_root dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/benchmarks" />
                    <junit>
                            <execs>1</execs>
                    </junit>
                    <versions>
                            <start>8924a5f</start>
                            <end>4c2ec16</end>
                    </versions>
            </project>
            <jmh_arguments>
                    -f 1 -tu s -bm thrpt -wi 1 -i 1 -r 1
            </jmh_arguments>
    </historian>"""
    
    def setUp(self):
        try:
            os.mkdir(expanduser('~/tmp'))
        except OSError:
            pass
        try:
            os.mkdir(expanduser('~/tmp/config'))
        except OSError:
           pass
        os.chdir(expanduser('~/tmp/config'))
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(self.xml)
        self.data['CL-params']['-f'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['config'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        
    def tearDown(self):
        shutil.rmtree(expanduser('~/tmp'))
    
    def test_config(self):
        writer = Writer(self.data, content='')
        writer.get_config([None],1)
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        config = os.listdir('.')[0]
        self.assertEqual(config, 'cloud-config-1.xml')
        tree = ET.parse(config)
        testTree = ET.parse(self.data['CL-params']['-f'])
        self.assertNotEqual(tree, testTree)
        root = tree.getroot()
        dir = root.find('.//project').attrib['dir'] 
        self.assertEqual(expanduser(dir), '/home/selin/tmp/project/protostuff')
        jmh = root.find('.//project/jmh_root').attrib['dir']
        self.assertEqual(expanduser(jmh), '/home/selin/tmp/project/benchmarks')
        v1 = root.find('.//project/versions/start').text
        v2 = root.find('.//project/versions/end').text
        self.assertIn(v1, '8924a5f')
        self.assertIn(v2, '4c2ec16')
        self.assertEqual(self.data['CL-params']['-f'],"/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml")
        
    def test_config2(self):
        writer = Writer(self.data, content='')
        writer.get_config(['a16e0bb', '5fa34fc', '01bc2b2', '4a5af86', 
                '5030820', '54af3bd', '8b83879'],1)
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        config = os.listdir('.')[0]
        self.assertEqual(config, 'cloud-config-1.xml')
        tree = ET.parse(config)
        testTree = ET.parse(self.data['CL-params']['-f'])
        self.assertNotEqual(tree, testTree)
        root = tree.getroot()
        dir = root.find('.//project').attrib['dir'] 
        self.assertEqual(expanduser(dir), '/home/selin/tmp/project/protostuff')
        jmh = root.find('.//project/jmh_root').attrib['dir']
        self.assertEqual(expanduser(jmh), '/home/selin/tmp/project/benchmarks')
        v1 = root.find('.//project/versions/start').text
        v2 = root.find('.//project/versions/end').text
        self.assertIn(v1, 'a16e0bb')
        self.assertIn(v2, '8b83879')
        
    def test_config3(self):
        writer = Writer(self.data, content='')
        writer.get_config([None],3)
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        config = os.listdir('.')[0]
        self.assertEqual(config, 'cloud-config-3.xml')
        
    def test_get_multi_configs(self):
        writer = Writer(self.data, content='random')
        config = writer.get_multi_configs(['a16e0bb', '5fa34fc', '01bc2b2', '4a5af86', 
                '5030820', '54af3bd', '8b83879'])
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser(config))
        tar.extractall(path=expanduser('./config'))
        tar.close()
        os.chdir('./config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 7)
        
    def test_get_multi_configs2(self):
        writer = Writer(self.data, content='')
        config = writer.get_multi_configs(['a16e0bb', '5fa34fc', '01bc2b2', '4a5af86', 
                '5030820', '54af3bd', '8b83879'])
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser(config))
        tar.extractall(path=expanduser('./config'))
        tar.close()
        os.chdir('./config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        
        
class MvnVersionWriterTest(unittest.TestCase):
    data = json.loads("""{
                          "CL-params": {
                            "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/version-test-conf.xml",
                            "-b": "versions",
                            "-t": "benchmark"
                          },
                          "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/version-test-conf.xml",
                          "project-id":"bt-sfabel",
                          "username":"selin",
                "distribution":"VersionDistributor"
                        }""") 
    
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <historian type="MvnVersionWalker">

        <project name="Log4j2" group="org.apache.logging.log4j" module="log4j">
                <jmh_root dir="/home/selin/Documents/Uni/Bachelorthesis/project/benchmarks" />
                <junit_root dir="/home/selin/Documents/Uni/Bachelorthesis/project/benchmarks" />
                <versions>
                        <version>2.0</version>
                        <version>2.0.1</version>
			<version>3.0</version>
                        <version>5.0.1</version>
			<version>6.0</version>
                        <version>7.0.1</version>
                </versions>
        </project>
        <jmh_arguments>
            -f 1 -tu s -bm thrpt -wi 1 -i 1 -r 1
        </jmh_arguments>
    </historian>"""
    
    def setUp(self):
        try:
            os.mkdir(expanduser('~/tmp'))
        except OSError:
            pass
        try:
            os.mkdir(expanduser('~/tmp/config'))
        except OSError:
           pass
        os.chdir(expanduser('~/tmp/config'))
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(self.xml)
        self.data['CL-params']['-f'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['config'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        
    def tearDown(self):
        shutil.rmtree(expanduser('~/tmp'))
        
    def test_config(self):
        writer = Writer(self.data, content='')
        writer.get_version_config([None])
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        config = os.listdir('.')[0]
        self.assertEqual(config, 'cloud-config-1.xml')
        tree = ET.parse(config)
        testTree = ET.parse(self.data['CL-params']['-f'])
        self.assertNotEqual(tree, testTree)
        root = tree.getroot()
        jmh = root.find('.//project/jmh_root').attrib['dir']
        self.assertEqual(jmh, '/home/selin/tmp/project/benchmarks')
        versions = []
        for item in root.iter():
            if item.tag == 'version':
                versions.append(item.text)
        self.assertEquals(versions, ['2.0', '2.0.1','3.0', '5.0.1','6.0','7.0.1'])
        
    def test_config2(self):
        writer = Writer(self.data, content='')
        writer.get_version_config(['2.4', '3.4','5.0'])
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        config = os.listdir('.')[0]
        self.assertEqual(config, 'cloud-config-1.xml')
        tree = ET.parse(config)
        testTree = ET.parse(self.data['CL-params']['-f'])
        self.assertNotEqual(tree, testTree)
        root = tree.getroot()
        jmh = root.find('.//project/jmh_root').attrib['dir']
        self.assertEqual(expanduser(jmh), '/home/selin/tmp/project/benchmarks')
        versions = []
        for item in root.iter():
            if item.tag == 'version':
                versions.append(item.text)
        self.assertEquals(versions, ['2.4', '3.4','5.0'])    
        
    def test_get_multi_configs(self):
        writer = Writer(self.data, content='')
        config = writer.get_multi_configs([None])
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser(config))
        tar.extractall(path=expanduser('./config'))
        tar.close()
        os.chdir('./config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        param = os.listdir('.')[0]
        self.assertEqual(param, 'cloud-config-1.xml')
        
class WriterTestAll(unittest.TestCase):
    data = json.loads("""{
                          "CL-params": {
                            "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                            "-o": "/home/selin/output/output.csv",
                            "-t": "benchmark"
                          },
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/Testing/project",
                          "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                          "project-id":"bt-sfabel",
                            "credentials": "/home/selin/storage-credentials.json",
                            "bucket-name": "clopper-storage",
                          "username":"selin",
                "distribution":"VersionDistributor"
                        }""") 
    
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <historian type="MvnCommitWalker">
            <project name="Protostuff" dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/protostuff">
                    <jmh_root dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/benchmarks" />
                    <junit>
                            <execs>1</execs>
                    </junit>
                    <versions>
                            <start>8924a5f</start>
                            <end>4c2ec16</end>
                    </versions>
            </project>
            <jmh_arguments>
                    -f 1 -tu s -bm thrpt -wi 1 -i 1 -r 1
            </jmh_arguments>
    </historian>"""
    
    def setUp(self):
        try:
            os.mkdir(expanduser('~/tmp'))
        except OSError:
            pass
        try:
            os.mkdir(expanduser('~/tmp/config'))
        except OSError:
           pass
        os.chdir(expanduser('~/tmp/config'))
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(self.xml)
        self.data['CL-params']['-f'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['config'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        
    def tearDown(self):
        shutil.rmtree(expanduser('~/tmp')) 
        
    def test_generate_input(self):
        writer = Writer(self.data, content='')
        config, param = writer.generate_input([['a16e0bb', '5fa34fc', '01bc2b2', '4a5af86', 
                '5030820', '54af3bd', '8b83879'],[None]])
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser(config))
        tar.extractall(path=expanduser('./config'))
        tar.close()
        os.chdir('./config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        self.assertEqual(param, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser(param))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        self.assertEqual(os.listdir('.')[0], 'cl-params-1.txt')
        
    def test_generate_input2(self):
        writer = Writer(self.data, content='random')
        config, param = writer.generate_input([['a16e0bb', '5fa34fc', '01bc2b2', '4a5af86', 
                '5030820', '54af3bd', '8b83879'],[None]])
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser(config))
        tar.extractall(path=expanduser('./config'))
        tar.close()
        os.chdir('./config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 7)
        self.assertEqual(param, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser(param))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 7)
        
    def test_generate_input3(self):
        writer = Writer(self.data, content='')
        config, param = writer.generate_input([[None],['foo','bar','baz']])
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser(config))
        tar.extractall(path=expanduser('./config'))
        tar.close()
        os.chdir('./config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        self.assertEqual(param, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser(param))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        self.assertEqual(os.listdir('.')[0], 'cl-params-1.txt')
        
    def test_generate_input4(self):
        writer = Writer(self.data, content='')
        config, param = writer.generate_input([['a16e0bb', '5fa34fc', '01bc2b2', '4a5af86', 
                '5030820', '54af3bd', '8b83879'],['foo','bar','baz']])
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser(config))
        tar.extractall(path=expanduser('./config'))
        tar.close()
        os.chdir('./config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        self.assertEqual(param, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser(param))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 1)
        self.assertEqual(os.listdir('.')[0], 'cl-params-1.txt')
        
    def test_generate_input5(self):
        writer = Writer(self.data, content='random')
        config, param = writer.generate_input([['a16e0bb', '5fa34fc', '01bc2b2', '4a5af86', 
                '5030820', '54af3bd', '8b83879'],['foo','bar','baz']])
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser(config))
        tar.extractall(path=expanduser('./config'))
        tar.close()
        os.chdir('./config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 7)
        self.assertEqual(param, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser(param))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 7)
        
class RMITWriter(unittest.TestCase):
    data = json.loads("""{
                          "CL-params": {
                            "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                            "-o": "/home/selin/output/output.csv",
                            "-t": "benchmark"
                          },
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/Testing/project",
                          "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                          "project-id":"bt-sfabel",
                            "credentials": "/home/selin/storage-credentials.json",
                            "bucket-name": "clopper-storage",
                          "username":"selin",
                "distribution":"RMIT"
                        }""") 
    
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <historian type="MvnCommitWalker">
            <project name="Protostuff" dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/protostuff">
                    <jmh_root dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/benchmarks" />
                    <junit>
                            <execs>1</execs>
                    </junit>
                    <versions>
                            <start>8924a5f</start>
                            <end>4c2ec16</end>
                    </versions>
            </project>
            <jmh_arguments>
                    -f 1 -tu s -bm thrpt -wi 1 -i 1 -r 1
            </jmh_arguments>
    </historian>"""
    
    def setUp(self):
        try:
            os.mkdir(expanduser('~/tmp'))
        except OSError:
            pass
        try:
            os.mkdir(expanduser('~/tmp/config'))
        except OSError:
           pass
        os.chdir(expanduser('~/tmp/config'))
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(self.xml)
        self.data['CL-params']['-f'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['config'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        
    def tearDown(self):
        shutil.rmtree(expanduser('~/tmp')) 
        
    def test_generate_input(self):
        writer = Writer(self.data, content='random')
        config, param = writer.generate_input([['5fa34fc', 'a16e0bb','8924a5f'], 
                                                ['abc', 'abc', 'xyz']])
        self.assertEqual(config, expanduser('~/tmp/config.tar.gz'))
        tar = tarfile.open(expanduser(config))
        tar.extractall(path=expanduser('./config'))
        tar.close()
        os.chdir('./config')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 3)
        self.assertEqual(param, expanduser('~/tmp/params.tar.gz'))
        tar = tarfile.open(expanduser(param))
        tar.extractall(path=expanduser('./test-param'))
        tar.close()
        os.chdir('./test-param')
        num_files = len([name for name in os.listdir('.')])
        self.assertEquals(num_files, 3)
        self.assertItemsEqual(os.listdir('.'), ['cl-params-1.txt','cl-params-2.txt','cl-params-3.txt'])
        with open('cl-params-2.txt', 'r') as f:
            buf = f.read()
        self.assertIn("--tests 'abc$'", buf)
        self.assertIn('-o ~/tmp/out.csv', buf)
        self.assertIn('-f ~/tmp/config/cloud-config-2.xml', buf)
        self.assertIn('--cloud ~/storage-credentials.json clopper-storage', buf)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(WriterTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(ParamWriterTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(MvnCommitsWriterTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(MvnVersionWriterTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(WriterTestAll)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(RMITWriter)
    unittest.TextTestRunner(verbosity=5).run(suite)