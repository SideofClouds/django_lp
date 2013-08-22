'''
Created on 20.08.2013

@author: dfodorean
'''
from django.test import TestCase
from factories import AnswerFactory, LevelFactory, QuestionFactory, PageFactory
from factories import QuestionnaireFactory


class QuestionnaireMethodTests(TestCase):
    def test_get_nr_of_questions_with_0_questions(self):
        q = QuestionnaireFactory()
        self.assertEqual(q.get_nr_of_questions(), 0)

    def test_get_nr_of_questions_with_1_question(self):
        questionnaire = QuestionnaireFactory()
        page = PageFactory(questionnaire=questionnaire)
        QuestionFactory(page=page)
        self.assertEqual(questionnaire.get_nr_of_questions(), 1)

    def test_get_nr_of_questions_with_3_questions(self):
        nrq = 3  # number of questions to be created
        questionnaire = QuestionnaireFactory()
        page = PageFactory(questionnaire=questionnaire)
        for _ in range(nrq):
            QuestionFactory(page=page)
        self.assertEqual(questionnaire.get_nr_of_questions(), nrq)

    def test_get_max_level_with_1_level(self):
        q = QuestionnaireFactory()
        lvl = LevelFactory(questionnaire=q, threshold=90)
        self.assertEqual(q.get_max_level(), lvl)

    def test_get_max_level_with_3_levels(self):
        q = QuestionnaireFactory()
        LevelFactory(questionnaire=q, threshold=40)
        lvl2 = LevelFactory(questionnaire=q, threshold=50)
        LevelFactory(questionnaire=q, threshold=30)
        self.assertEqual(q.get_max_level(), lvl2)

    def test_get_max_nr_answers_with_1_question(self):
        q = QuestionnaireFactory()
        page = PageFactory(questionnaire=q)
        question = QuestionFactory(page=page)
        AnswerFactory(question=question)
        self.assertEqual(q.get_max_nr_answers(), 1)

    def test_get_max_nr_answers_with_3_questions(self):
        q = QuestionnaireFactory()
        page = PageFactory(questionnaire=q)
        question1 = QuestionFactory(page=page)
        question2 = QuestionFactory(page=page)
        question3 = QuestionFactory(page=page)
        for _ in range(3):
            AnswerFactory(question=question1)

        for _ in range(4):
            AnswerFactory(question=question2)

        for _ in range(2):
            AnswerFactory(question=question3)

        self.assertEqual(q.get_max_nr_answers(), 4)
