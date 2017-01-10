import re, sys, traceback, math, numpy
from bat.models import *
from numpy import *
import sys, traceback, datetime, time, math , csv
from datetime import datetime
from bat.batReportObjs import *
from bat.utils import *
from bat.batReportConstants import *
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

import openpyxl

ISTH_SCORE_NAME = "ISTH BAT Score"

# Objs for summarising results and display
# In order of hierarchy
# The instrument has sections. 
# Each section has multiple questions. 
# Each question can be associated with multiple scorecards.
# Each scorecard can be associated with multiple answers. 
# The score of a question is the max obtained from different scorecards.

# The flag ifAnswered is set if there is a question answer instance that is present for the answer
# The answer score is populated if present

def createScoreReport():

  try:
  
    f = open ( "ISTH-unit-test_csv.csv" , "r" )
    #ISTH-unit-test-results_1.csv
    fout = open ( "ISTH-unit-test-results_final_out.csv" , "w" )
    reader = csv.reader(f)
    writer = csv.writer(fout, delimiter=",")

    strline = ''
    strline += "Study,"
    strline += "UPIN,"
    strline += "ISTH-BAT,"
    strline += "Modified ISTH Score,"
    strline += "In database,"
    strline += "Calculated Score,"
    strline += "Administration Complete / Incomplete,"  
    strline += "Different from online,"  
    strline += "Different from DB"  
    strline +="\n"
    fout.write(strline  )      

    for i, line in enumerate ( f ):
        data = line.replace("\r","").replace("\t","").split(",")
        
#Study	UPIN	ISTH-BAT	Modified ISTH Score	In database	Calculated Score	Administration Complete / Incomplete	Different from online	Different from DB	Magan's manual score		        
        
        #print " line = " + str ( data )
        if i == 0 or i == 1:
    
          continue
    
        strline = ''
        print " data ******* = " + str ( data )        
        study = data[0]
        strline += study + " , "
        
        upin = int(data[1])
        
        strline += str(upin) + " , "       

        isthBatScore = data[2]

        strline += isthBatScore + " , "   
        
        modifiedIsthBatScore = data[3]   
        
        strline += modifiedIsthBatScore + " , "           
        
        inDatabase = data[4]          

        strline += inDatabase + " , "  
        
        print " upin ******* = " + str ( inDatabase ) 
    
        instrumentObj = calcScore(upin, False, False)
        
        completeFlag = True
        
        if instrumentObj.administration.stop is None:
          completeFlag = False
    
        instrumentScore = sum( [ a.sectionScore for a in instrumentObj.sectionObjList ] )

        strline += str(instrumentScore) + " , "   

       # data.append (str(instrumentScore))
       # print ( " online score = " + str ( data[2]) + " db score = " + str ( data[4]) + " calc score = " + str ( instrumentScore))
       # print " data = " + str ( data )
       # strline = ''
        #for x in data:
          #strline += x +","
        if completeFlag:
          strline += "Complete,"
        else:
          strline += "Not Complete," 

        if instrumentScore != int(data[2]):
          strline += "Different,"
        else:
          strline += ","

        if data[4] != '':  
          if instrumentScore != int(data[4]):
            strline += "Different"
          else:
            strline += ""    
        else:
          strline += ""          
        print " new line for upin " + str ( upin ) 
        strline +="\n"
        fout.write(strline  )
      
    f.close()
    fout.close()
    
  except:
      traceback.print_exc(file=sys.stdout)
        
createScoreReport()
  