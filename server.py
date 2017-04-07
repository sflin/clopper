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

import grpc

import clopper_pb2
import clopper_pb2_grpc

_ONE_DAY_IN_SECONDS = 60

class Clopper(clopper_pb2_grpc.ClopperServicer):
    
    status = "SLEEPING"
    instance_name = 'instance-2'

    
    def SayHello(self, request, context):
        self.status = "RUNNING"
        return clopper_pb2.Greeting(greeting='Hello %s, this is instance %s' 
                                    % (request.name, self.instance_name))
        
    def UpdateStatus(self, request, context):
        return clopper_pb2.InstanceUpdate(status=self.status)

    def ExecuteHopper(self, request, context):
        if request.trigger == 'my input':
            self.status = "HOPPING"
            print (self.UpdateStatus(request, context))
            # get project data from client
            
            # generate arguments for hopper
            config = "../../config.xml" # get config from client
            type = "unit" # get type from client: unit or benchmark
            args = "python ../../hopper.py -f " + config + " -o output.csv -t " + type
            #execute hopper
            subprocess.call(args, shell=True)
    
    
def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
  clopper_pb2_grpc.add_ClopperServicer_to_server(Clopper(), server)
  server.add_insecure_port('localhost:8080')
  server.start()
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop(0)

if __name__ == '__main__':
  serve()