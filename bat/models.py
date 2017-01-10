from django.db import models
import datetime


GENDER_CHOICES = (('M', 'Male'),('F', 'Female'))
ANSWER_TYPE_CHOICES = (('checkbox','Checkbox'),('radio', 'Radio Button'),('enum','Enumeration'))
LOGIC_TYPE_CHOICES = (('simple','Simple'),('percent','%'),('difference','Difference'),('union','Union'))

# Copied ISTH BAT model file for separate reports project on 2/9/15

#=========================================================================================
# Question and Answer
#=========================================================================================

class Instrument(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    def __str__(self):
        return self.title
    class Admin:
        pass  

class InstrumentSection(models.Model):
    name = models.CharField(max_length = 255)
    instrument = models.ForeignKey(Instrument, related_name = 'sections')
    sequence = models.IntegerField(max_length=10)
    def __str__(self):
        return self.name
    class Admin:
        list_display=('id','sequence','name','instrument')
        pass     

class QuestionAnswer(models.Model):
    text = models.CharField(max_length=255, )
    sequence = models.IntegerField()
    num_value = models.IntegerField(max_length=10, )
    max_value = models.IntegerField(max_length=10,null=True,blank=True)
    score = models.IntegerField()
    isfitb = models.BooleanField()

    class Admin:
        list_display=('id','text','num_value','score','sequence','isfitb')
        list_filter=['isfitb', 'num_value']
        search_fields=['text']
        pass
    class Meta:
        ordering = ['sequence']          
    def __str__(self):
        return str(self.id)+" "+str(self.text)


class Question(models.Model):
    text = models.TextField(max_length=1000)
    format = models.CharField(max_length=8, choices = ANSWER_TYPE_CHOICES)
    parent = models.ForeignKey('self', null=True,blank=True, related_name = "children")
    conditional_on_parent = models.BooleanField()
    conditional_on_parent_value = models.IntegerField(null=True, blank=True)
    instrumentsection = models.ForeignKey(InstrumentSection, related_name = 'questions')
    sequence = models.IntegerField()
    explicit_context = models.ForeignKey('self', null=True, blank=True, related_name = 'explicit_properites')
    answers = models.ManyToManyField(QuestionAnswer, related_name = "questions")
    instructions = models.TextField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return str(self.id)+" "+self.text
    class Admin:
        list_display=('id','sequence','text','format','parent','conditional_on_parent','conditional_on_parent_value','instrumentsection')
        list_filter=['instrumentsection', 'conditional_on_parent']
        search_fields=['text']
        pass     
    #class Meta:
    #	ordering = ('sequence')

class QuestionCondition(models.Model):
    conditional_question = models.ForeignKey(Question,related_name="additional_conditions")
    condition_question  = models.ForeignKey(Question,related_name="dependent_conditions")
    condition_answer = models.ForeignKey(QuestionAnswer)

    class Admin:
        list_display=('id','conditional_question','condition_question','condition_answer')
        pass      

class SpecialQuestion(models.Model):
    sex_question = models.IntegerField() #296
    ethnicity_question = models.IntegerField() #207
    race_question = models.IntegerField() #297
    relationship_question = models.IntegerField()# 13
    relationship_diagnosis_question = models.IntegerField()# 14
    relationship_symptom_question = models.IntegerField()# 15
    menses_lengthofday_question =  models.IntegerField()# 116
    menses_numberofpads_question = models.IntegerField()# 298
    menses_typeofproduct_question = models.IntegerField() #299
    menses_detail_question = models.IntegerField()#300      

#=========================================================================================
# Study Management
#=========================================================================================

class Role(models.Model):
    id = models.IntegerField(primary_key = True, max_length=4)
    role_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank = True)
    def __str__(self):
        return self.role_name
    class Admin:
        list_display=('id','role_name','description')
        pass

class Site(models.Model):
    id = models.IntegerField(primary_key = True, max_length=3)
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    class Admin:
        list_display=('id','name')
        pass      

class Study(models.Model):
    id = models.IntegerField(primary_key = True, max_length=3)
    name = models.CharField(max_length=255)
    instruments = models.ManyToManyField(Instrument, related_name='studies')
    def __str__(self):
        return self.name
    class Admin:
        list_display=('id','name')
        filter_vertical=['instruments']
        pass      

class InstrumentAdministrator(models.Model):
    id = models.IntegerField(primary_key = True, max_length = 5)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=8)
    allowed_sites = models.ManyToManyField(Site, related_name = "allowed_administrators")
    allowed_studies = models.ManyToManyField(Study, related_name = "allowed_administrators")
    waiver_signed = models.DateTimeField(null=True)
    role = models.ForeignKey(Role, null=True, blank=True)

    def __str__(self):
        return self.name
    class Admin:
        list_display=('id','name','role','waiver_signed')
        filter_vertical=['allowed_sites', 'allowed_studies']
        pass

    def sign_waiver(self):
        self.waiver_signed = datetime.datetime.now()
        self.save()

    def waiver_expired(self):
        #Checks if it has been a year (365 days) since the waiver was signed
        #Returns True if it has.
        td = datetime.timedelta(days=365)
        if self.waiver_signed is not None:
            td2 = datetime.datetime.today() - self.waiver_signed
            if td < td2:
                return True
            else:
                return False
        else:
            return True        

class SessionAgent(models.Model):
    session_key = models.CharField(max_length = 40)
    admin = models.IntegerField(max_length = 5, null=True, blank=True)
    site = models.IntegerField(max_length = 3, null=True, blank=True)
    upin = models.IntegerField(null=True, blank=True)
    administration = models.IntegerField(null=True, blank=True)
    logged_in = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    logged_out = models.DateTimeField(null=True, blank=True)

    def update(self, dt):
        self.last_updated = dt
        self.save()

    def login(self, dt):
        self.logged_in = dt
        self.logged_out = None
        self.save()

    def logout(self, dt):
        self.upin = None
        self.administration = None
        self.logged_out = dt
        self.save()

    def set_administration(self,administration):
        self.administration = administration.id
        self.save()

    def clear(self):
        self.admin = None
        self.site = None
        self.upin = None
        self.administration = None
        self.logged_in = None
        self.last_updated = None
        self.logged_out = None
        self.save()

class SessionLog(models.Model):
    timestamp = models.DateField()
    event = models.CharField(max_length=255)
    administrator = models.ForeignKey(InstrumentAdministrator, null=True, blank=True)
    def __str__(self):
        return self.event
    class Admin:
        list_display=('id','timestamp','event','administrator')
        pass

#=========================================================================================
# Responder
# - these tables contain data that is collected from the administration
# - TODO: rename Administration to Responder, need a systematic search and replace in all model, view and template files. .
# - Added site and study foreign keys: ALTER TABLE `pratwebapp`.`prat_administration` ADD site_id INT(11) NOT NULL,
#  ADD study_id INT(11) NOT NULL;
# - Added instrument administrator foreign key: ALTER TABLE `pratwebapp`.`prat_administration` ADD instrumentadministrator_id INT(11) NOT NULL;
# - dropped dob column
#	ALTER TABLE prat_administration DROP COLUMN dob;
#=========================================================================================
class Diagnosis(models.Model):
    name = models.CharField(max_length = 80)
    def __str__(self):
        return self.name
    class Admin:
        list_display=('id','name')
        pass     

class UPIN(models.Model):
    #The id is 6 digits by convention
    id = models.IntegerField(primary_key = True)
    created = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(InstrumentAdministrator, null=True,blank=True)
    study = models.ForeignKey(Study)
    #diagnosis = models.ForeignKey(Diagnosis, null=True,blank=True)
    def __str__(self):
        return str(self.id)
    #class Admin:
        #list_display=('id','created','created_by','study','diagnosis')
        #list_filter=['created_by','study','diagnosis']
        #pass
        
class Administration(models.Model):
    upin = models.ForeignKey(UPIN, related_name='administrations')
    instrument = models.ForeignKey(Instrument, blank=True, null=True)
    site = models.ForeignKey(Site)
    instrumentadministrator = models.ForeignKey(InstrumentAdministrator)
    start = models.DateTimeField(null=True, blank=True)
    stop = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    class Admin:
        list_display=('upin','start','site','instrumentadministrator')
        list_filter=['site','instrumentadministrator']
        pass
        
class QuestionAnswerInstance(models.Model):
    administration = models.ForeignKey(Administration)
    instrument = models.ForeignKey(Instrument)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(QuestionAnswer,related_name = "instances")
    context = models.ForeignKey('self',related_name = "context_instances", null=True, blank=True)
    time_stamp = models.DateTimeField(null=True,blank=True)
    def __str__(self):
        return str(self.id)
    class Admin:
        list_display=('id','administration','question','answer','context','time_stamp')
        list_filter=['administration']
        pass  
        
class FillInTheBlank(models.Model):
    text = models.CharField(max_length = 255)
    fills = models.ForeignKey(QuestionAnswerInstance, related_name = "blank")
    def __str__(self):
        return self.text
    class Admin:
        list_display=('text','fills')
        pass   

#=========================================================================================
# Metadata and Media
#=========================================================================================

class QuestionXref(models.Model):
    source = models.CharField(max_length=255, )
    ui = models.CharField(max_length = 20, )
    source_version = models.CharField(max_length=20, )
    url = models.URLField()
    question = models.ForeignKey(Question, related_name = 'links')
    def __str__(self):
        return self.url
    class Admin:
        list_display=('source','ui','url')
        pass    

class QuestionAnswerXref(models.Model):
    label = models.CharField(max_length=120, blank=True, null=True)
    source = models.CharField(max_length=20)
    ui = models.CharField(max_length = 20, )
    source_version = models.CharField(max_length=20, blank=True, null=True)
    url = models.URLField( )
    questionanswer = models.ForeignKey(QuestionAnswer, related_name = 'links', null=True, blank=True)
    def __str__(self):
        return self.url
    class Admin:
        list_display=('label','source','ui','url','questionanswer')
        pass       

class QuestionMedia(models.Model):
    question = models.ForeignKey(Question, related_name = 'image')
    label = models.CharField(max_length = 120, )
    reference_image = models.ImageField(null=True, upload_to="question/")
    def __str__(self):
        return self.label
    class Admin:
        list_display=('question','label')
        pass 

#=========================================================================================
# Ontology
#=========================================================================================


#class OntologyClass(models.Model):
#	name = models.CharField(max_length = 255)
#	isa = models.ForeignKey('self', null=True,blank=True,related_name = 'children')
#	concrete = models.BooleanField()
#	documentation = models.TextField(null=True,blank=True)
#	def __str__(self):
#		return self.name
#	class Admin:
#		list_display=('id','name','isa','concrete')
#		pass
#
#class OntologyInstance(models.Model):
#	instanceof = models.ForeignKey(OntologyClass, related_name = 'instances')
#	name = models.CharField(max_length = 255)
#	documentation = models.TextField(blank=True)
#	def __str__(self):
#		return self.name
#	class Admin:
#		list_display=('instanceof','name')
#		pass
#
#class OntologySymbol(models.Model):
#	name = models.CharField(max_length = 255)
#	def __str__(self):
#		return self.name
#	class Admin:
#		#list_display=('name','multiple','slottype','cardinality')
#		pass
#
#class OntologySlot(models.Model):
#	name = models.CharField(max_length=255)
#	multiple = models.BooleanField()
#	slottype = models.CharField(max_length=8, choices = SLOT_TYPE_CHOICES)
#	cardinality = models.IntegerField()
#	domain_class = models.ForeignKey(OntologyClass, null=True,related_name = 'class_level_slots')
#	range_classes = models.ManyToManyField(OntologyClass, null=True,blank=True, related_name = 'referenced_by_classes', filter_interface=models.HORIZONTAL)
#	allowed_values = models.ManyToManyField(OntologySymbol, null=True,blank=True, related_name = 'slots',filter_interface=models.HORIZONTAL)
#	def __str__(self):
#		return self.name +"_"+ str(self.domain_class)
#	class Admin:
#		list_display=('name','multiple','slottype','cardinality','domain_class')
#		pass
#
#class OntologyInstanceSlotValue(models.Model):
#	instance = models.ForeignKey(OntologyInstance, related_name = 'slotvalues')
#	slot = models.ForeignKey(OntologySlot)
#	value = models.CharField(max_length = 255)
#	def __str__(self):
#		return self.value
#	class Admin:
#		list_display=('instance','slot','value')
#		pass
#
##=========================================================================================
## Linkers.
## These tables de-couple the Instrument from the ontology, and ontology from context links
## so that either one can be flushed without breaking constraints of the other
##=========================================================================================
#
#class OntologySymbol_Link(models.Model):
#	symbol = models.ForeignKey(OntologySymbol, related_name = 'links', edit_inline=models.TABULAR)
#	name = models.CharField(max_length=60, )
#	link_url = models.CharField(max_length=255, )
#	def __str__(self):
#		return self.link_url
#
#class OntologyInstance_Link(models.Model):
#	concept = models.ForeignKey(OntologyInstance, related_name = 'links', edit_inline=models.TABULAR)
#	name = models.CharField(max_length=60,)
#	link_url = models.CharField(max_length=255, )
#	def __str__(self):
#		return self.link_url
#
#class InstrumentSection_OntologyClass(models.Model):
#	Instrumentsection = models.ForeignKey(InstrumentSection, related_name = 'ontology_link', edit_inline=models.TABULAR, num_in_admin=1)
#	ontologyclass = models.ForeignKey(OntologyClass, related_name = 'Instrument_links', )
#	class Admin:
#		pass
#
#class Question_OntologySlot(models.Model):
#	question = models.ForeignKey(Question, related_name = 'ontology_link', edit_inline=models.TABULAR,num_in_admin=1)
#	ontologyslot = models.ForeignKey(OntologySlot, related_name = 'question_links', )
#	class Admin:
#		list_display=('id','question','ontologyslot')
#		pass
#
#class QuestionAnswer_Ontology(models.Model):
#	answer = models.ForeignKey(QuestionAnswer, related_name = 'ontology_link', edit_inline=models.TABULAR, num_in_admin=1)
#	ontologysymbol = models.ForeignKey(OntologySymbol, blank=True, null=True, related_name = 'answer_links', )
#	ontologyinstance = models.ForeignKey(OntologyInstance, blank=True, null=True, related_name = 'answer_links', )
#	class Admin:
#		list_display=('answer','ontologyinstance')
#		pass
#
#

#=========================================================================================
# Scoring - stores a definition of a scoring system
#=========================================================================================

class ScoreCard(models.Model):
    score_name = models.CharField(max_length=255, ) #identifies the scoring system by name
    score = models.IntegerField()
    section = models.ForeignKey(InstrumentSection, blank=True, null=True,related_name = 'score_cards', )
    question = models.ForeignKey(Question, related_name = 'score_cards')
    answer = models.ManyToManyField(QuestionAnswer, related_name = 'score_cards' )
    instrument = models.ForeignKey(Instrument,related_name = 'score_cards')
    #logic can have 3 values
    #
    #simple (tests for existence or for > 1 if enum)
    #paired_percent (tests primary question/answer divided by additional question/answer, only 1 answer allowed)
    #paired_substract (tests primary question/answer minus additional question/answer, only 1 answer allowed)
    paired_card = models.ForeignKey('self',blank=True,null=True)
    paired_logic_type = models.CharField(max_length=20,choices = LOGIC_TYPE_CHOICES)
    logic_value = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return str(self.section)+":"+str(self.score)
    class Admin:
        list_display=('score_name','score','section','question','instrument')
        list_filter=['instrument','score_name','section']
        filter_horizontal=['answer']
        pass
        
class SectionScore(models.Model):
    administration = models.ForeignKey(Administration, related_name = 'scores')
    section = models.ForeignKey(InstrumentSection, related_name = 'score')
    score = models.IntegerField()