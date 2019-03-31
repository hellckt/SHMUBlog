# -*- coding: utf-8 -*-
from flask import url_for

from tests.base import BaseTestCase


class AuthTestCase(BaseTestCase):

    def test_login_normal_user(self):
        response = self.login()
        data = response.get_data(as_text=True)
        self.assertIn('登陆成功。', data)

    def test_login_blocked_user(self):
        response = self.login(email='blocked@126.com', password='123')
        data = response.get_data(as_text=True)
        self.assertIn('你的账号已经被封禁', data)

    def test_fail_login(self):
        response = self.login(email='wrong-username@126.com',
                              password='wrong-password')
        data = response.get_data(as_text=True)
        self.assertIn('错误的密码或邮箱。', data)

    def test_logout_user(self):
        self.login()
        response = self.logout()
        data = response.get_data(as_text=True)
        self.assertIn('注销成功。', data)

    def test_login_required(self):
        response = self.client.get(url_for('auth.logout'),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('请先登录。', data)

    def test_register_account(self):
        response = self.client.post(url_for('auth.register'), data=dict(
            name='test',
            email='test@126.com',
            username='test',
            password='12345678',
            password2='12345678'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('注册成功，请登陆。', data)
