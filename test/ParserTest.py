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
    
    def test_parse_result(self):
        test_project = '/home/selin/Documents/Uni/Bachelorthesis/Testing/project/benchmarks'
        test_result = p.parse(test_project)
        self.assertEqual(test_result, self.benchmarks)
        self.assertEqual(len(test_result), 9)
        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ParserTest)
    unittest.TextTestRunner(verbosity=5).run(suite)