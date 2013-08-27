from django.shortcuts import render, get_object_or_404, render_to_response
from questionnaires.models import Questionnaire, Page
from forms import create_page_form
from django.http.response import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from time import time
from persistence import QuestionnaireDB, PageDB, AnswerDB, QuestionDB
from random import randrange


def index(request, user_is_cheating):
    questionnaires = QuestionnaireDB().get_questionnaires()
    good_questionnaires = []
    for el in questionnaires:
        if el.get_nr_of_questions() > 0:
            good_questionnaires.append(el)

    if 'user_is_cheating' in request.session:
        user_is_cheating = request.session['user_is_cheating']
        request.session['user_is_cheating'] = 0
    else:
        user_is_cheating = 0

    return render(request, 'questionnaires/index.html',
                  {'questionnaire_list': good_questionnaires,
                   'user_is_cheating': user_is_cheating})


def detail(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
    nrq = questionnaire.get_nr_of_questions()

    first_page = PageDB(questionnaire).get_pages()[0]
    request.session.flush()
    return render(request, 'questionnaires/detail.html',
                  {'questionnaire': questionnaire,
                   'nr_questions': nrq,
                   'first_page': first_page})


def _get_next_page(questionnaire, page):
    """
    Returns the next page from the questionnaire.
    """
    pages = PageDB(questionnaire).get_pages()
    i = 0
    nr_of_pages = PageDB(questionnaire).get_nr_of_pages()
    while i < nr_of_pages - 1 and pages[i].id <= page.id:
        i += 1
    next_page = pages[i]
    return next_page


def _is_user_cheating(dict_pages, page_ids, page_id):
    if int(page_id) not in page_ids:
        return True

    if dict_pages == {}:
        if int(page_id) != page_ids[0]:
            return True

    else:
        if dict_pages.keys():
            page1_id = int(dict_pages.keys()[0])
            session_page = PageDB().get_page_by_id(page1_id)
            qpage = PageDB().get_page_by_id(page_id)
            if session_page.questionnaire != qpage.questionnaire:
                return True
    return False


def display_page(request, questionnaire_id, page_id):

    questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
    page = get_object_or_404(Page, pk=page_id)

    page_ids = [p.id for p in PageDB(questionnaire).get_pages()]

    if 'pages' not in request.session:
        request.session['pages'] = {}
        request.session['start_time'] = time()

    if _is_user_cheating(request.session['pages'], page_ids, int(page_id)):
        request.session.flush()
        request.session['user_is_cheating'] = randrange(1, 3)
        return HttpResponseRedirect(reverse('questionnaires:index'))

    last_page = PageDB(questionnaire).get_latest('id')

    next_page = _get_next_page(questionnaire, page)

    dict_page = page.to_page_dict()
    PageForm = create_page_form(dict_page)

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            quest_answr = form.cleaned_data

            request.session['pages'][page.id] = quest_answr

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


def _determine_level(levels, points):
    """
    Returns a string representing the level based on the points the user got.

    Pre-conditions: - levels is a dictionary with strings as keys and integers
                      as the values representing the thresholds
                    - points is an integer representing the points acquired
                      by the user
    """
    import operator
    level = None
    sorted_levels = sorted(levels.iteritems(), key=operator.itemgetter(1))
    for el in sorted_levels:
        if points <= el[1]:
            level = el[0]
            break

    max_level = max(levels.iterkeys(), key=lambda threshold: levels[threshold])
    if points >= levels[max_level]:
        level = max_level
    return level


def _get_question_changers(quiz, order=True, diff_pages={},
                           compare=lambda x, y: x < y):
    """
    Returns a tuple containing a list of questions, each with a list of
    answers, the new level that would have resulted if the user had selected
    these extra answers, and the associated score.

    Pre-conditions: - diff_pages is a dictionary containing dictionaries with
                      question ids, each with a list containing the answers
                      that the user hasn't selected
                    - order is a bool value representing the order by which the
                      unselected answers should be sorted
    """
    i = 1
    while i < quiz.max_nr_answers:
        question_changers = []
        aux_points = quiz.points
        for page in diff_pages:
            questions = diff_pages[page]
            maxy = 0
            chosen_question = None
            top_answers = None

            for q in questions:
                answers = sorted(questions[q], key=lambda x: x[1],
                                 reverse=order)[:i]
                score_sum = 0

                for answer in answers:
                    score_sum += answer[1]

                if compare(maxy, score_sum):
                    maxy = score_sum
                    chosen_question = q
                    top_answers = answers

            if chosen_question and top_answers:
                top_ans = [el[2] for el in top_answers]
                question_changers.append([chosen_question, top_ans])

            aux_points += maxy

            possible_new_level = _determine_level(quiz.levels, aux_points)

            if quiz.level != possible_new_level:
                return question_changers, possible_new_level, aux_points
        i += 1
    return None


def _get_dictionary_without_user_choices(user_selection, dict_pages):
    """
    Returns a dictionary containing the questionnaire pages with questions, but
    without the choices selected by the user.

    Pre-conditions: - user_selection is a dictionary containing dictionaries
                      with question ids, each with a list containing
                      the answers that the user selected
                    - dict_pages is a dictionary like the user_selection but
                      the questions contain all the answers from the quiz
    """
    diff_pages = {}
    for page in dict_pages:
        diff_pages[page] = {}
        for questions in dict_pages[page]:
            diff_pages[page][questions] = []
            for answer in dict_pages[page][questions]:
                if answer[0] not in map(int,
                                        user_selection[page][str(questions)]):
                    diff_pages[page][questions].append(answer)
    return diff_pages


def _get_outcome_changing_questions(quiz):
    """
    Returns a question from each page of the questionnaire with extra answers
    such that the outcome(level) would have been different (better/worse) if
    the user would have selected them.

    Pre-conditions: quiz is a Quiz object containing the following:
                    - a dictionary with page ids, containing dictionaries with
                      question ids, each with a list containing
                      all the answer ids from the questionnaire
                    - a dictionary with page ids, containing dictionaries with
                      question ids, each with a list containing lists
                      representing the answers that have id, score, label
                      that the user selected
                    - a u'string representing the level
                      that the user obtained/reached
                    - an integer representing the score that the user
                      obtained
                    - a level object representing the level with the highest
                      threshold
                    - the number of questions from the questionnaire
                    - the max number of answers among the questions from the
                      questionnaire
                    - a dictionary with level names as keys and integers
                      representing thresholds as values
    """
    diff_pages = _get_dictionary_without_user_choices(quiz.result,
                                                     quiz.dict_pages)
    result = None
    if quiz.level != quiz.max_level[0]:
        result = _get_question_changers(quiz, True, diff_pages)

    if result == None:
        result = _get_question_changers(quiz, False, diff_pages,
                                        compare=lambda x, y: x > y)
    return result


def display_results(request, questionnaire_id):
    if 'pages' not in request.session.keys():
        request.session['user_is_cheating'] = randrange(1, 3)
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

    quiz = questionnaire.to_quiz()
    quiz.result = request.session['pages']
    quiz.level = _determine_level(quiz.levels, points)
    quiz.points = points

    alternative_result = _get_outcome_changing_questions(quiz)

    request.session.flush()
    if alternative_result == None:
        return render(request, 'questionnaires/results.html',
                  {'questionnaire': questionnaire,
                   'points': points,
                   'level': quiz.level,
                   'elapsed_time': elapsed_time,
                   'alternative_result': 'None'
                   }
    )
    for el in alternative_result[0]:
        el[0] = QuestionDB().get_question_by_id(el[0])

    return render(request, 'questionnaires/results.html',
                  {'questionnaire': questionnaire,
                   'points': points,
                   'level': quiz.level,
                   'elapsed_time': elapsed_time,
                   'outcome_changing_questions': alternative_result[0],
                   'new_level': alternative_result[1],
                   'new_score': alternative_result[2],
                   }
    )
