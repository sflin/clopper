#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 08:04:31 2017

@author: selin
"""

import unittest
from src import parser as p
class ParserTest (unittest.TestCase):
    
    benchmarks = ['baseline', 
                  'runtime_deserialize_1_int_field',
                  'runtime_serialize_1_int_field',
                  'runtime_deserialize_10_int_field',
                  'runtime_serialize_10_int_fields',
                  'runtime_sparse_deserialize_1_int_field',
                  'testBar',
                  'testBaz',
                  'testFoo']
    units = ['testWriteNumericEnum',
             'testSerializeDeserializeNumericEnum',
             'testWriteStringEnum',
             'testEmptyFieldsPojo',
             'testComplexFieldsPojo']
             
    data = {"project":"/home/selin/Documents/Uni/Bachelorthesis/Testing/project",
            "CL-params": {"-t": "benchmark"}
            }
    def test_parse_result(self):
        test_result = p.parse(self.data)
        self.assertEqual(test_result, self.benchmarks)
        self.assertEqual(len(test_result), 9)
        
    def test_parse_unit(self):
        self.data['CL-params']['-t'] = 'unit'
        test_result = p.parse(self.data)
        self.assertEqual(test_result, self.units)
        self.assertEqual(len(test_result), 5)
        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ParserTest)
    unittest.TextTestRunner(verbosity=5).run(suite)