# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from todoism import create_app, db
from todoism.models import User, Item

app = create_app('testing')

with app.app_context():
    db.create_all()

    user = User(username='grey')
    user.set_password('123')
    db.session.add(user)

    item1 = Item(body='test item 1')
    item2 = Item(body='test item 2')
    item3 = Item(body='test item 3')
    item4 = Item(body='test item 4', done=True)
    user.items = [item1, item2, item3, item4]

    db.session.commit()
