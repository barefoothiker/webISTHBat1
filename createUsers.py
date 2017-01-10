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
from bat.models import *
from bat.settings import STATIC_DOC_ROOT
#from hemetrans.utils import *
import os, shutil, json, re
import sys, traceback, datetime, time, math
from datetime import datetime
import logging
from django.contrib.auth.models import User
instrumentAdministrators = InstrumentAdministrator.objects.all()

for i in instrumentAdministrators:
    email = ''
    #if i.email:
        #email = i.email
    #else:
    email = 'smitra@rockefeller.edu'
    
    e = User.objects.filter ( username = str ( i.id) )
    
    if len ( e ) > 0:
        continue
    
    user = User.objects.create_user(i.id, email, i.password)
    user.first_name = i.name
    user.last_name = '.'
    user.save()