#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 15:15:42 2017

@author: selin
"""
import src.clopper as cm
import unittest
import json
import os
        
     
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
                         "--cloud": "/home/selin/storage-credentials.json clopper-storage"
                      },
                      "project": "/home/selin/Documents/Uni/Bachelorthesis/project",
                      "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                      "distribution": "VersionDistributor",
                      "ssh-key":"/home/selin/ssh-key",
                      "username":"selin",
                      "setup":"False",
                      "bucket-name":"clopper-storage",
                      "credentials":"/home/selin/storage-credentials.json"
                      }"""
    
    def test_parse_json(self):
        data = json.loads(self.data)
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        test_data = cm.parse_json(config)
        self.assertEqual(data, test_data)
        
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
                        "-b": "commits",
                        "--cloud": "/home/selin/storage-credentials.json clopper-storage"
                      },
                      "project": "/home/selin/Documents/Uni/Bachelorthesis/project",
                      "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                      "distribution": "VersionDistributor",
                      "setup":"False",
                      "ssh-key":"api-file"
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
    
    def test_cloud_splitted(self):
        data = json.loads(self.data)
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))  
        test_data = cm.parse_json(config)
        self.assertNotIn('credentials', data)
        self.assertNotIn('bucket-name', data)
        self.assertIn('credentials', test_data)
        self.assertEquals(test_data['credentials'], "/home/selin/storage-credentials.json")
        self.assertIn('bucket-name', test_data)
        self.assertEquals(test_data['bucket-name'], 'clopper-storage')
        
    def test_cloud_splitted2(self):
        data = json.loads(self.data)
        data['CL-params']['--cloud']="clopper-storage /home/selin/storage-credentials.json"
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))  
        test_data = cm.parse_json(config)
        self.assertNotIn('credentials', data)
        self.assertNotIn('bucket-name', data)
        self.assertIn('credentials', test_data)
        self.assertEquals(test_data['credentials'], "/home/selin/storage-credentials.json")
        self.assertIn('bucket-name', test_data)
        self.assertEquals(test_data['bucket-name'], 'clopper-storage')            
    def test_no_total(self):
        data = json.loads(self.data)
        del data['total']
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(ValueError):
            cm.parse_json(config)
            
    def test_no_key_file(self):
        data = json.loads(self.data)
        del data['ssh-key']
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
                        "-b": "commits",
                        "--cloud": "/home/selin/storage-credentials.json clopper-storage"
                      },
                      "project": "/home/selin/Documents/Uni/Bachelorthesis/project",
                      "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                      "distribution": "VersionDistributor",
                      "setup":"True",
                      "ssh-key":"key-file"
                      }"""
                      
        
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
    
    def test_invalid_creds(self):
        data = json.loads(self.data)
        data['CL-params']['--cloud'] = 'foo.json clopper-storage'
        config = "./test-config.json"
        with open(config, 'w') as conf:
            conf.write(json.dumps(data))      
        with self.assertRaises(IOError):
            cm.parse_json(config)
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CloudManagerTestTwo)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(CloudManagerTestThree)
    unittest.TextTestRunner(verbosity=5).run(suite)    
    suite = unittest.TestLoader().loadTestsFromTestCase(CloudManagerTestFour)
    unittest.TextTestRunner(verbosity=5).run(suite)
    os.remove('./test-config.json')