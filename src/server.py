#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 08:02:45 2017
@author: selin
"""

"""The Python implementation of the hopper extension on cloud instances."""

from concurrent import futures
import time
import subprocess
import socket
import tarfile
import grpc
import os
import clopper_pb2
import clopper_pb2_grpc
import psutil
from os.path import expanduser
import shutil
import glob
from google.cloud import storage
import threading

_STATE = 'SLEEPING'
_ONE_MIN_IN_SECONDS = 60
_EXECUTIONS = 0

def prepare_execution():
    """Unpack project and get CL parametres for hopper execution."""
    
    try:
        tar = tarfile.open(expanduser('~/tmp/project.tar.gz'))
        tar.extractall(path=expanduser('~/tmp/project'))
        tar.close()
    except IOError:
        print "Project found."
        shutil.rmtree(expanduser('~/tmp/project'))
        tar = tarfile.open(expanduser('~/tmp/project.tar.gz'))
        tar.extractall(path=expanduser('~/tmp/project'))
    try:
        tar = tarfile.open(expanduser('~/tmp/config.tar.gz'))
        tar.extractall(path=expanduser('~/tmp/config'))
        tar.close()
    except IOError:
        print "Condition already satisfied."
        shutil.rmtree(expanduser('~/tmp/config'))
        tar = tarfile.open(expanduser('~/tmp/config.tar.gz'))
        tar.extractall(path=expanduser('~/tmp/config'))
    try:
        tar = tarfile.open(expanduser('~/tmp/params.tar.gz'))
        tar.extractall(path=expanduser('~/tmp/params'))
        tar.close()
    except IOError:
        print "Condition already satisfied."
        shutil.rmtree(expanduser('~/tmp/params'))
        tar = tarfile.open(expanduser('~/tmp/params.tar.gz'))
        tar.extractall(path=expanduser('~/tmp/params'))
    return

def verification():
    """Check if hopper is running."""
    
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == "python" and len(p.cmdline()) > 1 and "hopper.py" in p.cmdline()[1]:
            return True
    return False

def store_files():
    """After each execution, write file to cloud storage."""
    
    #TODO: configure storage bucket on instance
    storage_client = storage.Client(project='bt-sfabel')
    bucket = storage_client.get_bucket('clopper-storage')
    files = glob.glob(expanduser('~/output/*.csv'))
    for file in files:
        blob = bucket.blob(file.remove('~/output/'))
        blob.upload_from_filename(file)
        os.remove(file)
    #cmd = '{ for f in out-*.csv; do tail -n+15 "$f"; done } > $HOSTNAME-output.csv'
    #subprocess.Popen(cmd, shell=True)

def has_finished():
    """Trigger file storing if output-directory has files
        and check for more work."""

    if len(glob.glob(expanduser('~/output/*'))) > 0: # files to store
        store_files()
    global _EXECUTIONS
    if len(glob.glob(expanduser('~/tmp/params/*'))) == _EXECUTIONS:
        # shutil.rmtree(expanduser('~/output'))
        # shutil.rmtree(expanduser('~/tmp'))
        return True
    else:
        return False
    
def do_more_work():
    """Check if there is more work to do and call hopper execution."""
    
    global _EXECUTIONS
    if _EXECUTIONS < len(glob.glob(expanduser('~/tmp/params/*'))):
        _EXECUTIONS += 1
        with open(expanduser("~/tmp/params/cl-params-"+ str(_EXECUTIONS) +".txt")) as f:
            cl_params = f.read()
        args = "python ~/hopper/hopper.py " + cl_params
        my_env = os.environ.copy()
        my_env['JAVA_HOME'] = "/usr/lib/jvm/java-8-openjdk-amd64"
        with open(os.devnull, 'w') as fp:
            subprocess.Popen(args, shell=True, env=my_env, stdout=fp)
        return True
    else:
        return False
        
def execute_hopper():
    """ while status is not FINISHED check for pid existing; 
    HOPPER is running if pid exists,
    if no pid, check if output can be written and has finished
    if not: check for more work
    else, status ERROR"""
    
    global _STATE 
    while _STATE != 'FINISHED':
        if verification():
            _STATE = 'HOPPING'
        elif has_finished:
            _STATE = 'FINISHED'
        elif do_more_work():
            _STATE = 'HOPPING'
        else:
            _STATE = 'ERROR'
            # TODO: exit thread?
    print 'Exit thread'

class Clopper(clopper_pb2_grpc.ClopperServicer):
        
    status = 'SLEEPING'
    mode = 'NEW'
    instance_name = socket.gethostname()
    thread = threading.Thread(target=execute_hopper)
    

    def SayHello(self, request, context):        
        self.status = 'RUNNING'
        return clopper_pb2.Greeting(greeting = "Hello from %s" 
                                    % self.instance_name)
        
    def UpdateStatus(self, request, context):
        # TODO: check thread alive?
        global _STATE
        self.status = _STATE
        return clopper_pb2.InstanceUpdate(status=self.status, name=self.instance_name)
     
    def ExecuteHopper(self, request, context):
        if request.trigger == 'HOP':
            print "prepare for hopping now"
            prepare_execution()
            self.thread.start()
            return clopper_pb2.HopResults(status='PREPARING', name=self.instance_name)
        else:
            return clopper_pb2.HopResults(status='ERROR', name=self.instance_name)
    
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    clopper_pb2_grpc.add_ClopperServicer_to_server(Clopper(), server)
    server.add_insecure_port('localhost:8080') # instances are bound to port 8080
    server.start()
    try:
        while True:
            time.sleep(_ONE_MIN_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
  serve()