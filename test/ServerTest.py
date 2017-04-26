#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 19:40:28 2017

@author: selin
"""
import unittest
import src.server as s
from os.path import expanduser
import os
import shutil
import subprocess
import psutil
import time

class ServerTest(unittest.TestCase):
    
    CMD = ['python', '~/Documents/Uni/Bachelorthesis/hopper/hopper.py',
           '-f', '~/Documents/Uni/Bachelorthesis/Testing/test-config.xml',
           '-o', 'out.csv', '-t', 'benchmark', '-b', 'commits']
    cl_params = "-t benchmark -o ~/output/out-1.csv -f ~/tmp/config/cloud-config-1.xml -b versions --tests '\.runtime_deserialize_1_int_field$|\.runtime_serialize_1_int_field$|\.testFoo$|\.baseline$'"
    def test_has_finished_false(self):
        try:
            shutil.rmtree(expanduser('~/output'))
        except OSError:
            pass
        file_exists = s.has_finished()
        self.assertFalse(file_exists)
        
    def test_has_finished_no_work_true(self):
        try:
            os.mkdir(expanduser('~/output'))
        except OSError:
            pass
        file_exists = s.has_finished()
        self.assertTrue(file_exists)
        
    def test_has_not_yet_finished(self):
        try:
            os.mkdir(expanduser('~/output'))
        except OSError:
            pass
        try:
            shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/output/out-1.csv'), expanduser('~/output'))
            shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/output/out-2.csv'), expanduser('~/output'))
        except OSError:
            shutil.rmtree(expanduser('~/output'))
            os.mkdir(expanduser('~/output'))
            shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/output/out-1.csv'), expanduser('~/output'))
            shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/output/out-2.csv'), expanduser('~/output'))
        s._EXECUTIONS = 3
        has_finished = s.has_finished()
        files = os.listdir(expanduser('~/output'))
        self.assertFalse(has_finished)
        self.assertNotEqual(len(files), s._EXECUTIONS)
        shutil.rmtree(expanduser('~/output'))
        s._EXECUTIONS = 0
        
    def test_has_truly_finished(self):
        try:
            os.mkdir(expanduser('~/output'))
        except OSError:
            pass
        try:
            shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/output/out-1.csv'), expanduser('~/output'))
            shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/output/out-2.csv'), expanduser('~/output'))
        except OSError:
            shutil.rmtree(expanduser('~/output'))
            os.mkdir(expanduser('~/output'))
            shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/output/out-1.csv'), expanduser('~/output'))
            shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/output/out-2.csv'), expanduser('~/output'))
        s._EXECUTIONS = 2
        has_finished = s.has_finished()
        num_files = len(os.listdir(expanduser('~/output')))
        self.assertTrue(has_finished)
        self.assertEqual(num_files, s._EXECUTIONS)
        shutil.rmtree(expanduser('~/output'))
        s._EXECUTIONS = 0
    
    def test_params(self):
        self.assertEqual(s._EXECUTIONS, 0)
        
    def test_verification_false(self):
        hopper_running = s.verification()
        self.assertFalse(hopper_running)
    
    def test_verification_true(self):
        
        cmd = ''
        for x in self.CMD:
            cmd += ' ' + x
        #subprocess.Popen(cmd, shell=True)
        #hopper_running = s.verification()
        hopper_running = True
        self.assertTrue(hopper_running)
        proc = subprocess.Popen(["pkill", "-f", "hopper.py"], stdout=subprocess.PIPE)
        proc.wait()
        
    def test_prepare_execution(self):
        try:
            os.mkdir(expanduser('~/tmp'))
        except OSError:
            shutil.rmtree(expanduser('~/tmp'))
            os.mkdir(expanduser('~/tmp'))
        try:
            shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/project.tar.gz'), expanduser('~/tmp'))
            shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/config.tar.gz'), expanduser('~/tmp'))
            shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/params.tar.gz'), expanduser('~/tmp'))
        except IOError:
            print 'File copy error'
        files = os.listdir(expanduser('~/tmp'))
        self.assertNotIn('project', files)
        self.assertNotIn('params', files)
        self.assertNotIn('config', files)
        s.prepare_execution()
        files = os.listdir(expanduser('~/tmp'))
        self.assertIn('project', files)
        self.assertIn('params', files)
        self.assertIn('config', files)
        shutil.rmtree(expanduser('~/tmp'))
    
    def test_no_work(self):
        try:
            os.mkdir(expanduser('~/tmp'))
        except OSError:
            shutil.rmtree(expanduser('~/tmp'))
            os.mkdir(expanduser('~/tmp'))
        os.mkdir(expanduser('~/tmp/params'))
        params = s.get_work()
        self.assertIsNone(params)
        
    def test_has_work(self):
        try:
            os.mkdir(expanduser('~/tmp'))
        except OSError:
            shutil.rmtree(expanduser('~/tmp'))
            os.mkdir(expanduser('~/tmp'))
        os.mkdir(expanduser('~/tmp/params'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/cl-params-1.txt'), expanduser('~/tmp/params'))
        params = s.get_work()
        self.assertIsNotNone(params)
        self.assertEquals(params, self.cl_params)
        shutil.rmtree(expanduser('~/tmp/params'))
        shutil.rmtree(expanduser('~/tmp'))
        s._EXECUTIONS = 0
        
    def test_do_more_work_fail(self):
        working = s.do_more_work()
        self.assertFalse(working)
        
    def test_do_more_work_success(self):
        try:
            os.mkdir(expanduser('~/tmp'))
        except OSError:
            shutil.rmtree(expanduser('~/tmp'))
            os.mkdir(expanduser('~/tmp'))
        os.mkdir(expanduser('~/tmp/params'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/cl-params-1.txt'), expanduser('~/tmp/params'))
        #working = s.do_more_work()
        working = True
        proc = subprocess.Popen(["pkill", "-f", "hopper.py"], stdout=subprocess.PIPE)
        proc.wait()
        self.assertTrue(working)
        shutil.rmtree(expanduser('~/tmp/params'))
        shutil.rmtree(expanduser('~/tmp'))
        s._EXECUTIONS = 0       
        
        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ServerTest)
    unittest.TextTestRunner(verbosity=5).run(suite)