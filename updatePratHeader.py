import re, sys, traceback, math, numpy
from bat.models import *
from numpy import *
import sys, traceback, datetime, time, math , csv
from datetime import datetime

import logging

from django import forms
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import time, datetime, operator, random

def updateHeader():

  try:
  
    f = open ( "RUBHQ_AMA0692_restricted_multiple.csv" , "r" )
    fout = open ( "outReport.csv" , "w" )

    for i, line in enumerate ( f ):
        data = line.replace("\r","").replace("\t","").split(",")
        
#Study	UPIN	ISTH-BAT	Modified ISTH Score	In database	Calculated Score	Administration Complete / Incomplete	Different from online	Different from DB	Magan's manual score		        
        
        #print " line = " + str ( data )
        if i == 0 or i == 1:
    
          continue
        
        if i > 8:
          
          break
    
        strline = ''
        print " data ******* = " + str ( data )        
        #study = data[0]

        #if i == 7:
          
          #for elem in data:
            
            #if elem != '':

              #elem = elem.replace("MULT","")
              
              #question = Question.objects.get ( pk = int(elem) )
              
              #print ("question id = " + str(elem) + " value = " + str(question.text) )
        
        if i == 8:
          
          for elem in data:
            
            if elem != '':
              
              section = InstrumentSection.objects.get ( pk = int(elem) )
              
              print ("section id = " + str(elem) + " text = " + str(section.name) )
      
    f.close()
    fout.close()
    
  except:
      traceback.print_exc(file=sys.stdout)
        
updateHeader()
  