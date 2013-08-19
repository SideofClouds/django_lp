"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from questionnaires.models import Questionnaire, Page, Question, Level, Answer
from django.core.urlresolvers import reverse
from questionnaires.views import _get_level, _get_outcome_changing_questions


def create_questionnaire(name='test', description='test'):
    return Questionnaire.objects.create(name=name, description=description)


def create_page_for_questionnaire(test, page_nr=1):
    return Page.objects.create(questionnaire=test, page_nr=page_nr)


def create_questionnaire_with_1page(name='test', descr='test', nr=1):
    q = create_questionnaire(name, descr)
    page = create_page_for_questionnaire(q, nr)
    return q, page


def create_question_on_page(page, text='default'):
    return Question.objects.create(page=page, text=text)


def create_level(questionnaire, threshold=5, name='default'):
    return Level.objects.create(questionnaire=questionnaire,
                                name=name, threshold=threshold)


def create_answer(question, score=5, label='default'):
    return Answer.objects.create(question=question,
                                 label=label, score=score)


class QuestionnaireViewTests(TestCase):
    def test_index_view_with_no_questionnaires(self):
        response = self.client.get(reverse('questionnaires:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No questionnaires are available.")
        self.assertQuerysetEqual(
            response.context['questionnaire_list'], [])

    def test_index_view_with_no_questions(self):
        create_questionnaire(name='test', description='asdf')
        response = self.client.get(reverse('questionnaires:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['questionnaire_list'], [])

    def test_index_view_with_1_question(self):
        q = create_questionnaire(name='test', description='asdf')
        page = create_page_for_questionnaire(q)
        create_question_on_page(page)
        response = self.client.get(reverse('questionnaires:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['questionnaire_list'],
            ['<Questionnaire: test - asdf>'])

    def test_get_level_with_1_level(self):
        q = create_questionnaire()
        l1 = create_level(q, threshold=10, name='noob')
        self.assertEqual(_get_level(q, 5), l1.name)
        self.assertEqual(_get_level(q, 20), l1.name)

    def test_get_level_with_2_levels(self):
        q = create_questionnaire()
        l1 = create_level(q, threshold=20, name='noob')
        l2 = create_level(q, threshold=40, name='medium')
        self.assertEqual(_get_level(q, 10), l1.name)
        self.assertEqual(_get_level(q, 20), l1.name)
        self.assertEqual(_get_level(q, 21), l2.name)
        self.assertEqual(_get_level(q, 40), l2.name)
        self.assertEqual(_get_level(q, 41), l2.name)

    def test_get_outcome_changing_questions(self):
        q = create_questionnaire()
        create_level(q, threshold=40, name='noob')
        create_level(q, threshold=60, name='medium')
        create_level(q, threshold=80, name='advanced')
        create_level(q, threshold=100, name='expert')
        p1 = create_page_for_questionnaire(q, 1)
        p2 = create_page_for_questionnaire(q, 2)
        q1 = create_question_on_page(p1)
        create_answer(q1, -5)
        create_answer(q1, 5)
        q2 = create_question_on_page(p1)
        create_answer(q2, 5)
        create_question_on_page(p2)


class QuestionnaireMethodTests(TestCase):
    def test_questionnaire_creation(self):
        q = create_questionnaire()
        self.assertTrue(isinstance(q, Questionnaire))
        self.assertEqual(q.__unicode__(), q.name + ' - ' + q.description)

    def test_level_creation(self):
        q = create_questionnaire()
        l = create_level(q)
        self.assertTrue(isinstance(l, Level))
        self.assertEqual(l.__unicode__(), l.name)

    def test_page_creation(self):
        q = create_questionnaire()
        page = create_page_for_questionnaire(q)
        self.assertTrue(isinstance(page, Page))
        self.assertEqual(page.__unicode__(),
                         "%s - page %s" % (q.name, page.page_nr))

    def test_question_creation(self):
        q = create_questionnaire()
        page = create_page_for_questionnaire(q)
        question = create_question_on_page(page)
        self.assertTrue(isinstance(question, Question))
        res = "%s - Page %s - %s" % (page.questionnaire.name,
                                     page.page_nr, question.text)
        self.assertEqual(question.__unicode__(), res)

    def test_answer_creation(self):
        q = create_questionnaire()
        page = create_page_for_questionnaire(q)
        question = create_question_on_page(page)
        answer = create_answer(question)
        self.assertTrue(isinstance(answer, Answer))
        self.assertEqual(answer.__unicode__(), answer.label)

    def test_get_nr_of_questions_with_0_questions(self):
        q = create_questionnaire()
        self.assertEqual(q.get_nr_of_questions(), 0)

    def test_get_nr_of_questions_with_1_question(self):
        questionnaire, page = create_questionnaire_with_1page()
        create_question_on_page(page)
        self.assertEqual(questionnaire.get_nr_of_questions(), 1)

    def test_get_nr_of_questions_with_3_questions(self):
        nrq = 3  # number of questions to be created
        questionnaire, page = create_questionnaire_with_1page()
        for i in range(nrq):
            create_question_on_page(page, text='q%s' % i)
        self.assertEqual(questionnaire.get_nr_of_questions(), nrq)

    def test_get_max_level_with_1_level(self):
        q = create_questionnaire()
        lvl = create_level(q, 90)
        self.assertEqual(q.get_max_level(), lvl)

    def test_get_max_level_with_3_levels(self):
        q = create_questionnaire()
        create_level(q, 40)
        lvl2 = create_level(q, 50)
        create_level(q, 30)
        self.assertEqual(q.get_max_level(), lvl2)

    def test_get_max_nr_answers_with_1_question(self):
        q, page = create_questionnaire_with_1page()
        question = create_question_on_page(page)
        create_answer(question)
        self.assertEqual(q.get_max_nr_answers(), 1)

    def test_get_max_nr_answers_with_3_questions(self):
        q, page = create_questionnaire_with_1page()
        question1 = create_question_on_page(page)
        question2 = create_question_on_page(page)
        question3 = create_question_on_page(page)
        for _ in range(3):
            create_answer(question1)

        for _ in range(4):
            create_answer(question2)

        for _ in range(2):
            create_answer(question3)

        self.assertEqual(q.get_max_nr_answers(), 4)
