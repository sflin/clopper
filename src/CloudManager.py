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
import os
from os.path import expanduser
import shutil
from Writer import Writer
from Distributor import (Distributor, TestDistributor, VersionDistributor, 
                         VersionTestDistributor, RandomDistributor, 
                         DefaultDistributor, RandomVersionDistributor)

def clean_up():
    # clean up tar-dirs
    #shutil.rmtree(expanduser('~/tmp'))
    pass

def shut_down(node_dict, driver=None):
    """Shut down instances."""
    
    for node in node_dict.iteritems():
        # shut down servers on instances
        cmd = "ssh selin@" + node[1] + " rm -rf ~/tmp"
        subprocess.call(cmd, shell=True)
        #cmd = "ssh selin@" + node[1] + " rm -rf ~/output"
        #subprocess.call(cmd, shell=True)
        cmd = "ssh selin@" + node[1] + " fuser -k 8080/tcp"
        # close ssh connection
        #cmd = "fuser -k 5005" + node[0][-1] + "/tcp"
        subprocess.call(cmd, shell=True)
        # stop GCE instances
        if driver:
            driver.ex_stop_node(node)

def get_results():
    # TODO: implement method
    pass

def start_grpc_server(node_dict):
    """Start GRPC-server on cloud instances for communication."""
    
    for node in node_dict.iteritems():
        port = node[0][-1]
        ip = node[1]
        cmd = "python ./server" + str(port) + ".py"
        cmd = "ssh -L 222" + port + ":localhost:8080 selin@" + ip + ' python ~/server.py' # keys needed? cloud-manager ~/clopper/server.py
        print cmd
        subprocess.Popen(cmd, shell=True)

def transfer_file(node, file):
    """Transfer data via scp to instances."""
    
    ip = node[1]
    # TODO: check if "scp " + file + " selin@" + ip + ":~/tmp" is enough
    cmd = "scp -i ~/.ssh/google_compute_engine " + str(file) + " selin@" + ip + ":~/tmp"
    print cmd
    subprocess.call(cmd, shell=True) # blocking shell

def distribute_test_suite(node_dict, test_suite, data):
    
    # compress project-dir
    project = shutil.make_archive('project','gztar',root_dir= data['project']) # results in project.gz.tar, store project as /project/"name"    
    writer = Writer(data, test_suite.content)
    
    #distribute test suite among instances
    for node, bundle in zip(node_dict.iteritems(), test_suite):
        config, cl = writer.generate_input(bundle) 
        cmd = "ssh selin@" + node[1] + " mkdir ~/tmp"
        subprocess.call(cmd, shell=True)
        cmd = "ssh selin@" + node[1] + " mkdir ~/output"
        subprocess.call(cmd, shell=True)
        transfer_file(node, config) # cloud-config.xml
        transfer_file(node, cl) # cl-params.txt
        transfer_file(node, project)
        
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
    
    nodes = [driver.ex_get_node('instance-' + str(i)) for i in range(1, data['total']+1)]
    bools = [driver.ex_start_node(node) for node in nodes]
    #nodes = driver.ex_create_multiple_nodes('instance-','n1-standard-2', image,
                   #                         5, 'europe-west1-b', )
    running_nodes = driver.wait_until_running(nodes)
    node_dict={}
    for node, ip in running_nodes:
        node_dict[node.name] = ip[0]
    return node_dict

def get_instances(data):
    mode = data['mode']
    
    if mode == 'libcloud':
        driver = create_GCE_driver(data)
        node_dict = remote_hopper(driver)
    elif mode == 'ip':
        node_dict = data['ip-list']
    return node_dict
    
def parse_json(param):
    """Parse json-config file and check for valid input."""
    
    with open(param) as data_file:
        data = json.load(data_file)
    
    # check for valid input
    paras = ('mode', 'total', 'CL-params', 'project', 'config', 'distribution')
    if not all(para in data for para in paras):
        raise ValueError("Values required for: 'mode', 'total', 'CL-params'"+
                         "'project', 'config', and 'distribution'")
    if not '-t' in data['CL-params']:
        raise ValueError("-t flag required in CL-params.")
    if data['mode'] == 'libcloud' and not all(para in data for para in ('user-id', 'key', 'gce-project')):
        raise ValueError("libcloud-mode needs user-id, key and gce-project.")
    elif data['mode'] =='ip' and 'ip-list' not in data:
        raise ValueError("ip-mode needs ip-list")
    elif data['mode'] not in ('libcloud', 'ip'):
        raise ValueError("Mode not supported by clopper.")
    distri_modes = ('Distributor', 'TestDistributor', 'VersionDistributor', 
                         'VersionTestDistributor', 'RandomDistributor', 
                         'DefaultDistributor', 'RandomVersionDistributor')
    if data['distribution'] not in distri_modes:
        raise ValueError("Invalid distribution mode.")
    if not os.path.exists(data['config']):
        raise IOError("Config-file does not exist.")
    if not os.path.exists(data['project']):
        raise IOError("Project-folder does not exist.")
    if data['CL-params']['-t'] not in ('benchmark', 'unit'):
        raise ValueError("Invalid flag -t: Hopper only supports benchmark or unit tests.")
    if data['CL-params']['-b'] not in ('commits', 'versions'):
        raise ValueError("Invalid flag -b: Hopper only supports commits or versions.")
    return data

def run():
    # parse json
    data = parse_json(sys.argv[1])

    #os.mkdir(expanduser('~/tmp'))
    driver = None
    
    # get list of running instances, format: {instance-i : ip}
    node_dict = get_instances(data)
        
    # create and distribute test suite
    distributor = Distributor(data, strategy=eval(data['distribution']))
    test_suite = distributor.get_suite()
    distribute_test_suite(node_dict, test_suite, data)
    
    # wait for instances to start server
    start_grpc_server(node_dict)
    time.sleep(5)
    status_mode = data['status-mode']# ALL, NEW, ERR
    instances = data['total']
    
    # start grpc-client on local host
    ending = client.run(instances, status_mode)
    
    # shut down instances
    if ending == 'FINISHED':
        get_results()
        shut_down(driver, node_dict)
    clean_up()
    
if __name__ == '__main__':
    run()