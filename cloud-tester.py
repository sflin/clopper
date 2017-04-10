#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 14:25:23 2017

@author: selin
"""
import libcloud as lc
import subprocess
import time
import sys
import json
import client
import parser
import xml.etree.ElementTree as ET
import distribute as dis
from impl.MvnCommitWalker import MvnCommitWalker
from impl.MvnVersionWalker import MvnVersionWalker

def transfer_file(node, file):
    ip = node[1]
    cmd = "scp -i ~/.ssh/google_compute_engine " + file + " selin@" + ip + ":~" # probably only: "scp + + file + " selin@" + ip + ":~"
    subprocess.call(cmd, shell=True) # blocking shell

def create_GCE_driver(data):
    """Create GCE driver. Adaptable to other cloud-providers.""" 
    
    user_id = data['user-id']
    key = data['key']
    project = data['gce-project']
    
    ComputeEngine = lc.get_driver(lc.DriverType.COMPUTE, lc.DriverType.COMPUTE.GCE)
    driver = ComputeEngine(user_id, key, project=project)
    return driver
    
def remote_hopper(driver):
    """Create and boot GCE instances."""
    
    nodes = [driver.ex_get_node('instance-' + str(i)) for i in range(1,4)]
    bools = [driver.ex_start_node(node) for node in nodes]
    #nodes = driver.ex_create_multiple_nodes('instance-','n1-standard-2', image,
                   #                         5, 'europe-west1-b', )
    running_nodes = driver.wait_until_running(nodes)
    node_dict={}
    for node, ip in running_nodes:
        node_dict[node.name] = ip[0]
    return node_dict

def run():
    # parse json
    with open(sys.argv[1]) as data_file:
        data = json.load(data_file)
    
    mode = data['mode']
    distri_mode = data['distribution']
    config = data['CL-params']['-i'] 
    test_bundles = []
    bundles = ''
    
    # check parameters
    if mode == 'libcloud' or 'ip' and distri_mode == 'version' or 'test':
        pass
    else:
        print 'Invalid mode. Enter libcloud or ip for mode, and version or test for distribution.'
        exit()
    
    # get list of running instances, format: {instance-i : ip}
    if mode == 'libcloud':
        driver = create_GCE_driver(data)
        node_dict = remote_hopper(driver)
    elif mode == 'ip':
        node_dict = data['ip-list']
        
    # create test-suite distribution -- doesn't work yet
    if distri_mode == 'version':
        # get list of versions
        if data['CL-params']['-b'] and data['CL-params']['-b'] == 'versions': 
            versions = MvnVersionWalker.generate_version_list() # add **kwargs
        else:
            versions = MvnCommitWalker.generate_version_list()
        test_bundles = dis.distribute(versions)
        #random.shuffle(test_bundles)?
        
    elif distri_mode == 'test':
        # call parser to get list of tests
        tests = parser.parse(config)
        test_bundles = dis.distribute(tests)
        
    # distribute test-suite among instances
    for node, bundle in zip(node_dict.iteritems(), test_bundles):
        
        if distri_mode == 'versions':
            tree = ET.parse(data['CL-params']['-i']).getroot()
            # adapt start and end tag in config for each instance
            tree.find('.//project/versions/start').text = bundle[0]
            tree.find('.//project/versions/end').text = bundle[-1]
            tree.write('config.xml')
        else:
            for i in range(0,len(bundle)-1):
                bundles += bundle[i] + ','
            bundles += bundle[-1]
            data['CL-params']['--tests'] = bundles
            
        config = './config.xml'
        data['CL-params']['-i'] = config
        # generate file containing individual command line arguments
        with open('cl-params.txt', 'w') as cl_file:
            for param in data['CL-params']:
                cl_file.write(param + ' ' + data['CL-params'][param] + ' ')
                
        transfer_file(node, config)
        transfer_file(node, data['project'])
        transfer_file(node, cl_file)
        
        # start server
        port = node[0][-1]
        ip = node[1]
        cmd = "ssh -L 222" + port + ":localhost:8080 selin@" + ip + ' python ./server2.py' # keys needed? cloud-manager
        subprocess.Popen(cmd, shell=True) # non-blocking shell
        
    # wait for instances to start server
    time.sleep(15)
    client.run()
    # disconnect and destroy nodes

if __name__ == '__main__':
  run()