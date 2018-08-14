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


class ToDoTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('testing')
        self.app_context = app.test_request_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()

        user = User(username='grey')
        user.set_password('123')
        item1 = Item(body='Item 1', author=user)
        item2 = Item(body='Item 2', author=user)
        item3 = Item(body='Item 3', author=user)

        user2 = User(username='li')
        user2.set_password('456')
        item = Item(body='Item', author=user2)

        db.session.add(user)
        db.session.add(user2)
        db.session.commit()
        # Log the test user in
        self.client.post(url_for('auth.login'), json=dict(username='grey', password='123'))

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def test_app_page(self):
        response = self.client.get(url_for('todo.app'))
        data = response.get_data(as_text=True)
        self.assertIn('What needs to be done?', data)
        self.assertIn('Clear', data)

    def test_new_item(self):
        response = self.client.post(url_for('todo.new_item'), json=dict(body='Item 4'))
        data = response.get_json()
        self.assertEqual(data['message'], '+1')
        self.assertIn('Item 4', data['html'])

        response = self.client.post(url_for('todo.new_item'), json=dict(body=' '))
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'Invalid item body.')

    def test_edit_item(self):
        response = self.client.put(url_for('todo.edit_item', item_id=1), json=dict(body='New Item 1'))
        data = response.get_json()
        self.assertEqual(data['message'], 'Item updated.')
        self.assertEqual(Item.query.get(1).body, 'New Item 1')

        response = self.client.put(url_for('todo.edit_item', item_id=1), json=dict(body=' '))
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'Invalid item body.')

        response = self.client.put(url_for('todo.edit_item', item_id=4), json=dict(body='New Item Body'))
        data = response.get_json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['message'], 'Permission denied.')

    def test_delete_item(self):
        response = self.client.delete(url_for('todo.delete_item', item_id=1))
        data = response.get_json()
        self.assertEqual(data['message'], 'Item deleted.')
        self.assertEqual(Item.query.get(1), None)

        response = self.client.delete(url_for('todo.delete_item', item_id=4))
        data = response.get_json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['message'], 'Permission denied.')

    def test_toggle_item(self):
        response = self.client.patch(url_for('todo.toggle_item', item_id=1))
        data = response.get_json()
        self.assertEqual(data['message'], 'Item toggled.')
        self.assertEqual(Item.query.get(1).done, True)

        response = self.client.patch(url_for('todo.toggle_item', item_id=1))
        data = response.get_json()
        self.assertEqual(data['message'], 'Item toggled.')
        self.assertEqual(Item.query.get(1).done, False)

        response = self.client.patch(url_for('todo.toggle_item', item_id=4))
        data = response.get_json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['message'], 'Permission denied.')

    def test_clear_item(self):
        self.client.patch(url_for('todo.toggle_item', item_id=1))
        self.client.patch(url_for('todo.toggle_item', item_id=2))

        response = self.client.delete(url_for('todo.clear_items'))
        data = response.get_json()
        self.assertEqual(data['message'], 'All clear!')
        self.assertEqual(Item.query.get(1), None)
        self.assertEqual(Item.query.get(2), None)
        self.assertNotEqual(Item.query.get(3), None)
