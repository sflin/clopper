#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 14:25:23 2017

@author: selin
"""
import logging
import subprocess
from scp import SCPClient
import paramiko
import threading
import time
import sys
import json
import client
import os
import glob
from os.path import expanduser
import shutil
from Writer import Writer
import outputgenerator as og
from google.cloud import storage
from Distributor import (Distributor, TestDistributor, VersionDistributor, 
                         VersionTestDistributor, RandomDistributor, 
                         RandomVersionDistributor)
def parse_json(param):
    """Parse json-config file and check for valid input."""
    
    with open(param) as data_file:
        data = json.load(data_file)
    
    paras = ('total', 'CL-params', 'project', 'distribution', '-i')
    if not all(para in data for para in paras):
        raise ValueError("Values required for: 'total', 'CL-params'"+
                         "'project', 'distribution', and -i aka. API-key-file.")
    if not '-t' in data['CL-params']:
        raise ValueError("-t flag required in CL-params.")
    if not '-f' in data['CL-params']:
        raise ValueError("-f flag aka. config-file required in CL-params.")
    if not '-o' in data['CL-params']:
        raise ValueError("-o flag aka. output-file required in CL-params.")
    if not '--cloud' in data['CL-params']:
        raise ValueError("--cloud flag required in CL-params. ")
    if 'ip-list' not in data:
        raise ValueError("Ip-list required.")
    distri_modes = ('Distributor', 'TestDistributor', 'VersionDistributor', 
                         'VersionTestDistributor', 'RandomDistributor', 
                         'RandomVersionDistributor')
    if data['distribution'] not in distri_modes:
        raise ValueError("Invalid distribution mode.") 
    args = data['CL-params']['--cloud'].split(' ')
    data['bucket-name'], data['credentials'] = (args[0], args[1]) if '.json' in args[1] else (args[1], args[0])
    if not os.path.exists(data['credentials']):
        raise IOError("Credentials file does not exist.")
    if not os.path.exists(data['CL-params']['-f']):
        raise IOError("Config-file does not exist.")
    if not os.path.exists(data['project']):
        raise IOError("Project-folder does not exist.")
    if data['CL-params']['-t'] not in ('benchmark', 'unit'):
        raise ValueError("Invalid flag -t: Hopper only supports benchmarks or unit-tests.")
    if data['CL-params']['-b'] not in ('commits', 'versions'):
        raise ValueError("Invalid flag -b: Hopper only supports commits or versions.")
    data['username'] = data['username'] if 'username' in data else os.environ.get('USER')
    logging.info("Json-file is valid.")
    return data

def clean_up(data):
    """Clean up local host and bucket storage."""
    
    #shutil.rmtree(expanduser('~/tmp'))
    #shutil.rmtree(expanduser('~/output')) 
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']= data['credentials']
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(data['bucket-name'])
    bucket_files = bucket.list_blobs()
    bucket.delete_blobs(bucket_files)

def get_results(data):
    try:
        os.mkdir(expanduser('~/output'))
    except OSError:
        shutil.rmtree(expanduser('~/output'))
        os.mkdir(expanduser('~/output'))
        logging.warning("Replace output folder.")
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']= data['credentials']
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(data['bucket-name'])
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
        user = data['username']
        key_file= data['-i']
        cmd = "ssh -i " + key_file + " -o StrictHostKeyChecking=no -L 222" + port 
        cmd+= ":localhost:8080 " + user + "@" + ip + " python /home/" + user + "/server.py"
        subprocess.Popen(cmd, shell=True)

def distribute_test_suite(node_dict, test_suite, data):
    
    # compress project-dir
    project = shutil.make_archive(expanduser('~/tmp/project'),'gztar',root_dir= data['project'])
    writer = Writer(data, test_suite.content)
    #distribute test suite among instances
    for node, bundle in zip(node_dict.iteritems(), test_suite):
        config, cl = writer.generate_input(bundle) 
        ip = node[1]
        key_file = data['-i']
        user = data['username']
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip, username=user, key_filename=key_file)
        with SCPClient(client.get_transport()) as scp:
            # TODO: remove
            scp.put('/home/selin/Documents/Uni/Bachelorthesis/clopper/src/server.py', "/home/" + user)
            scp.put('/home/selin/Documents/Uni/Bachelorthesis/hopper/hopper.py', "/home/"+ user + "/hopper/hopper.py")
            scp.put('/home/selin/Documents/Uni/Bachelorthesis/hopper/impl/FileDumper.py', "/home/" + user + "/hopper/impl/FileDumper.py")
            scp.put(config, "/home/" + user + "/tmp/config.tar.gz")
            scp.put(cl, "/home/" + user + "/tmp/params.tar.gz")
            scp.put(project, "/home/" + user + "/tmp/project.tar.gz")
        client.close()
            
def set_up(node, data):
    
    user = data['username']
    ip = node[1]
    key_file = data['-i']
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=user, key_filename=key_file)
    with SCPClient(client.get_transport()) as scp:
        scp.put('cloud-configuration.sh', "/home/"+ user)
        scp.put(data['credentials'], "/home/"+ user)
    logging.info("Start installation on " + node[0])
    (stdin, stdout, stderr) = client.exec_command('bash ~/cloud-configuration.sh')
    counter = 0
    while not stdout.channel.exit_status_ready():
        time.sleep(1)
        counter += 1
        if counter % 60 == 0:
            logging.info("Installation in progress on " + node[0])
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        logging.info("Installation on " + node[0] + " completed.")
    else:
        logging.error("Installation failed on " + node[0])
    client.close()

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
    
    node_dict = data['ip-list'] # format: {instance-i : ip}
    
    # configure instances if required
    if 'setup' in data:
        threads = [threading.Thread(target=set_up, args=(node, data,)) for node in node_dict.iteritems()]
        [t.start() for t in threads]
        [thread.join() for thread in threads]
        logging.info("Instances successfully configured.")
        
    # create and distribute test suite
    distributor = Distributor(data, strategy=eval(data['distribution']))
    test_suite = distributor.get_suite()
    logging.info("Test suite generated and splitted.")
    for x in reversed(range(0, len(test_suite))):
        if test_suite[x] == [[None],[None]]:
            node = node_dict.keys()[x]
            del node_dict[node]
            del test_suite[x]
            logging.info("Testsuite too small for " + str(data['total']) + " instances. Release " + node)
            
    distribute_test_suite(node_dict, test_suite, data)
    logging.info("Splits distributed among instances.")
    
    # start gRPC-server on instances
    start_grpc_server(node_dict, data)
    logging.info("Waiting for instances to start grpc server...")
    time.sleep(5)
    
    # start gRPC-client on local host
    logging.info("Starting grpc client...")
    client.run(node_dict)
    
    # shut down instances
    logging.info("Grabbing results...")
    get_results(data)
    logging.info("Shutting down instances and clean up local host...")
    clean_up(data)
    logging.info("Execution finished.")
    
if __name__ == '__main__':
    run()