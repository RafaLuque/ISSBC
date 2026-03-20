#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
Created on Sat Jan 18 11:29:53 2014
Las vistas de la aplicaci�n. 
Corresponde al interfaz de usuario. 
@author: acalvo
"""


import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QLineEdit,QHBoxLayout, 
                             QVBoxLayout, QGridLayout, QApplication)
import ckControladorCalculadora as ctrl


class CalculadoraDlg(QWidget):
    def __init__(self):
        super(CalculadoraDlg, self).__init__()
        
        #Label Se crean las etiquetas
        labelPrimerDato=QLabel("A:",self)  
        labelSegundoDato=QLabel("B:",self)
        labelResultadoDato=QLabel("R:",self)
        #labelOperador=QtGui.QLabel(u"Operacion",self)
        
        #Entradas Se crean los controles para la entrada de datos
        self.aEdit = QLineEdit()
        self.bEdit = QLineEdit()
        self.rEdit = QLineEdit()
        self.explicacionEdit=QLineEdit()
       
        #Botones 
        self.sumaButtom=QPushButton('+')
        self.restaButtom=QPushButton('-')
        self.productoButtom=QPushButton('*') 
        self.divisionButtom=QPushButton('/')
        self.moduloButtom=QPushButton('M')
        
        #Se crea un gestor de distribuci�n de controles horizontal
        self.buttomsLayout = QHBoxLayout()
        self.buttomsLayout.addStretch()
        # Ver http://stackoverflow.com/questions/20452754/how-exactly-does-addstretch-work-in-qboxlayout
        # Ver https://qt-project.org/doc/qt-4.8/layout.html
        self.buttomsLayout.addWidget(self.sumaButtom)
        self.buttomsLayout.addWidget(self.restaButtom)
        self.buttomsLayout.addWidget(self.productoButtom)
        self.buttomsLayout.addWidget(self.divisionButtom)
        self.buttomsLayout.addWidget(self.moduloButtom)
        self.buttomsLayout.addStretch()
        
        #Rejilla de distribuci�n de los controles
        grid = QGridLayout()
        grid.setSpacing(5)
        grid.addWidget(labelPrimerDato, 0, 0)
        grid.addWidget(self.aEdit, 0, 1)
        grid.addWidget(labelSegundoDato, 1, 0)
        grid.addWidget(self.bEdit, 1, 1)
        grid.addWidget(labelResultadoDato, 2, 0)
        grid.addWidget(self.rEdit, 2, 1)
        grid.addWidget(self.explicacionEdit,3,0,1,2)


        #Dise�o principal de distribuci�n de controles
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(grid)
        mainLayout.addLayout(self.buttomsLayout)
        
        self.setLayout(mainLayout)
        
    
        self.setGeometry(150, 100, 100, 100)
        self.setWindowTitle(u"CALCULADORA")
        self.show()
 
        #self.center()
        #Conexiones:
        #==========
        self.sumaButtom.clicked.connect(self.sumar)
        self.restaButtom.clicked.connect(self.restar)
        self.productoButtom.clicked.connect(self.multiplicar)
        self.divisionButtom.clicked.connect(self.dividir)
        self.moduloButtom.clicked.connect(self.modulo)

    #
    def getDatos(self):
        self.explicacionEdit.clear()
        a=float(self.aEdit.text())
        b=float(self.bEdit.text())
        return a,b

    def sumar(self):
        a,b=self.getDatos()
        r=ctrl.eventSumar(a,b)
        self.rEdit.setText(str(r))

    def restar(self):
        
        a,b=self.getDatos()
        r=ctrl.eventRestar(a,b)
        self.rEdit.setText(str(r))
         

    def multiplicar(self):
        a,b=self.getDatos()
        r=ctrl.eventMultiplicar(a,b)
        self.rEdit.setText(str(r))
         
    def dividir(self):
        a,b=self.getDatos()
        r=ctrl.eventDividir(a,b)
        if not r==None:
            self.rEdit.setText(str(r))
        else:
            self.rEdit.clear()
            self.explicacionEdit.setText('Divisi�n por cero')
            
    def modulo(self):
        a,b=self.getDatos()
        r=ctrl.eventModulo(a,b)
        self.rEdit.setText(str(r))
        
if __name__ == "__main__":
    #ob=bccf.Objeto('ob1',[bccf.Atributo('diametro','int',29,'cm'),bccf.Atributo('peso','int',160,'gr'), bccf.Atributo('color','str','amarillo',None)])
    app = QApplication(sys.argv)
    form = CalculadoraDlg()
    sys.exit(app.exec_())


 