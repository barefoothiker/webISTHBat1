import os, re, sys, getopt, traceback, math, numpy
sys.path.append("/Users/mitras/projects/webISTHBat")
os.environ["DJANGO_SETTINGS_MODULE"] = "bat.settings"   
sys.path.append('/WWW/django2/code')
sys.path.append('/WWW/django2/code/batwebapp')
sys.path.append('/usr/local/lib/python2.5/site-packages')
from bat.models import *
from numpy import *
import sys, traceback, datetime, time, math , csv
from datetime import datetime
from bat.batReportObjs import *
from bat.batReportConstants import *
import logging
from django.contrib.auth.models import User 
from bat.batReportObjs import *
from bat.batReportConstants import *

#bat Web App
#Author:Siddhartha Mitra
#Rockefeller University, 2015
#
# this program calculates the score 
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#Imports
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

from django import forms
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import time, datetime, operator, random

ISTH_SCORE_NAME = "ISTH BAT Score"

def fetchScoreCardObj(administration, scoreCard):
    
  try:

    # question related to scorecard.
    scoreCardObj = ScoreCardObj() 
    scoreCardObj.scoreCard = scoreCard   

    question = scoreCard.question

    # answers pertaining to the scorecard 
    answers = scoreCard.answer.all()	   

    scores = []

    #if question.id == 36:
      #print " IN question 36 " 
    
    # if enum, use the first answer for the scorecard	
    if question.format=='enum':

        answer = answers[0]

	#print " *****___________***************** in ENUMMMMMMMMMM " + str ( answer.id )

        questionAnswerObj = QuestionAnswerObj()
        questionAnswerObj.questionAnswer = answer
	questionAnswerObj.question = question

        # fetch the question and answer instances, and update the score with the number of such responses
        questionAnswerInstances = QuestionAnswerInstance.objects.filter(administration = administration, question = question, answer = answer)
	
	numAnswers = len(questionAnswerInstances)	

	#if question.id == 58:
	  #print " ********************** num answers " + str ( numAnswers ) + " for scorecard " + str ( scoreCard.id )  

        answerValue = ''
	
        if len(questionAnswerInstances) > 0 :
            questionAnswerObj.answerScore = scoreCard.score			
            questionAnswerObj.ifAnswered = True
	    #if question.id == 58:
	      #print " ********************** in FFFFFFFFFFFF ETCH SCORE QA instances!! " 
		
	    questionAnswerInstance = questionAnswerInstances[0]
	    
	    try:
		  
		  if int(questionAnswerInstance.blank.get().text) >= 0:
		    answerValue = int(questionAnswerInstance.blank.get().text)
		  
		    #if question.id == 58:
		      #print " --------------- ** ^^^^ (((((((( ---- !!!! for numeric answer ENUM 222 " + str ( questionAnswerInstance.blank.get().text ) + " -- answerValue -- " + str (answerValue)

	    except:
		  pass	
		
	    #if question.id == 58:
	      #print " ********************** in answer value " + str (answerValue) 

	    questionAnswerObj.answerScore = answerValue
	    if answerValue != '' and answerValue != 0 and answerValue != '0':
	      questionAnswerObj.answerValue = answerValue
	      #questionAnswerObj.totalAnswerValue = answerValue	 
	      questionAnswerObj.answerValueDisplay = numAnswers	     
	      questionAnswerObj.numAnswers = numAnswers
	      
	      questionAnswerObj.totalAnswerValue = numAnswers	
	      
	      #if scoreCard.id == 107 or scoreCard.id == 110:
	      
		#print " in score card setting answer value INNNNNNN ENUM --- " + str ( answerValue) + " --- question = " + str ( question.text ) + " answer = " + str ( answer.text)
    
	#print " ADDING TO  card setting answer value ENUM --- " + str ( questionAnswerObj.answerValue)  + " --- answer  " + str ( answer.text)
        scoreCardObj.questionAnswerObjList.append ( questionAnswerObj)

    else:
        # for each answer in the list
        for answer in answers:

	    if scoreCard.id == 107 or scoreCard.id == 110:
	      print " @@@@ answer is = " + str ( answer ) + " id = " + str ( answer.id) + " question = " + str ( question.text) + " question id = " + str ( question.id) + " scorecard id = " + str(scoreCard.id)
 
            # fetch the question and answer instances
            questionAnswerInstances = QuestionAnswerInstance.objects.filter(administration = administration, question = question, answer = answer)

            questionAnswerObj = QuestionAnswerObj()
            questionAnswerObj.questionAnswer = answer
	    
	    questionAnswerObj.answerText = answer.text	    

	    totalAnswerValue = 0
            for questionAnswerInstance in questionAnswerInstances:
	      
		questionAnswerObj.ifAnswered = True
		answerValue = '' 

		if answer.isfitb:
		  try:
                        if int(questionAnswerInstance.blank.get().text) >= 0:
			  #print " &&&&^^^^^^ answer value = " + str ( answerValue )
			  answerValue = int(questionAnswerInstance.blank.get().text)
		  except:
                        pass
                    # if there was an answer >0 entered, then check logic value if present. If logic value present and answer entered greater 
                    # than logic value, add score card value, else just add scorecard value if answer > 0
                    
                    #print " answer value  " + str (  answerValue )
		  if answerValue > 0:
                        #if scoreCard.logic_value is not None and answerValue >= scoreCard.logic_value:
		      questionAnswerObj.answerScore = scoreCard.score
								
                        #else:
                            #questionAnswerObj.answerScore = scoreCard.score								
		else: 
		    #print " not in fitb " + " scorecard id = " + str ( scoreCard.id) + " scorecard score = " + str ( scoreCard.score)
                    questionAnswerObj.answerScore = scoreCard.score
		    if answerValue == '' and answer.text != "Yes":
		      answerValue = questionAnswerObj.answerScore
		      totalAnswerValue = questionAnswerObj.answerScore

		questionAnswerObj.ifAnswered = True
		answerValueDisplay = ''
		
		if questionAnswerObj.totalAnswerValueString != '':
		  
		  questionAnswerObj.totalAnswerValueString += ", "
		
		questionAnswerObj.totalAnswerValueString += str(answerValue)			
		
		questionAnswerObj.answerTextList.append(answer.text)
		
		if question.id == 58:
		  
		  print " ---- in fetch score for question " + str ( question ) + " answer value " + str ( answerValue ) 

		if answerValue != '' and answerValue != 0 and answerValue != '0':
		  questionAnswerObj.answerValue = answerValue
		  questionAnswerObj.answerValueDisplay = answerValue
		  
		  #questionAnswerObj.totalAnswerValue += totalAnswerValue
			  
		else:
		  questionAnswerObj.answerValue = answer.text 
		  questionAnswerObj.answerValueDisplay = answer.text
		  if answer.text == "Yes":
		    
		    if scoreCard.id == 107 or scoreCard.id == 110:
		      print " &&^^&& IN YES!!!! "
		    
		    questionAnswerObj.totalAnswerValue += 1
		    questionAnswerObj.answerValue = "1"
		    questionAnswerObj.answerValueDisplay += "( = 1)"
		    
		if scoreCard.id == 107 or scoreCard.id == 110:

		  print " in score card setting answer value NOT ENUM  --- " + str ( answerValue) + " --- question = " + str ( question.text ) + " answer = " + str ( answer.text)		
		  print " for question answer = " + str (answer) + " value is " + str ( answerValue )
		  
		questionAnswerObj.questionAnswerInstanceList.append (questionAnswerInstance)	
		
	    if scoreCard.id == 107 or scoreCard.id == 110:
	      print " ADDING TO  card setting answer value " + str ( questionAnswerObj.answerValue) + " --- answer  " + str ( answer.text)
	    
	    questionAnswerObj.answerTextString = ','.join(questionAnswerObj.answerTextList)	    
	    
            scoreCardObj.questionAnswerObjList.append ( questionAnswerObj)
	            
    #print "answer score =  " + str ([a.answerScore for a in scoreCardObj.questionAnswerObjList])
    
    scoreValues = [a.answerScore for a in scoreCardObj.questionAnswerObjList]
    
    answerValues = [a.answerValue for a in scoreCardObj.questionAnswerObjList]
    
    #if question.id == 58:
      
      #print " for question " + str ( question.text ) + " score values = " + str ( scoreValues ) + " answer values = " + str ( answerValues ) 
    
    scoreCardObj.scoreCardScore = max( scoreValues )

    #if scoreCard.id == 107 or scoreCard.id == 110 :

      #print "score values=  " + str (scoreValues) + " for score card = " + str(scoreCard.id) + " for question = " + str ( question)

      #print "answer values =  " + str (answerValues) + " for score card = " + str(scoreCard.id) + " for question = " + str ( question)
      
      #print "  maxValueTexts " + str ( [x.totalAnswerValue for x in scoreCardObj.questionAnswerObjList] )

      #print "score card score =  " + str (scoreCardObj.scoreCardScore)
    
    scoreCardObj.questionAnswerObjList[scoreValues.index(max( scoreValues ))].isMax = True
    
    if question.format == 'enum':
    
      maxValueText = scoreCardObj.questionAnswerObjList[scoreValues.index(max( scoreValues ))].totalAnswerValue
    
    else:
    
      maxValueText = scoreCardObj.questionAnswerObjList[scoreValues.index(max( scoreValues ))].answerValue
    
    #if scoreCard.id == 107 or scoreCard.id == 110 :    
      #print " maxValuetext = " + str (maxValueText) + " for score card = " + str(scoreCard.id)
    
    maxValue = 0
    try:
      maxValue = int(maxValueText)
    except:
      pass
    
    scoreCardObj.maxScoreCardAnswerValue = maxValue

    #if question.id == 57:    
      #print " maxValue = " + str (maxValue)
    
    #print " max value = " + str (scoreCardObj.maxScoreCardAnswerValue)
    
  except:
    traceback.print_exc(file=sys.stdout)    
    raise

  return scoreCardObj

def calcScore(upinId, fetchQuestionAnswerFlag, fetchContextsFlag):

  try:
    # UPIN
    upin = UPIN.objects.get ( pk = upinId )
    
    batInstrument = Instrument.objects.filter ( title = ISTH_BAT_INSTRUMENT) 
  
    #administration = Administration.objects.filter ( upin = upin, instrument = batInstrument ).exclude(stop__isnull = True )[0]
    
    administration = Administration.objects.filter ( upin = upin, instrument = batInstrument )[0]

    # Trial instrument or questionnaire
    instrument = administration.instrument

    # secions of the instrument
    instrumentSections = instrument.sections.all()

    # instantiate instrument obj	
    instrumentObj = InstrumentObj()
    instrumentObj.administration = administration

    #Iterate sections
    for instrumentSectionIndex, instrumentSection in enumerate (instrumentSections):

        # instantiate section obj and add to score obj
        sectionObj = SectionObj() 
        sectionObj.section = instrumentSection

        instrumentObj.sectionObjList.append ( sectionObj ) 

	if fetchContextsFlag:
	  sectionObj = fetchContexts ( sectionObj , administration )

        # Iterate over questions belonging to the section
        questions = instrumentSection.questions.all().order_by('sequence')
	
	#print " ** for section " + str ( instrumentSection ) 

        for question in questions:
	  
	    #print " ** ^^^^ for question " + str ( question ) 

            # instantiate question obj and add to section obj
            questionObj = QuestionObj() 
            questionObj.question = question

            sectionObj.questionObjList.append ( questionObj ) 
	    
            ## get the score cards for the question 			
            scoreCards  = ScoreCard.objects.filter(instrument = instrument, section = instrumentSection, question = question, score_name=ISTH_SCORE_NAME).exclude(score = 0)
            ## skip if no scorecards found for question
	    if fetchQuestionAnswerFlag:
	      questionObj = fetchQuestionAnswerList (questionObj, administration, sectionObj)

	    questionObj.numScoreCards = len(scoreCards)
            # iterate over score cards. Each record in the score card represents a different answer to the same question.
            for scoreCard in scoreCards:
	      
	        diff = 0
		quot = 0

                scoreCardObj = fetchScoreCardObj ( administration, scoreCard )
		
		if scoreCard.id == 107 or scoreCard.id == 110:
		
		  print " %%%%%%%%% score = " + str (scoreCard.score ) + " for id = " + str ( scoreCard.id)

		#if question.id == 57 or question.id == 58:                
                
		  #print " question id = " + str ( question.id ) + " for score card id = " + str ( scoreCard.id) + " score is " + str ( scoreCardObj.scoreCardScore ) + " logic type = " + str (scoreCard.paired_logic_type)
                
                questionObj.scoreCardObjList.append (scoreCardObj )

                # if paired logic, get paired score card

                if scoreCard.paired_logic_type != "simple":

                    pairedScoreCard = scoreCard.paired_card
                    
                    #print " fetching PAIRED score card obj " + str ( pairedScoreCard.id)                    

                    pairedScoreCardObj = fetchScoreCardObj ( administration, pairedScoreCard )	

                    # depending on paired logic, calculate score
                    if scoreCard.paired_logic_type == 'union':
		      
		      #if question.id == 91 or question.id == 89 :
			
			#print  " for question " + str ( question ) + " scorecard id = " + str (scoreCard.id) + "scoreCardObj.scoreCardScore " + str (scoreCardObj.scoreCardScore) + " scoreCard.logic_value " + str (scoreCard.logic_value) + " pairedScoreCardObj.scoreCardScore " + str (pairedScoreCardObj.scoreCardScore) + "scoreCard.paired_card.logic_value " + str (scoreCard.paired_card.logic_value)
			
			#print " *** scoreCard Answer Value " + str ( scoreCardObj.maxScoreCardAnswerValue ) + " scorecard logic value " + str( scoreCard.logic_value ) + " paired scoreCard Answer Value " + str ( pairedScoreCardObj.maxScoreCardAnswerValue ) + " paired scorecard logic value  " + str ( scoreCard.paired_card.logic_value )
			
                      if scoreCardObj.maxScoreCardAnswerValue >= scoreCard.logic_value and pairedScoreCardObj.maxScoreCardAnswerValue >= scoreCard.paired_card.logic_value:
                        scoreCardObj.scoreCardScore = scoreCard.score
                      else:
                        scoreCardObj.scoreCardScore = 0

                    elif scoreCard.paired_logic_type == 'difference':
                      diff = scoreCardObj.maxScoreCardAnswerValue - pairedScoreCardObj.maxScoreCardAnswerValue
                      if (diff) >= scoreCard.logic_value:
                          scoreCardObj.scoreCardScore = scoreCard.score
                      else:
                        scoreCardObj.scoreCardScore = 0                            

                    elif scoreCard.paired_logic_type == 'percent':
		      
		      #print " !!)))))))___@@@@@@@ IN score card score = " + str (scoreCardObj.scoreCardScore) + " PERCENT PAIRED SCORE " + str (pairedScoreCardObj.scoreCardScore)
                      
                      #print  " scorecard id = " + str (scoreCard.id) + " scoreCardObj.scoreCardScore " + str (scoreCardObj.scoreCardScore) + " scoreCard.logic_value " + str (scoreCard.logic_value) + " pairedScoreCardObj.scoreCardScore " + str (pairedScoreCardObj.scoreCardScore) + " scoreCard.paired_card.logic_value " + str (scoreCard.paired_card.logic_value)
		      quot = 0
		      #if scoreCard.id == 107 or scoreCard.id == 110 :
			#print " *** num = " + str ( scoreCardObj.maxScoreCardAnswerValue ) + " ** denom = " + str (pairedScoreCardObj.maxScoreCardAnswerValue) + " for scoreCard = " + str(scoreCard.id ) + " question " + str ( question.id ) 
		      if pairedScoreCardObj.maxScoreCardAnswerValue != 0:
			quot = 0
			try: 
			  quot = (float(scoreCardObj.maxScoreCardAnswerValue) / float(pairedScoreCardObj.maxScoreCardAnswerValue))*100
			except:
			  pass
		      #if scoreCard.id == 107 or scoreCard.id == 110 :
			#print  " scorecard = " + str ( scoreCard.id) + "question " + str ( question ) + " !!)))))))___@@@@@@@  quot = " + str (quot) + " logic value " + str (scoreCardObj.scoreCard.logic_value) + " paired logic value " + str (pairedScoreCardObj.scoreCard.logic_value)  + " for scoreCard = " + str(scoreCard.id ) + " question " + str ( question.id )

                      if quot >= float(scoreCard.logic_value):
			  #print " :::::::::::: ******* SETTING SCORE " + str (scoreCard.score) + " for scorecard = " + str ( scoreCard.id)
                          scoreCardObj.scoreCardScore = scoreCard.score
                      else:
                          scoreCardObj.scoreCardScore = 0  
			  
		    scoreCardDescription = ''
			  
                    #for questionAnswerObj in scoreCardObj.questionAnswerObjList:
		        ##print " in score card description ** " + str (questionAnswerObj.answerValue) + " ** answer " + str ( questionAnswerObj.questionAnswer.text) + " question = " + str ( question.text)
                        #scoreCardDescription += "\"" + str(questionAnswerObj.totalAnswerValue) + "\" "

		    scoreCardDescription += "\"" + str(scoreCardObj.maxScoreCardAnswerValue) + "\" "
                        
                    scoreCardDescription += "(" + scoreCard.question.text + ") " 
                        
                    scoreCardDescription += PAIRED_LOGIC_DESCRIPTION_MAP[scoreCard.paired_logic_type] + " "
                    
                    #for questionAnswerObj in pairedScoreCardObj.questionAnswerObjList:
		      ##print " in PAIRED score card description ** " + str (questionAnswerObj.answerValue) + " ** answer " + str ( questionAnswerObj.questionAnswer.text) + str ( question.text)		      
                      #scoreCardDescription += "\"" + str(questionAnswerObj.totalAnswerValue) + "\" "   
		      
		    scoreCardDescription += "\"" + str(pairedScoreCardObj.maxScoreCardAnswerValue) + "\" "		      
                        
                    scoreCardDescription += "(" + pairedScoreCard.question.text + "). " 
		    
		    scoreCardDescription += 'Rule: '
		    	  
		    if scoreCard.paired_logic_type == 'union':
		      
		      #print  " ^^^ FOR DESCRIPTION ^^^ scorecard id = " + str (scoreCard.id) + "scoreCardObj.scoreCardScore " + str (scoreCardObj.scoreCardScore) + " scoreCard.logic_value " + str (scoreCard.logic_value) + " pairedScoreCardObj.scoreCardScore " + str (pairedScoreCardObj.scoreCardScore) + "scoreCard.paired_card.logic_value " + str (scoreCard.paired_card.logic_value)
		      
		      scoreCardDescription += "Value: " 
		      
		      #for questionAnswerObj in scoreCardObj.questionAnswerObjList:
			
			#scoreCardDescription += str(questionAnswerObj.totalAnswerValue)	
			
		      scoreCardDescription += str(scoreCardObj.maxScoreCardAnswerValue) 			
		      
		      scoreCardDescription += " >= " + str ( scoreCard.logic_value ) + " AND paired value: "

		      #for questionAnswerObj in pairedScoreCardObj.questionAnswerObjList:
			
			#scoreCardDescription += str(questionAnswerObj.totalAnswerValue)
			
		      scoreCardDescription += str(pairedScoreCardObj.maxScoreCardAnswerValue) 			

		      scoreCardDescription += " >= " + str ( scoreCard.paired_card.logic_value)

		    elif scoreCard.paired_logic_type == 'difference':

		      scoreCardDescription += "Value: " 
		      
		      scoreCardDescription += str(scoreCardObj.maxScoreCardAnswerValue) 		      

		      #for questionAnswerObj in scoreCardObj.questionAnswerObjList:
			
			#scoreCardDescription += str(questionAnswerObj.totalAnswerValue)
			
		      scoreCardDescription += " MINUS paired value: " 
		      
		      #for questionAnswerObj in pairedScoreCardObj.questionAnswerObjList:
			
			#scoreCardDescription += str(questionAnswerObj.totalAnswerValue)		      
		      
		      scoreCardDescription += str(pairedScoreCardObj.maxScoreCardAnswerValue) 		      

		      scoreCardDescription += " is = " + str(diff) + ", which needs to be >= " + str(scoreCard.logic_value)	      

		    elif scoreCard.paired_logic_type == 'percent':
		      
		      scoreCardDescription += "Value: " 
		      
		      scoreCardDescription += str(scoreCardObj.maxScoreCardAnswerValue) 		      
		      
		      #for questionAnswerObj in scoreCardObj.questionAnswerObjList:
			
			#scoreCardDescription += str(questionAnswerObj.totalAnswerValue)
			
		      scoreCardDescription += " PERCENT paired value: "
		      
		      scoreCardDescription += str(pairedScoreCardObj.maxScoreCardAnswerValue) 		      
		      
		      #for questionAnswerObj in pairedScoreCardObj.questionAnswerObjList:
			
			#scoreCardDescription += str(questionAnswerObj.totalAnswerValue)
			
		      scoreCardDescription += " is = " + str(round(quot,2)) + ", which needs to be >= " + str(scoreCard.logic_value)	   
  
                    scoreCardObj.scoreCardDescription = scoreCardDescription
		    
	    scoreValues = [ a.scoreCardScore for a in questionObj.scoreCardObjList ]

	    #if question.id == 91 or question.id == 89:
              
              #print " for question " + str (question ) + " scores are " + str (scoreValues)    
            
	    if len ( scoreValues ) > 0 :
	      questionObj.questionScore = max( scoreValues  )
	      questionObj.scoreCardObjList[scoreValues.index(max( scoreValues ))].isMax = True
            
        scoreValues = [ a.questionScore for a in sectionObj.questionObjList ]
          
        sectionObj.sectionScore = max( scoreValues )			
        
        sectionObj.questionObjList [ scoreValues.index(max( scoreValues )) ].isMax = True
        
  except:
    traceback.print_exc(file=sys.stdout)
    raise
  return instrumentObj

if __name__ == "__main__":
  main(sys.argv[1:])
  
#test()