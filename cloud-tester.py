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
import os
import shutil
from Writer import Writer
from impl.GitRepoHandler import GitRepoHandler
import xml.etree.ElementTree as ET
import distribute as dis
from impl.MvnCommitWalker import MvnCommitWalker
from impl.MvnVersionWalker import MvnVersionWalker
from Distributor import Distributor

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

def shut_down(driver, node):
    """Shut down GCE instances."""
    
    driver.ex_stop_node(node)

def run():
    # parse json
    with open(sys.argv[1]) as data_file:
        data = json.load(data_file)
    
    mode = data['mode']
    distri_mode = data['distribution']
    config = data['CL-params']['-f'] 
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
    distributor = Distributor(data, strategy=eval(data['distribution']))
    test_suite = distributor.split()
    writer = Writer(data, test_suite.content)
    for node, bundle in zip(node_dict.iteritems(), test_suite):
        config, cl = writer.generate_input(bundle) 

        transfer_file(node, config)
        # compress project-dir
        project = shutil.make_archive('project','gztar',root_dir= data['project']) # results in project.gz.tar, store project as /project/project-name
        transfer_file(node, project)
        transfer_file(node, 'cl-params.txt') #cl
        # start server
    for node in node_dict.iteritems():
        port = node[0][-1]
        ip = node[1]
        cmd = "ssh -L 222" + port + ":localhost:8080 selin@" + ip + ' python ./server.py' # keys needed? cloud-manager
        #print cmd
        subprocess.Popen(cmd, shell=True) # non-blocking shell
        
    # wait for instances to start server
    time.sleep(3)
    status_mode = data['status-mode']# ALL, NEW, ERR
    instances = data['total']
    ending = client.run(instances, status_mode)
    # shut down instances
    if ending == 'FINISHED':
        for node in node_dict.iteritems():
            # shut down servers and exit ssh
            cmd = "ssh selin@" + node[1] + " signal.SIGINT && exit"
            subprocess.call(cmd, shell=True)
            if mode == 'libcloud':
                driver.ex_stop_node(node)
            
            
    # disconnect and destroy nodes

if __name__ == '__main__':
  run()