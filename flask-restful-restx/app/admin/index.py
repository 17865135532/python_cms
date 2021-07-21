from flask import redirect, url_for, request
from flask_admin import AdminIndexView, expose, helpers
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

from app.dao.mysql import db
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[validators.Email()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

    def validate_login(self):
        user = self.get_user()
        if user is None:
            raise validators.ValidationError('账号不存在')
        return user.verify_pwd(self.password.data)

    def get_user(self):
        return db.session.query(User).active.filter(User.email == self.email.data).first()


class IndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return self.render('index.html')

    @expose('/login', methods=('GET', 'POST'))
    def login_view(self):
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)
        if current_user.is_authenticated:
            return redirect(url_for('.index'))
        return self.render('login.html', form=form)

    @expose('/logout')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))


index_view = IndexView()
