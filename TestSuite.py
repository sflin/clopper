#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 09:02:46 2017

@author: selin
"""
import random

class TestSuite(list):
    
    def __init__(self, content, *args, **kwargs):
        list.__init__(self)
        self.content = content
        
    def randomize(self):
        
        random.shuffle(self)
        return self
    
    def nest(self, seq1, seq2, length):
        for i in xrange(length):
            tmp = TestSuite(content='versiontest')
            tmp.append(seq1[i])
            tmp.append(seq2[i])
            self.append(tmp)
        return self