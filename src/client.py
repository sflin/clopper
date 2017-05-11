#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 08:02:54 2017
This is the distributed hopper-extension which runs on the local machine
@author: selin
The Python implementation of the hopperextension.Clopper Client."""

import grpc
import threading
import logging
import clopper_pb2
import clopper_pb2_grpc

def status_request(stub):
    #TODO: adapt request-time
    for u in stub.UpdateStatus(clopper_pb2.StatusRequest(request='15')):
        if u.status == 'ERROR':
            logging.critical("ERROR on " + u.name)
        logging.info(u.name + ' --- ' + u.status)      
    return
 
def initial_greeting(stubs):
    
    responses = [stub.SayHello(clopper_pb2.HelloRequest(request='')) for stub in stubs]
    for r in responses:
        logging.info(r.greeting)

def create_stubs(ports):
    channels = [grpc.insecure_channel('localhost:222'+ pn) for pn in ports] # listen to port 2221 to 222x
    stubs = [clopper_pb2_grpc.ClopperStub(c) for c in channels]
    logging.info("Instances connected")
    return stubs

def run(node_dict):
    ports = [node[0].replace('instance-','') for node in node_dict.iteritems()]
    stubs = create_stubs(ports) 
    initial_greeting(stubs) 
    logging.info("Trigger hopper execution...")
    stati = [stub.ExecuteHopper(clopper_pb2.HopRequest(trigger='')) for stub in stubs]
    for s in stati:
        logging.info(s.name + ' --- ' + s.status)
    threads = [threading.Thread(target = status_request, args = (stub,)) for stub in stubs]
    [t.start() for t in threads]
    [thread.join() for thread in threads]
    logging.info("Shutting down cloud-manager-client...")

if __name__ == '__main__':
    run({'instance-1':'1','instance-2':'2'})