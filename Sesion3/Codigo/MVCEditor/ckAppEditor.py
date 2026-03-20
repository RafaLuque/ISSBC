# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 08:08:45 2016

@author: acalvo
"""


import os, sys
from PyQt5.QtWidgets import (QApplication)
from os.path import dirname, isdir, isfile, join
from ckVtsEditor import Programa

app=QApplication([])
w=Programa()
w.show()
    
sys.exit(app.exec_())