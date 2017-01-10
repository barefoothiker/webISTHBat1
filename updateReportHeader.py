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

def createScoreReport():

  try:
  
    f = open ( "ISTH-unit-test_csv.csv" , "r" )
 
        strline +="\n"
        fout.write(strline  )
      
    f.close()
    fout.close()
    
  except:
      traceback.print_exc(file=sys.stdout)
        
createScoreReport()
  