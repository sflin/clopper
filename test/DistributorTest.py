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
                                 RandomVersionDistributor, RandomDistributor)
from src.TestSuite import TestSuite

class TestSuiteTest (unittest.TestCase):
    data = json.loads("""{"CL-params": { "-t": "benchmark"},
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/Testing/project"
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
    
    benchmarks = ['baseline', 'runtime_deserialize_1_int_field',
                  'runtime_serialize_1_int_field', 
                  'runtime_deserialize_10_int_field',
                  'runtime_serialize_10_int_fields',
                  'runtime_sparse_deserialize_1_int_field',
                  'testBar', 'testBaz', 'testFoo']
    
    expected = [[['8924a5f', 'a16e0bb', '5fa34fc'], ['baseline', 'runtime_deserialize_1_int_field', 'runtime_serialize_1_int_field']], 
        [['8924a5f', 'a16e0bb', '5fa34fc'], ['baseline', 'runtime_deserialize_1_int_field', 'runtime_serialize_1_int_field']], 
        [['8924a5f', 'a16e0bb', '5fa34fc'], ['baseline', 'runtime_deserialize_1_int_field', 'runtime_serialize_1_int_field']]]
    
    def test_distributor_properties(self):
        versiondistributor = Distributor(self.data, strategy = VersionDistributor)
        self.assertEqual(versiondistributor.data, self.data)
        testdistributor = Distributor(self.data, strategy = TestDistributor)
        self.assertEqual(testdistributor.data, self.data)
        unidistributor = Distributor(self.data, strategy = VersionTestDistributor)
        self.assertEqual(unidistributor.data, self.data)
        unidistributor = Distributor(self.data, strategy = RandomVersionDistributor)
        self.assertEqual(unidistributor.data, self.data)
        unidistributor = Distributor(self.data, strategy = RandomDistributor)
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
    
class VersionDistributorTest (unittest.TestCase):
    data = json.loads("""{"CL-params": {"-t": "benchmark"},
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/Testing/project"
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
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(self.xml)
        self.data['CL-params']['-f'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['config'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['CL-params']['-b'] = "commits"
    
    #VersionDistributor 
    def test_get_target(self):
        versioner = VersionDistributor()
        test_versions = versioner.get_target(self.data)
        self.assertEquals(self.versions, test_versions)
        
    def test_shuffle_split(self):
        tester = VersionDistributor()
        splits = [1,2,3,4,5,6,7,8,9]
        test_suite = tester.split(splits, 1)
        self.assertItemsEqual(test_suite, [splits])
        test_suite = tester.split(splits, 2)
        self.assertEquals(len(test_suite), 2)
        self.assertIn(len(test_suite[0]), [4,5])
        self.assertItemsEqual(test_suite, [splits[:5], splits[5:]])
        self.assertIn(test_suite[1], [splits[:5], splits[5:]])
        test_suite = tester.split(splits, 5)
        self.assertEquals(len(test_suite), 5)
        self.assertIn(len(test_suite[0]), [1,2])
        test_suite = tester.split(splits[:5], 5)
        self.assertEquals(len(test_suite), 5)
        self.assertEquals(len(test_suite[0]), 1)
        self.assertItemsEqual(test_suite, [[splits[0]], [splits[1]],
                                               [splits[2]], [splits[3]],
                                               [splits[4]]])
        test_suite = tester.split(splits[:3], 5)
        self.assertItemsEqual(test_suite, [[1],[2],[3],[],[]])
        
        
    def test_get_suite_1inst(self):
        self.data['total'] = 1
        distributor = Distributor(self.data, strategy = VersionDistributor)
        test_result = distributor.get_suite()
        self.assertEquals(len(test_result), 1)
        self.assertEquals(len(test_result[0]), 2)
        self.assertItemsEqual(test_result, [[self.versions, [None]]])
        self.assertEquals(len(test_result[0][1]),1)
        self.assertEquals(test_result[0][1][0],None)
        self.assertEqual(test_result[0][0], self.versions)
        self.assertEqual(test_result[0][0][0], self.versions[0])
    
    def test_get_suite_3insts(self):
        self.data['total'] = 3
        distributor = Distributor(self.data, strategy = VersionDistributor)
        test_result = distributor.get_suite()
        num_items = len(test_result[0][0]) + len(test_result[1][0]) + len(test_result[2][0])
        self.assertEquals(num_items, len(self.versions))
        self.assertEquals(test_result[0][1][0], None)
        self.assertEquals(test_result[1][1][0], None)
        self.assertEquals(test_result[2][1][0], None)
        self.assertItemsEqual(test_result, [[self.versions[:14], [None]], [self.versions[14:28], [None]],
                                         [self.versions[28:], [None]]])

    def test_get_suite_5insts(self):
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
        self.assertItemsEqual(test_result, [[self.versions[:9], [None]], [self.versions[9:17], [None]],
                                         [self.versions[17:25], [None]], [self.versions[25:33], [None]],
                                         [self.versions[33:], [None]]])
        self.assertEquals(len(test_result), 5)
        
    def test_get_suite_50insts(self):
        self.data['total']=50
        distributor = Distributor(self.data, strategy = VersionDistributor)
        test_result = distributor.get_suite()
        for x in range(0, 50):
            self.assertEquals(test_result[x][1][0], None)
        self.assertNotEqual(test_result.content, 'random')
        expected = []
        [expected.append([[item], [None]]) for item in self.versions]
        [expected.append([[None],[None]]) for i in range(9)]
        self.assertItemsEqual(test_result, expected)
        self.assertEquals(len(test_result), 50)
        

class RandomVersionDistributorTest (unittest.TestCase):
    data = json.loads("""{"CL-params": {"-t": "benchmark"},
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/Testing/project"
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
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(self.xml)
        self.data['CL-params']['-f'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['config'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['CL-params']['-b'] = "commits"
    
    #RandomVersionDistributor 
    def test_get_target(self):
        versioner = RandomVersionDistributor()
        test_versions = versioner.get_target(self.data)
        self.assertItemsEqual(self.versions, test_versions)
        
    def test_split_shuffle(self):
        tester = RandomVersionDistributor()
        splits = [1,2,3,4,5,6,7,8,9]
        test_suite = tester.split(splits, 1)
        self.assertItemsEqual(test_suite, [splits])
        test_suite = tester.split(splits, 2)
        self.assertEquals(len(test_suite), 2)
        self.assertIn(len(test_suite[0]), [4,5])
        self.assertItemsEqual(test_suite, [splits[:5], splits[5:]])
        self.assertIn(test_suite[1], [splits[:5], splits[5:]])
        test_suite = tester.split(splits, 5)
        self.assertEquals(len(test_suite), 5)
        [self.assertEqual(len(test_suite[i]), 2) for i in range(4)]
        self.assertEqual(len(test_suite[-1]), 1)
        test_suite = tester.split(splits[:5], 5)
        self.assertEquals(len(test_suite), 5)
        self.assertEquals(len(test_suite[0]), 1)
        self.assertItemsEqual(test_suite, [[splits[0]], [splits[1]],
                                               [splits[2]], [splits[3]],
                                               [splits[4]]])
        test_suite = tester.split([1,2,3], 5)
        self.assertItemsEqual(test_suite, [[1],[2],[3],[],[]])

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

    def test_get_suite_3insts(self):
        self.data['total'] = 3
        distributor = Distributor(self.data, strategy = RandomVersionDistributor)
        test_result = distributor.get_suite()
        self.assertEquals(test_result.content, 'random')
        num_items = len(test_result[0][0]) + len(test_result[1][0]) + len(test_result[2][0])
        self.assertEquals(num_items, len(self.versions))
        self.assertEquals(test_result[0][1][0], None)
        self.assertEquals(test_result[1][1][0], None)
        self.assertEquals(test_result[2][1][0], None)
        self.assertNotEquals(test_result, [[self.versions[:13], [None]], [self.versions[13:26], [None]],
                                         [self.versions[26:], [None]]])

    def test_get_suite_5insts(self):
        self.data['total']=5
        distributor = Distributor(self.data, strategy = RandomVersionDistributor)
        test_result = distributor.get_suite()
        num_items = len(test_result[0][0]) + len(test_result[1][0]) + len(test_result[2][0]) + len(test_result[3][0]) + len(test_result[4][0])
        self.assertEquals(num_items, len(self.versions))
        self.assertEquals(test_result[0][1][0], None)
        self.assertEquals(test_result[1][1][0], None)
        self.assertEquals(test_result[2][1][0], None)
        self.assertEquals(test_result[3][1][0], None)
        self.assertEquals(test_result[4][1][0], None)
        self.assertEquals(test_result.content, 'random')
        self.assertNotEquals(test_result, [[self.versions[:8], [None]], [self.versions[8:16], [None]],
                                         [self.versions[16:24], [None]], [self.versions[24:32], [None]],
                                         [self.versions[32:], [None]]])
        self.assertEquals(len(test_result), 5)
        
    def test_get_suite_50insts(self):
        self.data['total']=50
        distributor = Distributor(self.data, strategy = RandomVersionDistributor)
        test_result = distributor.get_suite()
        for x in range(0, 50):
            self.assertEquals(test_result[x][1][0], None)
        self.assertEquals(test_result.content, 'random')
        expected = []
        [expected.append([[item], [None]]) for item in self.versions]
        [expected.append([[None],[None]]) for i in range(9)]
        self.assertItemsEqual(test_result, expected)
        self.assertEquals(len(test_result), 50)
    
class TestDistributorTest (unittest.TestCase):
    data = json.loads("""{"CL-params": {"-t": "benchmark"}
                        }""")
    
    benchmarks = ['baseline', 
                  'runtime_deserialize_1_int_field',
                  'runtime_serialize_1_int_field',
                  'runtime_deserialize_10_int_field',
                  'runtime_serialize_10_int_fields',
                  'runtime_sparse_deserialize_1_int_field',
                  'testBar',
                  'testBaz',
                  'testFoo']
        
    #TestDistributor
    def test_get_target_tests(self):
        tester = TestDistributor()
        tests = tester.get_target(self.data)
        self.assertItemsEqual(self.benchmarks, tests)
        
    def test_get_target_tests2(self):
        self.data['CL-params']['--tests'] = "'.*\\.runtime_sparse_deserialize_1_int_field$|.*\\.baseline$|.*\\.runtime_serialize_10_int_fields$'"
        tester = TestDistributor()
        tests = tester.get_target(self.data)
        self.assertItemsEqual(['runtime_sparse_deserialize_1_int_field','baseline','runtime_serialize_10_int_fields'], tests)
        del self.data['CL-params']['--tests']
        
    def test_split_shuffle(self):
        tester = TestDistributor()
        splits = [1,2,3,4,5,6,7,8,9]
        test_suite = tester.split(splits, 1)
        self.assertItemsEqual(test_suite, [splits])
        test_suite = tester.split(splits, 2)
        self.assertEquals(len(test_suite), 2)
        self.assertIn(len(test_suite[0]), [4,5])
        self.assertItemsEqual(test_suite, [splits[:5], splits[5:]])
        self.assertIn(test_suite[1], [splits[:5], splits[5:]])
        test_suite = tester.split(splits, 5)
        self.assertEquals(len(test_suite), 5)
        self.assertEqual(len(test_suite[0]), 2)
        self.assertEqual(len(test_suite[-1]), 1)
        test_suite = tester.split(splits[:5], 5)
        self.assertEquals(len(test_suite), 5)
        self.assertEquals(len(test_suite[0]), 1)
        self.assertItemsEqual(test_suite, [[splits[0]],[splits[1]],[splits[2]],
                                           [splits[3]],[splits[4]]])
        test_suite = tester.split(splits[:3], 5)
        self.assertItemsEqual(test_suite[-1], [])
        
    def test_get_target_unit(self):
        self.data['CL-params']['--tests'] = "'runtime_sparse_deserialize_1_int_field,baseline,runtime_serialize_10_int_fields'"
        self.data['CL-params']['-t'] = 'unit'
        tester = TestDistributor()
        tests = tester.get_target(self.data)
        self.assertEquals(tests, ['runtime_sparse_deserialize_1_int_field','baseline','runtime_serialize_10_int_fields'] )
        del self.data['CL-params']['--tests']
        self.data['CL-params']['-t'] = 'benchmark'
    
    def test_get_target_unit2(self):
        self.data['CL-params']['-t'] = 'unit'
        self.data['project']="/home/selin/Documents/Uni/Bachelorthesis/Testing/project"
        tester = TestDistributor()
        tests = tester.get_target(self.data)
        self.assertEquals(tests,  ['testWriteNumericEnum','testSerializeDeserializeNumericEnum','testWriteStringEnum','testEmptyFieldsPojo','testComplexFieldsPojo'])
        self.data['CL-params']['-t'] = 'benchmark'
        
    def test_get_suite_1inst(self):
        self.data['total'] = 1
        self.data['project'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/project"
        distributor = Distributor(self.data, strategy = TestDistributor)
        test_result = distributor.get_suite()
        self.assertEquals(len(test_result), 1)
        self.assertEquals(len(test_result[0]), 2)
        self.assertEquals(len(test_result[0][0]), 1)
        self.assertItemsEqual(test_result[0][1], self.benchmarks)
        
    def test_get_suite_3inst(self):
        self.data['total'] = 3
        self.data['project'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/project"
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
            
    def test_get_suite_5inst(self):
        self.data['total']=5
        self.data['project'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/project"
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
        self.assertGreater(len(test_result[0][1]),len(test_result[4][1]))
    
    def test_get_suite_11insts(self):
        self.data['total']=11
        self.data['project'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/project"
        distributor = Distributor(self.data, strategy = TestDistributor)
        test_result = distributor.get_suite()
        for x in range(0, 11):
            self.assertEquals(test_result[x][0][0], None)
        expected = []
        [expected.append([[None], [item]]) for item in self.benchmarks]
        [expected.append([[None],[None]]) for i in range(2)]
        self.assertItemsEqual(test_result, expected)
        self.assertEquals(len(test_result), 11)
        
class VersionTestDistributorTest (unittest.TestCase):
    data = json.loads("""{"CL-params": {"-t": "benchmark"},
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/Testing/project"
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
    
    benchmarks = ['baseline', 
                  'runtime_deserialize_1_int_field',
                  'runtime_serialize_1_int_field',
                  'runtime_deserialize_10_int_field',
                  'runtime_serialize_10_int_fields',
                  'runtime_sparse_deserialize_1_int_field',
                  'testBar',
                  'testBaz',
                  'testFoo'] 
    
    def setUp(self):
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(self.xml)
        self.data['CL-params']['-f'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['config'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['CL-params']['-b'] = "commits"
    
    def test_split(self):
        tester = VersionTestDistributor()
        splits = [1,2,3,4,5,6,7,8,9]
        test_suite = tester.split(splits, 1)
        
        self.assertItemsEqual(test_suite, [splits])
        test_suite = tester.split(splits, 2)
        self.assertEquals(len(test_suite), 2)
        self.assertIn(len(test_suite[0]), [4,5])
        self.assertEquals(test_suite, [splits[:5], splits[5:]])
        
        test_suite = tester.split(splits, 5)
        self.assertEquals(len(test_suite), 5)
        self.assertEquals(test_suite, [[1,2],[3,4],[5,6],[7,8],[9]])
        
        test_suite = tester.split(splits[:5], 5)
        self.assertEquals(len(test_suite), 5)
        self.assertEquals(len(test_suite[0]), 1)
        self.assertItemsEqual(test_suite, [[1],[2],[3],[4],[5]])
        test_suite = tester.split(splits[:3], 5)
        self.assertItemsEqual(test_suite, [[1],[2],[3],[],[]])
        
    def test_get_target(self):
        versioner = VersionTestDistributor()
        test_versions = versioner.get_versions(self.data)
        self.assertEquals(self.versions, test_versions)
        
    def test_get_target_tests(self):
        tester = VersionTestDistributor()
        tests = tester.get_tests(self.data)
        self.assertItemsEqual(self.benchmarks, tests)
        
    def test_get_target_tests2(self):
        self.data['CL-params']['--tests'] = "'.*\\.runtime_sparse_deserialize_1_int_field$|.*\\.baseline$|.*\\.runtime_serialize_10_int_fields$'"
        tester = VersionTestDistributor()
        tests = tester.get_tests(self.data)
        self.assertItemsEqual(['runtime_sparse_deserialize_1_int_field','baseline','runtime_serialize_10_int_fields'], tests)
        del self.data['CL-params']['--tests']
    
 
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
        self.assertIn(test_result[0][0],[self.versions[:21],self.versions[21:]])
        self.assertIn(test_result[1][0],[self.versions[:21],self.versions[21:]])
        self.assertNotEqual(test_result[0][1] + test_result[1][1], self.benchmarks)
        self.assertNotEqual(test_result[1][1], self.benchmarks)
        self.assertItemsEqual(test_result[0][1]+test_result[1][1], self.benchmarks)
    
    def test_small_tests(self):
        self.data['CL-params']['--tests'] = "'.*\\.runtime_sparse_deserialize_1_int_field$|.*\\.runtime_serialize_10_int_fields$'"
        self.data['total'] = 3
        distributor = Distributor(self.data, strategy = VersionTestDistributor)
        test_result = distributor.get_suite()
        self.assertEqual(len(test_result),3)
        self.assertEqual(test_result[2],[[None],[None]])
        self.assertEqual(test_result[0][0], self.versions[:21])
        self.assertEqual(test_result[1][0], self.versions[21:])
        self.assertIn(test_result[0][1], [['runtime_sparse_deserialize_1_int_field'],['runtime_serialize_10_int_fields']])
        self.assertIn(test_result[1][1], [['runtime_sparse_deserialize_1_int_field'],['runtime_serialize_10_int_fields']])
        del self.data['CL-params']['--tests']
        
    def test_small_versions(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <historian type="MvnCommitWalker">
                <project name="Protostuff" dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/protostuff">
                        <jmh_root dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/benchmarks" />
                        <junit>
                                <execs>1</execs>
                        </junit>
                        <versions>
                                <start>8924a5f</start>
                                <end>5fa34fc</end>
                        </versions>
                </project>
                <jmh_arguments>
                        -f 1 -tu s -bm thrpt -wi 1 -i 1 -r 1
                </jmh_arguments>
        </historian>"""
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(xml)
        self.data['total'] = 4
        distributor = Distributor(self.data, strategy = VersionTestDistributor)
        test_result = distributor.get_suite()
        self.assertEqual(len(test_result),4)
        self.assertEqual(test_result[3],[[None],[None]])
        self.assertEqual(test_result[0][0],['8924a5f'])
        self.assertEqual(test_result[1][0],['a16e0bb'])
        self.assertEqual(test_result[2][0],['5fa34fc'])
        [self.assertEqual(len(test_result[x][1]),3) for x in range(3)]
        
    def test_both_small(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <historian type="MvnCommitWalker">
                <project name="Protostuff" dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/protostuff">
                        <jmh_root dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/benchmarks" />
                        <junit>
                                <execs>1</execs>
                        </junit>
                        <versions>
                                <start>8924a5f</start>
                                <end>5fa34fc</end>
                        </versions>
                </project>
                <jmh_arguments>
                        -f 1 -tu s -bm thrpt -wi 1 -i 1 -r 1
                </jmh_arguments>
        </historian>"""
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(xml)
        self.data['total'] = 4
        self.data['CL-params']['--tests'] = "'.*\\.runtime_sparse_deserialize_1_int_field$|.*\\.runtime_serialize_10_int_fields$'"
        distributor = Distributor(self.data, strategy = VersionTestDistributor)
        test_result = distributor.get_suite()
        self.assertEqual(len(test_result),4)
        self.assertEqual(test_result[2],[[None],[None]])
        self.assertEqual(test_result[3],[[None],[None]])
        self.assertEqual(test_result[0][0],['8924a5f','a16e0bb'])
        self.assertEqual(test_result[1][0],['5fa34fc'])
        self.assertEqual(len(test_result[0][1]), 1)
        self.assertEqual(len(test_result[1][1]), 1)
        del self.data['CL-params']['--tests']
        
    def test_both_eq_small(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <historian type="MvnCommitWalker">
                <project name="Protostuff" dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/protostuff">
                        <jmh_root dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/benchmarks" />
                        <junit>
                                <execs>1</execs>
                        </junit>
                        <versions>
                                <start>8924a5f</start>
                                <end>a16e0bb</end>
                        </versions>
                </project>
                <jmh_arguments>
                        -f 1 -tu s -bm thrpt -wi 1 -i 1 -r 1
                </jmh_arguments>
        </historian>"""
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(xml)
        self.data['total'] = 4
        self.data['CL-params']['--tests'] = "'\\.runtime_sparse_deserialize_1_int_field$|\\.runtime_serialize_10_int_fields$'"
        distributor = Distributor(self.data, strategy = VersionTestDistributor)
        test_result = distributor.get_suite()
        self.assertEqual(len(test_result),4)
        self.assertEqual(test_result[2],[[None],[None]])
        self.assertEqual(test_result[3],[[None],[None]])
        self.assertEqual(test_result[0][0],['8924a5f'])
        self.assertEqual(test_result[1][0],['a16e0bb'])
        self.assertEqual(len(test_result[0][1]), 1)
        self.assertEqual(len(test_result[1][1]), 1)
        del self.data['CL-params']['--tests']
    
class RandomDistributorTest (unittest.TestCase):
    data = json.loads("""{"CL-params": {"-t": "benchmark"},
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/Testing/project"
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
    
    benchmarks = ['baseline', 
                  'runtime_deserialize_1_int_field',
                  'runtime_serialize_1_int_field',
                  'runtime_deserialize_10_int_field',
                  'runtime_serialize_10_int_fields',
                  'runtime_sparse_deserialize_1_int_field',
                  'testBar',
                  'testBaz',
                  'testFoo'] 
    
    def setUp(self):
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(self.xml)
        self.data['CL-params']['-f'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['config'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['CL-params']['-b'] = "commits"
        
    def test_split_shuffle(self):
        tester = RandomDistributor()
        splits = [1,2,3,4,5,6,7,8,9]
        test_suite = tester.split(splits, 1)
        self.assertItemsEqual(test_suite, [splits])
        test_suite = tester.split(splits, 2)
        self.assertEquals(len(test_suite), 2)
        self.assertIn(len(test_suite[0]), [4,5])
        self.assertItemsEqual(test_suite, [splits[:5], splits[5:]])
        self.assertIn(test_suite[1], [splits[:5], splits[5:]])
        test_suite = tester.split(splits, 5)
        self.assertEquals(len(test_suite), 5)
        self.assertEqual(len(test_suite[0]), 2)
        self.assertEqual(len(test_suite[-1]), 1)
        test_suite = tester.split(splits[:5], 5)
        self.assertEquals(len(test_suite), 5)
        self.assertEquals(len(test_suite[0]), 1)
        self.assertItemsEqual(test_suite, [[splits[0]],[splits[1]],[splits[2]],
                                           [splits[3]],[splits[4]]])
        test_suite = tester.split([1,2,3], 5)
        self.assertItemsEqual(test_suite, [[1],[2],[3],[],[]])
        
    def test_get_target(self):
        versioner = RandomDistributor()
        test_versions = versioner.get_versions(self.data)
        self.assertEquals(self.versions, test_versions)
        
    def test_get_target_tests(self):
        tester = RandomDistributor()
        tests = tester.get_tests(self.data)
        self.assertItemsEqual(self.benchmarks, tests)
        
    def test_get_target_tests2(self):
        self.data['CL-params']['--tests'] = "'.*\\.runtime_sparse_deserialize_1_int_field$|.*\\.baseline$|.*\\.runtime_serialize_10_int_fields$'"
        tester = RandomDistributor()
        tests = tester.get_tests(self.data)
        self.assertItemsEqual(['runtime_sparse_deserialize_1_int_field','baseline','runtime_serialize_10_int_fields'], tests)
        del self.data['CL-params']['--tests']
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
        
    def test_small_tests(self):
        self.data['CL-params']['--tests'] = "'.*\\.runtime_sparse_deserialize_1_int_field$|.*\\.runtime_serialize_10_int_fields$'"
        self.data['total'] = 3
        distributor = Distributor(self.data, strategy = RandomDistributor)
        test_result = distributor.get_suite()
        self.assertEqual(len(test_result),3)
        self.assertEqual(test_result[2],[[None],[None]])
        self.assertNotEqual(test_result[0][0], self.versions[:20])
        self.assertIn(len(test_result[0][0]),[20,21])
        self.assertIn(test_result[0][1], [['runtime_sparse_deserialize_1_int_field'],['runtime_serialize_10_int_fields']])
        self.assertIn(test_result[1][1], [['runtime_sparse_deserialize_1_int_field'],['runtime_serialize_10_int_fields']])
        del self.data['CL-params']['--tests']
        
    def test_small_versions(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <historian type="MvnCommitWalker">
                <project name="Protostuff" dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/protostuff">
                        <jmh_root dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/benchmarks" />
                        <junit>
                                <execs>1</execs>
                        </junit>
                        <versions>
                                <start>8924a5f</start>
                                <end>5fa34fc</end>
                        </versions>
                </project>
                <jmh_arguments>
                        -f 1 -tu s -bm thrpt -wi 1 -i 1 -r 1
                </jmh_arguments>
        </historian>"""
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(xml)
        self.data['total'] = 4
        distributor = Distributor(self.data, strategy = RandomDistributor)
        test_result = distributor.get_suite()
        self.assertEqual(len(test_result),4)
        self.assertEqual(test_result[3],[[None],[None]])
        [self.assertEqual(len(test_result[x][1]),3) for x in range(3)]
        [self.assertEqual(len(test_result[x][0]),1) for x in range(3)]
        
    def test_both_small(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <historian type="MvnCommitWalker">
                <project name="Protostuff" dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/protostuff">
                        <jmh_root dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/benchmarks" />
                        <junit>
                                <execs>1</execs>
                        </junit>
                        <versions>
                                <start>8924a5f</start>
                                <end>5fa34fc</end>
                        </versions>
                </project>
                <jmh_arguments>
                        -f 1 -tu s -bm thrpt -wi 1 -i 1 -r 1
                </jmh_arguments>
        </historian>"""
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(xml)
        self.data['total'] = 4
        self.data['CL-params']['--tests'] = "'.*\\.runtime_sparse_deserialize_1_int_field$|.*\\.runtime_serialize_10_int_fields$'"
        distributor = Distributor(self.data, strategy = RandomDistributor)
        test_result = distributor.get_suite()
        self.assertEqual(len(test_result),4)
        self.assertEqual(test_result[2],[[None],[None]])
        self.assertEqual(test_result[3],[[None],[None]])
        self.assertEqual(len(test_result[0][0]), 2)
        self.assertEqual(len(test_result[1][0]),1)
        self.assertEqual(len(test_result[0][1]), 1)
        self.assertEqual(len(test_result[1][1]), 1)
        del self.data['CL-params']['--tests']
        
    def test_both_eq_small(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <historian type="MvnCommitWalker">
                <project name="Protostuff" dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/protostuff">
                        <jmh_root dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/benchmarks" />
                        <junit>
                                <execs>1</execs>
                        </junit>
                        <versions>
                                <start>8924a5f</start>
                                <end>a16e0bb</end>
                        </versions>
                </project>
                <jmh_arguments>
                        -f 1 -tu s -bm thrpt -wi 1 -i 1 -r 1
                </jmh_arguments>
        </historian>"""
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(xml)
        self.data['total'] = 4
        self.data['CL-params']['--tests'] = "'.*\\.runtime_sparse_deserialize_1_int_field$|.*\\.runtime_serialize_10_int_fields$'"
        distributor = Distributor(self.data, strategy = RandomDistributor)
        test_result = distributor.get_suite()
        self.assertEqual(len(test_result),4)
        self.assertEqual(test_result[2],[[None],[None]])
        self.assertEqual(test_result[3],[[None],[None]])
        self.assertEqual(len(test_result[0][0]), 1)
        self.assertEqual(len(test_result[1][0]), 1)
        self.assertEqual(len(test_result[0][1]), 1)
        self.assertEqual(len(test_result[1][1]), 1)
        del self.data['CL-params']['--tests']
    
    # TODO: add test case
    def test_with_dates(self):
        pass
class MvnVersionDistributorTest (unittest.TestCase):
    data = json.loads("""{"CL-params": {"-t": "benchmark"},
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/Testing/project"
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
    
    versions = ['2.0', '2.0.1', '3.0', '5.0.1', '6.0', '7.0.1']
    
    def setUp(self):
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(self.xml)
        self.data['CL-params']['-f'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['config'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.data['CL-params']['-b'] = "versions"
    
    #VersionDistributor 
    def test_get_target(self):
        versioner = VersionDistributor()
        test_versions = versioner.get_target(self.data)
        self.assertEquals(self.versions, test_versions)
        
    def test_get_suite_1inst(self):
        self.data['total'] = 1
        distributor = Distributor(self.data, strategy = VersionDistributor)
        test_result = distributor.get_suite()
        self.assertEquals(len(test_result), 1)
        self.assertEquals(len(test_result[0]), 2)
        self.assertItemsEqual(test_result, [[self.versions, [None]]])
        self.assertEquals(len(test_result[0][1]),1)
        self.assertEquals(test_result[0][1][0],None)
        self.assertEqual(test_result[0][0], self.versions)
        self.assertEqual(test_result[0][0][0], self.versions[0])
    
    def test_get_suite_3insts(self):
        self.data['total'] = 3
        distributor = Distributor(self.data, strategy = VersionDistributor)
        test_result = distributor.get_suite()
        num_items = len(test_result[0][0]) + len(test_result[1][0]) + len(test_result[2][0])
        self.assertEquals(num_items, len(self.versions))
        self.assertEquals(test_result[0][1][0], None)
        self.assertEquals(test_result[1][1][0], None)
        self.assertEquals(test_result[2][1][0], None)
        self.assertItemsEqual(test_result, [[self.versions[:2], [None]], [self.versions[2:4], [None]],
                                         [self.versions[4:], [None]]])
        
    def test_get_suite_7insts(self):
        self.data['total']=8
        distributor = Distributor(self.data, strategy = VersionDistributor)
        test_result = distributor.get_suite()
        for x in range(0, 8):
            self.assertEquals(test_result[x][1][0], None)
        self.assertNotEqual(test_result.content, 'random')
        expected = []
        [expected.append([[item], [None]]) for item in self.versions]
        expected.append([[None],[None]])
        expected.append([[None],[None]])
        self.assertItemsEqual(test_result, expected)
        self.assertEquals(len(test_result), 8)
        
    def test_get_target2(self):
        versioner = RandomVersionDistributor()
        test_versions = versioner.get_target(self.data)
        self.assertEquals(self.versions, test_versions)
        
    def test_get_target3(self):
        versioner = VersionTestDistributor()
        test_versions = versioner.get_versions(self.data)
        self.assertEquals(self.versions, test_versions)
        
    def test_get_target4(self):
        versioner = RandomDistributor()
        test_versions = versioner.get_versions(self.data)
        self.assertEquals(self.versions, test_versions)
        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSuiteTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(VersionDistributorTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(RandomVersionDistributorTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDistributorTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(VersionTestDistributorTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(RandomDistributorTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(MvnVersionDistributorTest)
    unittest.TextTestRunner(verbosity=5).run(suite)