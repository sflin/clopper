#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 15:15:42 2017

@author: selin
"""
import src.CloudManager as cm
import unittest
import json
import os
import mock

class CloudManagerTestOne(unittest.TestCase):
    data = """{
                      "mode": "ip",
                      "total": 3,
                      "ip-list": {
                        "instance-1": "35.187.117.113",
                        "instance-2": "104.199.99.133",
                        "instance-3": "35.187.174.32"
                      },
                      "CL-params": {
                        "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                        "-o": "./output.csv",
                        "-t": "benchmark",
                        "-b": "commits"
                      },
                      "project": "/home/selin/Documents/Uni/Bachelorthesis/project",
                      "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                      "distribution": "VersionDistributor"
                      }"""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <historian type="MvnCommitWalker">
            <project name="Protostuff" dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/protostuff">
                    <jmh_root dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/benchmarks" />
                    <junit>
                            <execs>1</execs>
                    </junit>
                    <versions>
                            <start>8924a5f</start>
                            <end>01bc2b2</end>
                    </versions>
            </project>
            <jmh_arguments>
                    -f 1 -tu s -bm thrpt -wi 1 -i 1 -r 1
            </jmh_arguments>
    </historian>"""
    
    def setUp(self):
        self.data = json.loads(self.data)
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(self.xml)
        self.data['CL-params']['-f'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['config'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['CL-params']['-b'] = "commits"
        
    def test_get_instances_ip(self):
        nodes = cm.get_instances(self.data)
        self.assertEqual(nodes, self.data['ip-list'])
        
    def simple_boot(data):
        node_dict = {"instance-1": "35.187.117.113","instance-2": "104.199.99.133", "instance-3": "35.187.174.32"}
        return node_dict
        
    @mock.patch('src.CloudManager.boot_nodes', side_effect=simple_boot)
    def test_get_instances_libcloud(self, node_create):
        self.data['mode'] = 'libcloud'
        self.data['user-id'] = u'123'
        self.data['key'] = 'abc'
        self.data['gce-project'] = 'project'
        nodes = cm.get_instances(self.data)
        self.assertEqual(nodes, self.data['ip-list'])
     
class CloudManagerTestTwo(unittest.TestCase):
    data = """{
                      "mode": "ip",
                      "total": 3,
                      "ip-list": {
                        "instance-1": "35.187.117.113",
                        "instance-2": "104.199.99.133",
                        "instance-3": "35.187.174.32"
                      },
                      "CL-params": {
                        "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                        "-o": "./output.csv",
                        "-t": "benchmark",
                        "-b": "commits",
                        "--cloud":"True"
                      },
                      "project": "/home/selin/Documents/Uni/Bachelorthesis/project",
                      "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                      "distribution": "VersionDistributor",
                      "project-id":"bt-sfabel",
                      "username":"selin",
                      "setup":"False"
                      }"""
    
    def test_parse_json(self):
        data = json.loads(self.data)
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        test_data = cm.parse_json(config)
        self.assertEqual(data, test_data)
        
    """def test_libcloud_mode(self):
        data = json.loads(self.data)
        del data['ip-list']
        data['mode'] = 'libcloud'
        data['user-id'] = u'123'
        data['key'] = 'abc'
        data['gce-project'] = 'project'
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        test_data = cm.parse_json(config)
        self.assertEqual(data, test_data)"""
        
class CloudManagerTestThree(unittest.TestCase):
    data = """{
                      "mode": "ip",
                      "total": 3,
                      "ip-list": {
                        "instance-1": "35.187.117.113",
                        "instance-2": "104.199.99.133",
                        "instance-3": "35.187.174.32"
                      },
                      "CL-params": {
                        "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                        "-o": "./output.csv",
                        "-t": "benchmark",
                        "-b": "commits"
                      },
                      "project": "/home/selin/Documents/Uni/Bachelorthesis/project",
                      "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                      "distribution": "VersionDistributor",
                      "project-id":"bt-sfabel"
                      }"""
                      
        
    def test_username_set(self):
        data = json.loads(self.data)
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))  
        test_data = cm.parse_json(config)
        self.assertNotEqual(data, test_data)
        self.assertIn('username', test_data)
        self.assertEquals(test_data['username'], 'selin')
        
    """def test_no_mode(self):
        data = json.loads(self.data)
        del data['mode']
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)"""
            
    def test_no_total(self):
        data = json.loads(self.data)
        del data['total']
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)
            
    def test_no_cl_params(self):
        data = json.loads(self.data)
        del data['CL-params']
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)
            
    def test_no_project(self):
        data = json.loads(self.data)
        del data['project']
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)
            
    def test_no_config(self):
        data = json.loads(self.data)
        del data['CL-params']['-f']
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)
            
    def test_no_distribution(self):
        data = json.loads(self.data)
        del data['distribution']
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)
            
    def test_no_t_flag(self):
        data = json.loads(self.data)
        del data['CL-params']['-t']
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)

    def test_no_ip_list(self):
        data = json.loads(self.data)
        del data['ip-list']
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)
            
    """def test_libcloud_mode_fail(self):
        data = json.loads(self.data)
        data['mode'] = 'libcloud'
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)

    def test_libcloud_mode_fail2(self):
        data = json.loads(self.data)
        data['mode'] = 'libcloud'
        data['user-id'] = '123'
        data['gce-project'] = 'project'
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)
            
    def test_libcloud_mode_fail3(self):
        data = json.loads(self.data)
        data['mode'] = 'libcloud'
        data['key'] = 'abc'
        data['gce-project'] = 'project'
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)"""
            
class CloudManagerTestFour(unittest.TestCase):
    data = """{
                      "mode": "ip",
                      "total": 3,
                      "ip-list": {
                        "instance-1": "35.187.117.113",
                        "instance-2": "104.199.99.133",
                        "instance-3": "35.187.174.32"
                      },
                      "CL-params": {
                        "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                        "-o": "./output.csv",
                        "-t": "benchmark",
                        "-b": "commits"
                      },
                      "project": "/home/selin/Documents/Uni/Bachelorthesis/project",
                      "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                      "distribution": "VersionDistributor",
                      "project-id":"bt-sfabel"
                      }"""
                      
    def test_no_project_id(self):
        data = json.loads(self.data)
        del data['project-id']
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))  
        with self.assertRaises(ValueError):
            cm.parse_json(config)
        
    def test_invalid_distribution(self):
        data = json.loads(self.data)
        data['distribution'] = 'foo'
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)

    def test_invalid_config(self):
        data = json.loads(self.data)
        data['CL-params']['-f'] = 'foo'
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(IOError):
            cm.parse_json(config) 
            
    def test_invalid_project(self):
        data = json.loads(self.data)
        data['project'] = 'foo'
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(IOError):
            cm.parse_json(config)
            
    def test_invalid_t_flag(self):
        data = json.loads(self.data)
        data['CL-params']['-t'] = 'foo'
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)

    def test_invalid_b_flag(self):
        data = json.loads(self.data)
        data['CL-params']['-b'] = 'foo'
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)

    """def test_invalid_mode(self):
        data = json.loads(self.data)
        data['mode'] = 'foo'
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)  """ 
            
if __name__ == '__main__':
    #suite = unittest.TestLoader().loadTestsFromTestCase(CloudManagerTestOne)
    #unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(CloudManagerTestTwo)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(CloudManagerTestThree)
    unittest.TextTestRunner(verbosity=5).run(suite)    
    suite = unittest.TestLoader().loadTestsFromTestCase(CloudManagerTestFour)
    unittest.TextTestRunner(verbosity=5).run(suite)
    os.remove('./test-config.json')