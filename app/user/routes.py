# -*- coding: utf-8 -*-
from flask import request, current_app, render_template, flash, redirect, \
    url_for
from flask_login import login_required, current_user, fresh_login_required, \
    logout_user

from app import db
from app.decorators import permission_required
from app.models import User, Post
from app.user import bp
from app.user.forms import EditProfileForm, ChangePasswordForm, \
    PrivacySettingForm, DeleteAccountForm
from app.utils import redirect_back


@bp.route('/<username>', methods=['GET'])
def index(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SHMUBLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(user).order_by(
        Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('user/index.html', user=user, pagination=pagination,
                           posts=posts)


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
        flash('好的，你自由了。', 'success')
        return redirect(url_for('main.index'))
    return render_template('user/settings/delete_account.html', form=form)
