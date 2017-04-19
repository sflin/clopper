#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 08:02:54 2017
This is the distributed hopper-extension which runs on the local machine
@author: selin
The Python implementation of the hopperextension.Clopper Client."""

from __future__ import print_function

import grpc
import time
import socket
import clopper_pb2
import clopper_pb2_grpc

name = socket.gethostname()

def status_request(stubs):
    updates = [stub.UpdateStatus(clopper_pb2.StatusRequest(request='')) for stub in stubs]
    running = True
    for u in updates:
        print(u.name + ' --- ' + u.status)
        if running and u.status == 'FINISHED':
            running = False
        elif not running and u.status != 'FINISHED':
            running = True
    return running
        

def initial_greeting(stubs):
    responses = [stub.SayHello(clopper_pb2.HelloRequest(request='')) for stub in stubs] # initial greeting request
    for r in responses:
        print(name + ' received: ' + r.greeting)

def create_stubs(instances):
    
    channels = [grpc.insecure_channel('localhost:5005'+str(i)) for i in range(1, instances + 1)] # listen to port 2221 to 222x
    stubs = [clopper_pb2_grpc.ClopperStub(c) for c in channels]
    return stubs

def run(instances, mode='ALL'):
    #stubs = []
    running = True
    stubs = create_stubs(instances) 
    initial_greeting(stubs)
    # trigger hopper
    
    # start status-concept?
    print("Requesting for status now...")
    running = status_request(stubs)
    time.sleep(3)
    print("Requesting for data of hopper now...")
    data = [stub.ExecuteHopper(clopper_pb2.HopRequest(trigger='HOP')) for stub in stubs]
    running = status_request(stubs)
    while running:
        time.sleep(3)
        running = status_request(stubs)
    return 'FINISHED'
    
if __name__ == '__main__':
  run(2, 'STATUS')
