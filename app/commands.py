# -*- coding: utf-8 -*-
import click

from app.extensions import db
from app.models import Role


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='删除之前的表后再初始化.')
    def initdb(drop):
        """初始化数据库."""
        if drop:
            click.confirm('执行该命令将会删除当前数据库，确定要执行吗？', abort=True)
            db.drop_all()
            click.echo('删除所有表.')
        db.create_all()
        click.echo('初始化数据库.')

    @app.cli.command()
    def init():
        """初始化项目"""
        click.echo('初始化数据库...')
        db.create_all()

        click.echo('初始化用户角色与权限...')
        Role.init_role()

        click.echo('初始化完毕.')

    @app.cli.command()
    @click.option('--user', default=30, help='生成用户的数量，默认：30')
    @click.option('--follow', default=270, help='生成关注的数量，默认：270')
    @click.option('--post', default=270, help='生成博文的数量，默认：270')
    @click.option('--category', default=60, help='生成类别的数量，默认：60')
    @click.option('--comment', default=2700, help='生成评论的数量，默认：2700')
    @click.option('--collect', default=270, help='生成收藏的数量，默认：270')
    def fake(user, follow, collect, post, category, comment):
        """生成假数据"""
        from app.fake import fake_admin, fake_user, fake_comment, \
            fake_follow, fake_post, fake_category, fake_collect
        db.drop_all()
        db.create_all()

        click.echo('初始化用户角色与权限...')
        Role.init_role()
        click.echo('生成管理员...')
        fake_admin()
        click.echo('生成%d个用户...' % user)
        fake_user(user)
        click.echo('生成%d个关注...' % follow)
        fake_follow(follow)
        click.echo('生成%d个类别...' % category)
        fake_category(category)
        click.echo('生成%d篇博文......' % post)
        fake_post(post)
        click.echo('生成%d条评论...' % comment)
        fake_comment(comment)
        click.echo('生成%d个收藏...' % collect)
        fake_collect(collect)
        click.echo('数据生成完毕。')
