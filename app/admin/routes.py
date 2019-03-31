# -*- coding: utf-8 -*-
from flask import render_template, request, current_app, flash
from flask_login import login_required
from sqlalchemy import func

from app.admin import bp
from app.decorators import admin_required
from app.extensions import db
from app.models import Post, User, Category, Comment, Role, categorizing
from app.utils import redirect_back


@bp.route('/')
@login_required
@admin_required
def index():
    user_count = User.query.count()
    blocked_user_count = User.query.filter_by(active=False).count()
    post_count = Post.query.count()
    category_count = Category.query.count()
    comment_count = Comment.query.count()
    return render_template('admin/index.html',
                           user_count=user_count,
                           blocked_user_count=blocked_user_count,
                           post_count=post_count,
                           category_count=category_count,
                           comment_count=comment_count)


@bp.route('/manage/post')
@login_required
@admin_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SHMUBLOG_MANAGE_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.flag.desc(), Post.timestamp.desc()) \
        .paginate(page, per_page)
    posts = pagination.items
    return render_template('admin/manage_post.html', pagination=pagination,
                           posts=posts)


@bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('博文已删除', 'success')
    return redirect_back()


@bp.route('/manage/user')
@login_required
@admin_required
def manage_user():
    # 筛选条件
    # filter:'all', 'blocked', 'administrator'
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SHMUBLOG_MANAGE_POST_PER_PAGE']

    administrator = Role.query.filter_by(name='Administrator').first()

    if filter_rule == 'blocked':
        filtered_users = User.query.filter_by(active=False)
    elif filter_rule == 'administrator':
        filtered_users = User.query.filter_by(role=administrator)
    else:
        filtered_users = User.query

    pagination = filtered_users.order_by(User.member_since.desc()) \
        .paginate(page, per_page)
    users = pagination.items
    return render_template('admin/manage_user.html', pagination=pagination,
                           users=users)


@bp.route('/manage/user/<int:user_id>/block', methods=['POST'])
@login_required
@admin_required
def block_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('不能封禁管理员。', 'warning')
    else:
        user.block()
        flash('该账户已封禁。', 'success')
    return redirect_back()


@bp.route('/manage/user/<int:user_id>/unblock', methods=['POST'])
@login_required
@admin_required
def unblock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.unblock()
    flash('该账户已解封。', 'success')
    return redirect_back()


@bp.route('/manage/comment')
@login_required
@admin_required
def manage_comment():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SHMUBLOG_MANAGE_COMMENT_PER_PAGE']
    pagination = Comment.query.order_by(Comment.flag.desc()).paginate(
        page, per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', pagination=pagination,
                           comments=comments)


@bp.route('/manage/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect_back()


@bp.route('/manage/category')
@login_required
@admin_required
def manage_category():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SHMUBLOG_MANAGE_CATEGORY_PER_PAGE']
    pagination = db.session.query(Category.id, Category.name,
                                  func.count(Category.id).label('total')) \
        .join(categorizing).filter(categorizing.c.category_id == Category.id) \
        .join(Post).filter(Post.id == categorizing.c.post_id) \
        .group_by(Category.id) \
        .order_by(func.count(Category.id).desc()).paginate(page, per_page)
    categories = pagination.items
    return render_template('admin/manage_category.html', pagination=pagination,
                           categories=categories)


@bp.route('/manage/category/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    category = Category.query.order_by(Category.id.desc()).get_or_404(
        category_id)
    db.session.delete(category)
    db.session.commit()
    flash('该类别已删除', 'success')
    return redirect_back()
