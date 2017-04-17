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

_ONE_MIN_IN_SECONDS = 60
def prepare_execution():
    """Unpack project and get CL parametres for hopper execution."""
    
    #cmd = 'tar -xzf project.tar.gz -C ./project'
    #subprocess.call(cmd, shell=True)
    tar = tarfile.open('project.tar.gz')
    tar.extractall(path='project')
    tar.close()
    # get CL-arguments for hopper execution
    with open('cl-params.txt') as f: # check path
        cl_params = f.read()
    return cl_params

def verification():
    for pid in psutil.pids():
        p = psutil.Process(pid)
        # TODO: check filepath
        if p.name() == "python" and len(p.cmdline()) > 1 and "hopper.py" in p.cmdline()[1]:
            return True
    return False
        
def file_verification():
    for file in os.listdir('.'): # check for file in current dir (home-dir)
        if fnmatch.fnmatch(file, 'serveroutput.csv'):
            return True
    else:
        return False
        
def check_hopper_status():
    # HOPPING, STORING, ASLEEP
    # check for pid existing (see stackoverflow); HOPPER is running
    # if no pid, check if output written; STORING
    # nothing, status ERROR
    if verification():
        return 'HOPPING'
    elif file_verification(): # parse cl_params for -o path
        return 'STORING'
    else:
        return 'ERROR'
    
class Clopper(clopper_pb2_grpc.ClopperServicer):
        
    status = "SLEEPING"
    mode = 'NEW'
    instance_name = socket.gethostname()
    cl_params = ''

    def SayHello(self, request, context):
        """Greet local host on start up."""
        self.status = "RUNNING"
        return clopper_pb2.Greeting(greeting='Hello %s, this is %s' 
                                    % (request.name, self.instance_name))    
        
    def UpdateStatus(self, request, context):
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
        elif request.request == 'HOP':
            print 'start for hopping now'
            self.status = 'HOPPING'
            # start hopper
            self.cl_params = prepare_execution()
            # TODO: check file path
            args = "python ../hopper/hopper.py " + self.cl_params # check path
            subprocess.Popen(args, shell=True)
            return clopper_pb2.InstanceUpdate(status=self.status)
            

    def ExecuteHopper(self, request, context):
        # TODO: remove/rename method
        if request.trigger == 'my-input':
            # unpack project
            #self.cl_params = prepare_execution()
            # trigger hopper execution
            #args = "python ../../hopper.py " + cl_params # check path
            #subprocess.call(args, shell=True)
            self.status = "HOPPING"
            #if self.mode == 'ALL' or 'NEW':
                #print (self.UpdateStatus(request.trigger, context))
            return clopper_pb2.HopResults(data='HOPPING')
        else:
            return clopper_pb2.HopResults(data='ERR')
    
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    clopper_pb2_grpc.add_ClopperServicer_to_server(Clopper(), server)
    server.add_insecure_port('localhost:50051') # instances are bound to port 8080
    server.start()
    try:
        while True:
            time.sleep(_ONE_MIN_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
  serve()
