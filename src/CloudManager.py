#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 14:25:23 2017

@author: selin
"""
import libcloud as lc
import logging
import subprocess
from scp import SCPClient
import paramiko
import time
import sys
import json
import client
import os
import glob
from os.path import expanduser
import shutil
from Writer import Writer
import OutputGenerator as og
from google.cloud import storage
import googleapiclient.discovery
from Distributor import (Distributor, TestDistributor, VersionDistributor, 
                         VersionTestDistributor, RandomDistributor, 
                         RandomVersionDistributor)
driver = None
def clean_up(data):
    """Clean up local host and bucket storage."""
    
    shutil.rmtree(expanduser('~/tmp'))
    shutil.rmtree(expanduser('~/output')) 
    service = googleapiclient.discovery.build('storage', 'v1')
    buckets = service.buckets().list(project=data['project-id']).execute()
    storage_client = storage.Client(project=data['project-id'])
    bucket = storage_client.get_bucket(buckets['items'][0]['name'])
    bucket_files = bucket.list_blobs()
    bucket.delete_blobs(bucket_files)

def get_results(data):
    try:
        os.mkdir(expanduser('~/output'))
    except OSError:
        shutil.rmtree(expanduser('~/output'))
        os.mkdir(expanduser('~/output'))
        logging.warning("Replace output folder.")
    service = googleapiclient.discovery.build('storage', 'v1')
    buckets = service.buckets().list(project=data['project-id']).execute()
    storage_client = storage.Client(project=data['project-id'])
    bucket = storage_client.get_bucket(buckets['items'][0]['name'])
    bucket_files = bucket.list_blobs()
    for bf in bucket_files:
        blob = bucket.blob(bf.name)
        blob.download_to_filename(expanduser('~/output/' + str(blob.name)))
    files = glob.glob(expanduser('~/output/*.csv'))
    og.concat(data, files)

def start_grpc_server(node_dict, data):
    """Start GRPC-server on cloud instances for communication."""
    
    for node in node_dict.iteritems():
        port = node[0].replace('instance-', '')
        ip = node[1]
        cmd = "ssh -o StrictHostKeyChecking=no -L 222" + port + ":localhost:8080 " + data['username'] + "@" + ip + " python ~/server.py"
        subprocess.Popen(cmd, shell=True)

def distribute_test_suite(node_dict, test_suite, data):
    
    # compress project-dir
    project = shutil.make_archive(expanduser('~/tmp/project'),'gztar',root_dir= data['project']) # store project as /project/"name"    
    writer = Writer(data, test_suite.content)
    #distribute test suite among instances
    for node, bundle in zip(node_dict.iteritems(), test_suite):
        config, cl = writer.generate_input(bundle) 
        ip = node[1]
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip, username=data['username'])
        with SCPClient(client.get_transport()) as scp:
            scp.put(config, "/home/" + data['username'] + "/tmp/config.tar.gz")
            scp.put(cl, "/home/" + data['username'] + "/tmp/params.tar.gz")
            scp.put(project, "/home/" + data['username'] + "/tmp/project.tar.gz")
        
def create_nodes(data):
    """Create and boot remote cloud instances. Replacable by other cloud-providers."""
    
    user_id = data['user-id']
    key = data['key']
    project = data['project-id']
    global driver
    
    ComputeEngine = lc.get_driver(lc.DriverType.COMPUTE, lc.DriverType.COMPUTE.GCE)
    driver = ComputeEngine(user_id, key, project=project)    
    nodes = [driver.ex_get_node('instance-' + str(i)) for i in range(1, data['total']+1)]
    [driver.ex_start_node(node) for node in nodes]
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
        node_dict = create_nodes(data)
    elif mode == 'ip':
        node_dict = data['ip-list']
    return node_dict
    
def parse_json(param):
    """Parse json-config file and check for valid input."""
    
    with open(param) as data_file:
        data = json.load(data_file)
    
    paras = ('mode', 'total', 'CL-params', 'project', 'distribution', 'project-id')
    if not all(para in data for para in paras):
        raise ValueError("Values required for: 'mode', 'total', 'CL-params'"+
                         "'project', 'distribution', and 'project-id'.")
    if not '-t' in data['CL-params']:
        raise ValueError("-t flag required in CL-params.")
    if not '-f' in data['CL-params']:
        raise ValueError("-f flag aka. config-file required in CL-params.")
    if not '-o' in data['CL-params']:
        raise ValueError("-o flag aka. output-file required in CL-params.")
    if data['mode'] == 'libcloud' and not all(para in data for para in ('user-id', 'key')):
        raise ValueError("libcloud-mode needs user-id, and key.")
    elif data['mode'] =='ip' and 'ip-list' not in data:
        raise ValueError("ip-mode needs ip-list")
    elif data['mode'] not in ('libcloud', 'ip'):
        raise ValueError("Mode not supported by clopper.")
    distri_modes = ('Distributor', 'TestDistributor', 'VersionDistributor', 
                         'VersionTestDistributor', 'RandomDistributor', 
                         'RandomVersionDistributor')
    if data['distribution'] not in distri_modes:
        raise ValueError("Invalid distribution mode.")    
    if not os.path.exists(data['CL-params']['-f']):
        raise IOError("Config-file does not exist.")
    if not os.path.exists(data['project']):
        raise IOError("Project-folder does not exist.")
    if data['CL-params']['-t'] not in ('benchmark'):
        raise ValueError("Invalid flag -t: Clopper currently only supports benchmarks.")
    if data['CL-params']['-b'] not in ('commits', 'versions'):
        raise ValueError("Invalid flag -b: Hopper only supports commits or versions.")
    if not 'username' in data:
        data['username'] = os.environ.get('USER')
    logging.info("Json-file is valid.")
    return data

def run():
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt="%Y-%m-%d %H:%M:%S", filename='clopper-log.log', 
                        filemode='w', level=logging.INFO)
    logging.info("Starting execution")
    data = parse_json(sys.argv[1])
    try:
        os.mkdir(expanduser('~/tmp'))
    except OSError:
        shutil.rmtree(expanduser('~/tmp'))
        os.mkdir(expanduser('~/tmp'))
        logging.warning("Folder tmp replaced.")
    
    # get list of running instances, format: {instance-i : ip}
    node_dict = get_instances(data)
        
    # create and distribute test suite
    distributor = Distributor(data, strategy=eval(data['distribution']))
    test_suite = distributor.get_suite()
    logging.info("Test suite generated and splitted.")
    for x in reversed(range(0, len(test_suite))):
        if test_suite[x] == [[None],[None]]:
            del node_dict['instance-'+str(x+1)]   
            del test_suite[x]
            
    distribute_test_suite(node_dict, test_suite, data)
    logging.info("Splits distributed among instances.")
    
    # start gRPC-server on instances
    start_grpc_server(node_dict)
    logging.info("Waiting for instances to start grpc server...")
    time.sleep(5)
    
    # start gRPC-client on local host
    logging.info("Starting grpc client...")
    client.run(node_dict)
    
    # shut down instances
    logging.info("Grabbing results...")
    get_results(data)
    logging.info("Shutting down instances and clean up local host...")
    global driver
    if driver:
        [driver.ex_stop_node(node) for node in node_dict]
    clean_up(data)
    logging.info("Execution finished.")
    
if __name__ == '__main__':
    run()