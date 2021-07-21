from flask_script import Manager, Server
from flask_migrate import MigrateCommand

from application import app


manager = Manager(app=app)
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server(host='0.0.0.0', port=5000))


if __name__ == '__main__':
    manager.run()
