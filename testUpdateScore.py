import os, re, sys, getopt, traceback, math, numpy
sys.path.append("/Users/mitras/projects/webISTHBat")
os.environ["DJANGO_SETTINGS_MODULE"] = "bat.settings"   
sys.path.append('/WWW/django2/code')
sys.path.append('/WWW/django2/code/batwebapp')
sys.path.append('/usr/local/lib/python2.5/site-packages')
from bat.models import *

if __name__ == "__main__":
  print " *** " + str(sys.argv)
  main(sys.argv[1:])
  
#test()
