# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 08:08:06 2016

@author: acalvo
"""




def saveText(fileName, text):
    print (fileName,type(fileName))
    f = open(fileName, 'w')
    f.write(text)
    f.close()
    return True
    
def readText(fileName):
    f = open(fileName, 'r')
    text=f.read()
    f.close()
    return text
    
if __name__=="__main__":
    pass
