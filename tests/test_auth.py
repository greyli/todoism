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
from todoism.models import User


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('testing')
        self.app_context = app.test_request_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()

        user = User(username='grey')
        user.set_password('123')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def test_login(self):
        response = self.client.post(url_for('auth.login'), json=dict(username='grey', password='123'))
        data = response.get_json()
        self.assertEqual(data['message'], 'Login success.')

    def test_logout(self):
        self.client.post(url_for('auth.login'), json=dict(
            username='grey',
            password='123'
        ), follow_redirects=True)
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        data = response.get_json()
        self.assertIn(data['message'], 'Logout success.')

    def test_fail_login(self):
        response = self.client.post(url_for('auth.login'), json=dict(
            username='bad-username',
            password='123'
        ), follow_redirects=True)
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn(data['message'], 'Invalid username or password.')

    def test_view_protect(self):
        response = self.client.get(url_for('todo.app'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login on Todoism', data)

    def get_test_account(self):
        response = self.client.get(url_for('auth.register'), follow_redirects=True)
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('username', data)
        self.assertIn('password', data)
        self.assertIn(data['message'], 'Generate success')
        self.assertIsNotNone(User.query.filter(username=data['username']))
