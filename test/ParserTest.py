#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 08:04:31 2017

@author: selin
"""

import unittest
from src import parser as p
class ParserTest (unittest.TestCase):
    
    benchmarks = ['io.protostuff.benchmarks.RuntimeSchemaBenchmark.baseline', 
                  'io.protostuff.benchmarks.RuntimeSchemaBenchmark.generated_deserialize_10_int_field', 
                  'io.protostuff.benchmarks.RuntimeSchemaBenchmark.generated_deserialize_1_int_field', 
                  'io.protostuff.benchmarks.RuntimeSchemaBenchmark.generated_serialize_10_int_field', 
                  'io.protostuff.benchmarks.RuntimeSchemaBenchmark.generated_serialize_1_int_field', 
                  'io.protostuff.benchmarks.RuntimeSchemaBenchmark.runtime_deserialize_10_int_field', 
                  'io.protostuff.benchmarks.RuntimeSchemaBenchmark.runtime_deserialize_1_int_field', 
                  'io.protostuff.benchmarks.RuntimeSchemaBenchmark.runtime_serialize_10_int_fields', 
                  'io.protostuff.benchmarks.RuntimeSchemaBenchmark.runtime_serialize_1_int_field', 
                  'io.protostuff.benchmarks.RuntimeSchemaBenchmark.runtime_sparse_deserialize_10_int_field', 
                  'io.protostuff.benchmarks.RuntimeSchemaBenchmark.runtime_sparse_deserialize_1_int_field', 
                  'io.protostuff.benchmarks.RuntimeSchemaBenchmark.runtime_sparse_serialize_10_int_fields', 
                  'io.protostuff.benchmarks.RuntimeSchemaBenchmark.runtime_sparse_serialize_1_int_field', 
                  'io.protostuff.benchmarks.StringSerializerBenchmark.bufferedRecycledSerializer', 
                  'io.protostuff.benchmarks.StringSerializerBenchmark.bufferedSerializer', 
                  'io.protostuff.benchmarks.StringSerializerBenchmark.builtInSerializer']
    units = ['testSimple', 'testXIO', 'testFooArray', 'testXIOCharset', 'testString', 
             'testFooRepeated', 'normalMessage', 'normalExtendedMessage', 'unknownField', 
             'missingField', 'forceUseSunReflectionFactory', 'testWriteNumericEnum', 
             'testSerializeDeserializeNumericEnum', 'testWriteStringEnum', 'testEntityFullyAnnotated', 
             'testEntityPartlyAnnotated1', 'testEntityPartlyAnnotated2', 'testEntityInvalidAnnotated1', 
             'testEntityInvalidAnnotated2', 'testEntityInvalidTagNumber', 'testEntityWithFieldAlias',
             'privateConstructors', 'testEmptyFieldsPojo', 'testComplexFieldsPojo', 'testIt', 
             'testMuchExcludedEntity', 'testTaggedAndExcludedEntity', 'testEmptyMessage', 
             'testSerializeDeserialize', 'testMaxTag', 'testMissingTagException', 
             'testSerializePositiveInfinity', 'testDeserializePositiveInfinity', 
             'testSerializeNegativeInfinity', 'testDeserializeNegativeInfinity', 
             'testSerializeNaN', 'testDeserializeNaN', 'testSerialize', 'testDeserialize', 
             'testDeserializeDataSerializedAsSignedNumbers_backward_comp', 'normalMessage', 
             'unknownScalarField', 'unknownArrayField', 'unknownEmptyMessageField', 
             'unknownNestedMessageField', 'testEquals', 'testNotEqual', 'testHashcode', 
             'testImportedFieldIsAccessible', 'testProtoDescriptor', 'testGeneratedClass',
             'test_newInstance_withoutDefaultValues', 'test_newInstance_withDefaultValues',
             'testThatClassExists', 'testEmptyMessageSchema', 'testSerializeDeserialize_EmptyMessage', 
             'testSerializeDeserialize_MessageWithEmptyMessage_unset', 'testSerializeDeserialize_MessageWithEmptyMessage_is_set',
             'testEquals', 'testHashcode', 'testMergeTwice', 'testUnmodifiableList', 'testEquals', 'testNotEqual', 
             'testHashcode', 'testParseUnsignedInt', 'testUnsignedIntToString', 'testParseUnsignedLong', 
             'testUnsignedLongToString', 'checkConvertedValues', 'testToString_emptyString', 
             'testToString', 'testWriteNumericEnum', 'testSerializeDeserializeNumericEnum',
             'testWriteStringEnum', 'testEntityFullyAnnotated', 'testEntityPartlyAnnotated1', 
             'testEntityPartlyAnnotated2', 'testEntityInvalidAnnotated1', 'testEntityInvalidAnnotated2', 
             'testEntityInvalidTagNumber', 'testEntityWithFieldAlias', 'privateConstructors', 'testEmptyFieldsPojo', 
             'testComplexFieldsPojo', 'testIt', 'testMuchExcludedEntity', 'testTaggedAndExcludedEntity', 
             'testEmptyMessage', 'testSerializeDeserialize', 'testMaxTag', 'testMissingTagException', 
             'testBasics', 'testGetBuffers', 'testGetBuffersAndAppendData', 'testToCamelCase', 'testToPascalCase',
             'testToUnderscoreCase', 'testBasicProtoTypes', 'testCC', 'testCCU', 'testUC', 'testUCU', 
             'testUUC', 'testPC', 'testPCS', 'testPluralize', 'testSingularize', 'testTrim', 'testCutL', 'testCutR']
             
    data = {"project":"/home/selin/Documents/Uni/Bachelorthesis/project",
            "CL-params": {"-t": "benchmark"}
            }
    def test_parse_result(self):
        test_result = p.parse(self.data)
        self.assertEqual(test_result, self.benchmarks)
        self.assertEqual(len(test_result), 16)
        
    def test_parse_unit(self):
        self.data['CL-params']['-t'] = 'unit'
        test_result = p.parse(self.data)
        self.assertEqual(test_result, self.units)
        self.assertEqual(len(test_result), 111)
        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ParserTest)
    unittest.TextTestRunner(verbosity=5).run(suite)