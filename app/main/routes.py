# -*- coding: utf-8 -*-
from datetime import datetime

from flask import render_template, send_from_directory, current_app, request, \
    flash
from flask_login import current_user, login_required
from sqlalchemy import func

from app import db
from app.main import bp
from app.models import Collect, Post, Category, categorizing, User, Follow
from app.utils import redirect_back


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        # 记录用户最后活跃时间
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/')
@bp.route('/index')
def index():
    hot_post_limit = current_app.config.get('SHMUBLOG_HOT_POST_LIMIT')
    hot_posts = Post.query \
        .join(Collect).filter(Post.id == Collect.collected_id) \
        .group_by(Collect.collected_id) \
        .order_by(func.count(Collect.collector_id).desc()) \
        .limit(hot_post_limit)

    hot_category_limit = current_app.config.get('SHMUBLOG_HOT_CATEGORY_LIMIT')
    hot_categories = Category.query \
        .join(categorizing).filter(Category.id == categorizing.c.category_id) \
        .add_columns(func.count(categorizing.c.post_id).label('total')) \
        .group_by(Category.id) \
        .order_by(func.count(categorizing.c.post_id).desc()) \
        .limit(hot_category_limit)

    most_viewed_post_limit = current_app.config.get(
        'SHMUBLOG_MOST_VIEW_POST_LIMIT')
    most_viewed_posts = Post.query.order_by(Post.viewed.desc()).limit(
        most_viewed_post_limit)

    fresh_user_limit = current_app.config.get('SHMUBLOG_FRESH_USER_LIMIT')
    fresh_users = User.query.order_by(User.member_since.desc()).limit(
        fresh_user_limit)
    return render_template('index.html', hot_posts=hot_posts,
                           hot_categories=hot_categories,
                           most_viewed_posts=most_viewed_posts,
                           fresh_users=fresh_users)


@bp.route('/<string:username>/home')
@login_required
def home(username):
    followings = Follow.query.filter_by(follower_id=current_user.id).all()
    following_ids = [following.followed_id for following in followings]
    following_ids.append(current_user.id)
    pagination = Post.query.filter(Post.author_id.in_(following_ids)) \
        .order_by(Post.timestamp.desc()).paginate()
    posts = pagination.items
    return render_template('home.html', pagination=pagination,
                           posts=posts, user=current_user)


@bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if q == '':
        flash('请输入博文、用户、博文类别相关的关键字。', 'warning')
        return redirect_back()

    category = request.args.get('category', 'post')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SHMUBLOG_SEARCH_RESULT_PER_PAGE']
    if category == 'user':
        pagination = User.query.whooshee_search(q).paginate(page, per_page)
    elif category == 'category':
        pagination = Category.query.whooshee_search(q).paginate(page, per_page)
    else:
        pagination = Post.query.whooshee_search(q).paginate(page, per_page)
    results = pagination.items
    return render_template('search.html', q=q, results=results,
                           pagination=pagination, category=category)


@bp.route('/explore')
def explore():
    posts = Post.query.order_by(func.random()).limit(12)
    return render_template('explore.html', posts=posts)


@bp.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'],
                               filename)
