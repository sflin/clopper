#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 14:25:23 2017

@author: selin
"""

import subprocess
import time
import client

def set_up_instance(name, i, ip, to_config=False):
    
    filepath = '/home/selin/Documents/Uni/Bachelorthesis/cloud-configuration.sh'
    #print 'hi from ' + name
    if name=='instance-22':
        print 'ok'
        cmd = 'ssh -L 2222:localhost:8080 selin@' + ip + ' bash -s < ' + filepath
        #cmd = "scp -i ~/.ssh/google_compute_engine " + filepath + " selin@" + ip + ":~" #copy file to remote: not necessary
        subprocess.call(cmd, shell=True) #what does shell=True?
    cmd = "ssh -L 222" + str(i) + ":localhost:8080 selin@" + ip + ' python ./server.py'#replace by name: add ip to config 
    subprocess.Popen(cmd, shell=True) # new shell needed?
    #cmd = "sh cloud-configuration.sh" #check if file exists, add execution-permission
    #subprocess.call(cmd, shell=True)
    #transfer other files

def use_running_instances(cl_params):
    """Connect to running instances via ssh."""    
    # read ips into list, check for credentials
    ip_list = ['35.187.104.248','35.187.101.86'] #, '104.155.80.42']
    for ip, i in zip(ip_list, range(1, len(ip_list)+1)):
        print 'instance-'+ str(i) + ' ip: ' + ip
        set_up_instance('instance-'+ str(i), i, ip, True)
    time.sleep(10)
    client.run()

def run():
    # user prompt: how do you wish to execute hopper: remove this
    cl_params = raw_input("Please enter CL-parametres: ")
    choice = raw_input("How would you like to run hopper? Enter \'r\' for" +
                       "Remote or \'c\' for cloud: ")
    # try and catch?
    if choice == 'r':
        # execute 
        use_running_instances(cl_params)
    #elif choice == 'C':
     #   remote_hopper(cl_params)
    else:
        choice = raw_input("Enter \'L\' for local or \'R\' for remote: ")

if __name__ == '__main__':
  run()