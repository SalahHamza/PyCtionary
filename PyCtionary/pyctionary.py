#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    File name: pyctionary.py
    Author: Salah Hamza
    Date created: 09/08/2017
    Date last modified: 01/02/2018
    Python Version: 2.7
'''

from __future__ import print_function
import sys,os
from PyQt4.QtCore import SIGNAL, QObject, Qt
from PyQt4.QtGui import *
from custom_dictionary import *


def path_fixer(path):
    return path.replace('\\','/')

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Getting current working directory
cwd = os.getcwd()

#Assigning absolute path to logo variable to pass it later to QIcon
logo = resource_path(path_fixer(cwd+"\\img\\Wikipedia-icon.png"))




class Window(QMainWindow):
    # __ini__ is like a template, has all the necessities
    def __init__(self):
        super(Window,self).__init__()
        QApplication.setStyle("Plastique")
        self.setWindowTitle("Pyctionary")
        self.setGeometry(50,50,500,300)
        self.form_widget = FormWidget(self)
        self.setWindowIcon(QIcon(logo))
        self.setCentralWidget(self.form_widget)
        

        




class FormWidget(QWidget):

    def __init__(self, parent):        
        super(FormWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)


        self.le = QLineEdit()
        self.le.setObjectName("searchBar")
        

        self.pb = QPushButton()
        self.pb.setObjectName("wiki")
        self.pb.setText("Wikipedia")

        self.pc = QPushButton()
        self.pc.setObjectName("def")
        self.pc.setText("Definition")


        self.textBrowser = QTextBrowser()
        self.textBrowser.setObjectName('textBrowser')



        self.layout.addWidget(self.le)
        self.layout.addWidget(self.pb)
        self.layout.addWidget(self.pc)
        self.layout.addWidget(self.textBrowser)
        self.textBrowser.resize(self.textBrowser.sizeHint())

        self.setLayout(self.layout)

        QObject.connect(self.pb,SIGNAL('clicked()'),
                        self.button_click)
        QObject.connect(self.pc,SIGNAL('clicked()'),
                        self.button_click)


        self.dictionary = Custom_dictionary()






    def button_click(self):
        term = self.le.text()
        #check which button was click and set function
        if self.sender().objectName() == self.pb.objectName():
            func = self.wiki_summary
        else:
            func = self.word_definition
        if term:
            if hasattr(self, 'l_'):
                self.remove_sugg_widgets(self.l_)
            func(term)




    #creates a layout when there is some suggestions (layout is deleted after)
    def suggestion_layout(self,sugg_list,func):
        self.layout_ = QHBoxLayout(self)

        if hasattr(self, 'l_'):
            self.remove_sugg_widgets(self.l_)
        
        self.l_ = []
        
        self.label_ = QLabel('Suggested::')
        self.layout.addWidget(self.label_)
        
        for line in sugg_list:
            button = QToolButton()
            button.setText(str(line))
            button.setObjectName(line)
            button.setStyleSheet("background-color: white")
            self.layout_.addWidget(button)
            button.released.connect(func)
            self.l_.insert(0,button)
        self.layout.addLayout(self.layout_)



    def remove_sugg_widgets(self,l):
        for widget in l:
            self.layout_.removeWidget(widget)
            widget.deleteLater()
        del self.l_
        self.layout.removeItem(self.layout_)
        try:
            self.layout.removeWidget(self.label_)
            self.label_.deleteLater()
        except:
            pass

##    @staticmethod
##    def enc_text(text):
##        try:
##            if isinstance(text,basestring):
##                return text.encode('utf8').strip()
##            else:
##                return unicode(text).encode('utf8').strip()
##        except:
##            return text.encode('utf8','ignore')



    def wiki_button_released(self):
        sending_button = self.sender()
        
        term = str(sending_button.objectName())
        data = self.dictionary.wikipedia_summary(term)

        self.le.setText(term)

        self.print_summary(data)

        i = self.l_.index(sending_button)
        self.l_.pop(i).deleteLater()        
        
        if len(self.l_)==0:
            self.label_.deleteLater()
     



    
    def def_button_released(self):
        sending_button = self.sender()
        term = str(sending_button.objectName())
        text = self.dictionary.meaning(term)

        self.le.setText(term)
        
        if isinstance(text,dict):
            self.print_definition(text,term)
            
        i = self.l_.index(sending_button)
        self.l_.pop(i).deleteLater()
        
        if len(self.l_)==0:
            self.label_.deleteLater()





    def print_summary(self,data):
        if isinstance(data,tuple):
            self.textBrowser.setText("{}".format(data[0]))
            self.suggestion_layout(data[1],self.wiki_button_released)
        elif not data or isinstance(data,list):
            text_ = 'Nothing was found.'
            self.textBrowser.setText(text_)
            if isinstance(data,list):
                self.suggestion_layout(data,self.wiki_button_released)
                
        else:
            self.textBrowser.setOpenExternalLinks(True)
            self.textBrowser.setText("Term::  <a href='{0}'>{1}</a>".format(data.url,data.title))
            text_ ="\n\nSummary:\n{}\n\n".format(
                data.summary.encode('ISO 8859-1','ignore'))
            self.textBrowser.append(text_)
            
            



    def print_definition(self,meaning_,word):
        if isinstance(meaning_,dict):
            text_ = '{}::\n'.format(str(word).capitalize())
            self.textBrowser.setText(text_)
            for (key,value) in meaning_.iteritems():
                text_ = '{}:'.format(key)
                self.textBrowser.append('{}:'.format(key))
                for count,m in enumerate(value):
                    self.textBrowser.append('{0}. {1}.'.format(count+1,m))
            text_ = self.dictionary.synonym(word)
            self.textBrowser.append('\nSynonyms: {};'.format(", ".join(text_)))
            text_ = self.dictionary.antonym(word)
            
            self.textBrowser.append('\nAntonyms: {};'.format(", ".join(text_)))
        elif isinstance(meaning_,list):
            self.textBrowser.setText("Nothing was found.")
            self.suggestion_layout(meaning_,self.def_button_released)
        else:
            self.textBrowser.setText(meaning_)



    def wiki_summary(self,word):
        self.summary = self.dictionary.wikipedia_summary(str(word).capitalize())
        self.print_summary(self.summary)
        

    def word_definition(self,word):
        self.definition = self.dictionary.meaning(str(word))
        self.print_definition(self.definition,word)

def main():
    app = QApplication([])
    app.setStyleSheet("QMainWindow{background-color: LightSteelBlue ;border: 1px solid black;}")
    main_wind = Window()
    
    #p = main_wind.palette()
    #main_wind.setStyleSheet("QMainWindow{background-color: DarkSlateGray;border: 1px solid black;QPushButton-color: white;}")
    #p.setColor(main_wind.backgroundRole(), Qt.darkCyan)
    #main_wind.setPalette(p)
    #main_wind.setWindowFlags(Qt.FramelessWindowHint)
    
    main_wind.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
