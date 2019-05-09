# -*- coding: utf-8 -*-
import os
from datetime import datetime

from flask import current_app
from flask_avatars import Identicon
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, whooshee

# 角色-权限关系表
roles_permissions = db.Table('roles_permissions',
                             db.Column('role_id', db.Integer,
                                       db.ForeignKey('role.id')),
                             db.Column('permission_id', db.Integer,
                                       db.ForeignKey('permission.id')))


class Permission(db.Model):
    """权限表"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    roles = db.relationship('Role', secondary=roles_permissions,
                            back_populates='permissions')


class Role(db.Model):
    """角色表"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    users = db.relationship('User', back_populates='role')
    permissions = db.relationship('Permission', secondary=roles_permissions,
                                  back_populates='roles')

    @staticmethod
    def init_role():
        """初始化角色权限

        角色说明:
            Guest           未注册用户（没有任何权限）
            Blocked         被封禁的用户（没有任何权限）
            User            普通用户
            Administrator   管理员


        权限说明:
            FOLLOW          关注权限
            UNFOLLOW        取消关注权限
            COLLECT         收藏权限
            PUBLISH         博文发表权限
            COMMENT         评论权限
            UPLOAD          上传权限
            DELETE_POST     删除博文权限
            DELETE_COMMENT  删除评论权限
            DELETE_ACCOUNT  删除账户权限
            ADMINISTER      管理员权限
        """
        roles_permissions_map = {
            'User': ['FOLLOW', 'UNFOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD',
                     'PUBLISH', 'DELETE_POST', 'DELETE_COMMENT',
                     'DELETE_ACCOUNT'],
            'Administrator': ['FOLLOW', 'UNFOLLOW', 'COLLECT', 'UPLOAD',
                              'COMMENT', 'PUBLISH', 'DELETE_POST',
                              'DELETE_COMMENT', 'DELETE_ACCOUNT', 'ADMINISTER']
        }

        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(
                    name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()


# 关注关系表
class Follow(db.Model):
    """关注表"""
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    follower = db.relationship('User', foreign_keys=[follower_id],
                               back_populates='following', lazy='joined')
    followed = db.relationship('User', foreign_keys=[followed_id],
                               back_populates='followers', lazy='joined')


# 收藏关系表
class Collect(db.Model):
    """收藏表"""
    collector_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                             primary_key=True)
    collected_id = db.Column(db.Integer, db.ForeignKey('post.id'),
                             primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    collector = db.relationship('User', back_populates='collections',
                                lazy='joined')
    collected = db.relationship('Post', back_populates='collectors',
                                lazy='joined')


@whooshee.register_model('username', 'name')
class User(db.Model, UserMixin):
    """用户表"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(30))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.String(120))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    active = db.Column(db.Boolean, default=True)

    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))
    avatar_raw = db.Column(db.String(64))

    # 是否公开收藏
    public_collections = db.Column(db.Boolean, default=True)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    role = db.relationship('Role', back_populates='users')
    posts = db.relationship('Post', back_populates='author',
                            cascade='all')
    comments = db.relationship('Comment', back_populates='author',
                               cascade='all')
    collections = db.relationship('Collect', back_populates='collector',
                                  cascade='all')
    following = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                                back_populates='follower',
                                lazy='dynamic', cascade='all')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                back_populates='followed',
                                lazy='dynamic', cascade='all')
    notifications = db.relationship('Notification', back_populates='receiver',
                                    cascade='all')

    def __init__(self, **kwargs):
        """初始化用户"""
        super(User, self).__init__(**kwargs)
        self.set_role()  # 初始化用户角色
        self.follow(self)  # 让用户关注自己
        self.generate_avatar()  # 生成随机头像

    @property
    def is_admin(self):
        return self.role.name == 'Administrator'

    @property
    def is_active(self):
        return self.active

    @property
    def password(self):
        raise AttributeError('不允许直接读取密码')

    @password.setter
    def password(self, password):
        """加密明文密码"""
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """验证密码

        :param password: str, 用户输入的明文密码
        :return: bool, True or False
        """
        return check_password_hash(self.password_hash, password)

    def can(self, permission_name):
        """验证权限"""
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission and self.role and permission in self.role.permissions

    def set_role(self):
        """设置用户角色"""
        if self.role is None:
            if self.email == current_app.config['SHMUBLOG_ADMIN_EMAIL']:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(name='User').first()
            db.session.commit()

    def block(self):
        """封禁用户"""
        self.active = False
        db.session.commit()

    def unblock(self):
        """解禁用户"""
        self.active = True
        db.session.commit()

    def is_following(self, user):
        """是否关注了 user"""
        if user.id is None:
            return False
        return self.following.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        """是否被 user 关注"""
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    def follow(self, user):
        """关注 user"""
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        """取消关注 user"""
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    def collect(self, post):
        """收藏博文"""
        if not self.is_collecting(post):
            collect = Collect(collector=self, collected=post)
            db.session.add(collect)
            db.session.commit()

    def uncollect(self, post):
        """取消收藏博文"""
        collect = Collect.query.with_parent(self).filter_by(
            collected_id=post.id).first()
        if collect:
            db.session.delete(collect)
            db.session.commit()

    def is_collecting(self, post):
        """是否收藏了 post"""
        return Collect.query.with_parent(self).filter_by(
            collected_id=post.id).first() is not None

    def generate_avatar(self):
        """生成头像"""
        avatar = Identicon()
        filenames = avatar.generate(text=self.username)
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]
        db.session.commit()


categorizing = db.Table('categorizing',
                        db.Column('post_id', db.Integer,
                                  db.ForeignKey('post.id')),
                        db.Column('category_id', db.Integer,
                                  db.ForeignKey('category.id')))


@whooshee.register_model('name')
class Category(db.Model):
    """博文类型表"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    posts = db.relationship('Post', secondary=categorizing,
                            back_populates='categories')


@whooshee.register_model('title', 'body')
class Post(db.Model):
    """博文表"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    flag = db.Column(db.Integer, default=0)
    can_comment = db.Column(db.Boolean, default=True)
    viewed = db.Column(db.Integer, default=0)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    author = db.relationship('User', back_populates='posts')
    categories = db.relationship('Category', secondary=categorizing,
                                 back_populates='posts')
    comments = db.relationship('Comment', back_populates='post',
                               cascade='all, delete-orphan')
    collectors = db.relationship('Collect', back_populates='collected',
                                 cascade='all')


class Comment(db.Model):
    """评论表"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    flag = db.Column(db.Integer, default=0)

    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    post = db.relationship('Post', back_populates='comments')
    author = db.relationship('User', back_populates='comments')
    replies = db.relationship('Comment', back_populates='replied',
                              cascade='all')
    replied = db.relationship('Comment', back_populates='replies',
                              remote_side=[id])


class Notification(db.Model):
    """消息提醒表"""
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    receiver = db.relationship('User', back_populates='notifications')


@db.event.listens_for(User, 'after_delete', named=True)
def delete_avatars(**kwargs):
    """用户被删除后，同时删除生成的头像文件"""
    target = kwargs['target']
    for filename in [target.avatar_s, target.avatar_m, target.avatar_l,
                     target.avatar_raw]:
        # avatar_raw 可能为 None
        if filename is not None:
            path = os.path.join(current_app.config['AVATARS_SAVE_PATH'],
                                filename)
            # 文件名可能不是唯一的
            if os.path.exists(path):
                os.remove(path)
