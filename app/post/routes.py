# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, request, \
    current_app, abort
from flask_login import login_required, current_user

from app.decorators import permission_required
from app.extensions import db
from app.models import Post, Category, Comment, User
from app.post import bp
from app.post.forms import PostForm, CommentForm, EditPostForm, DeletePostForm
from app.utils import redirect_back


@bp.route('/new', methods=['GET', 'POST'])
@login_required
@permission_required('PUBLISH')
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        post = Post(title=title, body=body, author=current_user)
        for category_name in form.categories.data.split():
            category = Category.query.filter_by(name=category_name).first()
            if category is None:
                category = Category(name=category_name)
                db.session.add(category)
                db.session.commit()

            if category not in post.categories:
                post.categories.append(category)
        db.session.add(post)
        db.session.commit()
        flash('博文发布成功。', 'success')
        return redirect(url_for('post.show_post', post_id=post.id))
    return render_template('post/new_post.html', form=form)


@bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('PUBLISH')
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = EditPostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        post.title = title
        post.body = body
        for category_name in form.categories.data.split():
            category = Category.query.filter_by(name=category_name).first()
            if category is None:
                category = Category(name=category_name)
                db.session.add(category)
                db.session.commit()

            if category not in post.categories:
                post.categories.append(category)
        db.session.commit()
        flash('博文发布成功。', 'success')
        return redirect(url_for('post.show_post', post_id=post.id))

    form.title.data = post.title
    form.categories.data = ' '.join(
        [category.name for category in post.categories])
    form.body.data = post.body
    return render_template('post/edit_post.html', form=form)


@bp.route('/<int:post_id>/delete', methods=['GET', 'POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = DeletePostForm()
    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        flash('博文已删除。', 'success')
        return redirect(url_for('user.manage_posts'))
    form.id.data = post.id
    return render_template('post/delete_post.html', form=form)


@bp.route('/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(post.author_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SHMUBLOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post) \
        .order_by(Comment.timestamp.asc()) \
        .paginate(page, per_page)
    comments = pagination.items

    comment_form = CommentForm()

    return render_template('post/post.html', post=post, pagination=pagination,
                           comment_form=comment_form, comments=comments,
                           user=user)


@bp.route('/<int:post_id>/comment/new', methods=['POST'])
@login_required
@permission_required('COMMENT')
def new_comment(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    form = CommentForm()
    if form.validate_on_submit():
        body = form.body.data
        author = current_user._get_current_object()
        comment = Comment(body=body, author=author, post=post)

        replied_id = request.args.get('reply')
        if replied_id:
            comment.replied = Comment.query.get_or_404(replied_id)

        db.session.add(comment)
        db.session.commit()
        flash('评论发表成功。', 'success')
    return redirect(url_for('post.show_post', post_id=post_id, page=page))


@bp.route('/<int:post_id>/set_comment', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)

    if post.can_comment:
        post.can_comment = False
        flash('该博文已禁止评论。', 'info')
    else:
        post.can_comment = True
        flash('该博文已允许评论。', 'info')
    db.session.commit()
    return redirect(url_for('post.show_post', post_id=post_id))


@bp.route('/reply/comment/<int:comment_id>')
@login_required
@permission_required('COMMENT')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return redirect(url_for('post.show_post',
                            post_id=comment.post_id, reply=comment_id,
                            author=comment.author.name) + '#comment-form')


@bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
@permission_required('DELETE_COMMENT')
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除。', 'success')
    return redirect(url_for('user.manage_comments'))


@bp.route('/<int:post_id>/collect', methods=['POST'])
@login_required
@permission_required('COLLECT')
def collect(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.is_collecting(post):
        flash('你已收藏过了该博文。', 'info')
        return redirect(url_for('.show_post', post_id=post_id))

    current_user.collect(post)
    flash('博文已收藏。', 'success')
    return redirect(url_for('.show_post', post_id=post_id))


@bp.route('/<int:post_id>/uncollect', methods=['POST'])
@login_required
def uncollect(post_id):
    post = Post.query.get_or_404(post_id)
    if not current_user.is_collecting(post):
        flash('你并没有收藏过该博文。', 'info')
        return redirect(url_for('.show_post', post_id=post_id))

    current_user.uncollect(post)
    flash('已取消收藏该博文。', 'info')
    return redirect(url_for('.show_post', post_id=post_id))


@bp.route('/category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('类别已删除。', 'info')
    return redirect_back()
