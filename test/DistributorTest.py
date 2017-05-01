#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 17:16:12 2017

@author: selin
"""
import json
import unittest
from src.Distributor import (Distributor, VersionDistributor, 
                                 TestDistributor, VersionTestDistributor, 
                                 RandomVersionDistributor, RandomDistributor, 
                                 DefaultDistributor)
from src.TestSuite import TestSuite

class DistributorTest (unittest.TestCase):
    data = json.loads("""{
                          "mode": "ip",
                          "total": 1,
                          "ip-list": {
                            "instance-1": "130.211.94.53"
                          },
                          "CL-params": {
                            "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                            "-o": "./output.csv",
                            "-t": "benchmark",
                            "-b": "versions"
                          },
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/Testing/project",
                          "config": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml",
                          "distribution": "VersionDistributor",
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
    
    expected = [[['8924a5f', 'a16e0bb', '5fa34fc'], ['baseline', 'runtime_deserialize_1_int_field', 'runtime_serialize_1_int_field']], 
        [['8924a5f', 'a16e0bb', '5fa34fc'], ['baseline', 'runtime_deserialize_1_int_field', 'runtime_serialize_1_int_field']], 
        [['8924a5f', 'a16e0bb', '5fa34fc'], ['baseline', 'runtime_deserialize_1_int_field', 'runtime_serialize_1_int_field']]]
    

    def test_strategy(self):
        pass
    
    def test_distributor_properties(self):
        versiondistributor = Distributor(self.data, strategy = VersionDistributor)
        self.assertEqual(versiondistributor.data, self.data)
        testdistributor = Distributor(self.data, strategy = TestDistributor)
        self.assertEqual(testdistributor.data, self.data)
        unidistributor = Distributor(self.data, strategy = VersionTestDistributor)
        self.assertEqual(unidistributor.data, self.data)
        
    def test_TestSuite(self):
        
        suite = TestSuite(content='test')
        seq1 = 3*[self.versions[:3]]
        seq2 = 3*[self.benchmarks[:3]]
        suite = suite.nest(seq1, seq2, 3)
        self.assertEquals(len(suite), 3)
        self.assertEquals(len(suite[0]), 2)
        self.assertEquals(len(suite[1]), 2)
        self.assertEquals(len(suite[2]), 2)
        self.assertEquals(len(suite[0][0]), 3)
        self.assertEquals(len(suite[0][1]), 3)
        self.assertIn(suite[0][0][0], self.versions)
        self.assertIn(suite[0][1][0], self.benchmarks)
        self.assertEquals(suite, self.expected)
        
    #TestDistributor
    def test_split_1inst(self):
        self.data['total'] = 1
        distributor = Distributor(self.data, strategy = TestDistributor)
        test_result = distributor.get_suite()
        self.assertEquals(len(test_result), 1)
        self.assertEquals(len(test_result[0]), 2)
        self.assertEquals(len(test_result[0][0]), 1)
        self.assertItemsEqual(test_result[0][1], self.benchmarks)
       
    def test_split_3inst(self):
        self.data['total'] = 3
        distributor = Distributor(self.data, strategy = TestDistributor)
        test_result = distributor.get_suite()       
        num_items = len(test_result[0][1]) + len(test_result[1][1]) + len(test_result[2][1])
        self.assertEquals(num_items, len(self.benchmarks))
        self.assertEquals(test_result[0][0][0], None)
        self.assertEquals(test_result[1][0][0], None)
        self.assertEquals(test_result[2][0][0], None)
        for item in test_result[0][1]:
            self.assertIn(item, self.benchmarks)
        for item in test_result[1][1]:
            self.assertIn(item, self.benchmarks)
        for item in test_result[2][1]:
            self.assertIn(item, self.benchmarks)
            
    def test_split_5inst(self):
        self.data['total']=5
        distributor = Distributor(self.data, strategy = TestDistributor)
        test_result = distributor.get_suite()
        for item in test_result[0][1]:
            self.assertIn(item, self.benchmarks)
        for item in test_result[1][1]:
            self.assertIn(item, self.benchmarks)
        for item in test_result[2][1]:
            self.assertIn(item, self.benchmarks)
        for item in test_result[3][1]:
            self.assertIn(item, self.benchmarks)
        for item in test_result[4][1]:
            self.assertIn(item, self.benchmarks)
        self.assertEquals(len(test_result), 5)
        self.assertEquals(test_result[0][0][0], None)
        self.assertEquals(test_result[1][0][0], None)
        self.assertEquals(test_result[2][0][0], None)
        self.assertEquals(test_result[3][0][0], None)
        self.assertEquals(test_result[4][0][0], None)
        self.assertGreater(len(test_result[4][1]),len(test_result[0][1]))     
    
    #VersionDistributor
    def test_split_shuffled_1inst(self):
        self.data['total'] = 1
        distributor = Distributor(self.data, strategy = VersionDistributor)
        test_result = distributor.get_suite()
        self.assertEquals(len(test_result), 1)
        self.assertEquals(len(test_result[0]), 2)
        self.assertEquals(len(test_result[0][1]),1)
        self.assertEquals(test_result[0][1][0],None)
        self.assertEqual(test_result[0][0], self.versions)
        self.assertEqual(test_result[0][0][0], self.versions[0])
    
    def test_split_shuffled_3insts(self):
        self.data['total'] = 3
        distributor = Distributor(self.data, strategy = VersionDistributor)
        test_result = distributor.get_suite()
        num_items = len(test_result[0][0]) + len(test_result[1][0]) + len(test_result[2][0])
        self.assertEquals(num_items, len(self.versions))
        self.assertEquals(test_result[0][1][0], None)
        self.assertEquals(test_result[1][1][0], None)
        self.assertEquals(test_result[2][1][0], None)
        for item in test_result[0][0]:
            self.assertIn(item, self.versions)
        for item in test_result[1][0]:
            self.assertIn(item, self.versions)
        for item in test_result[2][0]:
            self.assertIn(item, self.versions)
        #print test_result
        #self.assertGreater(len(test_result[[2][0]]), len(test_result[0][0]))

    def test_split_shuffled_5insts(self):
        self.data['total']=5
        distributor = Distributor(self.data, strategy = VersionDistributor)
        test_result = distributor.get_suite()
        num_items = len(test_result[0][0]) + len(test_result[1][0]) + len(test_result[2][0]) + len(test_result[3][0]) + len(test_result[4][0])
        self.assertEquals(num_items, len(self.versions))
        self.assertEquals(test_result[0][1][0], None)
        self.assertEquals(test_result[1][1][0], None)
        self.assertEquals(test_result[2][1][0], None)
        self.assertEquals(test_result[3][1][0], None)
        self.assertEquals(test_result[4][1][0], None)
        self.assertNotEqual(test_result.content, 'random')
        for item in test_result[0][0]:
            self.assertIn(item, self.versions)
        for item in test_result[1][0]:
            self.assertIn(item, self.versions)
        for item in test_result[2][0]:
            self.assertIn(item, self.versions)
        for item in test_result[3][0]:
            self.assertIn(item, self.versions)
        for item in test_result[4][0]:
            self.assertIn(item, self.versions)
        self.assertEquals(len(test_result), 5)
        #self.assertGreater(len(test_result[-1]),len(test_result[0]))
    
    #RandomVersionDistributor
    def test_random_version_distributor_1inst(self):
        self.data['total'] = 1
        distributor = Distributor(self.data, strategy = RandomVersionDistributor)
        test_result = distributor.get_suite()
        self.assertEquals(test_result.content, 'random')
        self.assertEquals(len(test_result), 1)
        self.assertEquals(len(test_result[0]), 2)
        self.assertEquals(len(test_result[0][1]),1)
        self.assertEquals(test_result[0][1][0], None)
        for item in test_result[0][0]:
            self.assertIn(item, self.versions)
        self.assertNotEqual(test_result[0][0][0], self.versions[0])
        
    def test_random_version_distributor_2inst(self):
        self.data['total'] = 2
        distributor = Distributor(self.data, strategy = RandomVersionDistributor)
        test_result = distributor.get_suite()
        self.assertEquals(test_result.content, 'random')
        self.assertEquals(len(test_result), 2)
        self.assertEquals(len(test_result[0]), 2)
        self.assertEquals(len(test_result[1]), 2)
        self.assertEquals(len(test_result[0][1]),1)
        self.assertEquals(len(test_result[1][1]),1)
        self.assertEquals(test_result[0][1][0], None)
        self.assertEquals(test_result[1][1][0], None)
        self.assertItemsEqual(test_result[0][0]+test_result[1][0], self.versions)
        self.assertNotEqual(test_result[0][0][0], self.versions[0])
        self.assertNotEqual(test_result[1][0][0], self.versions[0])
    
    #VersionTestDistributor
    def test_version_test_distributor_1inst(self):
        self.data['total'] = 1
        distributor = Distributor(self.data, strategy = VersionTestDistributor)
        test_result = distributor.get_suite()
        self.assertNotEqual(test_result.content, 'random')
        self.assertEquals(len(test_result), 1)
        self.assertEquals(len(test_result[0]), 2)
        self.assertEquals(test_result[0][0],self.versions)
        self.assertNotEqual(test_result[0][1], self.benchmarks)
        self.assertItemsEqual(test_result[0][1], self.benchmarks)
        
    def test_version_test_distributor_2inst(self):
        self.data['total'] = 2
        distributor = Distributor(self.data, strategy = VersionTestDistributor)
        test_result = distributor.get_suite()
        self.assertNotEqual(test_result.content, 'random')
        self.assertEquals(len(test_result), 2)
        self.assertEquals(len(test_result[0]), 2)
        self.assertEquals(len(test_result[1]), 2)
        self.assertIn(test_result[0][0],[self.versions[:20],self.versions[20:]])
        self.assertIn(test_result[1][0],[self.versions[:20],self.versions[20:]])
        self.assertNotEqual(test_result[0][1] + test_result[1][1], self.benchmarks)
        self.assertNotEqual(test_result[1][1], self.benchmarks)
        self.assertItemsEqual(test_result[0][1]+test_result[1][1], self.benchmarks)
    
    #RandomDistributor
    def test_allrandom_1inst(self):
        self.data['total'] = 1
        distributor = Distributor(self.data, strategy = RandomDistributor)
        test_result = distributor.get_suite()
        self.assertEquals(len(test_result), 1)
        self.assertEquals(len(test_result[0]), 2)
        self.assertNotEquals(test_result[0][0][0], None)
        self.assertNotEquals(test_result[0][1][0], None)
        for item in test_result[0][0]:
            self.assertIn(item, self.versions)
        for item in test_result[0][1]:
            self.assertIn(item, self.benchmarks)
        self.assertNotEqual(test_result[0][0][0], self.versions[0])
        
    def test_allrandom_2inst(self):
        self.data['total'] = 2
        distributor = Distributor(self.data, strategy = RandomDistributor)
        test_result = distributor.get_suite()
        self.assertEquals(len(test_result), 2)
        self.assertEquals(len(test_result[0]), 2)
        self.assertEquals(len(test_result[1]), 2)
        self.assertNotEquals(test_result[0][0][0], None)
        self.assertNotEquals(test_result[0][1][0], None)
        self.assertNotEquals(test_result[1][0][0], None)
        self.assertNotEquals(test_result[1][1][0], None)
        self.assertItemsEqual(test_result[0][0]+test_result[1][0], self.versions)
        self.assertItemsEqual(test_result[0][1]+test_result[1][1], self.benchmarks)
        
    #DefaultDistributor
    def test_default_1inst(self):
        self.data['total'] = 1
        distributor = Distributor(self.data, strategy = DefaultDistributor)
        test_result = distributor.get_suite()
        self.assertNotEquals(test_result.content, 'random')
        self.assertEquals(len(test_result), 1)
        self.assertEquals(len(test_result[0]), 2)
        self.assertEquals(len(test_result[0][0]),len(self.versions))
        self.assertEquals(len(test_result[0][1]),1)
        self.assertEquals(test_result[0][0], self.versions)
        self.assertEquals(test_result[0][1][0], None)
        
    def test_default_2inst(self):
        self.data['total'] = 2
        distributor = Distributor(self.data, strategy = DefaultDistributor)
        test_result = distributor.get_suite()
        self.assertNotEquals(test_result.content, 'random')
        self.assertEquals(len(test_result), 2)
        self.assertEquals(len(test_result[0]), 2)
        self.assertEquals(len(test_result[1]), 2)
        self.assertEquals(len(test_result[0][0]),len(self.versions))
        self.assertEquals(len(test_result[0][1]),1)
        self.assertEquals(len(test_result[1][0]),len(self.versions))
        self.assertEquals(len(test_result[1][1]),1)
        self.assertEquals(test_result[0][0][0], self.versions[0])
        self.assertEquals(test_result[0][0][-1], self.versions[-1])
        self.assertEquals(test_result[0][1][0], None)
        self.assertEquals(test_result[1][0][0], self.versions[0])
        self.assertEquals(test_result[1][0][-1], self.versions[-1])
        self.assertEquals(test_result[1][1][0], None)

    def test_with_dates(self):
        pass
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(DistributorTest)
    unittest.TextTestRunner(verbosity=5).run(suite)