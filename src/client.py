#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 08:02:54 2017
This is the distributed hopper-extension which runs on the local machine
@author: selin
The Python implementation of the hopperextension.Clopper Client."""

import grpc
import socket
import threading
import clopper_pb2
import clopper_pb2_grpc

def status_request(stub):
    
    for u in stub.UpdateStatus(clopper_pb2.StatusRequest(request='30')):
        if u.status == 'ERROR':
            print "ERROR on " + u.name
        print u.name + ' --- ' + u.status      
    return
 
def initial_greeting(stubs):
    
    host = socket.gethostname()
    responses = [stub.SayHello(clopper_pb2.HelloRequest(request='')) for stub in stubs] # initial greeting request
    for r in responses:
        print host + ' received: ' + r.greeting

def create_stubs(instances):
    
    channels = [grpc.insecure_channel('localhost:222'+str(i)) for i in range(1, instances + 1)] # listen to port 2221 to 222x
    stubs = [clopper_pb2_grpc.ClopperStub(c) for c in channels]
    return stubs

def run(instances, mode='ALL'):
    stubs = create_stubs(instances) 
    initial_greeting(stubs)    

    print "Requesting for data of hopper now..."
    stati = [stub.ExecuteHopper(clopper_pb2.HopRequest(trigger='HOP')) for stub in stubs]
    for s in stati:
        print s.name + ' --- ' + s.status
    # requesting stati from instances
    threads = [threading.Thread(target = status_request, args = (stub,)) for stub in stubs]
    print "Requesting for stati of hopper now..."
    [t.start() for t in threads]
    [thread.join() for thread in threads]
    print 'Shutting down Cloud-Manager-Client'
    return 'FINISHED'
    
if __name__ == '__main__':
    run(1, 'STATUS')
