# -*- coding: utf-8 -*-
from flask import url_for

from app import db
from app.models import Category, Post, Comment, User
from .base import BaseTestCase


class PostTestCase(BaseTestCase):
    """TODO: 完成博文相关的单元测试"""

    def setUp(self):
        super(PostTestCase, self).setUp()
        self.login()

        category = Category(name='默认')
        user = User.query.filter_by(email='normal@126.com').first()
        post = Post(title='测试博文标题', body='测试内容', author=user)
        post.categories.append(category)
        comment = Comment(body='测试评论', post=post, author=user)

        db.session.add_all([category, post, comment])
        db.session.commit()

    def test_user_index_page(self):
        response = self.client.get('/user/normal')
        data = response.get_data(as_text=True)
        self.assertIn('普通用户', data)
        self.assertIn('normal', data)
        self.assertIn('测试博文标题', data)
        self.assertIn('测试内容', data)
        self.assertIn('默认', data)

    def test_post_page(self):
        response = self.client.get(url_for('post.show_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('测试博文标题', data)
        self.assertIn('测试评论', data)

    def test_post_page_filter_by_category(self):
        response = self.client.get(
            url_for('post.show_post', post_id=1, category_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('默认', data)
        self.assertIn('测试博文标题', data)
