from flask import url_for

from app.models import User
from .base import BaseTestCase


class UserTestCase(BaseTestCase):
    def test_index_page(self):
        response = self.client.get(url_for('user.index', username='normal'))
        data = response.get_data(as_text=True)
        self.assertIn('普通用户', data)

    def test_follow(self):
        # 测试未登陆关注
        response = self.client.post(url_for('user.follow', username='admin'),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('请先登录。', data)

        # 测试关注
        self.login()
        response = self.client.post(url_for('user.follow', username='admin'),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('关注成功。', data)

        # 测试重复关注
        response = self.client.post(url_for('user.follow', username='admin'),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('你已经关注过admin了。', data)

    def test_unfollow(self):
        response = self.client.post(url_for('user.follow', username='admin'),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('请先登录。', data)

        self.login()
        response = self.client.post(url_for('user.unfollow', username='admin'),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('你并没有关注admin。', data)

        self.client.post(url_for('user.follow', username='admin'),
                         follow_redirects=True)

        response = self.client.post(url_for('user.unfollow', username='admin'),
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('取消了对admin关注。', data)

    def test_show_followers(self):
        response = self.client.get(
            url_for('user.show_followers', username='normal'))
        data = response.get_data(as_text=True)
        self.assertIn('普通用户 的关注者', data)
        self.assertIn('没有人关注他。', data)

        user = User.query.get(1)
        user.follow(User.query.get(2))

        response = self.client.get(
            url_for('user.show_followers', username='normal'))
        data = response.get_data(as_text=True)
        self.assertIn('管理员', data)
        self.assertNotIn('没有人关注他。', data)

    def test_show_following(self):
        response = self.client.get(
            url_for('user.show_following', username='normal'))
        data = response.get_data(as_text=True)
        self.assertIn('普通用户 关注的人', data)
        self.assertIn('这个B一个人都没关注。', data)

        user = User.query.get(2)
        user.follow(User.query.get(1))

        response = self.client.get(
            url_for('user.show_following', username='normal'))
        data = response.get_data(as_text=True)
        self.assertIn('管理员', data)
        self.assertNotIn('这个B一个人都没关注。', data)

    def test_edit_profile(self):
        self.login()
        response = self.client.post(url_for('user.edit_profile'), data=dict(
            username='newname',
            name='新名字',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('资料更新成功。', data)
        user = User.query.get(2)
        self.assertEqual(user.name, '新名字')
        self.assertEqual(user.username, 'newname')

    def test_change_password(self):
        user = User.query.get(2)
        self.assertTrue(user.validate_password('123'))

        self.login()
        response = self.client.post(url_for('user.change_password'), data=dict(
            old_password='error-password',
            password='new-password',
            password2='new-password',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('旧密码错误，请重新输入。', data)

        self.login()
        response = self.client.post(url_for('user.change_password'), data=dict(
            old_password='123',
            password='new-password',
            password2='new-password',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('密码已修改，请重新登陆。', data)
        self.assertTrue(user.validate_password('new-password'))
        self.assertFalse(user.validate_password('old-password'))

    def test_privacy_setting(self):
        self.login()
        response = self.client.post(url_for('user.privacy_setting'), data=dict(
            public_collections='',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('设置成功。', data)

        user = User.query.get(2)

        self.assertEqual(user.public_collections, False)

    def test_delete_account(self):
        self.login()
        response = self.client.post(url_for('user.delete_account'), data=dict(
            username='normal',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('好的，你自由了。', data)
        self.assertEqual(User.query.get(2), None)
