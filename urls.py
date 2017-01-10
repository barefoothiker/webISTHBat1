from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.views.generic import TemplateView
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'bat.views.home'),
    (r'^batreports/$', 'bat.views.home'),
    (r'^batreports/landing/$', 'bat.views.landing'),
    (r'^batreports/loginLanding/$', 'bat.views.loginLanding'),
    (r'^batreports/scoreReport/$', 'bat.views.scoreReport'),
    (r'^batreports/listUPINs/$', 'bat.views.listUPINs'),
    (r'^batreports/individualReport/$', 'bat.views.individualReport'),    
    
    (r'^batreports/selectParameters/$', 'bat.views.selectParameters'),    
    (r'^batreports/aggregateReport/$', 'bat.views.aggregateReport'),
    (r'^batreports/downloadReport/$', 'bat.views.downloadReport'),
    
    (r'^batreports/createOutputGraphReport/$', 'bat.views.createOutputGraphReport'),    
    (r'^batreports/previewReport/$', 'bat.views.previewReport'),
    (r'^batreports/createOutputReport/$', 'bat.views.createOutputReport'), 
    (r'^batreports/graphReport/$', 'bat.views.graphReport'), 
    (r'^batreports/outputGraphReport/$', 'bat.views.outputGraphReport'),   
    
    (r'^batreports/displayInstrumentAdministratorList/$', 'bat.views.displayInstrumentAdministratorList'),
    (r'^batreports/displayInstrumentAdministratorDetailList/$', 'bat.views.displayInstrumentAdministratorDetailList'),        

    (r'^batreports/displaySiteList/$', 'bat.views.displaySiteList'),
    (r'^batreports/displayStudyList/$', 'bat.views.displayStudyList'),

    (r'^batreports/editInstrumentAdministrator/$', 'bat.views.editInstrumentAdministrator'),
    (r'^batreports/submitInstrumentAdministrator/$', 'bat.views.submitInstrumentAdministrator'),

    (r'^batreports/addInstrumentAdministrator/$', 'bat.views.addInstrumentAdministrator'),
    (r'^batreports/submitAddInstrumentAdministrator/$', 'bat.views.submitAddInstrumentAdministrator'),

    (r'^batreports/editSite/$', 'bat.views.editSite'),
    (r'^batreports/submitSite/$', 'bat.views.submitSite'),

    (r'^batreports/addSite/$', 'bat.views.addSite'),
    (r'^batreports/submitAddSite/$', 'bat.views.submitAddSite'),

    (r'^batreports/editStudy/$', 'bat.views.editStudy'),
    (r'^batreports/submitStudy/$', 'bat.views.submitStudy'),

    (r'^batreports/addStudy/$', 'bat.views.addStudy'),
    (r'^batreports/submitAddStudy/$', 'bat.views.submitAddStudy'),
    
    (r'^batreports/summaryReport/$', 'bat.views.summaryReport'), 
    (r'^batreports/outputSummaryReport/$', 'bat.views.outputSummaryReport'),     
    (r'^batreports/createOutputSummaryReport/$', 'bat.views.createOutputSummaryReport'),  
    
    (r'^batreports/listUserSiteUPINS/$', 'bat.views.listUserSiteUPINS'),  
    (r'^batreports/listUserStudyUPINS/$', 'bat.views.listUserStudyUPINS'),  
    
    (r'^batreports/submitListUPINSummary/$', 'bat.views.submitListUPINSummary'),  

    (r'^batreports/updateNames/$', 'bat.views.updateNames'), 
    
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
    (r'^admin/', include(admin.site.urls)),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
    (r'^register/', 'bat.views.register'),
    (r'^accounts/', include('registration.urls')),
        
) 
