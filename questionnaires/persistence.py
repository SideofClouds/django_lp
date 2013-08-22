'''
Created on 13.08.2013

@author: dfodorean
'''
from questionnaires.models import Questionnaire, Answer, Page, Question


class QuestionnaireDB(object):
    def get_questionnaires(self):
        return Questionnaire.objects.all()


class LevelDB(object):
    def __init__(self, questionnaire):
        self.questionnaire = questionnaire

    def get_levels(self):
        return self.questionnaire.level_set.all()

    def order_levels_by(self, column):
        return self.questionnaire.level_set.all().order_by(column)


class PageDB(object):
    def __init__(self, questionnaire=None):
        self.questionnaire = questionnaire

    def get_pages(self):
        return self.questionnaire.page_set.all()

    def get_nr_of_pages(self):
        return self.questionnaire.page_set.count()

    def get_latest(self, column):
        return self.questionnaire.page_set.latest(column)

    def get_page_by_id(self, page_id):
        return Page.objects.get(pk=page_id)


class QuestionDB(object):
    def __init__(self, page=None):
        self.page = page

    def get_questions(self):
        return self.page.question_set.all()

    def get_question_by_id(self, question_id):
        return Question.objects.get(pk=question_id)


class AnswerDB(object):
    def __init__(self, question=None):
        self.question = question

    def get_answers(self):
        return self.question.answer_set.all()

    def get_number_of_answers(self):
        return self.question.answer_set.count()

    def get_answer_by_id(self, answer_id):
        return Answer.objects.get(pk=answer_id)

    def get_answers_without(self, exclude_id_list):
        return self.question.answer_set.exclude(id__in=exclude_id_list)
