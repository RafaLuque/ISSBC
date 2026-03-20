# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 11:48:33 2014
Aplicación que se va a desarrollar de acuerdo con la arquitectura
Modelo, Vista, Controlador

@author: acalvo
"""
import sys
from PyQt5.QtWidgets import (QApplication)
import ckVtsCalculadora as vts
app = QApplication(sys.argv) #Crea una aplicación
form = vts.CalculadoraDlg()   #Crea una insytancia del formulario
sys.exit(app.exec_())   #Se inicia la aplicación y se espera eventos