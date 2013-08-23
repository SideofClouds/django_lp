'''
Created on 20.08.2013

@author: dfodorean
'''
from django.test import TestCase
from questionnaires.models import Quiz
from questionnaires.views import _get_outcome_changing_questions

dict_pages = {}
dict_pages[1] = {1: [[1, 10, ''], [2, -5, ''], [3, -3, '']],
                 2: [[4, 3, ''], [5, -3, ''], [6, -3, ''], [0, 9, '']],
                 3: [[7, -5, ''], [8, 10, ''], [9, -5, '']]}
dict_pages[2] = {4: [[10, 10, ''], [12, -5, ''], [13, -3, '']],
                 5: [[14, -5, ''], [15, 10, ''], [16, -3, '']],
                 6: [[17, -5, ''], [18, 10, ''], [19, -5, '']]}

result = {}
max_level = 'Expert'
nr_of_questions = 6
max_nr_answers = 3
levels = {'Noob': 30, 'Medium': 50, 'Advanced': 70, 'Expert': 90}


class QuestionnaireAlgorithmTests(TestCase):
    def test_get_outcome_changing_questions_medium_level(self):
        result[1] = {'1': ['2', '3'],
                     '2': ['4', '5', '6'],
                     '3': ['7', '9']}
        result[2] = {'4': ['12', '13'],
                     '5': ['15', '16'],
                     '6': ['17', '19']}
        level = 'Medium'
        points = 44
        quiz = Quiz(dict_pages, result, level, points, max_level,
                    nr_of_questions, max_nr_answers, levels)
        alternative_result = _get_outcome_changing_questions(quiz)
        self.assertEqual([[1, ['']]], alternative_result[0])
        self.assertEqual('Advanced', alternative_result[1])
        self.assertEqual(54, alternative_result[2])

    def test_get_outcome_changing_questions_lowest_level(self):
        result[1] = {'1': ['1'],
                     '2': ['5', '6', '0'],
                     '3': ['7', '9']}
        result[2] = {'4': ['12', '13'],
                     '5': ['15', '16'],
                     '6': ['17', '19']}
        level = 'Noob'
        points = 20
        quiz = Quiz(dict_pages, result, level, points, max_level,
                    nr_of_questions, max_nr_answers, levels)
        alternative_result = _get_outcome_changing_questions(quiz)
        self.assertEqual([[3, ['']], [4, ['']]], alternative_result[0])
        self.assertEqual('Medium', alternative_result[1])
        self.assertEqual(40, alternative_result[2])

    def test_get_outcome_changing_questions_highest_level(self):
        result[1] = {'1': ['1'],
                     '2': ['4', '0'],
                     '3': ['8']}
        result[2] = {'4': ['10'],
                     '5': ['15'],
                     '6': ['18']}
        level = 'Expert'
        points = 90
        quiz = Quiz(dict_pages, result, level, points, max_level,
                    nr_of_questions, max_nr_answers, levels)
        alternative_result = _get_outcome_changing_questions(quiz)
        self.assertEqual([[3, ['', '']], [6, ['', '']]], alternative_result[0])
        self.assertEqual('Advanced', alternative_result[1])
        self.assertEqual(70, alternative_result[2])

    def test_get_outcome_changing_questions_highest_level2(self):
        result[1] = {'1': ['1'],
                     '2': ['5', '6', '0'],
                     '3': ['7', '9']}
        result[2] = {'4': ['12', '13'],
                     '5': ['15', '16'],
                     '6': ['17', '19']}
        level = 'Expert'
        points = 84
        quiz = Quiz(dict_pages, result, level, points, max_level,
                    nr_of_questions, max_nr_answers, levels)
        alternative_result = _get_outcome_changing_questions(quiz)
        self.assertEqual(None, alternative_result)
