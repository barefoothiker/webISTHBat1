#
#bat Web App
#Author:Siddhartha Mitra
#Rockefeller University, 2015
#
import re, sys, traceback, math, numpy
from bat.models import *
from numpy import *
import sys, traceback, datetime, time, math
from datetime import datetime
from bat.batReportObjs import *
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
from time import gmtime, strftime

#def countAnswers(administration, card):
	#question = card.question
	#answer_text = ''
	#if question.format=='enum':
		#answer = card.answer.get()
		#answer_text = answer.text
		#qais = QuestionAnswerInstance.objects.filter(administration = administration, question = question, answer = answer)
		#question_value = len(qais)
	#else:
		#question_value = 0
		#for answer in card.answer.all():
			#answer_text = " ".join((answer_text,"'%s'"%answer.text))
			#qais = QuestionAnswerInstance.objects.filter(administration = administration, question = question, answer = answer)
			#if qais:
				#for qai in qais:
					#if qai.answer.isfitb:
						#try:
							#if int(qai.blank.get().text) >= 0:
								#question_value += int(qai.blank.get().text)
						#except:
							#pass
					#else:
						#question_value += 1
	#return answer_text,question_value

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

def fetchContexts (sectionObj , administration):
  
  instrumentSection = sectionObj.section
  
  # Iterate over questions belonging to the section
  questions = instrumentSection.questions.all().order_by('sequence')

  # contexts 
  contexts = QuestionAnswerInstance.objects.filter(administration = administration, context__isnull = False).order_by("context")
  
  contextObjMap = {}
  
  for context in contexts:
    
      question = context.question      

      if question not in questions:
	continue
    
      contextId = context.context_id
      
      if contextId not in contextObjMap:
	
	contextObj = ContextObj()
	contextObjMap [contextId] = contextObj
      
      else:
	
	contextObj = contextObjMap [contextId]
	
      questionAnswerInstanceObj = QuestionAnswerInstanceObj()
      
      questionAnswerInstanceObj.questionAnswerInstance = context

      answer = context.answer
      
      # if enum, use the first answer for the scorecard	
      if question.format=='enum':
	  
	  answerValue = ''
    
	  try:
		
		answerValue = context.blank.get().text

	  except:
		pass	
    
	  if answerValue != '' and answerValue != 0 and answerValue != '0':
		
	    questionAnswerInstanceObj.answerValue = answerValue		
    
	  contextObj.questionAnswerInstanceObjList.append ( questionAnswerInstanceObj)	  
      
      else:

	#answerValue = context.answer.text
	
	answerValue = ''  
	
	#if answer.isfitb:

	try:
	      
	      answerValue = context.blank.get().text

	except:
	      pass
	
	if answerValue != '' and answerValue != 0 and answerValue != '0':
	  
       #   print " for context " + str (context.answer.text) + " adding answer " + str (answerValue)
	      
	  questionAnswerInstanceObj.answerValue = answerValue	
	  
	contextObj.questionAnswerInstanceObjList.append (questionAnswerInstanceObj)
	    
	contextObj.questionAnswerInstanceObjList.sort(key=lambda x: x.questionAnswerInstance.question.text)
	  
  for contextId, contextObj in contextObjMap.iteritems():
	  #print " context RRR " + str (contextId)
	  
      sectionObj.contextObjList.append ( contextObj)
      
  sectionObj.numContextObjs = len (sectionObj.contextObjList)  
	  
  return sectionObj

def fetchQuestionAnswerList (questionObj, administration, sectionObj):
  # check if there are any question answers, and if so, add the answers to the list. These answers are not scored
  # but for display purposes only.
  question = questionObj.question
  answers = question.answers.all()
  
  upin = administration.upin
  
  # if enum, use the first answer for the scorecard	
  if question.format=='enum':

      answer = answers[0]
    
      #print " ** ^^^^ ---- for answer ENUM " + str ( answer.text ) 	+ " for upin = " + str (upin.id)
      
      questionAnswerObj = QuestionAnswerObj()
      questionAnswerObj.questionAnswer = answer
      questionAnswerObj.question = question
      questionAnswerObj.answerText = ''

      # fetch the question and answer instances, and update the score with the number of such responses
      questionAnswerInstances = QuestionAnswerInstance.objects.filter(administration = administration, question = question, answer = answer)
      
      numAnswers = len(questionAnswerInstances)
      answerValue = ''

      if len(questionAnswerInstances) > 0 :
	  questionAnswerObj.ifAnswered = True
	  
	  #print " ** ^^^^ ---- !!!! for numeric answer ENUM "
	  
	  questionAnswerInstance = questionAnswerInstances[0]

	  try:
		#print " ** ^^^^ (((((((( ---- !!!! for numeric answer ENUM 222 " + str ( questionAnswerInstance.blank.get().text )
		
		if int(questionAnswerInstance.blank.get().text) >= 0:
		  
		  answerValue = int(questionAnswerInstance.blank.get().text)

	  except:
		pass	

      if answerValue != '' and answerValue != 0 and answerValue != '0':
	    
	questionAnswerObj.ifAnswered = True	
	questionAnswerObj.answerValue = answerValue
	questionAnswerObj.numAnswers = numAnswers
	
	questionAnswerObj.totalAnswerValue = numAnswers	
	if questionAnswerObj.totalAnswerValue == '':
	  questionAnswerObj.totalAnswerValue = answerValue  

      questionObj.questionAnswerObjList.append ( questionAnswerObj)
      
  else:
      # for each answer in the list
      for answer in answers:
	
	  #print " answers are  = " + str ( answers )

	  # fetch the question and answer instances
	  questionAnswerInstances = QuestionAnswerInstance.objects.filter(administration = administration, question = question, answer = answer)

	  questionAnswerObj = QuestionAnswerObj()
	  questionAnswerObj.questionAnswer = answer
	  questionAnswerObj.answerText = answer.text
	  
	  totalAnswerValue = '' 

	  for questionAnswerInstance in questionAnswerInstances:
	    
	      answerValue = answer.text
	      questionAnswerObj.answerText = ''
	      
	      #print " ** ^^^^ ---- for answer " + str ( answer.text ) 			    

	      questionAnswerObj.ifAnswered = True
		
	      if answer.isfitb:
		try:
		      #print " ** ^^^^ ---- !!!! for numeric answer " + str ( questionAnswerInstance.blank.get().text )
		      
		      if int(questionAnswerInstance.blank.get().text) >= 0:
			
			answerValue = int(questionAnswerInstance.blank.get().text)
			#totalAnswerValue += answerValue

		except:
		      pass

	      questionAnswerObj.answerTextList.append(answer.text)		      

	      if answerValue != '' and answerValue != 0 and answerValue != '0':
		    
		questionAnswerObj.ifAnswered = True	
		questionAnswerObj.answerValue = answerValue
		
		if questionAnswerObj.totalAnswerValueString != '':
		  
		  questionAnswerObj.totalAnswerValueString += ", "
		
		questionAnswerObj.totalAnswerValueString += str(answerValue)		
	       
		questionAnswerObj.questionAnswerInstanceList.append (questionAnswerInstance)
	      
		
	  questionAnswerObj.answerTextString = ','.join(questionAnswerObj.answerTextList)
	      
	  questionObj.questionAnswerObjList.append ( questionAnswerObj)		
	  
  return questionObj
  
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

	    print " !!!@@@@@ len scorecard = " + str(len(scoreCards))
            # iterate over score cards. Each record in the score card represents a different answer to the same question.
            for scoreCard in scoreCards:
	      
	        print " !!!@@@@@ scorecard = " + str(scoreCard)
	      
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

def getSelectionObj(request):

  selectionObj = SelectionObj()

  studyId = request.POST.get('studyId', 0 )   
  siteId = request.POST.get('siteId', 0 )   
  instrumentAdministratorId = request.POST.get('instrumentAdministratorId', 0 )   
  instrumentId = request.POST.get('instrumentId', 0 )   
  diagnosisId = request.POST.get('diagnosisId', 0 )  
  encodingFormat = request.POST.get('encodingFormat', 0 )   

  study = ''
  if studyId != 0:
    study = Study.objects.get ( pk = studyId )

  site = ''
  if siteId != 0 and siteId != '':
    site = Site.objects.get ( pk = siteId )

  instrumentAdministrator = ''
  print " adimn *** = " + str(instrumentAdministratorId)
  if instrumentAdministratorId != 0 and instrumentAdministratorId != '':
    instrumentAdministrator = InstrumentAdministrator.objects.get ( pk = instrumentAdministratorId )

  instrument = ''
  if instrumentId != 0:
    instrument = Instrument.objects.get ( pk = instrumentId )

  diagnosis = ''
  if diagnosisId != 0:
    diagnosis = Diagnosis.objects.get ( pk = diagnosisId )

  selectionObj.site = site
  selectionObj.instrumentAdministrator = instrumentAdministrator
  selectionObj.instrument = instrument
  selectionObj.study = study
  selectionObj.diagnosis = diagnosis
  selectionObj.encodingFormat = encodingFormat   

  return selectionObj

def getReportOptionsObj(request):
  
  reportOptionsObj = ReportOptionsObj (  )

  downloadOrPreview = request.POST.get('downloadOrPreview',"0")
  
  reportUpinIds = request.POST.getlist('reportUpinId' )    
  instrumentSectionIds = request.POST.getlist('instrumentSectionId')

  sectionQuestionIds = request.POST.getlist('sectionQuestionId')    
  multipleChoiceIds = request.POST.getlist('multipleChoiceId')

  printSelectionParameters = request.POST.get('printSelectionParameters',"0")
  
  reportOptionsObj.downloadOrPreview = downloadOrPreview
  reportOptionsObj.reportUpinIds = reportUpinIds
  reportOptionsObj.instrumentSectionIds = instrumentSectionIds
  reportOptionsObj.multipleChoiceIds = multipleChoiceIds

  reportOptionsObj.printSelectionParameters = False

  if printSelectionParameters == "1":
    reportOptionsObj.printSelectionParameters = True
    
  print " ^^^^^ instrumentSectionIds are " + str (reportOptionsObj.instrumentSectionIds)  
  
  return reportOptionsObj

def getReportObj(upinObjList, selectionObj, reportOptionsObj):

  reportObj = ReportObj()

  try:  

    instrumentSections = InstrumentSection.objects.filter ( instrument = selectionObj.instrument )  

    questionCounter = 0
    sectionCounter = 0
    answerCounter = 0
    
    #print " before iterate sections " + str (".") + " for sections " + str (reportOptionsObj.instrumentSections)

    for instrumentSectionId in reportOptionsObj.instrumentSectionIds:
      
      instrumentSection = InstrumentSection.objects.get ( pk = instrumentSectionId)
      #reportObj.headerColumns.append ( instrumentSection.name)
      questions = Question.objects.filter ( instrumentsection = instrumentSection ).order_by("sequence")
      sectionCounter = sectionCounter + 1
      
      #print " iterate section " + str (instrumentSection)

     # print " before iterate querstions " + str (".") + " sections = " + str(instrumentSection)     

      for question in questions:

        questionCounter = questionCounter + 1   

        questionAnswers = question.answers.all()      
	
	#print " for question " + str (question)

        if str(question.id) in reportOptionsObj.multipleChoiceIds:                   

          for questionAnswer in questionAnswers:

	    #print " multiple choices for question " + str (questionCounter)
        
            #reportObj.questionCounters.append ( "MULT" + str ( questionCounter) )  

            reportObj.questionCounters.append ( "MULT " + str(questionAnswer.text) )  

            reportObj.headerColumns.append ( question.text)

            reportObj.subHeaderColumns.append ( questionAnswer.text)                        

            #reportObj.sectionCounters.append ( str ( sectionCounter ) )                         

            reportObj.sectionCounters.append ( str ( instrumentSection.name ) ) 

        else:

	  #print " not printing multiple choices for question " + str (questionCounter)

          #reportObj.questionCounters.append ( questionCounter )             

	  reportObj.questionCounters.append ( question.text )             

          reportObj.headerColumns.append ( question.text)

          reportObj.subHeaderColumns.append ( "")

          #reportObj.sectionCounters.append ( str ( sectionCounter ) )           

	  reportObj.sectionCounters.append ( str ( instrumentSection.name ) )   

    reportObj.headerColumns.append("Score")

    reportObj.subHeaderColumns.append ( "")

    reportObj.questionCounters.append ( "" )             

    reportObj.sectionCounters.append ( "" )        

    reportDetailObjList = []

    #print " in report obj for upin "
    
    for upinObj in upinObjList: 
      
      #print " in report obj for upin " + str ( upinObj.upin.id ) + " report upin ids " + str(reportOptionsObj.reportUpinIds)

      if str(upinObj.upin.id) not in reportOptionsObj.reportUpinIds: 
        continue

      #print " ******* after filter in report obj for upin " + str ( upinObj.upin.id )

      reportDetailObj = ReportDetailObj()   
      reportDetailObj.upinId = upinObj.upin.id
      reportDetailObj.columnValues.append ( upinObj.upin.id )

      #reportDetailObj.columnValues.append ( selectionObj.site )
      #reportDetailObj.columnValues.append ( selectionObj.instrumentAdministrator )

      reportDetailObj.columnValues.append ( upinObj.administration.site )
      reportDetailObj.columnValues.append ( upinObj.administration.instrumentadministrator )

      administration = upinObj.administration
      
      if administration.stop is not None:

	difference = administration.stop - administration.start
	reportDetailObj.columnValues.append ( str(difference.seconds/60) )

      else:

	reportDetailObj.columnValues.append ("Administration not completed.")
	
      instrumentObj = upinObj.instrumentObj

      for sectionObj in instrumentObj.sectionObjList :
        
        if str(sectionObj.section.id) not in reportOptionsObj.instrumentSectionIds:
            continue
        
        #reportDetailObj.columnValues.append ( sectionObj.sectionScore )            

        for questionObj in sectionObj.questionObjList :

          questionAnswers = questionObj.question.answers.all()

          question = questionObj.question
	  
	  #if question.id in [53]:
	    
	    #print ( " question id = " + str(question.id) + " question " + str(question.text) + " format = " + str(questionObj.question.format) ) 

          if questionObj.question.format=='enum':
	    
	    if str(questionObj.question.id) in reportOptionsObj.multipleChoiceIds and len (questionAnswers) > 0:

	      for questionAnswer in questionAnswers:
		
		#if question.id in [53]:
		  
		  #print ( " questionAnswer = " + str(questionAnswer) ) 		

		#questionAnswer = questionAnswers[0]
    
		# fetch the question and answer instances, and update the score with the number of such responses
		questionAnswerInstances = QuestionAnswerInstance.objects.filter(administration = administration, question = question, answer = questionAnswer)
		answerValue = ''
		if len(questionAnswerInstances) > 0 :
		    #questionAnswerObj.answerScore = scoreCard.score			
		    #questionAnswerObj.ifAnswered = True
		  
		    #if question.id in [53]:
		  
		      #print " ENUM ********************** in FFFFFFFFFFFF ETCH SCORE QA instances!! for : " + str(upinObj.upin.id)
			
		    questionAnswerInstance = questionAnswerInstances[0]
		    
		    try:
			  
			  answerValue = questionAnswerInstance.blank.get().text
    
		    except:
			  pass	
			
		    #if answerValue == '':
		      #answerValue = questionAnswer.text
	
		    #questionAnswerObj.answerScore = answerValue
		    #if answerValue != '' and answerValue != 0 and answerValue != '0':
		      #questionAnswerObj.answerValue = answerValue
		      #questionAnswerObj.answerValueDisplay = answerValue
    
		    #print " ENUM &&&&&& answer value for : " + str(answerValue) + " .. text .. " + str (questionAnswerInstance.answer.text)
		
		reportDetailObj.columnValues.append ( answerValue )

	    else: 

		questionAnswer = questionAnswers[0]
		
		#if question.id in [53]:
		  
		  #print ( " questionAnswer = " + str(questionAnswer) ) 		

		#questionAnswer = questionAnswers[0]
    
		# fetch the question and answer instances, and update the score with the number of such responses
		questionAnswerInstances = QuestionAnswerInstance.objects.filter(administration = administration, question = question, answer = questionAnswer)
		answerValue = ''
		if len(questionAnswerInstances) > 0 :
		    #questionAnswerObj.answerScore = scoreCard.score			
		    #questionAnswerObj.ifAnswered = True
		  
		    #if question.id in [53]:
		  
		      #print " ENUM ********************** in FFFFFFFFFFFF ETCH SCORE QA instances!! for : " + str(upinObj.upin.id)
			
		    questionAnswerInstance = questionAnswerInstances[0]
		    
		    try:
			  
			  answerValue = questionAnswerInstance.blank.get().text
    
		    except:
			  pass	
			
		    #if answerValue == '':
		      #answerValue = questionAnswer.text
	
		    #questionAnswerObj.answerScore = answerValue
		    #if answerValue != '' and answerValue != 0 and answerValue != '0':
		      #questionAnswerObj.answerValue = answerValue
		      #questionAnswerObj.answerValueDisplay = answerValue
    
		    #print " ENUM &&&&&& answer value for : " + str(answerValue) + " .. text .. " + str (questionAnswerInstance.answer.text)
		
		reportDetailObj.columnValues.append ( answerValue )


          else:

            if str(questionObj.question.id) in reportOptionsObj.multipleChoiceIds:                   

              if len (questionAnswers) > 0:

                for questionAnswer in questionAnswers:

                  answerValue = ""

                  # fetch the question and answer instances, and update the score with the number of such responses
                  questionAnswerInstances = QuestionAnswerInstance.objects.filter(administration = upinObj.administration , question = questionObj.question, answer = questionAnswer) 

                  if len (questionAnswerInstances) > 0:

		    #if question.id in [53]:
		    
		      #print " IN NOT ENUM mult choice ********************** in FFFFFFFFFFFF ETCH SCORE QA instances!! for : " + str(upinObj.upin.id)

                    for questionAnswerInstance in questionAnswerInstances: 
		      answerValue == ''
		      try:
			answerValue = questionAnswerInstance.blank.get().text
		      except:
			pass
		      
		      #if answerValue == '':
                        #answerValue = questionAnswer.text

                      break
		    
		  #if question.id in [53]:		    
		    
		    #print " IN NOT ENUM mult choice answer for : " + str(answerValue)

                  reportDetailObj.columnValues.append ( answerValue )

            else:

              if len (questionAnswers) > 0:

                answered = False

                answerValue = ""

                for questionAnswer in questionAnswers: 

		  #print " for answer IN NOT ENUM NOT MULT CHOICE********************** i : " + str(upinObj.upin.id) + " answer = " + str (questionAnswer)

                  if answered:

                    break

                  # fetch the question and answer instances, and update the score with the number of such responses

                  administration = upinObj.administration

                  questionAnswerInstances = QuestionAnswerInstance.objects.filter(administration = administration ,  question = question, answer = questionAnswer) 

                  if len (questionAnswerInstances) > 0:
		    
  
		    #print " for question answer instance IN NOT ENUM NOT MULT CHOICE********************** i : " + str(upinObj.upin.id) 
		    

                    for questionAnswerInstance in questionAnswerInstances:

                      if questionAnswerInstance.answer.isfitb:
			#print " not fitb IN NOT ENUM NOT MULT CHOICE********************** i : " + str(upinObj.upin.id) + " answerValue = " + str (answerValue)
                        answerValue = questionAnswerInstance.blank.get().text 
                      else:
			
			answerValue = questionAnswerInstance.answer.text
	       
			#if question.id in [53]:
	       
			  #print " fitb IN NOT ENUM NOT MULT CHOICE********************** i : " + str(upinObj.upin.id) + " answerValue = " + str (answerValue)   
		      
		      #print " IN NOT ENUM NOT MULT CHOICE********************** i : " + str(upinObj.upin.id) + " answerValue = " + str (answerValue)

                      answered = True

                      break

		#print " appending IN NOT ENUM NOT MULT CHOICE********************** i : " + str(upinObj.upin.id) + " answerValue = " + str (answerValue) + " answered = " + str ( answered)
                if answered:
	 
		  #if question.id in [53]:

		    #print  " in else 1 " 

		  reportDetailObj.columnValues.append ( answerValue  )

                else:
		  
		  #if question.id in [53]:

		    #print " in else 2 "  
		  
		  reportDetailObj.columnValues.append ( "  ")                                    

              else:
		
		
		  #if question.id in [53]:
		      #print " in else 3 "  

		  reportDetailObj.columnValues.append ( "  ")

      reportDetailObj.columnValues.append ( sum( [ a.sectionScore for a in instrumentObj.sectionObjList if str(a.section.id) in reportOptionsObj.instrumentSectionIds] ) )

      reportDetailObjList.append (reportDetailObj)                

    reportObj.reportDetailObjList = reportDetailObjList

  except:
    traceback.print_exc(file=sys.stdout)

  return reportObj 
  
def getUPINObjList(selectionObj, fetchQuestionAnswerFlag):

  try:  

    upinObjList = [] 

    if selectionObj.site != '':

      administrations = Administration.objects.filter ( instrument = selectionObj.instrument, site = selectionObj.site )

    else:

      administrations = Administration.objects.filter ( instrument = selectionObj.instrument)

    instrumentAdministrator = selectionObj.instrumentAdministrator

    #roleId = selectionObj.instrumentAdministrator.role.id  

    for administration in administrations:
      #print " for upin " + str ( administration.upin ) + " site " + str (administration.site) + " study " + str ( administration.upin.study )

      #if not administration.upin :
    
         #continue

      upin = ''

      try:
      
	upin = administration.upin

      except:
	
	continue

      if upin.study != selectionObj.study:
        continue

      #authorizedRole = False

      #if (roleId == 1003 and upin.created_by == instrumentAdministrator) or (instrumentAdministrator.role.id == 1001 or instrumentAdministrator.role.id == 1002) :             
        #authorizedRole = True

      #if not authorizedRole:
        #continue

      upinObj = UPINObj()

      upinObj.upin = upin        

      upinObj.administration = administration

      fetchQuestionAnswerFlag = False

      fetchContextsFlag = False

      instrumentObj = calcScore(upin.id, fetchQuestionAnswerFlag, fetchContextsFlag)    

      upinObj.instrumentObj = instrumentObj

      upinObj.score = sum( [ a.sectionScore for a in instrumentObj.sectionObjList ] )             

      upinObjList.append ( upinObj )

      #if len ( upinObjList ) > 10 :
      #break

    upinObjList.sort(key=lambda x: x.upin.id)

  except:
    traceback.print_exc(file=sys.stdout)

  return upinObjList

def fetchGraphReportSummaryObj(instrument, siteIds, studyIds, instrumentAdministratorIds, sectionIds, sectionSummaryObjMap):
  
  try: 
   
    administrations = Administration.objects.filter ( instrument = instrument )
    
    for administration in administrations:
      
	#if instrument == demographicsInstrument:
	  #print " in demographics for admin " + str (administration) 	      
    
	if str(administration.site.id) not in siteIds:
	    continue
	 
	upin = administration.upin
	
	if str(upin.study.id) not in studyIds:
	    continue
	
	instrumentAdministrator = administration.instrumentadministrator 
	
	if str(instrumentAdministrator.id) not in instrumentAdministratorIds:
	    continue
	
	roleId = instrumentAdministrator.role.id  
	
	authorizedRole = False
	
	if (roleId == 1003 and upin.created_by == instrumentAdministrator) or (instrumentAdministrator.role.id == 1001 or instrumentAdministrator.role.id == 1002) :             
		authorizedRole = True
		
	if not authorizedRole:
	    continue
	
	#print " for adminsitration = " + str (administration) + " upin = " + str (administration.upin)
	
	questionAnswerInstances = list(QuestionAnswerInstance.objects.filter ( administration = administration, instrument = instrument ))
	
	questionAnswerInstances.sort(key=lambda x: x.question.text)
	
	for questionAnswerInstance in questionAnswerInstances:
	    
	    section = questionAnswerInstance.question.instrumentsection
	    
	    if str(section.id) not in sectionIds:
		continue	

	    questionAnswerInstanceValue = ''
	    
	    if questionAnswerInstance.answer.isfitb:
		questionAnswerInstanceValue = questionAnswerInstance.blank.get().text 
	    else:
		questionAnswerInstanceValue = questionAnswerInstance.answer.text			
		
	    question = questionAnswerInstance.question
	    
	    questionAnswer = questionAnswerInstance.answer                
	    
	    # if section exists in summary obj map                 
	    if section in sectionSummaryObjMap:
		
		#print " !!!!&&&&& section found = " + str (section)
    
		sectionSummaryObj = sectionSummaryObjMap[section]
		
		questionSummaryObjMap = sectionSummaryObj.questionSummaryObjMap
		
		#print " adding to old section " + str (administration) + " section " + str (section)                        
		
		# if key ( question + answer text ) exits in qa summary map
		if question in questionSummaryObjMap:
		    
		    #print " !!!!**** question found = " + str (question)
		    
		    questionSummaryObj = questionSummaryObjMap [question]
		    
		    questionAnswerSummaryObjMap = questionSummaryObj.questionAnswerSummaryObjMap
		    
		    if questionAnswerInstance.answer.isfitb:
			
			if questionAnswerInstanceValue in questionAnswerSummaryObjMap:
			
			    questionAnswerSummaryObj = questionAnswerSummaryObjMap [questionAnswerInstanceValue]
			
			else:
			
			    questionAnswerSummaryObj = QuestionAnswerSummaryObj()
			
			    questionAnswerSummaryObj.questionAnswer = questionAnswerInstanceValue
			    
			    questionAnswerSummaryObj.questionAnswerIsfitb = True
			    
			    questionAnswerSummaryObjMap [questionAnswerInstanceValue] = questionAnswerSummaryObj
			
			questionAnswerSummaryObj.answerValues.append ( questionAnswerInstanceValue )
    
			questionAnswerSummaryObj.administrationList.append(administration)			    
			#print " is fitb "
			#questionAnswerInstanceValue = questionAnswerInstance.blank.get().text 
		    else:
		    
			if questionAnswer in questionAnswerSummaryObjMap:
			    
			    #print " ^^^^^^^^^^ ****** for answer = " + str (questionAnswer) + " question = " + str (question) + " admin = " + str (administration)
			    
			    questionAnswerSummaryObj = questionAnswerSummaryObjMap [questionAnswer]
			    
			    questionAnswerSummaryObj.answerValues.append ( questionAnswerInstanceValue )
    
			    questionAnswerSummaryObj.administrationList.append(administration)
		    
		    #print " adding to existing qa section " + str (administration) + " qa " + str (keyString)
		    
	    else: # section does not exist
		  
		sectionSummaryObj = SectionSummaryObj ()
		
		sectionSummaryObj.section = section 
		
		questionSummaryObjMap = sectionSummaryObj.questionSummaryObjMap
		
		# Iterate over questions belonging to the section
		questions = section.questions.all().order_by('sequence')                    
    
		for question in questions : 
		
		    questionSummaryObj = QuestionSummaryObj()
    
		    questionAnswerSummaryObjMap = questionSummaryObj.questionAnswerSummaryObjMap
		    
		    #print " LOADING MAP for question " + str ( question ) 
		    
		    #for scoreCard in scoreCards:
		
		    questionAnswers = question.answers.all()
					    
		    if not questionAnswerInstance.answer.isfitb:
		
			for questionAnswer in questionAnswers:
			
			    if questionAnswer not in questionAnswerSummaryObjMap:
			    
				questionAnswerSummaryObj = QuestionAnswerSummaryObj ()
			    
				questionAnswerSummaryObj.questionAnswer = questionAnswer
			    
				questionAnswerSummaryObjMap [ questionAnswer ] = questionAnswerSummaryObj   
				    
				#print " LOADING MAP for question ANSWER " + str ( questionAnswer ) 
				
		    questionSummaryObjMap [question] = questionSummaryObj
		
		#print " adding to new section " + str (administration) + " section " + str (section)  
		
		sectionSummaryObjMap [ section ] = sectionSummaryObj
    
    #print " graphReportSelectionsObj " + str (graphReportSelectionsObj)
    
    for section, sectionSummaryObj in sectionSummaryObjMap.iteritems():
	
	for question, questionSummaryObj in sectionSummaryObj.questionSummaryObjMap.iteritems():
	  
	    questionAnswerSummaryObjList = []	  
	
	    totalNumAdministrations = 0
    
	    for questionAnswer, questionAnswerSummaryObj in questionSummaryObj.questionAnswerSummaryObjMap.iteritems():
	
		administrationList = questionAnswerSummaryObj.administrationList
		
		questionAnswerSummaryObj.numAdministrations = len (administrationList) 
		
		totalNumAdministrations = totalNumAdministrations + len (administrationList)
		
		#print " for answer " + str (questionAnswer) + " admins = " + str ( [x.upin.id for x in administrationList] )
		
		questionAnswerSummaryObjList.append (questionAnswerSummaryObj)
		
		if instrument.title == "ISTH/SSC Demographics Tool":
		
		  print " adding questionAnswerSummaryObj " + str (questionAnswerSummaryObj.questionAnswer)
    
	    questionSummaryObj.totalNumAdministrations = totalNumAdministrations 
	    
	    questionAnswerSummaryObjList.sort ( key = lambda x: x.questionAnswer, reverse = True)
	    
	    questionSummaryObj.questionAnswerSummaryObjList = questionAnswerSummaryObjList
	    
  except: 
    traceback.print_exc(file=sys.stdout)    
    raise   
	   
  return sectionSummaryObjMap

def createGraphReportObj(request):
    
  sectionSummaryObjMap = {}
  
  demographicsSectionSummaryObjMap = {}
  
  graphReportSelectionsObj = GraphReportSelectionsObj ()    
  
  try:

      printSelectionParameters = request.POST.getlist('printSelectionParameters' )
      
      studyIds = request.POST.getlist('studyId' )    
      #print " studies = " + str ( studyIds )
      sectionIds = request.POST.getlist('sectionId')
      #print " sections = " + str ( sectionIds )         
      instrumentAdministratorIds = request.POST.getlist('instrumentAdministratorId')    
      #print " instrumentAdministratorIds = " + str ( instrumentAdministratorIds )        
      siteIds = request.POST.getlist('siteId')  
      
      displayDemographicsData = request.POST.get('displayDemographicsData','0')
      
      graphReportSelectionsObj = GraphReportSelectionsObj()
      
      for studyId in studyIds:
	  study = Study.objects.get ( pk = studyId)
	  graphReportSelectionsObj.studies.append ( study )        

      for sectionId in sectionIds:
	  section = InstrumentSection.objects.get ( pk = sectionId)
	  graphReportSelectionsObj.sections.append ( section )     
	  
      for siteId in siteIds:
	  site = Site.objects.get ( pk = siteId)
	  graphReportSelectionsObj.sites.append ( site )        

      for instrumentAdministratorId in instrumentAdministratorIds:
	  instrumentAdministrator = InstrumentAdministrator.objects.get ( pk = instrumentAdministratorId)
	  graphReportSelectionsObj.instrumentAdministrators.append ( instrumentAdministrator ) 
	  
      graphReportSelectionsObj.printSelectionParameters = printSelectionParameters
      graphReportSelectionsObj.displayDemographicsData = displayDemographicsData
		      
      batInstrument = Instrument.objects.filter ( title = ISTH_BAT_INSTRUMENT) [0]
      
      sections = batInstrument.sections.all()
      
      if displayDemographicsData == '1':
      
	demographicsInstrument = Instrument.objects.filter ( title = DEMOGRAPHICS_INSTRUMENT) [0]
      
	demographicsSections = demographicsInstrument.sections.all()
	
	demographicsSectionIds = []

	if len ( demographicsSections ) > 0:

	  demographicsSection = demographicsSections[0]
	  
	  demographicsSectionIds.append (str(demographicsSection.id))
	  
	  #print " for demographics " 

	  demograhicsSectionSummaryObjMap = fetchGraphReportSummaryObj(demographicsInstrument, siteIds, studyIds, instrumentAdministratorIds, demographicsSectionIds, demographicsSectionSummaryObjMap)
	
      sectionSummaryObjMap = fetchGraphReportSummaryObj(batInstrument, siteIds, studyIds, instrumentAdministratorIds, sectionIds, sectionSummaryObjMap)
	      
  except:
    traceback.print_exc(file=sys.stdout)    
    raise
  
  return sectionSummaryObjMap, demographicsSectionSummaryObjMap, graphReportSelectionsObj   

def loadSummaryReportObj(summaryReportMonthObj, administration):
  
  try:
    
    userMap = summaryReportMonthObj.userMap
    
    #print " appending to month year = " + str (startMonthYear) + " for site = " + str ( site ) + " admin = " + str ( administration ) +  " user = " + str ( instrumentAdministrator )
    
    instrumentAdministrator = administration.instrumentadministrator
    
    if instrumentAdministrator in userMap:
      
	summaryReportUserObj = userMap[instrumentAdministrator]
	
	summaryReportUserObj.adminList.append ( administration )
	
	#print " adding adminstration " + str (instrumentAdministrator) + " for month year ) " + str (adminMonthYear)
	summaryReportUserObj.adminCount = summaryReportUserObj.adminCount + 1
    
  except:
    traceback.print_exc(file=sys.stdout)    
    raise
  
  return      

def createSummaryReportObj(request):
  
  summaryReportSelectionsObj = SummaryReportSelectionsObj ()    
  
  siteSummaryObjMap = {}
  studySummaryObjMap = {}
  
  try:
    
    studyIds = request.POST.getlist('studyId' )             
    siteIds = request.POST.getlist('siteId')     
    instrumentAdministratorIds = request.POST.getlist('instrumentAdministratorId')
    
    printSelectionParameters = request.POST.getlist('printSelectionParameters')
    
    startDateString = request.POST.get('startDate',"")
    endDateString = request.POST.get('endDate',"")
    
    summaryReportSelectionsObj.startDate = startDateString
    summaryReportSelectionsObj.endDate = endDateString    
    
    for studyId in studyIds:
	study = Study.objects.get ( pk = studyId)
	summaryReportSelectionsObj.studies.append ( study )          
	
    for siteId in siteIds:
	site = Site.objects.get ( pk = siteId)
	summaryReportSelectionsObj.sites.append ( site )        

    for instrumentAdministratorId in instrumentAdministratorIds:
	instrumentAdministrator = InstrumentAdministrator.objects.get ( pk = instrumentAdministratorId)
	summaryReportSelectionsObj.instrumentAdministrators.append ( instrumentAdministrator ) 
	
    summaryReportSelectionsObj.sites.sort (key=lambda x: x.name)  
    summaryReportSelectionsObj.studies.sort (key=lambda x: x.name)  	
	
    summaryReportSelectionsObj.printSelectionParameters = printSelectionParameters    
    
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
    
    monthYearList = []
                
    instrumentAdministrators = InstrumentAdministrator.objects.all ()  
    
    print " start year = " + str ( startYear) + " end year = " + str ( endYear) + " compare " + str (endYear > startYear)
    print " start month = " + str ( startMonth) + " end month = " + str ( endMonth)
    
    endMonthSave = endMonth
    
    if endYear > startYear:
      endMonthForYear = 12
    else:
      endMonthForYear = endMonth
    
    while year >= startYear and year <= endYear:
      #print " for year " + str ( year ) + " month is " + str (month) + " start month = " + str (startMonth) + " end month for year = " + str (endMonthForYear)
      while month >= startMonth and month <= endMonthForYear:
	#print " ****month = " + str ( month) + " yr = " + str ( year)
	if ( year < endYear and month <= 12 ) or ( year == endYear and month <= endMonthForYear):
	  monthYearList.append( str (month) + "-" + str(year) )	
	  #print " ADDING month year = " + str (month) + "-" + str(year)
	month = month + 1
	
      month = 1
      year = year + 1
      if year > startYear:
	startMonth = 1
      if year < endYear: 
	endMonthForYear = 12      
      else:
	endMonthForYear = endMonthSave
	
    # build site map    
    sites = Site.objects.all()        
    for site in sites:
      if str(site.id) not in siteIds:
	continue 
      summaryReportObj = SummaryReportObj()	
      summaryReportObj.monthYearList = monthYearList
      for monthYear in monthYearList:
	summaryReportMonthObj = SummaryReportMonthObj()
	summaryReportObj.monthYearMap[monthYear] = summaryReportMonthObj
	#print " adding to map date site " + str ( monthYear )
      siteSummaryObjMap [site] = summaryReportObj
      
    # build study map    
    studies = Study.objects.all()        
    for study in studies:
      if str(study.id) not in studyIds:
	continue
      summaryReportObj = SummaryReportObj()	
      summaryReportObj.monthYearList = monthYearList      
      for monthYear in monthYearList:
	summaryReportMonthObj = SummaryReportMonthObj()
	summaryReportObj.monthYearMap[monthYear] = summaryReportMonthObj      
	#print " adding to map date site " + str ( monthYear)	
      studySummaryObjMap [study] = summaryReportObj            

    for instrumentAdministrator in instrumentAdministrators:
      if str ( instrumentAdministrator.id) in instrumentAdministratorIds:
	allowedSites = instrumentAdministrator.allowed_sites.all()
	
	for site in allowedSites:
	  if site in siteSummaryObjMap:
	    summaryReportObj = siteSummaryObjMap [site]
	    summaryReportObj.instrumentAdministratorList.append(instrumentAdministrator)
	    for monthYear in monthYearList:
	      summaryReportMonthObj = summaryReportObj.monthYearMap[monthYear]
	      
	      userMap = summaryReportMonthObj.userMap
	      summaryReportUserObj = SummaryReportUserObj()
	      userMap[instrumentAdministrator] = summaryReportUserObj	      
	  
	allowedStudies = instrumentAdministrator.allowed_studies.all()
	
	for study in allowedStudies:
	  if study in studySummaryObjMap:	  
	    summaryReportObj = studySummaryObjMap [study]
	    summaryReportObj.instrumentAdministratorList.append(instrumentAdministrator)
	    for monthYear in monthYearList:
	      summaryReportMonthObj = summaryReportObj.monthYearMap[monthYear]
	      
	      userMap = summaryReportMonthObj.userMap
	      summaryReportUserObj = SummaryReportUserObj()
	      userMap[instrumentAdministrator] = summaryReportUserObj		
    
    summaryReportSelectionsObj.startDateString = startDate
    summaryReportSelectionsObj.endDateString = endDate   
      
    selectedAdministrations = Administration.objects.filter (start__range = [startDate, endDate ],stop__range = [startDate, endDate ] )
    
    summaryReportObj = SummaryReportObj()
    
    userReportPrintObjMap = {}
    userReportPrintObjList = []
    
    totalMonthAdminCount = 0
    totalAdminCount = 0
    
    instrumentAdministrators = InstrumentAdministrator.objects.all()
    instrumentAdministratorList = []
    
    for instrumentAdministrator in instrumentAdministrators :
	
	waiverOkFlag = getWaiverOkFlag (instrumentAdministrator)
		
	if not waiverOkFlag :
	    continue  
	  
	if str(instrumentAdministrator.id) not in instrumentAdministratorIds:
	  continue	  
	  
	instrumentAdministratorList.append (instrumentAdministrator)	
	
	userReportPrintObj = UserReportPrintObj()
	
	userReportPrintObj.instrumentAdministrator = instrumentAdministrator
	
	userSiteReportObjMap = userReportPrintObj.userSiteReportObjMap
	userStudyReportObjMap = userReportPrintObj.userStudyReportObjMap
	
	for site in summaryReportSelectionsObj.sites:
	  
	  userSiteReportPrintObj = UserSiteReportPrintObj()
	  userSiteReportPrintObj.site = site
	  userSiteReportObjMap [ site ] = userSiteReportPrintObj  	

	for study in summaryReportSelectionsObj.studies:
	  
	  userStudyReportPrintObj = UserStudyReportPrintObj()
	  userStudyReportPrintObj.study = study
	  userStudyReportObjMap [ study ] = userStudyReportPrintObj  
	
	userReportPrintObjMap [ instrumentAdministrator ] = userReportPrintObj
	
	#print " adding instrument admin -------- " + str (instrumentAdministrator)

    #print " after adding admins @@@@@@@@ "
    
    for index, administration in enumerate ( selectedAdministrations ):
      
      if administration.start > administration.stop:
	continue
      
      adminMonth = administration.start.month
      adminYear = administration.start.year
      
      adminMonthYear = str ( adminMonth ) + "-" + str ( adminYear ) 
            
      instrumentAdministrator = administration.instrumentadministrator
      
      #print " administrator is " + str (instrumentAdministrator)
      
      site = administration.site
      
      study = administration.upin.study
      
      if str(site.id) not in siteIds:
	continue
      
      if str(study.id) not in studyIds:
	continue
      
      if str(instrumentAdministrator.id) not in instrumentAdministratorIds:
	continue

      if site in siteSummaryObjMap:
	      
	siteSummaryReportObj = siteSummaryObjMap [site]

      if study in studySummaryObjMap:
		
	studySummaryReportObj = studySummaryObjMap [study]		  

      totalAdminCount = totalAdminCount +1
      siteSummaryReportObj.totalAdminCount = totalAdminCount  
      studySummaryReportObj.totalAdminCount = totalAdminCount  
      
      siteMonthYearMap = siteSummaryReportObj.monthYearMap 
      
      summaryReportMonthObj = siteMonthYearMap [adminMonthYear]      

      loadSummaryReportObj(summaryReportMonthObj, administration) 
      
      totalMonthAdminCount = totalMonthAdminCount + 1
      summaryReportMonthObj.totalMonthAdminCount = totalMonthAdminCount
      
      studyMonthYearMap = studySummaryReportObj.monthYearMap      

      summaryReportMonthObj = studyMonthYearMap [adminMonthYear]      
     
      loadSummaryReportObj(summaryReportMonthObj, administration)
            
      totalMonthAdminCount = totalMonthAdminCount + 1
      summaryReportMonthObj.totalMonthAdminCount = totalMonthAdminCount      

      if instrumentAdministrator in userReportPrintObjMap:
	
	userReportPrintObj = UserReportPrintObj()
	
	userReportPrintObj = userReportPrintObjMap [instrumentAdministrator]
	
	userStudyReportObjMap = userReportPrintObj.userStudyReportObjMap
	userSiteReportObjMap  = userReportPrintObj.userSiteReportObjMap
	
	userStudyReportPrintObj = ''
	userSiteReportPrintObj = ''
	
	if site in userSiteReportObjMap:
	  
	  userSiteReportPrintObj = userSiteReportObjMap [ site ] 
	
	if study in userStudyReportObjMap:
	  
	  userStudyReportPrintObj = userStudyReportObjMap [ study ] 
	  
	userStudyReportPrintObj.totalNumAdministrations = userStudyReportPrintObj.totalNumAdministrations + 1
	userStudyReportPrintObj.administrationList.append ( administration )

	userSiteReportPrintObj.totalNumAdministrations = userSiteReportPrintObj.totalNumAdministrations + 1
	userSiteReportPrintObj.administrationList.append ( administration )
	
    siteReportPrintObjList = []
    
    #print " total admin count = " + str (summaryReportObj.totalAdminCount)
		
    for site, summaryReportObj in siteSummaryObjMap.iteritems() :
      
      siteReportPrintObj = SiteReportPrintObj()
      
      if site.name.find("'") != -1:

	site.name = site.name.replace("'","")
      
      siteReportPrintObj.site = site
      
      siteReportPrintObj.summaryReportObj = summaryReportObj
      
      siteReportPrintObj.instrumentAdministratorList = summaryReportObj.instrumentAdministratorList
      siteReportPrintObj.monthYearList = summaryReportObj.monthYearList
      
      userCount = 0      
      for monthYear, summaryReportMonthObj in summaryReportObj.monthYearMap.iteritems() :
 
	instrumentAdministratorCount = 0	
	for instrumentAdministrator, summaryReportUserObj in summaryReportMonthObj.userMap.iteritems():

	  summaryReportPrintObj = SummaryReportPrintObj()
	  
	  summaryReportPrintObj.monthYearId = userCount
	  summaryReportPrintObj.instrumentAdministratorId = instrumentAdministratorCount
	  summaryReportPrintObj.numAdministrations = summaryReportUserObj.adminCount
	  
	  siteReportPrintObj.summaryReportPrintObjList.append (summaryReportPrintObj)
	  
	  instrumentAdministratorCount = instrumentAdministratorCount + 1
	  
	userCount = userCount +1
	
	siteReportPrintObj.numInstrumentAdministrators = instrumentAdministratorCount

      siteReportPrintObjList.append (siteReportPrintObj)
      	
      studyReportPrintObjList = []
		  
    for study, summaryReportObj in studySummaryObjMap.iteritems() :
      
      studyReportPrintObj = StudyReportPrintObj()
      
      studyReportPrintObj.study = study	
      
      studyReportPrintObj.summaryReportObj = summaryReportObj
      
      studyReportPrintObj.instrumentAdministratorList = summaryReportObj.instrumentAdministratorList
      studyReportPrintObj.monthYearList = summaryReportObj.monthYearList
      
      userCount = 0      
      for monthYear, summaryReportMonthObj in summaryReportObj.monthYearMap.iteritems() :
	#print " month year = " + str ( monthYear ) 
	
	instrumentAdministratorCount = 0
	for instrumentAdministrator, summaryReportUserObj in summaryReportMonthObj.userMap.iteritems():
	  #print " user = " + str ( user ) + " count = " + str (summaryReportUserObj.adminCount)
	  summaryReportPrintObj = SummaryReportPrintObj()
	  
	  summaryReportPrintObj.monthYearId = userCount
	  summaryReportPrintObj.instrumentAdministratorId = instrumentAdministratorCount
	  summaryReportPrintObj.numAdministrations = summaryReportUserObj.adminCount
	  
	  studyReportPrintObj.summaryReportPrintObjList.append (summaryReportPrintObj)
	  
	  instrumentAdministratorCount = instrumentAdministratorCount + 1
	  
	userCount = userCount + 1
	
	studyReportPrintObj.numInstrumentAdministrators = instrumentAdministratorCount	

      studyReportPrintObjList.append (studyReportPrintObj) 
      
    userReportSiteList = []
    userReportStudyList = []
    
    for instrumentAdministrator,userReportPrintObj in userReportPrintObjMap.items():
      
      userSiteReportObjMap = userReportPrintObj.userSiteReportObjMap
      
      for site, userSiteReportPrintObj in userSiteReportObjMap.items():
	
	userReportPrintObj.userSiteReportPrintObjList.append ( userSiteReportPrintObj )
	
	userReportSiteList.append(site)
	
	#print " for user " + str (instrumentAdministrator) + " adding for site " + str ( site )
	
      userStudyReportObjMap = userReportPrintObj.userStudyReportObjMap
      
      for study, userStudyReportPrintObj in userStudyReportObjMap.items():
	
	userReportPrintObj.userStudyReportPrintObjList.append ( userStudyReportPrintObj )
	
	userReportStudyList.append(study)
	  
	  #print " for user " + str (instrumentAdministrator) + " adding for study " + str ( study )
	  
	#for userStudyReportPrintObj in userReportPrintObj.userStudyReportPrintObjList :	  
	  
	  #print " **** study = " + str ( userStudyReportPrintObj.study ) + " num admin = " + str ( userStudyReportPrintObj.totalNumAdministrations) 

	#for userSiteReportPrintObj in userReportPrintObj.userSiteReportPrintObjList :	  
	  
	  #print " **** site = " + str ( userSiteReportPrintObj.site ) + " num admin = " + str ( userSiteReportPrintObj.totalNumAdministrations) 

      userReportPrintObj.userSiteReportPrintObjList.sort (key=lambda x: x.site.name)  
      userReportPrintObj.userStudyReportPrintObjList.sort (key=lambda x: x.study.name)  
      
      userReportPrintObjList.append (userReportPrintObj)
      
    userReportPrintSummaryObj = UserReportPrintSummaryObj()
    
    userReportSiteList.sort ()
    userReportStudyList.sort ()
    
    userReportPrintSummaryObj.userReportPrintObjList = userReportPrintObjList
    userReportPrintSummaryObj.userReportSiteList = userReportSiteList
    userReportPrintSummaryObj.userReportStudyList = userReportStudyList
      
  except:
    traceback.print_exc(file=sys.stdout)    
    raise

  return summaryReportSelectionsObj, siteReportPrintObjList , studyReportPrintObjList , userReportPrintSummaryObj

def getWaiverOkFlag(instrumentAdministrator):
    
    time365Days = datetime.timedelta(days=365)	

    waiverOkFlag = False

    earliest_cutoff_date = datetime.datetime.strptime(EARLIEST_CUTOFF_DATE, "%m/%d/%Y")

    if instrumentAdministrator.waiver_signed and instrumentAdministrator.waiver_signed.date() > earliest_cutoff_date.date() :	    

	numDaysElapsed = datetime.datetime.today() - instrumentAdministrator.waiver_signed
    
	waiverExpirationDate = instrumentAdministrator.waiver_signed + time365Days
	
	waiverOkFlag = True	
	
	#if numDaysElapsed < time365Days:
	  #waiverOkFlag = True	

    return waiverOkFlag 