#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 15:15:42 2017

@author: selin
"""
from src import CloudManager as cm
import unittest
import json
import os

class CloudManagerTestOne(unittest.TestCase):
    data = json.loads("""{
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
                      "status-mode": "ALL"
                      }""")
    
    def test_get_instances_ip(self):
        nodes = cm.get_instances(self.data)
        self.assertEqual(nodes, self.data['ip-list'])

    """def test_create_GCE_driver(self):
        pass
    
    def test_remote_hopper(self):
        pass
    
    def test_get_instances_libcloud(self):
        data = self.data
        data['mode'] = 'libcloud'
        data['user-id'] = u'123'
        data['key'] = 'abc'
        data['gce-project'] = 'project'
        nodes = cm.get_instances(self.data)
        self.assertEqual(nodes, self.data['ip-list'])
        del data['user-id']
        del data['key']
        del data['gce-project']
        data['mode'] = 'ip'"""       
        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CloudManagerTestOne)
    unittest.TextTestRunner(verbosity=5).run(suite)
