'''
Created on 30.07.2013

@author: dfodorean
'''
from django import forms
from persistence import QuestionDB, AnswerDB


def create_page_form(page):
    form_attrs = {}

    for question in QuestionDB(page).get_questions():
        answers_models = AnswerDB(question).get_answers()
        answers_choices = []

        for el in answers_models:
            answers_choices.append((el.id, el.label))
        answers_choices = tuple(answers_choices)

        form_attrs['question%s' % question.id] = forms.MultipleChoiceField(
            label=question.text,
            choices=answers_choices,
            widget=forms.CheckboxSelectMultiple(),
            error_messages={'required': 'This question needs to be answered!'}
        )
    return type('PageForm', (forms.Form,), form_attrs)
