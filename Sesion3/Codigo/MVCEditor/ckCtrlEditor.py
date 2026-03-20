# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 08:08:25 2016

@author: acalvo
"""

import ckModAppEditor as modAp


def saveEvent(fileName,text):
    modAp.saveText(fileName,text)
    

def saveAsEvent(fileName,text):
    print(fileName,text)
    modAp.saveText(fileName,text)

def readEvent(fileName):
    text=modAp.readText(fileName)
    return text
    
    