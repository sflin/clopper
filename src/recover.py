#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 16 10:54:24 2017

@author: selin
"""
import json
import paramiko
import sys
import subprocess

with open(sys.argv[1]) as data_file:
    data = json.load(data_file)
node_dict = data['ip-list']
ports = [node[0].replace('instance-','') for node in node_dict.iteritems()]
for node in node_dict.iteritems():
    ip = node[1]
    key_file = data['-i']
    user = data['username']
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=user, key_filename=key_file)
    client.exec_command("fuser -k 8080/tcp")
    client.close()
for port in ports:
    cmd = "fuser -k 222" + port + "/tcp"
    subprocess.Popen(cmd, shell=True)