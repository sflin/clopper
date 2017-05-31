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
import os

with open(sys.argv[1]) as data_file:
    data = json.load(data_file)
node_dict = data['ip-list']
ports = [node[0].replace('instance-','') for node in node_dict.iteritems()]
for node in node_dict.iteritems():
    ip = node[1]
    key_file = data['ssh-key']
    user = data['username'] if 'username' in data else os.environ.get('USER')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=user, key_filename=key_file)
    client.exec_command("fuser -k 8080/tcp")
    client.exec_command("rm -rf tmp")
    client.exec_command("mkdir ~/tmp")
    client.close()
for port in ports:
    cmd = "fuser -k 222" + port + "/tcp"
    subprocess.Popen(cmd, shell=True)
