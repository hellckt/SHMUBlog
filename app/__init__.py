# -*- coding: utf-8 -*-
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, request

from app.commands import register_commands
from app.extensions import db, bootstrap, login_manager, csrf, ckeditor, \
    moment, avatars
from config import config

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask(__name__)

    # 加载配置变量
    app.config.from_object(config[config_name])

    # 注册日志处理器
    register_logging(app)

    # 初始化插件
    register_extensions(app)

    # 注册蓝本(blueprint)
    register_blueprints(app)

    # 注册项目自定义命令
    register_commands(app)

    # 注册shell上下文处理函数
    register_shell_context(app)

    return app


def register_logging(app):
    """日志相关"""

    class RequestFormatter(logging.Formatter):
        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(
        os.path.join(basedir, 'logs/shmublog.log'),
        maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    if not app.debug:
        app.logger.addHandler(file_handler)


def register_extensions(app):
    """初始化拓展"""
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    moment.init_app(app)
    avatars.init_app(app)


def register_blueprints(app):
    """加载蓝图(blueprint)

    ❕之后建立的蓝图都需要在这里注册
    """
    # 主体模块
    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    # 认证模块
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 用户模块
    from .user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    # 博文模块
    from .post import bp as post_bp
    app.register_blueprint(post_bp, url_prefix='/post')

    # 管理员模块
    from .admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # 错误模块
    from .errors import bp as errors_bp
    app.register_blueprint(errors_bp)


def register_shell_context(app):
    """注入 Flask 脚本上下文"""

    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)
