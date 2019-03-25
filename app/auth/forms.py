# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, \
    ValidationError, EqualTo

from app.models import User


class LoginForm(FlaskForm):
    email = StringField('邮箱',
                        validators=[DataRequired(), Length(1, 254), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')


class RegisterForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired(), Length(1, 30)])
    email = StringField('邮箱',
                        validators=[DataRequired(), Length(1, 254), Email()])
    username = StringField('用户名',
                           validators=[DataRequired(), Length(1, 20),
                                       Regexp('^[a-zA-Z0-9]*$',
                                              message='用户名只能包含数字、字母')])
    password = PasswordField('密码',
                             validators=[DataRequired(), Length(8, 128),
                                         EqualTo('password2')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('该邮箱已被注册。')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用。')
