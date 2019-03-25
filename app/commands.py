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
