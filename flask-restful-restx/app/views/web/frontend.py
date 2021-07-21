# -*- coding: utf-8 -*-
from flask import render_template, request, flash, Markup

from app.dao.mysql import db
from app.views.web import frontend_v1
from app.forms import HelloForm, TelephoneForm, ContactForm, IMForm, ButtonForm, ExampleForm
from app.models import User


@frontend_v1.route('/')
def index():
    return render_template('web/index.html')


@frontend_v1.route('/form', methods=['GET', 'POST'])
def test_form():
    form = HelloForm()
    return render_template(
        'web/form.html', form=form, telephone_form=TelephoneForm(),
        contact_form=ContactForm(), im_form=IMForm(),
        button_form=ButtonForm(), example_form=ExampleForm())


@frontend_v1.route('/nav', methods=['GET', 'POST'])
def test_nav():
    return render_template('web/nav.html')


@frontend_v1.route('/pagination', methods=['GET', 'POST'])
def test_pagination():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.paginate(page, per_page=10)
    messages = pagination.items
    return render_template('web/pagination.html', pagination=pagination, messages=messages)


@frontend_v1.route('/flash', methods=['GET', 'POST'])
def test_flash():
    flash('A simple default alert—check it out!')
    flash('A simple primary alert—check it out!', 'primary')
    flash('A simple secondary alert—check it out!', 'secondary')
    flash('A simple success alert—check it out!', 'success')
    flash('A simple danger alert—check it out!', 'danger')
    flash('A simple warning alert—check it out!', 'warning')
    flash('A simple info alert—check it out!', 'info')
    flash('A simple light alert—check it out!', 'light')
    flash('A simple dark alert—check it out!', 'dark')
    flash(Markup('A simple success alert with <a href="#" class="alert-link">an example link</a>. Give it a click if you like.'), 'success')
    return render_template('web/flash.html')


@frontend_v1.route('/table')
def test_table():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.paginate(page, per_page=10)
    messages = pagination.items
    titles = [('user_id', '#'), ('user_name', 'User'), ('email', 'Email'), ('telephone', 'Telephone'), ('address', 'Address'), ('created_at', 'Create Time')]
    return render_template('web/table.html', messages=messages, titles=titles)


@frontend_v1.route('/table/<message_id>/view')
def view_message(message_id):
    message = User.query.get(message_id)
    if message:
        return f'Viewing {message_id} with name "{message.user_name}". Return to <a href="/web/table">table</a>.'
    return f'Could not view message {message_id} as it does not exist. Return to <a href="/web/table">table</a>.'


@frontend_v1.route('/table/<message_id>/edit')
def edit_message(message_id):
    message = User.query.get(message_id)
    if message:
        message.user_state = 'inactive'
        db.session.commit()
        return f'Message {message_id} has been editted by toggling draft status. Return to <a href="/web/table">table</a>.'
    return f'Message {message_id} did not exist and could therefore not be edited. Return to <a href="/web/table">table</a>.'


@frontend_v1.route('/table/<message_id>/delete', methods=['POST'])
def delete_message(message_id):
    message = User.query.get(message_id)
    if message:
        db.session.delete(message)
        db.session.commit()
        return f'Message {message_id} has been deleted. Return to <a href="/web/table">table</a>.'
    return f'Message {message_id} did not exist and could therefore not be deleted. Return to <a href="/web/table">table</a>.'


@frontend_v1.route('/icon')
def test_icon():
    return render_template('web/icon.html')
