#!/usr/bin/python
# -*- coding:utf-8 -*-
# @FileName  :manage.py.py
# @Time      :2020/8/31 下午3:57

from flask_script import Manager, Server
from flask_migrate import MigrateCommand

from application import app


manager = Manager(app=app)
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server(host='0.0.0.0', port=8006))


if __name__ == '__main__':
    manager.run()

