#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 08:02:45 2017
This is the implementation of the manager which manages the distributed execution
of hopper (aka clopper) on remote cloud instances. 
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
import fnmatch
from os.path import expanduser
import shutil

_ONE_MIN_IN_SECONDS = 60
_EXECUTIONS = 0
def prepare_execution():
    """Unpack project and get CL parametres for hopper execution."""
    
    try:
        tar = tarfile.open(expanduser('~/tmp/project.tar.gz')) # remove ~/tmp/project after execution!
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
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == "python" and len(p.cmdline()) > 1 and "hopper.py" in p.cmdline()[1]:
            return True
    return False
        
def has_finished():
    try:
        num_files = len(os.listdir(expanduser('~/output')))
    except OSError:
        print "No such directory."
        return False
    global _EXECUTIONS
    if num_files == _EXECUTIONS:
        return True
    else:
        return False
    
def get_work():
    
    try:
        num_files = len(os.listdir(expanduser('~/tmp/params')))
    except OSError:
        return None
    global _EXECUTIONS
    if _EXECUTIONS < num_files:
        _EXECUTIONS += 1
        with open(expanduser('~/tmp/params/cl-params-'+ str(_EXECUTIONS) +'.txt')) as f:
            cl_params = f.read()
        return cl_params
    else:
        return None
    
def do_more_work():
    
    cl_params = get_work()
    if cl_params:
        args = "python ~/hopper/hopper.py " + cl_params # check path
        #args = "python ~/Documents/Uni/Bachelorthesis/hopper/hopper.py " + cl_params
        print args
        my_env = os.environ.copy()
        my_env["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
        with open(os.devnull, 'w') as fp:
            subprocess.Popen(args, shell=True, env=my_env, stdout=fp)
        return True
    else:
        return False
        
    
def check_hopper_status():
    """ status: HOPPING, STORING, ASLEEP
    check for pid existing; HOPPER is running
    if no pid, check if output written; STORING
    nothing, status ERROR"""
    
    if verification():
        return 'HOPPING'
    elif do_more_work():
        return 'HOPPING'
    elif has_finished(): # parse cl_params for -o path
        return 'STORING'
    else:
        return 'ERROR'
    
def get_status(status):
    
    return status
    
class Clopper(clopper_pb2_grpc.ClopperServicer):
        
    status = "SLEEPING"
    mode = 'NEW'
    instance_name = socket.gethostname()

    def SayHello(self, request, context):
        """Greet local host on start up."""
        
        self.status = "RUNNING"
        return clopper_pb2.Greeting(greeting='Hello, this is %s' 
                                    % self.instance_name)
        
    def UpdateStatus(self, request, context):
        # TODO: clean up method
        #    print self.status
        if self.status == 'RUNNING':
            print 'is running or sleeping'
            return clopper_pb2.InstanceUpdate(status=self.status, name=self.instance_name)
        elif self.status == 'FINISHED':
            print 'has finished'
            return clopper_pb2.InstanceUpdate(status=self.status, name=self.instance_name)
        else:
            answer = check_hopper_status()
            if answer == 'STORING':
                print 'is storing'
                self.status = 'FINISHED'
                return clopper_pb2.InstanceUpdate(status='STORING', name=self.instance_name)
            else:
                self.status = answer
                return clopper_pb2.InstanceUpdate(status=self.status, name=self.instance_name)

            

    def ExecuteHopper(self, request, context):
        # TODO: clean up method
        if request.trigger == 'HOP':
            print 'start for hopping now'
            self.status = 'HOPPING'
            # start hopper
            prepare_execution()
            cl_params = get_work()
            args = "python ~/hopper/hopper.py " + cl_params # check path
            #args = "python ~/Documents/Uni/Bachelorthesis/hopper/hopper.py " + cl_params
            print args
            my_env = os.environ.copy()
            my_env["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
            with open(os.devnull, 'w') as fp: # TODO: suppressing log, doesn't work 
                subprocess.Popen(args, shell=True, env=my_env, stdout=fp)
            return clopper_pb2.HopResults(status=self.status, name=self.instance_name)
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
