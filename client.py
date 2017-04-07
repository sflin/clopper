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
import clopper_pb2
import clopper_pb2_grpc

name = 'Leonore'
def run():
    channel = grpc.insecure_channel('localhost:2221')
    channel2 = grpc.insecure_channel('localhost:2222')
    stub = clopper_pb2_grpc.ClopperStub(channel)
    stub2 = clopper_pb2_grpc.ClopperStub(channel2)
    response = stub.SayHello(clopper_pb2.HelloRequest(name=name))
    response2 = stub2.SayHello(clopper_pb2.HelloRequest(name=name))
    print(name + ' received: ' + response.greeting)
    print(name + ' received: ' + response2.greeting)
    print("Requesting for status now...")
    time.sleep(3)
    update = stub.UpdateStatus(clopper_pb2.StatusRequest(request = 'status please!'))
    print("Instance is in status: " + update.status)
    print("Requesting for data of hopper now...")
    time.sleep(3)
    #serverdata = stub.ExecuteHopper(clopper_pb2.HopRequest(trigger='my input'))
    #print("Leonore received data: ")
    #for line in serverdata:
    #    print(line)
    print("Requesting for status now...")
    time.sleep(3)
    update2 = stub.UpdateStatus(clopper_pb2.StatusRequest(request = 'status please!'))
    print("Instance is in status: " + update2.status)

if __name__ == '__main__':
  run()
