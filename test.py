from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.shortcuts import render_to_response
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from hemetrans.models import *
from hemetrans.settings import STATIC_DOC_ROOT
#from hemetrans.utils import *
import os, shutil, json, re
import sys, traceback, datetime, time, math
from datetime import datetime
import logging

ps = Patient.objects.all()

for p in ps:
  print " first name " + p.firstName
  phs = PatientHistory.objects.filter ( patient = p ) 
  for ph in phs:
      print " patient history " + str ( ph.id ) 
      vs = ph.vitalSign.all()
      for v in vs:
          vitalSignValue = VitalSignValue.objects.filter( patientHistory = p, vitalSign = v ) [0]
          print " value " + str ( vitalSignValue.measuredValue ) 
