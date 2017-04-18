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

def status_request(stubs, modus='STATUS'):
    updates = [stub.UpdateStatus(clopper_pb2.StatusRequest(request = modus)) for stub in stubs]
    if updates:        
        for u in updates:
            """options = defaultdict(lambda: (u.s, None), 
                              {'STORING': (suite, None), 
                               'FINISHED': (None, suite), 
                               'ERROR': (suite[0], suite[1])})
                return options[u.status]"""
            if u.status == 'STORING':
                #send instance to sleep / disconnect
                print('Grabing results of instance-' + str(updates.index(u) + 1))
                #return True
            elif u.status == 'FINISHED':
                print('Sending instance-'+ str(updates.index(u) + 1) + ' to sleep')
                #return False
            elif u.status == 'ERROR':
                print('Instance-'+ str(updates.index(u) + 1) + ' on status ERROR')
                #return False
            else:
                print("Instance-" + str(updates.index(u) + 1) + " is in status: " + u.status) # get instance name
                #return True
    else:
        print ('error')
        #return False

def initial_greeting(stubs):
    responses = [stub.SayHello(clopper_pb2.HelloRequest(name=name)) for stub in stubs] # initial greeting request
    for r in responses:
        print(name + ' received: ' + r.greeting)

def create_stubs(instances):
    
    channels = [grpc.insecure_channel('localhost:222'+str(i)) for i in range(1, instances + 1)] # listen to port 2221 to 222x
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
    running = status_request(stubs, 'STATUS')
    time.sleep(3)
    print("Requesting for data of hopper now...")
    data = [stub.ExecuteHopper(clopper_pb2.HopRequest(trigger='HOP')) for stub in stubs]
    for d in data:
        print (d)
    running = status_request(stubs, 'HOP')
    time.sleep(3)
    print("Requesting for first status now...")
    running = status_request(stubs, 'STATUS')
    time.sleep(3)
    print("Requesting for second status now...")
    running = status_request(stubs, 'STATUS')
    time.sleep(15)
    print("Requesting for third status now...")
    running = status_request(stubs, 'STATUS')
    time.sleep(15)
    print("Requesting for fourth status now...")
    running = status_request(stubs, 'STATUS')
    time.sleep(15)
    print("Requesting for fifth status now...")
    running = status_request(stubs, 'STATUS')
    time.sleep(15)
    print("Requesting for sixth status now...")
    running = status_request(stubs, 'STATUS')
    time.sleep(15)
    print("Requesting for seventh status now...")
    running = status_request(stubs, 'STATUS')
    time.sleep(15)
    print("Requesting for eigth status now...")
    running = status_request(stubs, 'STATUS')
    time.sleep(20)
    print("Requesting for ninth status now...")
    running = status_request(stubs, 'STATUS')
    time.sleep(15)
    print("Requesting for tenth status now...")
    running = status_request(stubs, 'STATUS')
    """while running:
        time.sleep(3)
        running = status_request(stubs, 'STATUS')
    return 'FINISHED'"""
    

if __name__ == '__main__':
  run(1, 'STATUS')
