# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import unittest

from flask import url_for

from todoism import create_app, db


class HomeTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('testing')
        self.app_context = app.test_request_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def test_index(self):
        response = self.client.get(url_for('home.index'))
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Todoism', data)

    def test_intro(self):
        response = self.client.get(url_for('home.intro'))
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('We are todoist, we use todoism.', data)

    def test_change_language(self):
        response = self.client.get(url_for('home.intro'))
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('We are todoist, we use todoism.', data)
        self.assertIn('Login', data)

        response = self.client.get(url_for('home.set_locale', locale='JP'))
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'Invalid locale.')

        response = self.client.get(url_for('home.set_locale', locale='zh_Hans_CN'))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Setting updated.')

        response = self.client.get(url_for('home.intro'))
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(u'我们是Todo爱好者，我们使用Todoism。', data)
        self.assertIn(u'登录', data)
