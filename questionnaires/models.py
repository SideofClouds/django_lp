from django.db import models


class Quiz(object):
    def __init__(self, dict_pages={}, result={}, level='', points=0,
                 max_level='', nr_of_questions=0, max_nr_answers=0, levels=[]):
        self.dict_pages = dict_pages
        self.result = result  # dict with pages & questions & selected answers
        self.level = level
        self.points = points
        self.max_level = max_level
        self.nr_of_questions = nr_of_questions
        self.max_nr_answers = max_nr_answers
        self.levels = levels


class Questionnaire(models.Model):
    name = models.CharField('Name', max_length=70)
    description = models.TextField('Description', max_length=1000)
    #pub_date = models.DateTimeField('Publication date')

    def __unicode__(self):
        return self.name + ' - ' + self.description

    def to_quiz(self):
        pages = self.page_set.all()
        dict_pages = {}

        for page in pages:
            dict_pages[page.id] = {}
            for question in page.question_set.all():
                dict_pages[page.id][question.id] = []
                for answer in question.answer_set.all():
                    dict_pages[page.id][question.id].append([answer.id,
                                                             answer.score,
                                                             answer.label])
        max_level = self.get_max_level()
        max_level = [max_level.name, max_level.threshold]
        nr_of_questions = self.get_nr_of_questions()
        max_nr_answers = self.get_max_nr_answers()

        levels = {}
        for level in self.level_set.all().order_by('threshold'):
            levels[level.name] = level.threshold

        return Quiz(dict_pages, {}, '', 0, max_level,
                    nr_of_questions, max_nr_answers, levels)

    def get_nr_of_questions(self):
        """
        Returns the number of questions from the questionnaire.
        """
        nrq = 0
        pages = self.page_set.all()
        for page in pages:
            nrq += page.question_set.count()
        return nrq

    def get_max_level(self):
        """
        Returns the level with the highest threshold.
        """
        maxy = -1000
        max_level = None
        for lvl in self.level_set.all():
            if maxy < lvl.threshold:
                maxy = lvl.threshold
                max_level = lvl
        return max_level

    def get_max_nr_answers(self):
        """
        Returns the max number of answers among the questions from
        the questionnaire.
        """
        pages = self.page_set.all()
        maxy = 0
        for page in pages:
            for question in page.question_set.all():
                nr_answers = question.answer_set.count()
                if maxy < nr_answers:
                    maxy = nr_answers
        return maxy


class Level(models.Model):
    questionnaire = models.ForeignKey(Questionnaire)
    name = models.CharField(max_length=50)
    threshold = models.IntegerField()

    def __unicode__(self):
        return self.name


class Page(models.Model):
    questionnaire = models.ForeignKey(Questionnaire)

    page_nr = models.IntegerField()

    def __unicode__(self):
        return "%s - page %s" % (self.questionnaire.name, self.page_nr)

    def to_page_dict(self):
        questions_dict = {}
        questions = self.question_set.all()
        for q in questions:
            questions_dict[q.id] = [q.text, {}]
            for answer in q.answer_set.all():
                questions_dict[q.id][1][answer.id] = answer.label
        return questions_dict


class Question(models.Model):
    page = models.ForeignKey(Page)
    text = models.TextField(max_length=500)

    def __unicode__(self):
        return "%s - Page %s - %s" % (self.page.questionnaire.name,
                                     self.page.page_nr, self.text)


class Answer(models.Model):
    question = models.ForeignKey(Question)
    label = models.CharField(max_length=250)
    score = models.IntegerField(default=0)

    def __unicode__(self):
        return self.label
