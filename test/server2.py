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
import tarfile
import grpc
import os
import clopper_pb2
import clopper_pb2_grpc
from os.path import expanduser
import shutil
import glob
import threading

_STATE = 'SLEEPING'
_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_EXECUTIONS = 0

def prepare_execution():
    """Unpack project and get CL parametres for hopper execution."""
    
    try:
        tar = tarfile.open(expanduser('~/tmp-instance-2/project.tar.gz'))
        tar.extractall(path=expanduser('~/tmp-instance-2/project'))
        tar.close()
    except IOError:
        shutil.rmtree(expanduser('~/tmp-instance-2/project'))
        tar = tarfile.open(expanduser('~/tmp-instance-2/project.tar.gz'))
        tar.extractall(path=expanduser('~/tmp-instance-2/project'))
    try:
        tar = tarfile.open(expanduser('~/tmp-instance-2/config.tar.gz'))
        tar.extractall(path=expanduser('~/tmp-instance-2/config'))
        tar.close()
    except IOError:
        shutil.rmtree(expanduser('~/tmp-instance-2/config'))
        tar = tarfile.open(expanduser('~/tmp-instance-2/config.tar.gz'))
        tar.extractall(path=expanduser('~/tmp-instance-2/config'))
    try:
        tar = tarfile.open(expanduser('~/tmp-instance-2/params.tar.gz'))
        tar.extractall(path=expanduser('~/tmp-instance-2/params'))
        tar.close()
    except IOError:
        shutil.rmtree(expanduser('~/tmp-instance-2/params'))
        tar = tarfile.open(expanduser('~/tmp-instance-2/params.tar.gz'))
        tar.extractall(path=expanduser('~/tmp-instance-2/params'))
    return

def has_finished():
    """Check for more work in params-directory."""

    global _EXECUTIONS
    if len(glob.glob(expanduser('~/tmp-instance-2/params/*'))) == _EXECUTIONS:
        return True
    else:
        return False
    
def do_more_work():
    """Get command-line params and call hopper."""
    
    global _EXECUTIONS
    _EXECUTIONS += 1
    with open(expanduser("~/tmp-instance-2/params/cl-params-"+ str(_EXECUTIONS) +".txt")) as f:
        cl_params = f.read()
    args = "python ~/hopper/hopper.py " + cl_params
    my_env = os.environ.copy()
    my_env['JAVA_HOME'] = "/usr/lib/jvm/java-8-openjdk-amd64"
    #replace real process for testing purpose; server1 will execute same work
    proc = subprocess.Popen('ls -l', shell=True, stdout= subprocess.PIPE)
    #proc = subprocess.Popen(args, shell=True, env=my_env, stdout=subprocess.PIPE)
    return proc

def execute_hopper():
    """ Triggers hopper execution and monitors execution and more work to do."""
    
    global _STATE 
    if has_finished():
        _STATE = 'FINISHED'
    else:
        proc = do_more_work()
        _STATE = 'HOPPING'
        time.sleep(2)
    while _STATE != 'FINISHED':
        if proc.poll() == None:
            _STATE = 'HOPPING'
        elif proc.poll() == 1:
            _STATE = 'ERROR'
            proc = do_more_work()
        elif proc.poll() == 0:
            if has_finished():
                _STATE = 'FINISHED'
            else:
                proc = do_more_work()
                _STATE = 'HOPPING'
        else:
            _STATE = 'UNKNOWN'
            
def clean_up():
    subprocess.Popen('fuser -k 2222/tcp', shell=True)
    
class Clopper(clopper_pb2_grpc.ClopperServicer):
        
    status = 'SLEEPING'
    instance_name = 'instance-2'
    thread = threading.Thread(target=execute_hopper)
    

    def SayHello(self, request, context):        
        self.status = 'RUNNING'
        return clopper_pb2.Greeting(greeting = "Hello from %s" % self.instance_name)
        
    def UpdateStatus(self, request, context):
        global _STATE
        counter = 0
        while self.thread.isAlive(): 
            time.sleep(1)
            counter +=1
            if self.status != _STATE or counter % int(request.request) == 0:
                self.status = _STATE
                yield clopper_pb2.InstanceUpdate(status = self.status, name = self.instance_name)
        clean_up()
     
    def ExecuteHopper(self, request, context):
        try:
            prepare_execution()
        except:
            self.status = 'ERROR'
            return clopper_pb2.HopResults(status=self.status, name=self.instance_name)
        self.status = 'PREPARING'
        self.thread.start()
        return clopper_pb2.HopResults(status=self.status, name=self.instance_name)
    
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    clopper_pb2_grpc.add_ClopperServicer_to_server(Clopper(), server)
    server.add_insecure_port('localhost:2222')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
  serve()
