import re, sys, traceback, math, numpy
from numpy import *
import sys, traceback, datetime, time, math
from datetime import datetime
import logging

class QuestionAnswerInstanceObj(object):
    def __init__(self):
        self.questionAnswerInstance = ''
        self.answerValue = ''
    def __unicode__(self):
        return str(self.questionAnswerInstance)

class ContextObj(object):
    def __init__(self):
        self.questionAnswerInstanceObjList = []
    def __unicode__(self):
        return str(self.questionAnswerInstanceObjList)
    
class QuestionAnswerObj(object):

    def __init__(self):

        self.questionAnswer = ''
        self.question = ''        
        self.ifAnswered = False

        self.answerScore = 0
        self.answerValue = 0 

        self.numAnswers = 0
        self.totalAnswerValue = 0 
        self.totalAnswerValueString = ''         
        
        self.answerTextList = []
        self.answerTextString = ''

        self.answerValueDisplay = 0 
        self.answerText = ''            

        self.isMax = False
        self.printFlag = False
        self.questionAnswerInstanceList = []
        
    def __unicode__(self):
        return str(self.questionAnswer)

class ScoreCardObj(object):
    def __init__(self):
        self.scoreCard = ''
        self.questionAnswerObjList = []
        self.scoreCardScore = 0
        self.scoreCardDescription = ''
        self.isMax = False
        self.printFlag = False
        self.maxScoreCardAnswerValue = 0
    def __unicode__(self):
        return str(self.scoreCard)

class QuestionObj(object):
    def __init__(self):
        self.question = ''
        self.scoreCardObjList = []
        self.questionScore = 0
        self.isMax = False
        self.printFlag = False
        self.numScoreCards = 0
        self.questionAnswerObjList = []
    def __unicode__(self):
        return str(self.question)

class SectionObj(object):
    def __init__(self):
        self.section = ''
        self.questionObjList = []
        self.sectionScore = 0
        self.isMax = False
        self.printFlag = False
        self.contextObjList = []   
        self.numContextObjs = 0        
    def __unicode__(self):
        return str(self.section)

class InstrumentObj(object):
    def __init__(self):
        self.sectionObjList = []
        self.instrumentScore = 0
        self.administration = ''
        self.totalNumContextObjs = 0
    def __unicode__(self):
        return str(self.administration)
    
class StudyInstrumentObj(object):
    def __init__(self):
        self.instrument = []
        self.selectedFlag = []
    def __unicode__(self):
        return str(self.instrument)
    
class StudyObj(object):
    def __init__(self):
        self.study = ''
        self.studyInstrumentObjList = []
    def __unicode__(self):
        return str(self.study)

class UPINObj(object):
    def __init__(self):
        self.upin = ''
        self.administration = ''	
        self.score = ''	
        self.instrumentObj = ''
    def __unicode__(self):
        return str(self.administration)

class SelectionObj(object):
    def __init__(self):
        self.site = ''
        self.study = ''
        self.instrumentAdminsitrator = ''
        self.instrument = ''
        self.diagnosis = ''
        self.encodingFormat = ''
    def __unicode__(self):
        return str(self.site) + " - " + str(self.study)    
    
class UserSummarySelectionObj(object):
    def __init__(self):
        self.startDate = ''
        self.endDate = ''        
        self.sites = []
        self.studies = []
        
        self.selectedSite = ''
        self.selectedStudy = ''
        
        self.instrumentAdministrator = ''
        self.instrumentAdministrators = []        
        self.instrument = ''
        
        self.printSelectionParameters = ''

    def __unicode__(self):
        return str(self.instrumentAdministrator)     
    
class QuestionViewObj(object):
    def __init__(self):
        self.question = ''
        self.isSelected = False
    def __unicode__(self):
        return str(question)    

class ReportDetailObj(object):
    def __init__(self):
        self.columnValues = []
        self.upinId = ''
    def __unicode__(self):
        return str(self.columnValues)        
    
class ReportObj(object):
    def __init__(self):
        self.headerColumns = []
        self.subHeaderColumns = []
        self.questionCounters = []
        self.sectionCounters = []
        self.reportDetailObjList = []	
    def __unicode__(self):
        return str(self.headerColumns)    
    
class ReportOptionsObj(object):
    def __init__(self):
        
        self.reportUpinIds = []
        self.instrumentSections = []
        self.multipleChoiceIds = []
        self.downloadOrPreview = ''
        self.printSelectionParameters = ''

    def __unicode__(self):
        return str(self.reportUpinIds)
    
class GraphReportSelectionsObj(object):
    def __init__(self):

        self.studies = []   
        self.sections = []
        self.instrumentAdministrators = []   
        self.sites = []     
        self.printSelectionParameters = False
        self.displayDemographicsData = False

    def __unicode__(self):
        return str(self.instrumentAdministrators)           
    
class SummaryReportSelectionsObj(object):
    def __init__(self):

        self.studies = []   
        self.instrumentAdministrators = []   
        self.sites = []     
        self.startDate = ''
        self.endDate = ''
        self.printSelectionParameters = False
        
    def __unicode__(self):
        return str(self.instrumentAdministrators)     
    
class SummaryReportObj(object):
    def __init__(self):

        self.monthYearMap = {}
        self.instrumentAdministratorList = []
        self.monthYearList = []
        self.totalAdminCount = 0
        
    def __unicode__(self):
        return str(self.monthYear)     
        
class SummaryReportMonthObj(object):
    def __init__(self):

        self.userMap = {}   
        self.totalMonthAdminCount = 0

    def __unicode__(self):
        return str(self.userMap)     
    
class SummaryReportUserObj(object):
    def __init__(self):

        self.adminCount = 0
        self.adminList = []        

    def __unicode__(self):
        return str(self.adminList)     
    
class SectionSummaryObj(object):
    def __init__(self):
        
        self.section = ''
        self.questionSummaryObjMap = {}

    def __unicode__(self):
        return str(self.section)   
    
class SummaryReportPrintObj(object):
    def __init__(self):

        self.monthYearId = 0
        self.instrumentAdminsitratorId = 0
        self.numAdministrations = 0

    def __unicode__(self):
        return str(self.monthYearId) 
    
class SiteReportPrintObj(object):
    def __init__(self):

        self.site = ''
        self.summaryReportPrintObjList = []
        self.instrumentAdministratorList = []
        self.numInstrumentAdministrators = 0
        self.monthYearList = []
        self.summaryReportObj = ''

    def __unicode__(self):
        return str(self.site) 

class StudyReportPrintObj(object):
    def __init__(self):

        self.study = ''
        self.summaryReportPrintObjList = []
        self.instrumentAdministratorList = []
        self.numInstrumentAdministrators = 0        
        self.monthYearList = []        
        self.summaryReportObj = ''
        
    def __unicode__(self):
        return str(self.study) 
    
class UserReportPrintObj(object):
    def __init__(self):

        self.instrumentAdministrator = ''
        
        self.userStudyReportPrintObjList = []
        self.userSiteReportPrintObjList = []
        
        self.userStudyReportObjMap = {}
        self.userSiteReportObjMap = {}
        
    def __unicode__(self):
        return str(self.instrumentAdministrator) 

class UserReportPrintSummaryObj(object):
    def __init__(self):

        self.userReportPrintObjList = []
        self.userReportSiteList = []
        self.userReportStudyList = []
        
    def __unicode__(self):
        return str(self.userReportPrintObjList) 
    
class UserStudyReportPrintObj(object):
    def __init__(self):

        self.study = ''
        self.totalNumAdministrations = 0        
        self.administrationList = []
        
    def __unicode__(self):
        return str(self.study) 
    
class UserSiteReportPrintObj(object):
    def __init__(self):

        self.site = ''
        self.totalNumAdministrations = 0        
        self.administrationList = []        
        
    def __unicode__(self):
        return str(self.site) 
    
class QuestionSummaryObj(object):
    def __init__(self):
        
        self.question = ''
        self.questionAnswerSummaryObjMap = {}
        self.questionAnswerSummaryObjList = []
        self.totalNumAdministrations = 0
        
    def __unicode__(self):
        return str(self.question)    
    
class QuestionAnswerSummaryObj(object):
    def __init__(self):
        
        self.questionAnswer = ''
        self.questionAnswerIsfitb = False
        self.numAdministrations = 0        
        self.administrationList = []
        self.answerValues = []
        
    def __unicode__(self):
        return str(self.questionAnswer)
    
class UserRoleObj(object):
    def __init__(self):
        
        self.role = ''
        self.isSelected = False
        
    def __unicode__(self):
        return str(self.role) 
    
class UserSiteObj(object):
    def __init__(self):
        
        self.site = ''
        self.isSelected = False
        
    def __unicode__(self):
        return str(self.study) 
    
class UserStudyObj(object):
    def __init__(self):
        
        self.study = ''
        self.isSelected = False
        
    def __unicode__(self):
        return str(self.study) 
    
class UserSectionObj(object):
    def __init__(self):
        
        self.section = ''
        self.isSelected = False
        
    def __unicode__(self):
        return str(self.section)
    
class InstrumentAdministratorObj(object):
    def __init__(self):
        
        self.instrumentAdministrator = ''
        self.displayInList = False
        
        self.signWaiverFlag = False
        self.waiverExpirationDate = ''
        self.waiverStatus = ''
        
        self.administrations = []
        self.numAdministrations = 0 
        self.roleObjList = [] 
        self.studyObjList = [] 
        self.siteObjList = []  
        self.email = ''  
        
    def __unicode__(self):
        return str(self.instrumentAdministrator)