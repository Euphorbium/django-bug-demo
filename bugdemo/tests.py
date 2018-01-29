from django.test import TestCase
from django.contrib.staticfiles.testing import LiveServerTestCase
from django.urls import reverse
from django.conf import settings

from .models import Choice, Question

import requests
import subprocess
import multiprocessing


class TestDatabaseLocking(LiveServerTestCase):
    fixtures = ['bugdemo/bugdemofixtures.json', ]

    def setUp(self):
        new_question = Question(question_text='demo question ?')
        new_question.save()

    def tearDown(self):
        subprocess.call(['rm', 'index.html'])

    def _get_webpage():
        requests.get(self.live_server_url + reverse('bugdemo', args=['New sample question']))

    def _curl_webpage(self):
        subprocess.call(['curl', self.live_server_url + reverse('bugdemo', args=['Next sample question'])])

    def testStuff(self):
        self.assertEqual(Question.objects.count(), 2)
        self.assertEqual(Choice.objects.count(), 2)

        new_question = Question(question_text='demo question ?')
        new_question.save()
        self.assertEqual(Question.objects.count(), 3)

        resp = requests.get(self.live_server_url + reverse('bugdemo', args=['New sample question']))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Question.objects.count(), 4)

        subprocess.call(['curl', self.live_server_url + reverse('bugdemo', args=['Next sample question'])])
        self.assertEqual(Question.objects.count(), 5)

        subprocess.call(['wget', self.live_server_url + reverse('bugdemo', args=['Yet another sample question'])])
        self.assertEqual(Question.objects.count(), 6)

        for i in range(20):
            subprocess.call(['curl', self.live_server_url + reverse('bugdemo', args=['Next sample question' + str(i)])])
            self.assertEqual(Question.objects.count(), 7 + i)

        print('num objects {}'.format(Question.objects.count()))
        url = self.live_server_url + reverse('bugdemo', args=['Yet another sample question'])
        subprocess.call(['python', '-c', 'from urllib import request; request.urlopen("{}")'.format(url)])
        self.assertEqual(Question.objects.count(), 27)

        print('num objects {}'.format(Question.objects.count()))

        # multiprocessing.Process(target=self._get_webpage)
        p=multiprocessing.Process(target=self._curl_webpage)

        subprocess.call(['curl', self.live_server_url + reverse('bugdemo', args=['Next sample question'])])
        p.start(); 
        r=multiprocessing.Process(target=self._curl_webpage)

        r.start()

        p.join()


        import time

        time.sleep(1)
        r.join()
        self.assertEqual(Question.objects.count(), 30)
