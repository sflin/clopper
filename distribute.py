#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 14:53:48 2017

@author: selin
"""

import random

def distribute (target, total_inst):
    """Calculate random distribution of given target list (versions or tests)."""
    
    random.shuffle(target)
    x = len(target)/total_inst
    splitted_test_suite = []
    # worst case: 4 elements, 5 instances
    for i in range(total_inst-1):
        if x < 1:
            randoms = random.sample(range(len(target)), len(target))
            rand_list = [target[i] for i in randoms]
            splitted_test_suite.append(rand_list)
        else:
            splitted_test_suite.append(target[i*x:(i+1)*x])
    splitted_test_suite.append(target[(total_inst-1)*x:]) # if odd number - assign the last elements
    return splitted_test_suite
