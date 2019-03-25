# -*- coding: utf-8 -*-
from datetime import datetime

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

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
            Locked          被锁定的用户
            User            普通用户
            Administrator   管理员


        权限说明:
            FOLLOW          关注权限
            COLLECT         收藏权限
            PUBLISH         博文发表权限
            COMMENT         评论权限
            UPLOAD          上传权限
            ADMINISTER      管理员权限
        """
        roles_permissions_map = {
            'Locked': ['FOLLOW', 'COLLECT'],
            'User': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD', 'PUBLISH'],
            'Administrator': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD',
                              'PUBLISH', 'ADMINISTER']
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


class User(db.Model, UserMixin):
    """用户表"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(30))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)

    active = db.Column(db.Boolean, default=True)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    role = db.relationship('Role', back_populates='users')

    def __init__(self, **kwargs):
        """初始化用户"""
        super(User, self).__init__(**kwargs)
        self.set_role()

    @property
    def is_admin(self):
        return self.role.name == 'Administrator'

    @property
    def is_active(self):
        return self.active

    def can(self, permission_name):
        """验证权限"""
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission and self.role and permission in self.role.permissions

    def set_password(self, password):
        """加密明文密码"""
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """验证密码

        :param password: str, 用户输入的明文密码
        :return: bool, True or False
        """
        return check_password_hash(self.password_hash, password)

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
