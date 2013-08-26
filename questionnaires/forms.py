'''
Created on 30.07.2013

@author: dfodorean
'''
from django import forms


def create_page_form(page):
    """
    Returns a PageForm class.

    Pre-conditions: 'page' is a dictionary having question ids as keys, the
                        values being lists with two elements:
                        - the question text
                        - a dictionary with answer ids and answer labels
    """
    form_attrs = {}

    for question in page:
        answers = page[question][1]
        answers_choices = []

        for el in answers:
            answers_choices.append((el, answers[el]))
        answers_choices = tuple(answers_choices)

        form_attrs[str(question)] = forms.MultipleChoiceField(
            label=page[question][0],
            choices=answers_choices,
            widget=forms.CheckboxSelectMultiple(),
            error_messages={'required': 'This question needs to be answered!'}
        )
    return type('PageForm', (forms.Form,), form_attrs)
