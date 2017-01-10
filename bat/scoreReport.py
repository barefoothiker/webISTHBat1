import re, sys, traceback, math, numpy
from bat.models import *
from numpy import *
import sys, traceback, datetime, time, math , csv
from datetime import datetime
from bat.batReportObjs import *
from bat.batReportConstants import *
import logging


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

# Objs for summarising results and display
# In order of hierarchy
# The instrument has sections. 
# Each section has multiple questions. 
# Each question can be associated with multiple scorecards.
# Each scorecard can be associated with multiple answers. 
# The score of a question is the max obtained from different scorecards.

# The flag ifAnswered is set if there is a question answer instance that is present for the answer
# The answer score is populated if present


# Test UPIN ids ( as per Evernote note ) 

#UPIN: 356665// (blood transfusion as a medical treatment after surgery)// ISTH score is 2 (should be 4) // Modified ISTH score is 0 (should be 4)

#UPIN: 990756// (Menorrhagia Section, treatment reported as iron therapy) //ISTH score is correct (2)// Modified ISTH score is 1 (should be 3)

#UPIN 582203// (1. GI Bleeding=Yes 2. Hematochezia 3. Associated with Ulcer)// ISTH score is correct// Modified ISTH score is 0 (should be 1)

#UPIN 657073// (1. 2 surgeries 2. no pre-treatment 3. no post-op bleeding) // ISTH score is correct// Modified ISTH score is 0 (should be -1)

#UPIN 107416// (1. 1 intervention 2. no pre-treatment 3. no bleeding pre-treatment was platelet infusion.
#No bleeding or treatment for post-op bleeding)//ISTH (or modified?) score 1 (should be 0)

def fetchScoreCardObj(administration, scoreCard):
    
  try:

    # question related to scorecard.
    scoreCardObj = ScoreCardObj() 
    scoreCardObj.scoreCard = scoreCard   

    question = scoreCard.question

    # answers pertaining to the scorecard 
    answers = scoreCard.answer.all()	

    scores = []

    # if enum, use the first answer for the scorecard	
    if question.format=='enum':

        answer = answers[0]

        answerObj = AnswerObj()
        answerObj.answer = answer

        # fetch the question and answer instances, and update the score with the number of such responses
        questionAnswerInstances = QuestionAnswerInstance.objects.filter(administration = administration, question = question, answer = answer)

        if len(questionAnswerInstances) > 0 :
            answerObj.answerScore = scoreCard.score			
            answerObj.ifAnswered = True

        scoreCardObj.answerObjList.append ( answerObj)

    else:
        # for each answer in the list
        for answer in answers:

            # fetch the question and answer instances
            questionAnswerInstances = QuestionAnswerInstance.objects.filter(administration = administration, question = question, answer = answer)

            answerObj = AnswerObj()
            answerObj.answer = answer

            for questionAnswerInstance in questionAnswerInstances:

                answerObj.ifAnswered = True
                # if numeric, get the value entered and compare with any paired logic value as needed
                if answer.isfitb:

                    answerValue = 0

                    try:
                        if int(questionAnswerInstance.blank.get().text) >= 0:
                            answerValue = int(questionAnswerInstance.blank.get().text)
                    except:
                        pass
                    # if there was an answer >0 entered, then check logic value if present. If logic value present and answer entered greater 
                    # than logic value, add score card value, else just add scorecard value if answer > 0
                    if answerValue > 0:
                        if scoreCard.logic_value is not None and answerValue >= scoreCard.logic_value:
                            answerObj.answerScore = scoreCard.score								
                        else:
                            answerObj.answerScore = scoreCard.score								
                else: 
                    answerObj.answerScore = scoreCard.score

                answerObj.ifAnswered = True				

            scoreCardObj.answerObjList.append ( answerObj)

    scoreCardObj.scoreCardScore = max( [a.answerScore for a in scoreCardObj.answerObjList])
    
  except:
    raise

  return scoreCardObj

def calcScore(upinId):

  try:
    # UPIN
    upin = UPIN.objects.get ( pk = upinId )
    
    batInstrument = Instrument.objects.filter ( title = ISTH_BAT_INSTRUMENT) 
  
    administration = Administration.objects.filter ( upin = upin, instrument = batInstrument ).exclude(stop__isnull = True )[0]

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

        # Iterate over questions belonging to the section
        questions = instrumentSection.questions.all().order_by('sequence')

        for question in questions:

            # instantiate question obj and add to section obj
            questionObj = QuestionObj() 
            questionObj.question = question

            sectionObj.questionObjList.append ( questionObj ) 

            # get the score cards for the question 			
            scoreCards  = ScoreCard.objects.filter(instrument = instrument, section = instrumentSection, question = question, score_name=ISTH_SCORE_NAME).exclude(score = 0)
            # skip if no scorecards found for question
            if len ( scoreCards ) == 0 :
                continue
            # iterate over score cards. Each record in the score card represents a different answer to the same question.
            for scoreCard in scoreCards:

                scoreCardObj = fetchScoreCardObj ( administration, scoreCard )

                questionObj.scoreCardObjList.append (scoreCardObj )

                # if paired logic, get paired score card

                if scoreCard.paired_logic_type != "simple":

                    pairedScoreCard = scoreCard.paired_card

                    pairedScoreCardObj = fetchScoreCardObj ( administration, pairedScoreCard )	

                    # depending on paired logic, calculate score
                    if scoreCard.paired_logic_type == 'union':
                        if scoreCardObj.scoreCardScore >= scoreCard.logic_value and pairedScoreCardObj.scoreCardScore >= scoreCard.paired_card.logic_value:
                            scoreCardObj.scoreCardScore = scoreCard.score

                    elif scoreCard.paired_logic_type == 'difference':
                        diff = scoreCardObj.scoreCardScore - pairedScoreCardObj.scoreCardScore
                        if (diff) >= scoreCard.logic_value:
                            scoreCardObj.scoreCardScore = scoreCard.score

                    elif scoreCard.paired_logic_type == 'percent':
                        quot = (float(scoreCardObj.scoreCardScore) / (float(pairedScoreCardObj.scoreCardScore)+0.000001))*100
                        if quot >= float(scoreCard.logic_value):
                            scoreCardObj.scoreCardScore = scoreCard.score
                            
                    scoreCardDescription = ''
                    
                    #scoreCardDescription = scoreCard.question.text + " " + scoreCard.paired_logic_type + " " + pairedScoreCard.question.text
                    
                    for answerObj in scoreCardObj.answerObjList:
                        scoreCardDescription += "\"" + answerObj.answer.text + "\" "
                        
                    scoreCardDescription += "(" + scoreCard.question.text + ") " 
                        
                    scoreCardDescription += PAIRED_LOGIC_DESCRIPTION_MAP[scoreCard.paired_logic_type] + " "
                    
                    for answerObj in pairedScoreCardObj.answerObjList:
                        scoreCardDescription += "\"" + answerObj.answer.text + "\" "
                        
                    scoreCardDescription += "(" + pairedScoreCard.question.text + ") " 
                        
                    scoreCardObj.scoreCardDescription = scoreCardDescription

            questionObj.questionScore = max( [ a.scoreCardScore for a in questionObj.scoreCardObjList ]  )

        sectionObj.sectionScore = max( [ a.questionScore for a in sectionObj.questionObjList ]  )			
  except:
    raise
  return instrumentObj


f = open ( "ISTH-unit-test-6.txt" , "r" )
fout = open ( "ISTH-unit-test-results.txt" , "w" )
writer = csv.writer(fout, delimiter="\t")
for line in f:
  data = line.split("\t")
  upin = data[1]
  instrumentObj = calcScore(upin)
  instrumentScore = sum( [ a.sectionScore for a in instrumentObj.sectionObjList ] )
  data.append (str(instrumentScore))
  print ( " online score = " + str ( data[2]) + " db score = " + str ( data[4]) + " calc score = " + str ( instrumentScore))
  writer.writerows(data)  
  
f.close()
fout.close()