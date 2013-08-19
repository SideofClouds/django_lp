'''
Created on 17.07.2013

@author: dfodorean
'''

from django.contrib import admin
from questionnaires.models import Questionnaire, Question, Level, Answer, Page

from django.db import models
from django.forms import TextInput, Textarea


class LevelInLine(admin.TabularInline):
    model = Level
    extra = 3


class PageInLine(admin.TabularInline):
    model = Page
    extra = 1


class QuestionnaireAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,              {'fields': ['name', 'description']}),
    ]
    inlines = [LevelInLine, PageInLine]
    list_display = ('name', 'description')
    search_fields = ['name', 'description']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '70'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }
    list_filter = ['name']
    ordering = ['name', 'description']


class AnswerInLine(admin.StackedInline):
    model = Answer
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Question', {'fields': ['page', 'text']}),
    ]
    inlines = [AnswerInLine]
    search_fields = ['text']
    list_display = ('text', 'page')
    ordering = ['text', 'page']
    list_filter = ['page']

admin.site.register(Questionnaire, QuestionnaireAdmin)
admin.site.register(Question, QuestionAdmin)
