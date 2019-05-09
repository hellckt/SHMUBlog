from flask import url_for

from .base import BaseTestCase


class AdminTestCase(BaseTestCase):
    """TODO: 完成管理员相关的单元测试"""

    def setUp(self):
        super(AdminTestCase, self).setUp()
        self.login(email='hellckt@126.com', password='123')

    def test_index_page(self):
        response = self.client.get(url_for('admin.index'))
        data = response.get_data(as_text=True)
        self.assertIn('SHMUBlog 管理面板', data)

    def test_bad_permission(self):
        self.logout()
        response = self.client.get(url_for('admin.index'),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('请先登录。', data)
        self.assertNotIn('SHMUBlog 管理面板', data)

        self.login()  # 没有管理权限的普通用户
        response = self.client.get(url_for('admin.index'))
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 404)
        self.assertNotIn('SHMUBlog 管理面板', data)
