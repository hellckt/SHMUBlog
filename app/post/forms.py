# -*- coding: utf-8 -*-

from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from app.models import Post


class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 60)])
    categories = StringField('分类（多个分类请用空格隔开）',
                             validators=[Optional(), Length(0, 64)])
    body = CKEditorField('内容', validators=[DataRequired()])
    submit = SubmitField('发表')


class EditPostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 60)])
    categories = StringField('分类（多个分类请用空格隔开）',
                             validators=[Optional(), Length(0, 64)])
    body = CKEditorField('内容', validators=[DataRequired()])
    submit = SubmitField('修改')


class DeletePostForm(FlaskForm):
    id = HiddenField('博文编号')
    title = StringField('确认标题', validators=[DataRequired(), Length(1, 60)])
    submit = SubmitField('删除')

    def validate_title(self, field):
        post = Post.query.get_or_404(self.id.data)
        if self.title.data != post.title:
            raise ValidationError('输入标题错误')


class CommentForm(FlaskForm):
    body = TextAreaField('回复内容', validators=[DataRequired()])
    submit = SubmitField('提交')
