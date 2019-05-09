# -*- coding: utf-8 -*-

import unittest

import flask
from flask import url_for

from app import create_app
from app.extensions import db
from app.models import Role, User


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app('testing')

        @app.route('/mock_forbidden_error')
        def mock_forbidden_error():
            flask.abort(403)

        @app.route('/mock_internal_error')
        def mock_internal_error():
            flask.abort(500)

        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

        db.create_all()
        Role.init_role()

        admin_user = User(email='hellckt@126.com', name='管理员',
                          username='admin')
        admin_user.password = '123'
        normal_user = User(email='normal@126.com', name='普通用户',
                           username='normal')
        normal_user.password = '123'

        blocked_user = User(email='blocked@126.com', name='被封禁的用户',
                            username='blocked')
        blocked_user.password = '123'
        blocked_user.block()

        db.session.add_all([admin_user, normal_user, blocked_user])
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.context.pop()

    def login(self, email=None, password=None):
        if email is None and password is None:
            email = 'normal@126.com'
            password = '123'

        return self.client.post(url_for('auth.login'), data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('auth.logout'), follow_redirects=True)
