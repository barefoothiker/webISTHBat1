from django.contrib import admin
from bat.models import *
from django.contrib.auth.models import User

admin.site.register(Site)
admin.site.register(Study)
admin.site.register(ScoreCard)
admin.site.register(UPIN)
admin.site.register(InstrumentAdministrator)
