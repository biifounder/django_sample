from django.contrib import admin
from .models import *

admin.site.register(User)

admin.site.register(Year)
admin.site.register(Subject)
admin.site.register(Unit)
admin.site.register(Lesson)
admin.site.register(Outcome)
admin.site.register(Question)

admin.site.register(YearEval)
admin.site.register(SubjectEval)
admin.site.register(UnitEval)
admin.site.register(LessonEval)
admin.site.register(OutcomeEval)
admin.site.register(QEval)
admin.site.register(QDubl)