# Create your views here.
from django.views import generic
from django.shortcuts import render, get_object_or_404, render_to_response
from questionnaires.models import Questionnaire, Page
from forms import create_page_form
from django.http.response import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from time import time
from persistence import QuestionnaireDB, PageDB, LevelDB, AnswerDB, QuestionDB
from models import Quiz


class IndexView(generic.ListView):
    template_name = 'questionnaires/index.html'
    context_object_name = 'questionnaire_list'

    def get_queryset(self):
        questionnaires = QuestionnaireDB().get_questionnaires()
        good_questionnaires = []
        for el in questionnaires:
            if el.get_nr_of_questions() > 0:
                good_questionnaires.append(el)
        return good_questionnaires


def detail(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
    nrq = questionnaire.get_nr_of_questions()

    first_page = PageDB(questionnaire).get_pages()[0]
    return render(request, 'questionnaires/detail.html',
                  {'questionnaire': questionnaire,
                   'nr_questions': nrq,
                   'first_page': first_page})


def _get_next_page(questionnaire, page):
    """
    Returns the next page from the questionnaire and the current page number.
    """
    pages = PageDB(questionnaire).get_pages()
    i = 0
    nr_of_pages = PageDB(questionnaire).get_nr_of_pages()
    while i < nr_of_pages - 1 and pages[i].id <= page.id:
        i += 1
    next_page = pages[i]
    return next_page


def display_page(request, questionnaire_id, page_id):

    questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
    page = get_object_or_404(Page, pk=page_id)
    last_page = PageDB(questionnaire).get_latest('id')

    next_page = _get_next_page(questionnaire, page)

    PageForm = create_page_form(page)

    if 'pages' not in request.session:
        request.session['pages'] = {}
        request.session['start_time'] = time()

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            quest_answr = form.cleaned_data

            request.session['pages']["page%s" % page.id] = quest_answr

            if page != last_page:
                return HttpResponseRedirect(
                            reverse(
                                'questionnaires:qpage',
                                args=(questionnaire_id, next_page.id)
                            )
                )
            else:
                return HttpResponseRedirect(
                            reverse(
                            'questionnaires:results_page',
                            args=(questionnaire_id)
                            )
                )
    else:
        form = PageForm()

    return render_to_response('questionnaires/qpage.html',
        {'form': form,
         'questionnaire': questionnaire,
         'page': page,
         'last_page': last_page,
         'next_page': next_page},
        context_instance=RequestContext(request),
    )


def _get_question_changers(quiz, order, dif_pages,
                           compare=lambda x, y: x < y):
    """
    Returns a tuple containing a list of questions, each with a list of
    answers, the new level that would have resulted if the user had selected
    these extra answers, and the associated score.

    Pre-conditions: - dif_pages is a dictionary containing dictionaries
                      with question ids, each with a list containing the answers
                      that the user hasn't selected
                    - order is a string representing the order by which the
                      unselected answers should be sorted (ascending or
                      descending depending if the user reached the highest
                      level or not)
                    quiz is a Quiz object containing the following:
                    - a Questionnaire object
                    - a dictionary containing dictionaries with question ids,
                      each with a list containing the answers
                      that the user selected
                    - a u'string representing the level
                      that the user obtained/reached
                    - an integer representing the score that the user
                      obtained
    """
    max_nr_answers = quiz.questionnaire.get_max_nr_answers()
    i = 1
    while i < max_nr_answers:
        question_changers = []
        aux_points = quiz.points
        for page in dif_pages:
            questions = dif_pages[page]
            maxy = 0
            chosen_question = None
            top_answers = None

            for q in questions:
                answers = questions[q].order_by(order)[:i]
                score_sum = 0

                for answer in answers:
                    score_sum += answer.score

                if compare(maxy, score_sum):
                    maxy = score_sum
                    chosen_question = q
                    top_answers = answers

            if chosen_question and top_answers:
                question_changers.append([chosen_question, top_answers])

            aux_points += maxy

            possible_new_level = _get_level(quiz.questionnaire, aux_points)

            if quiz.level != possible_new_level:
                return question_changers, possible_new_level, aux_points
        i += 1
    return None


def _get_dictionary_without_user_choices(pages):
    """
    Returns a dictionary containing the questionnaire pages with questions, but
    without the choices selected by the user.

    Pre-conditions: - pages is a dictionary containing dictionaries
                      with question ids, each with a list containing the answers
                      that the user selected
    """
    dif_pages = {}
    for page in pages:
        page_obj = PageDB().get_page_by_id(int(page[4:]))
        dif_pages[page] = {}

        for q in QuestionDB(page_obj).get_questions():
            chosen_answers = map(int, pages[page]['question%s' % q.id])
            dif_pages[page][q.id] = AnswerDB(q).get_answers_without(
                                                    chosen_answers)
    return dif_pages


def _get_outcome_changing_questions(quiz):
    """
    Returns a question from each page of the questionneire with extra answers
    such that the outcome(level) would have been different (better/worse) if
    the user would have selected them.

    Pre-conditions: quiz is a Quiz object containing the following:
                    - a Questionnaire object
                    - a dictionary containing dictionaries with question ids,
                      each with a list containing the answers
                      that the user selected
                    - a u'string representing the level
                      that the user obtained/reached
                    - an integer representing the score that the user
                      obtained
                    - a level object representing the level with the highest
                      threshold
    """
    dif_pages = _get_dictionary_without_user_choices(quiz.pages)
    result = None
    if quiz.level != quiz.max_level.name:
        result = _get_question_changers(quiz, '-score', dif_pages)

    if result == None:
        result = _get_question_changers(quiz, 'score', dif_pages,
                                        compare=lambda x, y: x > y)
    if result != None:
        for el in result[0]:
            el[0] = QuestionDB().get_question_by_id(el[0])

    return result


def _get_level(questionnaire, points):
    """
    Returns the level from a given questionnaire based on the number of points.

    Pre-conditions: - questionnaire is a Questionnaire object
                    - points is an integer representing the score obtained by
                      the user
    """
    levels = LevelDB(questionnaire).order_levels_by('threshold')
    level = None
    for el in levels:
        if points <= el.threshold:
            level = el.name
            break

    final_level = levels[len(levels) - 1]
    if points >= final_level.threshold:
        level = final_level.name

    return level


def display_results(request, questionnaire_id):
    if 'pages' not in request.session.keys():
        return HttpResponseRedirect(
                    reverse(
                        'questionnaires:detail',
                        args=(questionnaire_id),
                    )
        )
    questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
    points = 0
    elapsed_time = time() - request.session['start_time']
    elapsed_time = int(elapsed_time)

    for questions in request.session['pages'].values():
        for answers in questions.values():
            for answer in answers:
                points += AnswerDB().get_answer_by_id(int(answer)).score

    level = _get_level(questionnaire, points)
    max_lv = questionnaire.get_max_level()
    quiz = Quiz(questionnaire, request.session['pages'], level, points, max_lv)
    alternative_result = _get_outcome_changing_questions(quiz)

    request.session.flush()
    if alternative_result == None:
        return render(request, 'questionnaires/results.html',
                  {'questionnaire': questionnaire,
                   'points': points,
                   'level': level,
                   'elapsed_time': elapsed_time,
                   'alternative_result': 'None'
                   }
    )

    return render(request, 'questionnaires/results.html',
                  {'questionnaire': questionnaire,
                   'points': points,
                   'level': level,
                   'elapsed_time': elapsed_time,
                   'outcome_changing_questions': alternative_result[0],
                   'new_level': alternative_result[1],
                   'new_score': alternative_result[2],
                   }
    )
