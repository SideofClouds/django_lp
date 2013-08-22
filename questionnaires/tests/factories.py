'''
Created on 20.08.2013

@author: dfodorean
'''
import factory
from questionnaires import models
import random


class QuestionnaireFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Questionnaire

    name = 'Quiz'
    description = 'interesting description'


class LevelFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Level
    questionnaire = factory.SubFactory(QuestionnaireFactory)

    name = factory.Sequence(lambda n: 'Level{0}'.format(n))
    threshold = factory.Sequence(lambda n: '{0}'.format(n + 10))


class PageFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Page
    questionnaire = factory.SubFactory(QuestionnaireFactory)

    page_nr = factory.Sequence(lambda n: '{0}'.format(n))


class QuestionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Question
    page = factory.SubFactory(PageFactory)

    text = factory.Sequence(lambda n: 'Question{0}'.format(n))


class AnswerFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Answer
    question = factory.SubFactory(QuestionFactory)

    label = factory.Sequence(lambda n: 'Answer{0}'.format(n))
    score = random.randrange(-5, 6)
