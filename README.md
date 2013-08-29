django_lp
=========

django questionnaires app
==============
Questionnaires
==============

Questionnaires is a simple Django app to conduct Web-based tests.
Each quiz can have multiple pages with questions and multiple choices
that the user can select.

Quick start
-----------
0. Unzip the package.

1. Install the app using the command 'python setup.py install'

2. Add "questionnaires" to your INSTALLED_APPS setting, 
   and enable the admin app like this:

INSTALLED_APPS = (
          ...
	  'django.contrib.admin',
          'questionnaires',
)

3. Add the following line to settings.py to save every request in session.

SESSION_SAVE_EVERY_REQUEST = True

4. In your settings.py file uncomment the last line from TEMPLATE_LOADERS to look like this:

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

5. Include the questionnaries URLconf in your project urls.py like this:

	url(r'^questionnaires/', include('questionnares.urls', namespace='questionnaires')),

6. Make sure you configured your database settings and run 'manage.py syncdb'.

7. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a questionnaire (you'll need the Admin app enabled).

8. Visit http://127.0.0.1:8000/questionnaires/ to participate in the
   questionnaire.
