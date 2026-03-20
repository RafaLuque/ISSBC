# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 16:25:14 2014
Modelo de la aplicación. 
Incluye todas las tareas, inferencias y conocimiento del dominio 
que se considera en la aplicación. Puede trabajar de forma 
autónoma independiente de los otros módulos

@author: acalvo
"""

import math

def suma(a,b):
    return a+b
    

def producto(a,b):
    return a*b
    
def resta(a,b):
    return a-b
    
def division(a,b):
    if b!=0:
        return a/b
    else:
        None
        
        
def modulo(a,b):
    m= math.sqrt(a**2+b**2)
    return m
       

if __name__=='__main__':
    a=3.0
    b=4.0
    print (suma(a,b))
    print (producto(a,b))
    print (resta(a,b))
    print (division(a,b))
    print (modulo(a,b))
