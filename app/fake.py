# -*- coding: utf-8 -*-
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User, Category, Post, Comment

fake = Faker()


def fake_admin():
    admin = User(name='科特',
                 username='cotte',
                 email='hellckt@126.com',
                 bio=fake.sentence())
    admin.password = 'hellckt123'
    db.session.add(admin)
    db.session.commit()


def fake_user(count=30):
    for i in range(count):
        user = User(name=fake.name(),
                    username=fake.user_name(),
                    bio=fake.sentence(),
                    member_since=fake.date_this_decade(),
                    email=fake.email())
        user.password = '12345678'
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_follow(count=270):
    for i in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.follow(User.query.get(random.randint(1, User.query.count())))
    db.session.commit()


def fake_category(count=60):
    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_post(count=270):
    for i in range(count):
        post = Post(title=fake.sentence(),
                    body=fake.paragraph(30),
                    author=User.query.get(
                        random.randint(1, User.query.count())),
                    timestamp=fake.date_time_this_year())

        for j in range(random.randint(1, 5)):
            category = Category.query.get(
                random.randint(1, Category.query.count()))
            if category not in post.categories:
                post.categories.append(category)
        db.session.add(post)
    db.session.commit()


def fake_comment(count=2700):
    for i in range(count):
        comment = Comment(
            author=User.query.get(random.randint(1, User.query.count())),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()


def fake_collect(count=270):
    for i in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.collect(Post.query.get(random.randint(1, Post.query.count())))
    db.session.commit()
