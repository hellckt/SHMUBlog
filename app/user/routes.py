# -*- coding: utf-8 -*-
from flask import request, current_app, render_template, flash, redirect, \
    url_for
from flask_login import login_required, current_user, fresh_login_required, \
    logout_user
from sqlalchemy import func

from app import db
from app.decorators import permission_required
from app.models import User, Post, Category, categorizing, Collect, Comment
from app.user import bp
from app.user.forms import EditProfileForm, ChangePasswordForm, \
    PrivacySettingForm, DeleteAccountForm
from app.utils import redirect_back


@bp.route('/<username>', methods=['GET'])
def index(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id', None, type=int)
    per_page = current_app.config['SHMUBLOG_POST_PER_PAGE']
    if category_id:
        pagination = Post.query.with_parent(user) \
            .filter(Post.categories.any(id=category_id)) \
            .order_by(Post.timestamp.desc()).paginate(page, per_page)
    else:
        pagination = Post.query.with_parent(user).order_by(
            Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items

    # TODO: 考虑优化查询
    count_categories = db.session.query(Category.id, Category.name,
                                        func.count(Category.id).label('total')) \
        .join(categorizing).filter(categorizing.c.category_id == Category.id) \
        .join(Post).filter(Post.id == categorizing.c.post_id,
                           Post.author_id == user.id) \
        .group_by(Category.id) \
        .order_by(func.count(Category.id).desc()).all()
    return render_template('user/index.html', user=user, pagination=pagination,
                           posts=posts, categories=count_categories)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
@permission_required('FOLLOW')
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        flash(f'你已经关注过{user.username}了。', 'info')
        return redirect(url_for('user.index', username=username))

    current_user.follow(user)
    flash('关注成功。', 'success')
    return redirect_back()


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
@permission_required('UNFOLLOW')
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if not current_user.is_following(user):
        flash(f'你并没有关注{user.username}。', 'info')
        return redirect(url_for('user.index', username=username))

    current_user.unfollow(user)
    flash(f'取消了对{user.username}关注。', 'info')
    return redirect_back()


@bp.route('/<username>/followers')
def show_followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SHMUBLOG_USER_PER_PAGE']
    pagination = user.followers.paginate(page, per_page)
    follows = pagination.items
    return render_template('user/followers.html', user=user,
                           pagination=pagination, follows=follows)


@bp.route('/<username>/following')
def show_following(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SHMUBLOG_USER_PER_PAGE']
    pagination = user.following.paginate(page, per_page)
    follows = pagination.items
    return render_template('user/following.html', user=user,
                           pagination=pagination, follows=follows)


@bp.route('/<username>/collections')
def show_collections(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SHMUBLOG_POST_PER_PAGE']
    pagination = Collect.query.with_parent(user).order_by(
        Collect.timestamp.desc()).paginate(page, per_page)
    collects = pagination.items
    return render_template('user/collections.html', user=user,
                           pagination=pagination, collects=collects)


@bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('资料更新成功。', 'success')
        return redirect(url_for('.index', username=current_user.username))
    form.name.data = current_user.name
    form.username.data = current_user.username
    form.bio.data = current_user.bio
    return render_template('user/settings/edit_profile.html', form=form)


@bp.route('/settings/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.validate_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.commit()
            flash('密码已修改，请重新登陆。', 'success')
            logout_user()
            return redirect(url_for('auth.login'))
        else:
            flash('旧密码错误，请重新输入。', 'warning')
    return render_template('user/settings/change_password.html', form=form)


@bp.route('/settings/privacy', methods=['GET', 'POST'])
@login_required
def privacy_setting():
    form = PrivacySettingForm()
    if form.validate_on_submit():
        current_user.public_collections = form.public_collections.data
        db.session.commit()
        flash('设置成功。', 'success')
    form.public_collections.data = current_user.public_collections
    return render_template('user/settings/edit_privacy.html', form=form)


@bp.route('/settings/account/delete', methods=['GET', 'POST'])
@fresh_login_required
@permission_required('DELETE_ACCOUNT')
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        db.session.delete(current_user._get_current_object())
        db.session.commit()
        logout_user()
        flash('好的，你自由了。', 'success')
        return redirect(url_for('main.index'))
    return render_template('user/settings/delete_account.html', form=form)


@bp.route('/management/posts')
@login_required
def manage_posts():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SHMUBLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(current_user) \
        .order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('user/management/manage_posts.html',
                           pagination=pagination, posts=posts)


@bp.route('/management/comments')
@login_required
def manage_comments():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SHMUBLOG_COMMENT_PER_PAGE']
    pagination = Comment.query \
        .filter(Comment.post_id.in_([post.id for post in current_user.posts])) \
        .order_by(Comment.timestamp.desc()).paginate(page, per_page)
    comments = pagination.items
    return render_template('user/management/manage_comments.html',
                           pagination=pagination, comments=comments)
