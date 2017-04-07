#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 14:53:48 2017

@author: selin
"""

import random

def distribute (target, total_inst, instance):
    """Calculate random distribution of given target list (versions or tests)."""
    
    if total_inst < instance:
        raise ValueError
    x = len(target)/total_inst
    if total_inst == instance or x==0:
        if x==0:
            random.shuffle(target)
        return target[(instance-1)*x:]
    else:
        return target[(instance-1)*x:instance*x]

def main():
    t = [1,2,3,4,5,6,7,8,9]
    random.shuffle(t)
    print t
    try:
        print distribute(t, 6, 1)
        print distribute(t, 6, 2)
        print distribute(t, 6, 3)
        print distribute(t, 6, 4)
        print distribute(t, 6, 5)
        print distribute(t, 6, 6)
    except ValueError:
        print 'An error occurred'
        
if __name__ == '__main__':
    main()