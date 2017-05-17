#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 01:24:56 2017

@author: selin
"""

import src.clopper as cm
import unittest
import os
import subprocess
import mock
import shutil
from os.path import expanduser
import src.clopper_pb2
import src.clopper_pb2_grpc
from src.Writer import Writer
import src.client
import logging
import threading
import glob
        
class IntegrationTest(unittest.TestCase):
  
    def simple_distribute(node_dict, test_suite, data):
        print test_suite
        print node_dict
        project = shutil.make_archive(expanduser('~/tmp/project'),'gztar',root_dir= data['project']) # store project as /project/"name"    
        writer = Writer(data, test_suite.content)
        #distribute test suite among instances
        for node, bundle in zip(node_dict.iteritems(), test_suite):
            config, cl = writer.generate_input(bundle) 
            name = node[0]
            try:
                os.mkdir(expanduser('~/tmp-' + name))
            except OSError:
                pass
            shutil.copyfile(config, expanduser('~/tmp-' + name + '/config.tar.gz'))
            shutil.copyfile(cl, expanduser('~/tmp-' + name + '/params.tar.gz'))
            shutil.copyfile(project, expanduser('~/tmp-' + name + '/project.tar.gz'))
            
    def start_local(node_dict, data):
        for node in node_dict.iteritems():
            port = node[0].replace('instance-','')
            # use testing version of server, only server1 is doing real hopping
            subprocess.Popen('python /home/selin/Documents/Uni/Bachelorthesis/clopper/test/server' + port +'.py', shell=True)
            
    def run_minimal(node_dict):
        ports = [node[0].replace('instance-','') for node in node_dict.iteritems()]
        stubs = src.client.create_stubs(ports) 
        src.client.initial_greeting(stubs) 
        logging.info("Trigger hopper preparation...")
        stati = [stub.ExecuteHopper(src.clopper_pb2.HopRequest(trigger='')) for stub in stubs]
        for s in stati:
            if s.status == 'ERROR':
                logging.critical("ERROR on " + s.name + ". Hopper preparation failed.")
            else:
                logging.info(s.name + ' --- ' + s.status)
        threads = [threading.Thread(target = src.client.status_request, args = (stub,)) for stub in stubs]
        [t.start() for t in threads]
        [thread.join() for thread in threads]
        logging.info("Shutting down cloud-manager-client...")
    
    @mock.patch('src.CloudManager.distribute_test_suite', side_effect=simple_distribute)
    @mock.patch('src.CloudManager.start_grpc_server', side_effect=start_local)
    @mock.patch('src.CloudManager.client.run', side_effect=run_minimal)
    def test_run(self, distribute, local, run):
        cm.run()
        assert distribute.called
        assert distribute.call_count == 1
        assert local.called
        assert local.call_count == 1
        assert run.called
        assert run.call_count == 1
        files = glob.glob(expanduser('~/Documents/Uni/Bachelorthesis/clopper/test/*.csv'))
        assert os.path.basename(files[0]) == 'integration-output.csv'
        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(IntegrationTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    shutil.rmtree(expanduser('~/tmp-instance-1'))
    shutil.rmtree(expanduser('~/tmp-instance-2'))