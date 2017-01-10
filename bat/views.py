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
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from bat.models import *
from bat.settings import STATIC_DOC_ROOT
import bat.utils
from bat.utils import *
import csv
import urllib

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/registration/")
    else:
        form = UserCreationForm()
    return render_to_response("registration/register.html", {
        'form': form,
    })

@login_required
def landing(request):

    batreportsHomeButton = request.POST.get('batreportsHomeButton', "0")

    if batreportsHomeButton == "0":
        return home( request )
    if batreportsHomeButton == "1":
        return selectParameters( request )
    elif batreportsHomeButton == "4":
        return listUPINs ( request )
    elif batreportsHomeButton == "2":
        return graphReport ( request )
    elif batreportsHomeButton == "3":
        return individualReport ( request )

@login_required
def updateNames(request):

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

    return render_to_response('batreports/landing.html', {

    })

@login_required
def scoreReport(request):
    selectedMenu = "Individual"
    try:
        upinId = request.POST.get('upinId', "0")

        scoreReportScreen = request.POST.get('scoreReportScreen', "0")
        #print " scoreReportScreen " + str (scoreReportScreen)
        try:
            #print " for upin id " + str (upinId)
            upin = UPIN.objects.get ( pk = int(upinId))
        except :
            traceback.print_exc(file=sys.stdout)
            messages.add_message(request, messages.ERROR, 'Invalid UPIN ' + str(upinId) + '. Please enter a valid UPIN.')

            if  scoreReportScreen == "0" :
                return listUPINs ( request )
            else:
                return individualReport ( request )

        fetchQuestionAnswerFlag = True

        fetchContextsFlag = True

        instrumentObj = calcScore(upinId, fetchQuestionAnswerFlag, fetchContextsFlag)

        print " scores are " + str([ a.sectionScore for a in instrumentObj.sectionObjList ] )

        instrumentObj.instrumentScore = sum( [ a.sectionScore for a in instrumentObj.sectionObjList ] )

        instrumentObj.totalNumContextObjs = sum( [ a.numContextObjs for a in instrumentObj.sectionObjList ] )

    except:
        traceback.print_exc(file=sys.stdout)
        messages.add_message(request, messages.ERROR, 'Error occurred while fetching score for ' + str(upinId) )

    return render_to_response('batreports/scoreReport.html', {
        'upin': upin,
        'instrumentObj': instrumentObj,
        'selectedMenu': selectedMenu,
        'user':request.user
    })

def fetchSummaryUPINSiteListObjs(request):

    upinObjList = []

    userSummarySelectionObj = UserSummarySelectionObj()

    startDateString = request.POST.get('startDate', 0 )
    endDateString = request.POST.get('endDate', 0 )

    studyIds = request.POST.getlist('studyId' )

    #print " fetching summary site information for study ids " + str(studyIds)

    siteIds = request.POST.getlist('siteId' )

    selectedSiteId = request.POST.get('selectedSiteId', 0 )

    siteOrStudySelectionFlag = request.POST.get('siteOrStudySelectionFlag', '0' )

    selectedInstrumentAdministratorId = request.POST.get('selectedInstrumentAdministratorId', 0 )

    instrumentAdministratorIds = request.POST.getlist('instrumentAdministratorId' )

    printSelectionParameters = request.POST.getlist('printSelectionParameters' )

    for instrumentAdministratorId in instrumentAdministratorIds:
        instrumentAdministrator = InstrumentAdministrator.objects.get ( pk = instrumentAdministratorId)
        userSummarySelectionObj.instrumentAdministrators.append(instrumentAdministrator)

    for studyId in studyIds:
        study = Study.objects.get ( pk = studyId)
        userSummarySelectionObj.studies.append(study)

    for siteId in siteIds:
        site = Site.objects.get ( pk = siteId)
        userSummarySelectionObj.sites.append(site)

    selectedSite = Site.objects.get ( pk = selectedSiteId )

    userSummarySelectionObj.selectedSite = selectedSite

    instrumentAdministrator = InstrumentAdministrator.objects.get ( pk = selectedInstrumentAdministratorId )

    userSummarySelectionObj.instrumentAdministrator = instrumentAdministrator

    userSummarySelectionObj.startDate = startDateString
    userSummarySelectionObj.endDate = endDateString

    batInstrument = Instrument.objects.filter ( title = ISTH_BAT_INSTRUMENT)

    startDate = datetime.datetime.strptime(startDateString, "%m/%d/%Y")

    if endDateString != "":
        endDate = datetime.datetime.strptime(endDateString, "%m/%d/%Y")
    else:
        endDate = datetime.datetime.now()

    startMonth = startDate.month
    startYear = startDate.year

    year = startYear
    month = startMonth

    endMonth = endDate.month
    endYear = endDate.year

    #print "start date " + str ( startDateString ) + " end date " + str ( endDateString ) + " instrumentAdministratorId = " + str (instrumentAdministrator.id) + " selectedsiteIds = " + str ( selectedSiteId ) + " studyId = " + str ( studyIds )

    allowedSites = instrumentAdministrator.allowed_sites.all()

    administrations = Administration.objects.filter (start__range = [startDate, endDate ],stop__range = [startDate, endDate ] , instrumentadministrator = instrumentAdministrator, site__in = allowedSites)

    #print " num found = " + str (len (administrations))

    userId = int (request.user.username)

    roleId = instrumentAdministrator.role.id

    allowedStudies = instrumentAdministrator.allowed_studies.all()

    for administration in administrations:

        #if administration.site not in allowedSites.all():
            #continue

        if str(administration.site.id) != selectedSiteId:
            continue

        upin = administration.upin

        #print " allowed studies = " + str (allowedStudies.all())

        if upin.study not in allowedStudies.all():
            continue

        #print " for admin " + str (administration) + " site = " + str (selectedSiteId) + " studies " + str (studyIds) + " study id = " + str (administration.upin.study.id)

        if str(upin.study.id) not in studyIds:
            continue

        #print " ** after studies "

        authorizedRole = False

        if (roleId == 1003 and upin.created_by == instrumentAdministrator) or (instrumentAdministrator.role.id == 1001 or instrumentAdministrator.role.id == 1002) :
            authorizedRole = True

        if not authorizedRole:
            continue

        upinObj = UPINObj()

        upinObj.upin = upin

        upinObj.administration = administration

        upinObjList.append ( upinObj )

    return upinObjList, userSummarySelectionObj, siteOrStudySelectionFlag

@login_required
def listUserSiteUPINS(request):

    selectedMenu = "Summary"

    upinObjList, userSummarySelectionObj, siteOrStudySelectionFlag = fetchSummaryUPINSiteListObjs (request)

    return render_to_response('batreports/listSummaryUPINs.html', {
            'upinObjList': upinObjList,
            'selectedMenu': selectedMenu,
            'userSummarySelectionObj':userSummarySelectionObj,
            'siteOrStudySelectionFlag':siteOrStudySelectionFlag,
            'user':request.user
            },
    context_instance=RequestContext(request))

@login_required
def submitListUPINSummary(request):

    submitListUpinSummaryButton = request.POST.get('submitListUpinSummaryButton', '0' )

    if submitListUpinSummaryButton == '0':
        return outputSummaryReport(request)
    elif submitListUpinSummaryButton == '1':
        return downloadListUPINSummary(request)

def fetchSummaryUPINStudyListObjs(request):

    upinObjList = []

    userSummarySelectionObj = UserSummarySelectionObj()

    startDateString = request.POST.get('startDate', 0 )
    endDateString = request.POST.get('endDate', 0 )

    siteIds = request.POST.getlist('siteId' )
    studyIds = request.POST.getlist('studyId' )

    selectedStudyId = request.POST.get('selectedStudyId', 0 )

    siteOrStudySelectionFlag = request.POST.get('siteOrStudySelectionFlag', '0' )

    selectedInstrumentAdministratorId = request.POST.get('selectedInstrumentAdministratorId', 0 )

    instrumentAdministratorIds = request.POST.getlist('instrumentAdministratorId' )

    for siteId in siteIds:
        site = Site.objects.get ( pk = siteId)
        userSummarySelectionObj.sites.append(site)

    for studyId in studyIds:
        study = Study.objects.get ( pk = studyId)
        userSummarySelectionObj.studies.append(study)

    for instrumentAdministratorId in instrumentAdministratorIds:
        instrumentAdministrator = InstrumentAdministrator.objects.get ( pk = instrumentAdministratorId)
        userSummarySelectionObj.instrumentAdministrators.append(instrumentAdministrator)

    selectedStudy = Study.objects.get ( pk = selectedStudyId)

    userSummarySelectionObj.selectedStudy = selectedStudy

    instrumentAdministrator = InstrumentAdministrator.objects.get ( pk = selectedInstrumentAdministratorId )

    userSummarySelectionObj.instrumentAdministrator = instrumentAdministrator

    userSummarySelectionObj.startDate = startDateString
    userSummarySelectionObj.endDate = endDateString

    #print "start date " + str ( startDateString ) + " end date " + str ( endDateString ) + " instrumentAdministrator = " + str (instrumentAdministrator.id) + " siteIds = " + str ( siteIds ) + " selectedStudyId = " + str ( selectedStudyId )

    batInstrument = Instrument.objects.filter ( title = ISTH_BAT_INSTRUMENT)

    startDate = datetime.datetime.strptime(startDateString, "%m/%d/%Y")
    if endDateString != "":
        endDate = datetime.datetime.strptime(endDateString, "%m/%d/%Y")
    else:
        endDate = datetime.datetime.now()

    startMonth = startDate.month
    startYear = startDate.year

    year = startYear
    month = startMonth

    endMonth = endDate.month
    endYear = endDate.year

    administrations = Administration.objects.filter (start__range = [startDate, endDate ],stop__range = [startDate, endDate ] , instrumentadministrator = instrumentAdministrator)

    #print " num found = " + str (len (administrations))

    userId = int (request.user.username)

    roleId = instrumentAdministrator.role.id

    allowedSites = instrumentAdministrator.allowed_sites.all()
    allowedStudies = instrumentAdministrator.allowed_studies.all()

    for administration in administrations:

        #print " for admin " + str (administration) + " site = " + str (selectedStudyId) + " studies " + str (siteIds)

        if administration.site not in allowedSites.all():
            continue

        if str(administration.site.id) not in siteIds:
            continue

        upin = administration.upin

        if upin.study not in allowedStudies.all():
            continue

        if str(upin.study.id) != selectedStudyId :
            continue

        authorizedRole = False

        if (roleId == 1003 and upin.created_by == instrumentAdministrator) or (instrumentAdministrator.role.id == 1001 or instrumentAdministrator.role.id == 1002) :
            authorizedRole = True

        if not authorizedRole:
            continue

        upinObj = UPINObj()

        upinObj.upin = upin

        upinObj.administration = administration

        upinObjList.append ( upinObj )

    return upinObjList, userSummarySelectionObj, siteOrStudySelectionFlag

@login_required
def listUserStudyUPINS(request):

    selectedMenu = "Summary"

    userSummarySelectionObj = UserSummarySelectionObj()

    upinObjList, userSummarySelectionObj, siteOrStudySelectionFlag = fetchSummaryUPINStudyListObjs (request)

    return render_to_response('batreports/listSummaryUPINs.html', {
            'upinObjList': upinObjList,
            'selectedMenu': selectedMenu,
            'userSummarySelectionObj':userSummarySelectionObj,
            'siteOrStudySelectionFlag':siteOrStudySelectionFlag,
            'user':request.user
            },
    context_instance=RequestContext(request))


@login_required
def listUPINs(request):

    selectedMenu = "Single"
    upinObjList = []

    batInstrument = Instrument.objects.filter ( title = ISTH_BAT_INSTRUMENT)

    #administrations = Administration.objects.filter ( instrument = batInstrument ).exclude(stop__isnull = True )
    administrations = Administration.objects.filter ( instrument = batInstrument )
    userId = int (request.user.username)

    instrumentAdministrator = InstrumentAdministrator.objects.get ( pk = userId)

    roleId = instrumentAdministrator.role.id

    allowedSites = instrumentAdministrator.allowed_sites.all()
    allowedStudies = instrumentAdministrator.allowed_studies.all()

    for administration in administrations:

        if administration.site not in allowedSites.all():
            continue

        upin = administration.upin

        if upin.study not in allowedStudies.all():
            continue

        authorizedRole = False

        if (roleId == 1003 and upin.created_by == instrumentAdministrator) or (instrumentAdministrator.role.id == 1001 or instrumentAdministrator.role.id == 1002) :
            authorizedRole = True

        if not authorizedRole:
            continue

        upinObj = UPINObj()

        upinObj.upin = upin

        upinObj.administration = administration

        upinObjList.append ( upinObj )

    return render_to_response('batreports/listUPINs.html', {
            'upinObjList': upinObjList,
            'selectedMenu': selectedMenu,
            'user':request.user
            },
            context_instance=RequestContext(request))

@login_required
def selectParameters(request):
    selectedMenu = "Aggregate"
    try:

        studies = Study.objects.all ().order_by("name")

        users = User.objects.all()

        userId = int(request.user.username)

        instrumentAdministrator = InstrumentAdministrator.objects.get ( pk = userId)

        allowedSites = instrumentAdministrator.allowed_sites.all().order_by("name")
        allowedStudies = instrumentAdministrator.allowed_studies.all().order_by("name")

        instrumentAdministratorList = []

        instrumentAdministrators = InstrumentAdministrator.objects.all ()

        for instrumentAdministrator in instrumentAdministrators :
            allowedSites2 = instrumentAdministrator.allowed_sites.all()
            allowedStudies2 = instrumentAdministrator.allowed_studies.all()

            waiverOkFlag = getWaiverOkFlag (instrumentAdministrator)

            if not waiverOkFlag :
                continue

            if any ( i in allowedSites for i in allowedSites2) and any ( i in allowedStudies for i in allowedStudies2)  :
                instrumentAdministratorList.append ( instrumentAdministrator )

        instrumentAdministratorList.sort(key=lambda x: x.name)


        print " ISTH_BAT_INSTRUMENT " + (ISTH_BAT_INSTRUMENT)


        batInstrument = Instrument.objects.filter ( title = ISTH_BAT_INSTRUMENT) [0]

        instruments = []
        instruments.append ( batInstrument )

        diagnoses = Diagnosis.objects.all()

        encodingFormats = ["Text", "Numerical"]

    except:
        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/selectParameters.html', {

        'studies': studies,
        'instrumentAdministratorList': instrumentAdministratorList,
        'allowedSites': allowedSites,
        'allowedStudies': allowedStudies,
        'instruments': instruments,
        'diagnoses': diagnoses,
        'encodingFormats': encodingFormats,
        'selectedMenu': selectedMenu,
        'user':request.user

    })
@login_required
def graphReport(request):
    selectedMenu = "Graph"
    try:

        studyList = Study.objects.all ().order_by("name")

        batInstrument = Instrument.objects.filter ( title = ISTH_BAT_INSTRUMENT) [0]

        studies = []

        for study in studyList:

            if batInstrument in study.instruments.all():

                studies.append(study)

        sites = Site.objects.all ().order_by("name")

        userId = int(request.user.username)

        instrumentAdministrator = InstrumentAdministrator.objects.get ( pk = userId)

        allowedSites = instrumentAdministrator.allowed_sites.all().order_by("name")
        allowedStudies = instrumentAdministrator.allowed_studies.all().order_by("name")

        instrumentAdministratorList = []

        instrumentAdministrators = InstrumentAdministrator.objects.all ()

        for instrumentAdministrator in instrumentAdministrators :
            allowedSites2 = instrumentAdministrator.allowed_sites.all()
            allowedStudies2 = instrumentAdministrator.allowed_studies.all()

            waiverOkFlag = getWaiverOkFlag (instrumentAdministrator)

            if not waiverOkFlag :
                continue

            if any ( i in allowedSites for i in allowedSites2) and any ( i in allowedStudies for i in allowedStudies2)  :
                instrumentAdministratorList.append ( instrumentAdministrator )

        instrumentAdministratorList.sort(key=lambda x: x.name)

        sections = InstrumentSection.objects.filter(instrument = batInstrument).order_by("name")

    except:
        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/graphReport.html', {

        'studies': studies,
        'instrumentAdministratorList': instrumentAdministratorList,
        'sites': sites,
        'sections': sections,
        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def outputGraphReport(request):

    sectionSummaryObjMap = {}

    demographicsSectionSummaryObjMap = {}

    graphReportSelectionsObj = GraphReportSelectionsObj ()

    selectedMenu = "Graph"

    try:

        barOrPieChart = request.POST.get('barOrPieChart','0' )

        sectionSummaryObjMap, demographicsSectionSummaryObjMap, graphReportSelectionsObj = createGraphReportObj(request)

    except:
        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/outputGraphReport.html', {

        'sectionSummaryObjMap': sectionSummaryObjMap,
        'demographicsSectionSummaryObjMap':demographicsSectionSummaryObjMap,
        'graphReportSelectionsObj':graphReportSelectionsObj,
        'barOrPieChart':barOrPieChart,
        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def aggregateReport(request):

    selectedMenu = "Aggregate"

    selectionObj = getSelectionObj(request)

    # do not fetch questions and answers for this - only need score
    fetchQuestionAnswerFlag = False

    print " 1 - before getting upin obj list (aggregate report) " + strftime("%H:%M:%S",gmtime())

    upinObjList = getUPINObjList(selectionObj, fetchQuestionAnswerFlag)

    print " 2 - after getting upin obj list (aggregate report) " + strftime("%H:%M:%S",gmtime())

    instrumentSections = InstrumentSection.objects.filter ( instrument = selectionObj.instrument )

    questions = Question.objects.all()

    questionViewObjList = []

    for question in questions:

        questionViewObj = QuestionViewObj()

        questionViewObj.question = question

        if question.id in DEFAULT_MULTIPLE_CHOICE_REPORT_QUESTION_IDS:
            questionViewObj.isSelected = True

        questionViewObjList.append ( questionViewObj )

    return render_to_response('batreports/aggregateReport.html', {
        'upinObjList': upinObjList,
        'instrumentSections' : instrumentSections,
        'selectionObj' : selectionObj,
        'questionViewObjList' : questionViewObjList,
        'selectedMenu': selectedMenu,
        'user':request.user

        },
    context_instance=RequestContext(request))

def home(request):
    selectedMenu = "Home"
    return render_to_response('batreports/landing.html', {
        'selectedMenu': selectedMenu,
        'user':request.user
            })
@login_required
def loginLanding(request):
    selectedMenu = "Home"
    return render_to_response('batreports/landing.html', {
        'selectedMenu': selectedMenu,
        'user':request.user
            })

@login_required
def downloadReport(request):

    print " 1 - in download report " + strftime("%H:%M:%S", gmtime())

    reportOptionsObj = getReportOptionsObj (request )

    downloadOrPreview = reportOptionsObj.downloadOrPreview

    if downloadOrPreview == "0":
        print " 2 - in create output report" + strftime("%H:%M:%S", gmtime())
        return createOutputReport (request)
    elif downloadOrPreview == "1":
        print " 2 - in preview report" + strftime("%H:%M:%S", gmtime())
        selectionObj = getSelectionObj(request)
        fetchQuestionAnswerFlag = True
        upinObjList = getUPINObjList(selectionObj, fetchQuestionAnswerFlag)

        return previewReport (upinObjList, selectionObj, reportOptionsObj, request)

def previewReport(upinObjList, selectionObj, reportOptionsObj, request):

    print " 4 - before get report obj " + strftime("%H:%M:%S", gmtime())

    reportObj = getReportObj(upinObjList, selectionObj, reportOptionsObj)

    print " 5 - after get report obj " + strftime("%H:%M:%S", gmtime())

    selectedMenu = "Aggregate"

    return render_to_response('batreports/previewReport.html', {
        'reportObj' : reportObj,
        'selectionObj' : selectionObj,
        'reportDate' : datetime.datetime.now().strftime("%a, %d %b %H:%M:%S %Y"),
        'reportOptionsObj': reportOptionsObj,
        'selectedMenu': selectedMenu,
        'user':request.user
        },
        context_instance=RequestContext(request))

@login_required
def createOutputReport(request):

    downloadOrCancel = request.POST.get('downloadOrCancel', "0")

    if downloadOrCancel == "1":
        return aggregateReport (request)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="AggregateReport.csv"'

    selectionObj = getSelectionObj(request)

    fetchQuestionAnswerFlag = True

    print " 3 - before getting upin obj list " + strftime("%H:%M:%S",gmtime())

    upinObjList = getUPINObjList(selectionObj, fetchQuestionAnswerFlag)

    print " 4 - after getting upin obj list " + strftime("%H:%M:%S",gmtime())

    reportOptionsObj = getReportOptionsObj (request )

    print " 5 - after getting report options obj list " + strftime("%H:%M:%S",gmtime())

    reportObj = getReportObj(upinObjList, selectionObj, reportOptionsObj)

    print " 6 - after getting report obj list " + strftime("%H:%M:%S",gmtime())

    writer = csv.writer(response,delimiter=",")

    rowData = [str (datetime.datetime.now().strftime("%a, %d %b %H:%M:%S %Y"))]
    writer.writerow(rowData)

    if reportOptionsObj.printSelectionParameters:

        rowData = [str ( selectionObj.site)]
        writer.writerow(rowData)
        rowData = [str ( selectionObj.instrumentAdministrator)]
        writer.writerow(rowData)
        rowData = [str ( selectionObj.study)]
        writer.writerow(rowData)
        rowData = [str ( selectionObj.instrument)]
        writer.writerow(rowData)
        rowData = [str ( selectionObj.diagnosis)]
        writer.writerow(rowData)
        rowData = [str ( selectionObj.encodingFormat)]
        writer.writerow(rowData)

    rowData = ["","","",""]

    for questionCounter in reportObj.questionCounters:
        rowData.append(str(questionCounter))

    writer.writerow(rowData)

    rowData = ["","","",""]

    for sectionCounter in reportObj.sectionCounters:
        rowData.append(str(sectionCounter))

    writer.writerow(rowData)

    rowData = ["PID","SiteID","Admin","PriTime"]

    for headerColumn in reportObj.headerColumns:
        rowData.append(str(headerColumn))

    writer.writerow(rowData)

    rowData = ["","","",""]

    for subHeaderColumn in reportObj.subHeaderColumns:
        rowData.append(str(subHeaderColumn))

    writer.writerow(rowData)

    for reportDetailObj in reportObj.reportDetailObjList:

        rowData = []

        for columnValue in reportDetailObj.columnValues:
            rowData.append(str(columnValue))

        writer.writerow(rowData)

    return response

@login_required
def createOutputGraphReport(request):

    submitButton = request.POST.get('submitButton', "0")

    if submitButton == "0":
        return graphReport (request)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="GraphReportData.csv"'

    sectionSummaryObjMap, demographicsSectionSummaryObjMap, graphReportSelectionsObj   = createGraphReportObj(request)

    writer = csv.writer(response,delimiter=",")

    rowData = [str (datetime.datetime.now().strftime("%a, %d %b %H:%M:%S %Y"))]
    writer.writerow(rowData)

    rowData = []
    writer.writerow(rowData)

    if graphReportSelectionsObj.printSelectionParameters:

        dataString = "Selection Parameters"

        rowData = [dataString]
        writer.writerow(rowData)

        rowData = []
        writer.writerow(rowData)

        dataString = ""

        for site in graphReportSelectionsObj.sites:
            dataString += str ( site ) + ","

        rowData = ["Sites:",dataString]
        writer.writerow(rowData)

        dataString = ""

        for study in graphReportSelectionsObj.studies:
            dataString += str ( study ) + ","

        rowData = ["Study:",dataString]
        writer.writerow(rowData)

        dataString = ""

        for instrumentAdministrator in graphReportSelectionsObj.instrumentAdministrators:
            dataString += str ( instrumentAdministrator ) + ","

        rowData = ["Instrument Administrators:",dataString]
        writer.writerow(rowData)

        dataString = ""

        for section in graphReportSelectionsObj.sections:
            dataString += str ( section ) + ","

        rowData = ["Sections:",dataString]
        writer.writerow(rowData)

        rowData = []
        writer.writerow(rowData)

    rowData = ["Question","Answer","Response","Number Responding","UPINs"]

    writer.writerow(rowData)

    for section, sectionSummaryObj in sectionSummaryObjMap.iteritems():

        for question, questionSummaryObj in sectionSummaryObj.questionSummaryObjMap.iteritems():

            for questionAnswer, questionAnswerSummaryObj in questionSummaryObj.questionAnswerSummaryObjMap.iteritems():

                rowData = []

                rowData.append(section.name)

                rowData.append(question.text)

                if questionAnswerSummaryObj.questionAnswerIsfitb:
                    rowData.append(questionAnswer)
                else:
                    rowData.append(questionAnswer.text)

                rowData.append(questionAnswerSummaryObj.numAdministrations)

                administrationString = ""

                for administration in questionAnswerSummaryObj.administrationList :

                    administrationString += str ( administration.upin.id        ) + ","

                rowData.append(administrationString)

                writer.writerow(rowData)

    if graphReportSelectionsObj.displayDemographicsData:

        #print " demographics data "

        for section, sectionSummaryObj in demographicsSectionSummaryObjMap.iteritems():

            #print " ** demographics data section "

            for question, questionSummaryObj in sectionSummaryObj.questionSummaryObjMap.iteritems():

                #print " demographics data question "

                for questionAnswerSummaryObj in questionSummaryObj.questionAnswerSummaryObjList:

                    #print " demographics data answer "

                    rowData = []

                    rowData.append(section.name)

                    rowData.append(question.text)

                    if questionAnswerSummaryObj.questionAnswerIsfitb:
                        rowData.append(questionAnswerSummaryObj.questionAnswer)
                    else:
                        rowData.append(questionAnswerSummaryObj.questionAnswer.text)

                    rowData.append(questionAnswerSummaryObj.numAdministrations)

                    administrationString = ""

                    for administration in questionAnswerSummaryObj.administrationList :

                        administrationString += str ( administration.upin.id    ) + ","

                    rowData.append(administrationString)

                    writer.writerow(rowData)

    return response

@login_required
def displayStudyList(request):

    selectedMenu = "StudyList"
    try:

        studyList = Study.objects.all().order_by("name")

    except:

        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/studyList.html', {

        'studyList': studyList,
        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def displaySiteList(request):

    selectedMenu = "SiteList"
    try:

        siteList = Site.objects.all().order_by("name")

    except:

        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/siteList.html', {

        'siteList': siteList,
        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def displayInstrumentAdministratorList(request):

    selectedMenu = "UserManagement"
    try:

        instrumentAdministrators = InstrumentAdministrator.objects.all().order_by("name")

        print " ISTH_BAT_INSTRUMENT " + (ISTH_BAT_INSTRUMENT)

        batInstrument = Instrument.objects.filter ( title = ISTH_BAT_INSTRUMENT)

        instrumentAdministratorObjList = []

        time365Days = datetime.timedelta(days=365)

        username = request.user.username

        for instrumentAdministrator in instrumentAdministrators :

            instrumentAdministratorObj = InstrumentAdministratorObj()

            user = User.objects.filter ( username = instrumentAdministrator.id )[0]

            instrumentAdministratorObj.email = user.email

            if username == "105" or int(username) == instrumentAdministrator.id:

                instrumentAdministratorObj.displayInList = True

            instrumentAdministratorObj.instrumentAdministrator = instrumentAdministrator

            waiverStatus = "Not Signed"

            signWaiverFlag = False

            waiverExpirationDate = ''

            earliest_cutoff_date = datetime.datetime.strptime(EARLIEST_CUTOFF_DATE, "%m/%d/%Y")

            if instrumentAdministrator.waiver_signed and instrumentAdministrator.waiver_signed.date() > earliest_cutoff_date.date() :

                instrumentAdministratorObj.waiverStatus = waiverStatus

                numDaysElapsed = datetime.datetime.today() - instrumentAdministrator.waiver_signed

                waiverExpirationDate = instrumentAdministrator.waiver_signed + time365Days

                if numDaysElapsed < time365Days:

                    waiverStatus = "Valid"
                else:
                    #waiverStatus = "Expired"
                    waiverStatus = "Valid"

            else:

                instrumentAdministrator.waiver_signed = None

            instrumentAdministratorObj.signWaiverFlag = signWaiverFlag
            instrumentAdministratorObj.waiverExpirationDate = waiverExpirationDate
            instrumentAdministratorObj.waiverStatus = waiverStatus

            administrations = Administration.objects.filter ( instrumentadministrator = instrumentAdministrator, instrument = batInstrument )

            instrumentAdministratorObj.administrations = administrations
            instrumentAdministratorObj.numAdministrations = len(administrations)

            instrumentAdministratorObjList.append ( instrumentAdministratorObj )

        instrumentAdministratorObjList.sort(key=lambda x: x.instrumentAdministrator.name)

    except:

        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/instrumentAdministratorList.html', {

        'instrumentAdministratorObjList': instrumentAdministratorObjList,
        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def displayInstrumentAdministratorDetailList(request):

    selectedMenu = "UserManagement"

    upinObjList = []
    instrumentAdministrator = ''

    try:

        batInstrument = Instrument.objects.filter ( title = ISTH_BAT_INSTRUMENT)
        instrumentAdministratorId = request.POST.get('instrumentAdministratorId', "0")

        instrumentAdministrator = InstrumentAdministrator.objects.get(pk = instrumentAdministratorId)

        upinObjList = []

        administrations = Administration.objects.filter ( instrumentadministrator = instrumentAdministrator , instrument = batInstrument)

        fetchQuestionAnswerFlag = False

        fetchContextsFlag = False

        for administration in administrations:

            upinObj = UPINObj()

            upin = administration.upin

            upinObj.upin = upin

            upinObj.administration = administration

            #print " upin = " + str (upin.id)

            instrumentObj = calcScore(upin.id, fetchQuestionAnswerFlag, fetchContextsFlag)

            upinObj.instrumentObj = instrumentObj

            upinObj.score = sum( [ a.sectionScore for a in instrumentObj.sectionObjList ] )

            upinObjList.append ( upinObj )

        upinObjList.sort(key=lambda x: x.upin.id)

    except:

        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/instrumentAdministratorDetail.html', {

        'upinObjList': upinObjList,
        'instrumentAdministrator': instrumentAdministrator,
        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def editStudy(request):

    selectedMenu = "StudyList"

    studyObj = StudyObj()

    try:

        studyId = request.POST.get('studyId', "0")

        study = Study.objects.get ( pk = studyId )

        studyObj.study = study

        instruments = Instrument.objects.all()

        print " before "

        for instrument in instruments:

            print " in adding " + str(instrument)

            instrumentObj = InstrumentObj()

            instrumentObj.instrument = instrument

            if instrument in study.instruments.all():

                instrumentObj.selectedFlag = True

            studyObj.studyInstrumentObjList.append (instrumentObj)

    except:

        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/editStudy.html', {

        'studyObj': studyObj,
        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def editSite(request):

    selectedMenu = "SiteList"

    try:

        siteId = request.POST.get('siteId', "0")

        site = Site.objects.get ( pk = siteId )

    except:

        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/editSite.html', {

        'site': site,
        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def editInstrumentAdministrator(request):

    selectedMenu = "UserManagement"

    instrumentAdministratorObj = InstrumentAdministratorObj()
    try:

        instrumentAdministratorId = request.POST.get('instrumentAdministratorId', "0")

        instrumentAdministrator = InstrumentAdministrator.objects.get ( pk = instrumentAdministratorId)

        instrumentAdministratorObj.instrumentAdministrator = instrumentAdministrator

        time365Days = datetime.timedelta(days=365)

        waiverStatus = "Not Signed"

        signWaiverFlag = False

        earliest_cutoff_date = datetime.datetime.strptime(EARLIEST_CUTOFF_DATE, "%m/%d/%Y")

        waiverExpirationDate = None

        if instrumentAdministrator.waiver_signed and instrumentAdministrator.waiver_signed.date() > earliest_cutoff_date.date() :

            instrumentAdministratorObj.waiverStatus = waiverStatus

            numDaysElapsed = datetime.datetime.today() - instrumentAdministrator.waiver_signed

            waiverExpirationDate = instrumentAdministrator.waiver_signed + time365Days

            if numDaysElapsed < time365Days:
                signWaiverFlag = True
                waiverStatus = "Valid"
            else:
                #waiverStatus = "Expired"
                waiverStatus = "Valid"

        else:

            instrumentAdministrator.waiver_signed = None

        instrumentAdministratorObj.signWaiverFlag = signWaiverFlag
        instrumentAdministratorObj.waiverExpirationDate = waiverExpirationDate
        instrumentAdministratorObj.waiverStatus = waiverStatus

        roleId = instrumentAdministrator.role.id

        allowedSites = instrumentAdministrator.allowed_sites.all()
        allowedSiteIds = [x.id for x in allowedSites]

        allowedStudies = instrumentAdministrator.allowed_studies.all()
        allowedStudyIds = [x.id for x in allowedStudies]

        roles = Role.objects.all()

        for role in roles:
            roleObj = UserRoleObj()
            if role.id == roleId:
                roleObj.isSelected = True
            roleObj.role = role
            instrumentAdministratorObj.roleObjList.append ( roleObj )

        sites = Site.objects.all()

        for site in sites:
            siteObj = UserSiteObj()
            if site.id in allowedSiteIds:
                siteObj.isSelected = True
            siteObj.site = site
            instrumentAdministratorObj.siteObjList.append ( siteObj )

        studies = Study.objects.all()

        for study in studies:
            studyObj = UserStudyObj()
            if study.id in allowedStudyIds:
                studyObj.isSelected = True
            studyObj.study = study
            instrumentAdministratorObj.studyObjList.append ( studyObj )

        #user = User.objects.filter ( username = instrumentAdministrator.id )[0]

        #instrumentAdministratorObj.email = user.email

    except:

        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/editInstrumentAdministrator.html', {

        'instrumentAdministratorObj': instrumentAdministratorObj,
        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def submitStudy(request):

    selectedMenu = "StudyList"

    try:

        studyId = request.POST.get('studyId', "0")

        studyName = request.POST.get('studyName', "0")

        study = Study.objects.get ( pk = studyId)

        study.name = studyName

        instrumentIds = request.POST.getlist('instrumentId')

        if request.user.username == '105':

            study.save()

            prevInstruments = study.instruments.all()
            prevInstrumentIds = [x.id for x in prevInstruments]

            for prevInstrumentId in prevInstrumentIds:
                instrument = Instrument.objects.get ( pk = prevInstrumentId )
                study.instruments.remove ( instrument )

            for instrumentId in instrumentIds:
                instrument = Instrument.objects.get ( pk = int(instrumentId) )
                study.instruments.add ( instrument )

    except:

        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/confirmEditStudy.html', {

        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def submitSite(request):

    selectedMenu = "SiteList"

    try:

        siteId = request.POST.get('siteId', "0")

        siteName = request.POST.get('siteName', "0")

        site = Site.objects.get ( pk = siteId)

        site.name = siteName

        if request.user.username == '105':

            site.save()

    except:

        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/confirmEditSite.html', {

        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def submitInstrumentAdministrator(request):

    selectedMenu = "UserManagement"

    instrumentAdministratorObj = InstrumentAdministratorObj()
    try:

        instrumentAdministratorId = request.POST.get('instrumentAdministratorId', "0")

        instrumentAdministrator = InstrumentAdministrator.objects.get ( pk = instrumentAdministratorId)

        signWaiverFlag = request.POST.get('signWaiverFlag', "")
        password = request.POST.get('password', "")
        email = request.POST.get('email', "")
        roleId = request.POST.get('roleId', "0")

        siteIds = request.POST.getlist('siteId')
        studyIds = request.POST.getlist('studyId')

        allowedSites = instrumentAdministrator.allowed_sites.all()
        allowedSiteIds = [x.id for x in allowedSites]

        allowedStudies = instrumentAdministrator.allowed_studies.all()
        allowedStudyIds = [x.id for x in allowedStudies]

        instrumentAdministrator.password = password

        user = User.objects.filter ( username = instrumentAdministrator.id )[0]
        user.set_password(password)
        user.email = email
        user.save()

        if signWaiverFlag == "1":
            instrumentAdministrator.waiver_signed = datetime.datetime.now()

        instrumentAdministrator.save()

        if request.user.username == '105':

            if roleId != "0":
                role = Role.objects.get( pk = roleId )
                instrumentAdministrator.role = role

            for allowedSiteId in allowedSiteIds:
                site = Site.objects.get ( pk = allowedSiteId )
                instrumentAdministrator.allowed_sites.remove ( site )

            for allowedStudyId in allowedStudyIds:
                study = Study.objects.get ( pk = allowedStudyId )
                instrumentAdministrator.allowed_studies.remove ( study )

            for siteId in siteIds:
                site = Site.objects.get ( pk = int(siteId) )
                instrumentAdministrator.allowed_sites.add ( site )

            for studyId in studyIds:
                study = Study.objects.get ( pk = int(studyId) )
                instrumentAdministrator.allowed_studies.add ( study )

            instrumentAdministrator.save()

    except:

        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/confirmEditInstrumentAdministrator.html', {

        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def summaryReport(request):

    selectedMenu = "Summary"
    try:

        studies = Study.objects.all ().order_by("name")

        sites = Site.objects.all ().order_by("name")

        userId = int(request.user.username)

        instrumentAdministrator = InstrumentAdministrator.objects.get ( pk = userId)

        allowedSites = instrumentAdministrator.allowed_sites.all().order_by("name")
        allowedStudies = instrumentAdministrator.allowed_studies.all().order_by("name")

        instrumentAdministratorList = []

        instrumentAdministrators = InstrumentAdministrator.objects.all ()

        for instrumentAdministrator in instrumentAdministrators :
            allowedSites2 = instrumentAdministrator.allowed_sites.all()
            allowedStudies2 = instrumentAdministrator.allowed_studies.all()

            waiverOkFlag = getWaiverOkFlag (instrumentAdministrator)

            if not waiverOkFlag :
                continue

            if any ( i in allowedSites for i in allowedSites2) and any ( i in allowedStudies for i in allowedStudies2)  :
                instrumentAdministratorList.append ( instrumentAdministrator )

        instrumentAdministratorList.sort(key=lambda x: x.name)

    except:
        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/summaryReport.html', {

        'studies': studies,
        'instrumentAdministrators': instrumentAdministratorList,
        'sites': sites,
        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def outputSummaryReport(request):

    siteSummaryObjList = []

    summaryReportSelectionsObj = SummaryReportSelectionsObj ()

    selectedMenu = "Summary"

    siteReportPrintObjList = []

    try:

        summaryReportSelectionsObj, siteReportPrintObjList, studyReportPrintObjList, userReportPrintSummaryObj = createSummaryReportObj(request)

    except:
        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/outputSummaryReport.html', {

        'siteReportPrintObjList': siteReportPrintObjList,
        'studyReportPrintObjList': studyReportPrintObjList,
        'summaryReportSelectionsObj':summaryReportSelectionsObj,
        'userReportPrintSummaryObj' : userReportPrintSummaryObj,
        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def individualReport(request):

    instrumentObj = ''

    selectedMenu = "Individual"

    print " *** IN INDIVIDUAL REPORT "

    try:

        upinId = request.POST.get('upinId', "0")

        if upinId != '0':

            fetchQuestionAnswerFlag = True

            fetchContextsFlag = True

            instrumentObj = calcScore(upinId, fetchQuestionAnswerFlag,  fetchContextsFlag)

            print " section scores are : " + str([ a.sectionScore for a in instrumentObj.sectionObjList ])

            instrumentObj.instrumentScore = sum( [ a.sectionScore for a in instrumentObj.sectionObjList ] )

    except:
        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/individualReport.html', {

        'instrumentObj': instrumentObj,
        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def addSite(request):

    selectedMenu = "UserManagement"

    return render_to_response('batreports/addSite.html', {

        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def addStudy(request):

    selectedMenu = "UserManagement"

    instruments = Instrument.objects.all()

    return render_to_response('batreports/addStudy.html', {

        'selectedMenu': selectedMenu,
        'instruments': instruments,
        'user':request.user

    })

@login_required
def addInstrumentAdministrator(request):

    selectedMenu = "UserManagement"

    try:

        sites = Site.objects.all()
        studies = Study.objects.all()
        roles = Role.objects.all()

    except:
        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/addInstrumentAdministrator.html', {

        'selectedMenu': selectedMenu,
        'sites': sites,
        'studies': studies,
        'roles': roles,
        'user':request.user

    })

@login_required
def submitAddSite(request):

    selectedMenu = "SiteList"

    try:

        siteName = request.POST.get('siteName', "0")

        sites = Site.objects.filter(name = siteName)

        maxSite = Site.objects.all().order_by("-id")[0]
        newId = maxSite.id + 1

        if len(sites) == 0:

            site = Site(id = newId, name = siteName)

            site.save()

    except:
        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/confirmAddSite.html', {

        'selectedMenu': selectedMenu,
        'user':request.user

    })

@login_required
def submitAddStudy(request):

    selectedMenu = "StudyList"

    try:

        studyName = request.POST.get('studyName', "0")
        instrumentIds = request.POST.get('instrumentId', "0")

        studies = Study.objects.filter(name = studyName)

        maxStudy = Study.objects.all().order_by("-id")[0]
        newId = maxStudy.id + 1

        if len(studies) == 0:

            study = Study(id = newId, name = studyName)

            study.save()

            for instrumentId in instrumentIds:
                instrument = Instrument.objects.get ( id = instrumentId )
                study.instruments.add ( instrument )

    except:
        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/confirmAddStudy.html', {

        'selectedMenu': selectedMenu,
        'user':request.user

    })


@login_required
def submitAddInstrumentAdministrator(request):

    selectedMenu = "UserManagement"

    try:

        instrumentAdministratorName = request.POST.get('instrumentAdministratorName', "0")

        signWaiverFlag = request.POST.get('signWaiverFlag', "")
        password = request.POST.get('password', "")

        email = request.POST.get('email', "")

        roleId = request.POST.get('roleId', "0")

        siteIds = request.POST.getlist('siteId')
        studyIds = request.POST.getlist('studyId')

        role = Role.objects.get ( id = roleId )

        maxInstrumentAdministrator = InstrumentAdministrator.objects.all().order_by("-id")[0]
        newId = maxInstrumentAdministrator.id + 1

        zero_date = datetime.datetime.strptime("01/01/1980", "%m/%d/%Y")

        instrumentAdministrator = InstrumentAdministrator ( id = newId , name = instrumentAdministratorName, password = password, role = role, waiver_signed = zero_date )

        if signWaiverFlag == "1":
            instrumentAdministrator.waiver_signed = datetime.datetime.now()

        instrumentAdministrator.save()

        for siteId in siteIds:
            site = Site.objects.get ( id = siteId )
            instrumentAdministrator.allowed_sites.add ( site )

        for studyId in studyIds:
            study = Study.objects.get ( id = studyId )
            instrumentAdministrator.allowed_studies.add ( study )

        instrumentAdministrator.save()

        # Save Django user

        user = User.objects.create_user(instrumentAdministrator.id, DEFAULT_EMAIL_ID, password)
        user.first_name = instrumentAdministrator.name
        user.last_name = '.'
        user.save()

    except:
        traceback.print_exc(file=sys.stdout)

    return render_to_response('batreports/confirmAddInstrumentAdministrator.html', {

        'selectedMenu': selectedMenu,
        'instrumentAdministrator': instrumentAdministrator,
        'user':request.user

    })

@login_required
def downloadListUPINSummary(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="UPINList.csv"'

    siteOrStudySelectionFlag = request.POST.get('siteOrStudySelectionFlag', "0")

    printSelectionParameters = request.POST.get('printSelectionParameters', "0")

    reportObjList = []

    batInstrument = Instrument.objects.filter ( title = ISTH_BAT_INSTRUMENT) [0]

    instrumentSections = InstrumentSection.objects.filter ( instrument = batInstrument )

    selectionObj = SelectionObj()

    selectionObj.instrument = batInstrument

    reportOptionsObj = ReportOptionsObj ()

    reportOptionsObj.multipleChoiceIds.extend (DEFAULT_MULTIPLE_CHOICE_REPORT_QUESTION_IDS)
    reportOptionsObj.instrumentSections.extend (instrumentSections)

    firstReportObj = True

    fetchQuestionAnswerObjFlag = True
    fetchContextsFlag = False

    reportObj = ReportObj()

    if siteOrStudySelectionFlag == "1":

        upinObjList, userSummarySelectionObj, siteOrStudySelectionFlag = fetchSummaryUPINSiteListObjs (request)

        for upinObj in upinObjList:

            upinObj.instrumentObj = calcScore(upinObj.upin.id, fetchQuestionAnswerObjFlag, fetchContextsFlag)

        selectionObj.instrumentAdministrator = userSummarySelectionObj.instrumentAdministrator
        selectionObj.site = userSummarySelectionObj.selectedSite

        if len (upinObjList) > 0:

            for study in userSummarySelectionObj.studies:

                selectionObj.study = study

                reportOptionsObj.reportUpinIds = [str ( x.upin.id ) for x in upinObjList if x.upin.study.id == study.id ]
                reportOptionsObj.instrumentSectionIds = [str ( x.id ) for x in instrumentSections]

                if len(reportOptionsObj.reportUpinIds) > 0:

                    #print " for study " + str (study) + " upins " + str ([x.upin.id for x in upinObjList]) + " report upins " + str (reportOptionsObj.reportUpinIds)

                    reportObjStudy = getReportObj(upinObjList, selectionObj, reportOptionsObj)

                    if firstReportObj == True:

                        firstReportObj = False

                        reportObj.headerColumns = reportObjStudy.headerColumns
                        reportObj.subHeaderColumns = reportObjStudy.subHeaderColumns
                        reportObj.questionCounters = reportObjStudy.questionCounters
                        reportObj.sectionCounters = reportObjStudy.sectionCounters

                    #print " adding details " + str (reportObjStudy.reportDetailObjList)

                    reportObj.reportDetailObjList.extend (reportObjStudy.reportDetailObjList)

    else:

        upinObjList, userSummarySelectionObj, siteOrStudySelectionFlag = fetchSummaryUPINStudyListObjs (request)

        for upinObj in upinObjList:

            upinObj.instrumentObj = calcScore(upinObj.upin.id, fetchQuestionAnswerObjFlag, fetchContextsFlag)

        selectionObj.instrumentAdministrator = userSummarySelectionObj.instrumentAdministrator
        selectionObj.study = userSummarySelectionObj.selectedStudy

        if len (upinObjList) > 0:

            for site in userSummarySelectionObj.sites:

                selectionObj.site = site

                administrationIds = []

                reportOptionsObj.reportUpinIds = []

                for upinObj in upinObjList:

                    administration = Administration.objects.filter (upin = upinObj.upin)[0]

                    if administration.site.id == site.id:

                        reportOptionsObj.reportUpinIds.append ( str ( upinObj.upin.id ) )

                reportOptionsObj.instrumentSectionIds = [str ( x.id ) for x in instrumentSections]

                if len(reportOptionsObj.reportUpinIds) > 0:

                    reportObjSite = getReportObj(upinObjList, selectionObj, reportOptionsObj)

                    if firstReportObj == True:

                        firstReportObj = False

                        reportObj.headerColumns = reportObjSite.headerColumns
                        reportObj.subHeaderColumns = reportObjSite.subHeaderColumns
                        reportObj.questionCounters = reportObjSite.questionCounters
                        reportObj.sectionCounters = reportObjSite.sectionCounters

                    reportObj.reportDetailObjList.extend (reportObjSite.reportDetailObjList)

    writer = csv.writer(response,delimiter=",")

    if printSelectionParameters == "1":

        rowData = [str (datetime.datetime.now().strftime("%a, %d %b %H:%M:%S %Y"))]
        writer.writerow(rowData)

        rowData = []
        writer.writerow(rowData)

        dataString = "Selection Parameters"

        rowData = [dataString]
        writer.writerow(rowData)

        rowData = []
        writer.writerow(rowData)

        rowData = ["Start Date:", userSummarySelectionObj.startDate]
        writer.writerow(rowData)

        rowData = ["End Date:",userSummarySelectionObj.endDate]
        writer.writerow(rowData)

        dataString = ""

        if siteOrStudySelectionFlag == "1":

            dataString = userSummarySelectionObj.selectedSite

        else:

            for site in userSummarySelectionObj.sites:
                dataString += str ( site ) + ","

        rowData = ["Sites:",dataString]
        writer.writerow(rowData)

        dataString = ""

        if siteOrStudySelectionFlag == "2":

            dataString = userSummarySelectionObj.selectedStudy

        else:

            for study in userSummarySelectionObj.studies:
                dataString += str ( study ) + ","

        rowData = ["Study:",dataString]
        writer.writerow(rowData)

        dataString = userSummarySelectionObj.instrumentAdministrator

        rowData = ["Instrument Administrator:",dataString]
        writer.writerow(rowData)

        rowData = []
        writer.writerow(rowData)

    rowData = ["","","",""]

    for questionCounter in reportObj.questionCounters:
        rowData.append(str(questionCounter))

    writer.writerow(rowData)

    rowData = ["","","",""]

    for sectionCounter in reportObj.sectionCounters:
        rowData.append(str(sectionCounter))

    writer.writerow(rowData)

    rowData = ["PID","SiteID","Admin","PriTime"]

    for headerColumn in reportObj.headerColumns:
        rowData.append(str(headerColumn))

    writer.writerow(rowData)

    rowData = ["","","",""]

    for subHeaderColumn in reportObj.subHeaderColumns:
        rowData.append(str(subHeaderColumn))

    writer.writerow(rowData)

    #for reportDetailObj in reportObj.reportDetailObjList:

        #rowData = []

        #for columnValue in reportDetailObj.columnValues:
            #rowData.append(str(columnValue))

        #writer.writerow(rowData)

    #rowData = ["","","",""]

    #for questionCounter in reportObj.questionCounters:
        #rowData.append(str(questionCounter))

    #writer.writerow(rowData)

    #rowData = ["","","",""]

    #for sectionCounter in reportObj.sectionCounters:
        #rowData.append(str(sectionCounter))

    #rowData = ["PID","SiteID","Admin","PriTime"]

    #for headerColumn in reportObj.headerColumns:
        #rowData.append(str(headerColumn))

    #writer.writerow(rowData)

    #rowData = ["","","",""]

    #for subHeaderColumn in reportObj.subHeaderColumns:
        #rowData.append(str(subHeaderColumn))

    #writer.writerow(rowData)

    for reportDetailObj in reportObj.reportDetailObjList:

        rowData = []

        for columnValue in reportDetailObj.columnValues:
            rowData.append(str(columnValue))

        writer.writerow(rowData)

    return response

def createOutputSummaryUserReport(request):

    print " in create output report "

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="SummaryUserReportData.csv"'

    summaryReportSelectionsObj, siteReportPrintObjList, studyReportPrintObjList, userReportPrintSummaryObj = createSummaryReportObj(request)

    writer = csv.writer(response,delimiter=",")

    rowData = [str (datetime.datetime.now().strftime("%a, %d %b %H:%M:%S %Y"))]
    writer.writerow(rowData)

    rowData = []
    writer.writerow(rowData)

    if summaryReportSelectionsObj.printSelectionParameters:

        dataString = "Selection Parameters"

        rowData = [dataString]
        writer.writerow(rowData)

        rowData = []
        writer.writerow(rowData)

        rowData = [summaryReportSelectionsObj.startDate]
        writer.writerow(rowData)

        rowData = [summaryReportSelectionsObj.endDate]
        writer.writerow(rowData)

        dataString = ""

        for site in summaryReportSelectionsObj.sites:
            dataString += str ( site ) + ","

        rowData = ["Sites:",dataString]
        writer.writerow(rowData)

        dataString = ""

        for study in summaryReportSelectionsObj.studies:
            dataString += str ( study ) + ","

        rowData = ["Study:",dataString]
        writer.writerow(rowData)

        dataString = ""

        for instrumentAdministrator in summaryReportSelectionsObj.instrumentAdministrators:
            dataString += str ( instrumentAdministrator ) + ","

        rowData = ["Instrument Administrators:",dataString]
        writer.writerow(rowData)

        rowData = []
        writer.writerow(rowData)

    rowData = ["User / Site Details.",]
    writer.writerow(rowData)

    rowData = []
    rowData.append("Administrator")

    for site in summaryReportSelectionsObj.sites :
        rowData.append (site.name )

    writer.writerow(rowData)

    for userReportPrintObj in userReportPrintSummaryObj.userReportPrintObjList :

        rowData = []
        rowData.append ( userReportPrintObj.instrumentAdministrator )

        for userSiteReportPrintObj in userReportPrintObj.userSiteReportPrintObjList :
            rowData.append ( userSiteReportPrintObj.totalNumAdministrations )

        writer.writerow(rowData)

    rowData = []
    rowData.append("Administrator")

    for study in summaryReportSelectionsObj.studies :
        rowData.append (study.name )

    writer.writerow(rowData)

    for userReportPrintObj in userReportPrintSummaryObj.userReportPrintObjList :

        rowData = []
        rowData.append ( userReportPrintObj.instrumentAdministrator )

        for userStudyReportPrintObj in userReportPrintObj.userStudyReportPrintObjList :
            rowData.append ( userStudyReportPrintObj.totalNumAdministrations )

        writer.writerow(rowData)

    rowData = []
    rowData.append("Administrator")

    return response

@login_required
def createOutputSummaryReport(request):

    submitButton = request.POST.get('submitButton', "0")

    if submitButton == "0":
        return summaryReport (request)
    elif submitButton == "2":
        return createOutputSummaryUserReport (request)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="SummaryReportData.csv"'

    summaryReportSelectionsObj, siteReportPrintObjList, studyReportPrintObjList, userReportPrintSummaryObj = createSummaryReportObj(request)

    writer = csv.writer(response,delimiter=",")

    rowData = [str (datetime.datetime.now().strftime("%a, %d %b %H:%M:%S %Y"))]
    writer.writerow(rowData)

    rowData = []
    writer.writerow(rowData)

    if summaryReportSelectionsObj.printSelectionParameters:

        dataString = "Selection Parameters"

        rowData = [dataString]
        writer.writerow(rowData)

        rowData = []
        writer.writerow(rowData)

        rowData = [summaryReportSelectionsObj.startDate]
        writer.writerow(rowData)

        rowData = [summaryReportSelectionsObj.endDate]
        writer.writerow(rowData)

        dataString = ""

        for site in summaryReportSelectionsObj.sites:
            dataString += str ( site ) + ","

        rowData = ["Sites:",dataString]
        writer.writerow(rowData)

        dataString = ""

        for study in summaryReportSelectionsObj.studies:
            dataString += str ( study ) + ","

        rowData = ["Study:",dataString]
        writer.writerow(rowData)

        dataString = ""

        for instrumentAdministrator in summaryReportSelectionsObj.instrumentAdministrators:
            dataString += str ( instrumentAdministrator ) + ","

        rowData = ["Instrument Administrators:",dataString]
        writer.writerow(rowData)

        rowData = []
        writer.writerow(rowData)

    rowData = ["Site Details.",]
    writer.writerow(rowData)

    for siteReportPrintObj in siteReportPrintObjList:

        if siteReportPrintObj.summaryReportObj.totalAdminCount == 0 :
            continue

        rowData = ["Site:",siteReportPrintObj.site]
        writer.writerow(rowData)

        rowData = ["Month","Administration","UPINs"]
        writer.writerow(rowData)

        for monthYear, summaryReportMonthObj in siteReportPrintObj.summaryReportObj.monthYearMap.iteritems():
            if summaryReportMonthObj.totalMonthAdminCount > 0 :

                rowData = []

                rowData.append(monthYear)

                for instrumentAdministrator, summaryReportUserObj in summaryReportMonthObj.userMap.iteritems():
                    if summaryReportUserObj.adminCount > 0:
                        rowData.append(instrumentAdministrator)

                for instrumentAdministrator, summaryReportUserObj in summaryReportMonthObj.userMap.iteritems():
                    for administration in summaryReportUserObj.adminList:
                        if summaryReportUserObj.adminCount > 0:
                            rowData.append(administration.upin.id)

                writer.writerow(rowData)

    rowData = ["Study Details"]
    writer.writerow(rowData)

    rowData = ["Month","Administration","UPINs"]
    writer.writerow(rowData)

    for studyReportPrintObj in studyReportPrintObjList:

        if studyReportPrintObj.summaryReportObj.totalAdminCount == 0 :
            continue

        rowData = ["Study:",studyReportPrintObj.study]
        writer.writerow(rowData)

        rowData = ["Month","Administration","UPINs"]
        writer.writerow(rowData)

        for monthYear, summaryReportMonthObj in studyReportPrintObj.summaryReportObj.monthYearMap.iteritems():
            if summaryReportMonthObj.totalMonthAdminCount > 0 :

                rowData = []

                rowData.append(monthYear)

                for instrumentAdministrator, summaryReportUserObj in summaryReportMonthObj.userMap.iteritems():
                    if summaryReportUserObj.adminCount > 0:
                        rowData.append(instrumentAdministrator)

                for instrumentAdministrator, summaryReportUserObj in summaryReportMonthObj.userMap.iteritems():
                    for administration in summaryReportUserObj.adminList:
                        if summaryReportUserObj.adminCount > 0:
                            rowData.append(administration.upin.id)

                writer.writerow(rowData)

    return response
