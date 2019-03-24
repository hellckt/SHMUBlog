# -*- coding: utf-8 -*-
from flask import current_app

from tests.base import BaseTestCase


class BasicTestCase(BaseTestCase):
    def test_app_exist(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_403_error_redirect_to_404_error(self):
        response = self.client.get('/mock_forbidden_error')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn('资源未找到', data)

    def test_404_error(self):
        response = self.client.get('/this_page_must_be_not_found')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn('资源未找到', data)

    def test_500_error(self):
        response = self.client.get('/mock_internal_error')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn('系统内部错误', data)
