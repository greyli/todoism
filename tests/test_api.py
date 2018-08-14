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
from todoism.models import User, Item


class APITestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('testing')
        self.app_context = app.test_request_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()

        user = User(username='grey')
        user.set_password('123')
        item = Item(body='Test Item', author=user)

        user2 = User(username='li')
        user2.set_password('456')
        item2 = Item(body='Test Item 2', author=user2)

        db.session.add(user)
        db.session.add(user2)
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def get_oauth_token(self):
        response = self.client.post(url_for('api_v1.token'), data=dict(
            grant_type='password',
            username='grey',
            password='123'
        ))
        data = response.get_json()
        return data['access_token']

    def set_auth_headers(self, token):
        return {
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_api_index(self):
        response = self.client.get(url_for('api_v1.index'))
        data = response.get_json()
        self.assertEqual(data['api_version'], '1.0')

    def test_get_token(self):
        response = self.client.post(url_for('api_v1.token'), data=dict(
            grant_type='password',
            username='grey',
            password='123'
        ))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', data)

    def test_get_user(self):
        token = self.get_oauth_token()
        response = self.client.get(url_for('api_v1.user'),
                                   headers=self.set_auth_headers(token))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['username'], 'grey')

    def test_new_item(self):
        token = self.get_oauth_token()
        response = self.client.post(url_for('api_v1.items'),
                                    json=dict(body='Buy milk'),
                                    headers=self.set_auth_headers(token))
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['body'], 'Buy milk')

        response = self.client.post(url_for('api_v1.items'), json=dict(body=' '), headers=self.set_auth_headers(token))
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'The item body was empty or invalid.')

    def test_edit_item(self):
        token = self.get_oauth_token()
        response = self.client.put(url_for('api_v1.item', item_id=1),
                                   json=dict(body='New Item Body'),
                                   headers=self.set_auth_headers(token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Item.query.get(1).body, 'New Item Body')

        response = self.client.put(url_for('api_v1.item', item_id=1), json=dict(body=' '),
                                   headers=self.set_auth_headers(token))
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'The item body was empty or invalid.')

        response = self.client.put(url_for('api_v1.item', item_id=2), json=dict(body='New Item Body'),
                                   headers=self.set_auth_headers(token))
        self.assertEqual(response.status_code, 403)

    def test_delete_item(self):
        token = self.get_oauth_token()

        response = self.client.delete(url_for('api_v1.item', item_id=1),
                                      headers=self.set_auth_headers(token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Item.query.get(1), None)

        response = self.client.delete(url_for('api_v1.item', item_id=2),
                                      headers=self.set_auth_headers(token))
        self.assertEqual(response.status_code, 403)

    def test_toggle_item(self):
        token = self.get_oauth_token()

        response = self.client.patch(url_for('api_v1.item', item_id=1),
                                     headers=self.set_auth_headers(token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Item.query.get(1).done, True)

        response = self.client.patch(url_for('api_v1.item', item_id=1),
                                     headers=self.set_auth_headers(token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Item.query.get(1).done, False)

        response = self.client.patch(url_for('api_v1.item', item_id=2),
                                     headers=self.set_auth_headers(token))
        self.assertEqual(response.status_code, 403)

    def test_clear_items(self):
        token = self.get_oauth_token()
        response = self.client.patch(url_for('api_v1.item', item_id=1),
                                     headers=self.set_auth_headers(token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Item.query.get(1).done, True)

        response = self.client.delete(url_for('api_v1.completed_items'),
                                      headers=self.set_auth_headers(token))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Item.query.get(1), None)

    def test_get_item(self):
        token = self.get_oauth_token()
        response = self.client.get(url_for('api_v1.item', item_id=1),
                                   headers=self.set_auth_headers(token))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', data)
        self.assertIn('self', data)
        self.assertIn('body', data)
        self.assertIn('author', data)
        self.assertEqual(data['id'], 1)

    def test_get_items(self):
        user = User.query.get(1)
        item2 = Item(body='Test Item 2', author=user)
        item3 = Item(body='Test Item 3', author=user)
        item4 = Item(body='Test Item 4', author=user, done=True)
        db.session.commit()

        token = self.get_oauth_token()
        response = self.client.get(url_for('api_v1.items'),
                                   headers=self.set_auth_headers(token))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('self', data)
        self.assertIn('items', data)
        self.assertIn('prev', data)
        self.assertIn('next', data)
        self.assertEqual(data['count'], 4)
        # get active items
        response = self.client.get(url_for('api_v1.active_items'),
                                   headers=self.set_auth_headers(token))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('self', data)
        self.assertIn('items', data)
        self.assertIn('prev', data)
        self.assertIn('next', data)
        self.assertEqual(data['count'], 3)
        # get completed items
        response = self.client.get(url_for('api_v1.completed_items'),
                                   headers=self.set_auth_headers(token))
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('self', data)
        self.assertIn('items', data)
        self.assertIn('prev', data)
        self.assertIn('next', data)
        self.assertEqual(data['count'], 1)

    def test_404_response(self):
        response = self.client.get('/api/foo')
        data = response.get_json()
        self.assertEqual(data['message'], 'The requested URL was not found on the server.')

    def test_405_response(self):
        response = self.client.delete(url_for('api_v1.index'))
        data = response.get_json()
        self.assertEqual(data['message'], 'The method is not allowed for the requested URL.')
