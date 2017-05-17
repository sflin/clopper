#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 10 14:58:12 2017

@author: selin
"""

import json
import unittest
import glob
import src.outputgenerator as og
import os
import shutil
class OutputGeneratorTest (unittest.TestCase):
    data = json.loads("""{"CL-params": {
                            "-f": "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml",
                            "-o": "/home/selin/output/output.csv",
                            "-t": "benchmark",
                            "--cloud": "/home/selin/storage-credentials.json clopper-storage"
                          },
                          "project": "/home/selin/Documents/Uni/Bachelorthesis/Testing/project"
                        }""")
    
    versions = ['8924a5f', 'a16e0bb', '5fa34fc', '01bc2b2']
    
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <historian type="MvnCommitWalker">
            <project name="Protostuff" dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/protostuff">
                    <jmh_root dir="/home/selin/Documents/Uni/Bachelorthesis/Testing/project/benchmarks" />
                    <junit>
                            <execs>1</execs>
                    </junit>
                    <versions>
                            <start>8924a5f</start>
                            <end>01bc2b2</end>
                    </versions>
            </project>
            <jmh_arguments>
                    -f 1 -tu s -bm thrpt -wi 1 -i 1 -r 1
            </jmh_arguments>
    </historian>"""
    
    xml_version = """<?xml version="1.0" encoding="UTF-8"?>
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
    
    params = {'tests': None, 'runner': 'mvn', 'build-type': 'clean', 
              'outfile': u'/home/selin/output/output.csv', 'step': None, 
              'cloud': '/home/selin/storage-credentials.json clopper-storage', 'backend': 'commits', 'start': None, 
              'config': u'/home/selin/Documents/Uni/Bachelorthesis/Testing/test-config.xml', 
              'invert': False, 'to': None, 'mode': 'commit-mode', 
              'type': u'benchmark', 'codeonly': False}
        
    def test_get_header(self):
        params = og.get_header(self.data)
        items = ['config','outfile', 'cloud','codeonly','type', 'backend', 'runner',
                 'start','to','step','invert','tests','mode','build-type']
        [self.assertIn(para, params) for para in items]
        
    def test_get_commits(self):
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(self.xml)
        self.params['config'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.params['backend'] = 'commits'
        versions = og.get_versions(self.params)
        self.assertEquals(self.versions, versions)
        
    def test_get_versions(self):
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(self.xml_version)
        self.params['config'] = "/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml"
        self.params['backend'] = "versions"
        versions = og.get_versions(self.params)
        self.assertEquals(['2.0', '2.0.1', '3.0', '5.0.1', '6.0', '7.0.1'], versions)
        self.params['backend'] = 'commits'
        
    def test_concat(self):
 
        with open("/home/selin/Documents/Uni/Bachelorthesis/Testing/test-conf.xml", 'w') as config:
            config.write(self.xml)
        files = glob.glob('/home/selin/Documents/Uni/Bachelorthesis/Testing/OutputGeneratorFiles/*.csv')
        og.concat(self.data, files)
        num_files = len([name for name in os.listdir('/home/selin/output')])
        self.assertEquals(num_files, 1)  
        self.assertEquals(glob.glob('/home/selin/output/*.csv')[0], self.data['CL-params']['-o'])
        
        
if __name__ == '__main__':
    try:
        os.mkdir('/home/selin/output')
    except OSError:
        pass
    suite = unittest.TestLoader().loadTestsFromTestCase(OutputGeneratorTest)
    unittest.TextTestRunner(verbosity=5).run(suite)
    shutil.rmtree('/home/selin/output')