# -*- coding: utf-8 -*-
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, \
    BooleanField
from wtforms.validators import DataRequired, Length, Regexp, Optional, \
    ValidationError, EqualTo

from app.models import User


class EditProfileForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired(), Length(1, 30)])
    username = StringField('用户名',
                           validators=[DataRequired(), Length(1, 20),
                                       Regexp('^[a-zA-Z0-9]*$',
                                              message='用户名只能包含数字、字母')])
    bio = TextAreaField('简介', validators=[Optional(), Length(0, 120)])
    submit = SubmitField('修改')

    def validate_username(self, field):
        if field.data != current_user.username and User.query.filter_by(
                username=field.data).first():
            raise ValidationError('该用户名已被使用。')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('修改')


class PrivacySettingForm(FlaskForm):
    public_collections = BooleanField('公开我的收藏')
    submit = SubmitField('修改')


class DeleteAccountForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField('确认')

    def validate_username(self, field):
        if field.data != current_user.username:
            raise ValidationError('错误的用户名')
