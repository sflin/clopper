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
import tarfile
import shutil
import time

class ServerTest(unittest.TestCase):
        
    def setUp(self):
        try:
            os.mkdir(expanduser('~/output'))
        except OSError:
            pass
        try:
            os.mkdir(expanduser('~/tmp'))
        except OSError:
            shutil.rmtree(expanduser('~/tmp'))
            os.mkdir(expanduser('~/tmp'))
            
    def tearDown(self):
        shutil.rmtree(expanduser('~/tmp'))
        
    def test_has_finished_no_work_true(self):
        os.mkdir(expanduser('~/tmp/params'))
        s._EXECUTIONS = 0
        has_finished = s.has_finished()
        self.assertTrue(has_finished)
        
    def test_has_not_yet_finished(self):
        os.mkdir(expanduser('~/tmp/params'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cl-params-1.txt'), expanduser('~/tmp/params'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cl-params-2.txt'), expanduser('~/tmp/params'))    
        s._EXECUTIONS = 1
        has_finished = s.has_finished()
        files = os.listdir(expanduser('~/tmp/params'))
        self.assertFalse(has_finished)
        self.assertNotEqual(len(files), s._EXECUTIONS)
        s._EXECUTIONS = 0
        
    def test_has_truly_finished(self):
        os.mkdir(expanduser('~/tmp/params'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cl-params-1.txt'), expanduser('~/tmp/params'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cl-params-2.txt'), expanduser('~/tmp/params'))   
        s._EXECUTIONS = 2
        files = os.listdir(expanduser('~/tmp/params'))
        has_finished = s.has_finished()
        self.assertTrue(has_finished)
        self.assertEqual(len(files), s._EXECUTIONS)
        s._EXECUTIONS = 0
    
    def test_params(self):
        s._EXECUTIONS = 0
        self.assertEqual(s._EXECUTIONS, 0)
        
    def test_prepare_execution(self):
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/project.tar.gz'), expanduser('~/tmp'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/config.tar.gz'), expanduser('~/tmp'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/params.tar.gz'), expanduser('~/tmp'))
        files = os.listdir(expanduser('~/tmp'))
        self.assertNotIn('project', files)
        self.assertNotIn('params', files)
        self.assertNotIn('config', files)
        s.prepare_execution()
        files = os.listdir(expanduser('~/tmp'))
        self.assertIn('project', files)
        self.assertIn('params', files)
        self.assertIn('config', files)
        
    def test_prepare_execution2(self):
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/project.tar.gz'), expanduser('~/tmp'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/config.tar.gz'), expanduser('~/tmp'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/params.tar.gz'), expanduser('~/tmp'))
        tar = tarfile.open(expanduser('~/tmp/project.tar.gz'))
        tar.extractall(path=expanduser('~/tmp/project'))
        tar.close()
        tar = tarfile.open(expanduser('~/tmp/config.tar.gz'))
        tar.extractall(path=expanduser('~/tmp/config'))
        tar.close()
        tar = tarfile.open(expanduser('~/tmp/params.tar.gz'))
        tar.extractall(path=expanduser('~/tmp/params'))
        tar.close()
        files_pre = os.listdir(expanduser('~/tmp'))
        s.prepare_execution()
        files_post = os.listdir(expanduser('~/tmp'))
        self.assertIn('project', files_post)
        self.assertIn('params', files_post)
        self.assertIn('config', files_post)
        self.assertEquals(files_pre, files_post)
    
        
    def test_do_more_work_err(self):
        os.mkdir(expanduser('~/tmp/params'))
        os.mkdir(expanduser('~/tmp/config'))
        s._EXECUTIONS = 1
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cl-params-2.txt'), expanduser('~/tmp/params'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cloud-config-2.xml'), expanduser('~/tmp/config'))
        proc = s.do_more_work()
        while proc.poll() == None:
            time.sleep(1)
        self.assertEquals(proc.poll(), 1)
        s._EXECUTIONS = 0
        
    def test_do_more_work_success(self):
        os.mkdir(expanduser('~/tmp/params'))
        os.mkdir(expanduser('~/tmp/config'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cloud-config-1.xml'), expanduser('~/tmp/config'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cl-params-1.txt'), expanduser('~/tmp/params'))
        proc = s.do_more_work()
        self.assertIsNone(proc.poll())
        while proc.poll() == None:
            time.sleep(1)
        self.assertEquals(proc.poll(), 0)
        s._EXECUTIONS = 0    
        
    def test_execute_hopper_FINISHED(self):
        os.mkdir(expanduser('~/tmp/params'))
        self.assertEqual(s._STATE, 'SLEEPING')
        s.execute_hopper()
        self.assertEqual(s._STATE, 'FINISHED')

    def test_execute_hopper(self):
        os.mkdir(expanduser('~/tmp/params'))
        os.mkdir(expanduser('~/tmp/config'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cloud-config-1.xml'), expanduser('~/tmp/config'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cl-params-1.txt'), expanduser('~/tmp/params'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cloud-config-2.xml'), expanduser('~/tmp/config'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cl-params-2.txt'), expanduser('~/tmp/params'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cloud-config-3.xml'), expanduser('~/tmp/config'))
        shutil.copy(expanduser('~/Documents/Uni/Bachelorthesis/Testing/server/cl-params-3.txt'), expanduser('~/tmp/params'))
        self.assertEqual(s._STATE, 'SLEEPING')
        s.execute_hopper()
        self.assertEqual(s._STATE, 'FINISHED')      
        s._EXECUTIONS = 0  
        s._STATE = 'SLEEPING'
        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ServerTest)
    unittest.TextTestRunner(verbosity=5).run(suite)