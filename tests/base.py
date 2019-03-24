# -*- coding: utf-8 -*-

import unittest

import flask

from app import create_app


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

    def tearDown(self):
        self.context.pop()
