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
from django.contrib.auth.models import User

def updateNames():

  try:
  
    f = open ( "name_list.txt" , "r" )
  
    for line in f: 

      data = line.split(",")
      
      instrumentAdministrators = InstrumentAdministrator.objects.filter ( name = data[0] ) 
      
      if len (instrumentAdministrators) > 0 :
        
        instrumentAdministrator = instrumentAdministrators[0]
        
        instrumentAdministrator.name = data[1]
        
        instrumentAdministrator.save()
        
      users = User.objects.filter ( first_name = data[0] ) 
      
      if len (users) > 0 :
        
        user = users[0]
        
        user.first_name = data[1]
        
        user.save()

    f.close()
    
  except:
      traceback.print_exc(file=sys.stdout)
        
updateNames()
  