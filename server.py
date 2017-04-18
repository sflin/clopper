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

_ONE_MIN_IN_SECONDS = 60
def prepare_execution():
    """Unpack project and get CL parametres for hopper execution."""
    
    tar = tarfile.open(expanduser('~/tmp/project.tar.gz')) # remove ~/tmp/project after execution!
    tar.extractall(path=expanduser('~/tmp'))
    tar.close()
    # get CL-arguments for hopper execution
    with open(expanduser('~/tmp/cl-params.txt')) as f:
        cl_params = f.read()
    return cl_params

def verification():
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == "python" and len(p.cmdline()) > 1 and "hopper.py" in p.cmdline()[1]:
            return True
    return False
        
def file_verification():
    for file in os.listdir(expanduser('~/output')):
        print file
        if fnmatch.fnmatch(file, 'serveroutput.csv'):
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
    elif file_verification(): # parse cl_params for -o path
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
        cmd = 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64; echo $JAVA_HOME'
        subprocess.call(cmd, shell=True)
        return clopper_pb2.Greeting(greeting='Hello %s, this is %s' 
                                    % (request.name, self.instance_name))    
        
    def UpdateStatus(self, request, context):
        # TODO: clean up method
        """options = defaultdict(lambda: self.status, 
                                  {'STATUS': (suite, None), 
                                   'STORING': (None, suite)})
        self.status = options[request.request]"""
        if request.request == 'STATUS':
            print self.status
            if self.status == 'RUNNING':
                print 'is running or sleeping'
                return clopper_pb2.InstanceUpdate(status=self.status)
            elif self.status == 'FINISHED':
                print 'has finished'
                return clopper_pb2.InstanceUpdate(status=self.status)
            else:
                answer = check_hopper_status()
                if answer == 'STORING':
                    print 'is storing'
                    self.status = 'FINISHED'
                    return clopper_pb2.InstanceUpdate(status='STORING')
                else:
                    self.status = answer
                    return clopper_pb2.InstanceUpdate(status=self.status)

            

    def ExecuteHopper(self, request, context):
        # TODO: clean up method
        if request.request == 'HOP':
            print 'start for hopping now'
            self.status = 'HOPPING'
            # start hopper
            cl_params = prepare_execution()
            args = "python /home/selin/hopper/hopper.py " + cl_params # check path
            subprocess.Popen(args, shell=True)
            return clopper_pb2.HopResults(data='%s has hopper successfully started' % self.instance_name)
        else:
            return clopper_pb2.HopResults(data='ERR')
    
    
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
