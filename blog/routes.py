#from curses import noecho
#from dataclasses import dataclass
from flask import Flask, render_template, request, session, flash, redirect, url_for
from blog import app
from blog.models import Entry, db
from blog.forms import EntryForm
from blog.forms import LoginForm
import functools

@app.route("/")
def index():
    all_posts = Entry.query.filter_by(is_published=True).order_by(Entry.pub_date.desc())
    return render_template("homepage.html", all_posts=all_posts)


def work_on_entry(entry_id=False):
    errors = None
    if entry_id == False:
        form_1 = EntryForm()
        if request.method == 'POST':
            if form_1.validate_on_submit():
                entry = Entry(
                    title=form_1.title.data,
                    body=form_1.body.data,
                    is_published=form_1.is_published.data
                )
                db.session.add(entry)
                db.session.commit()
            else:
                errors = form_1.errors
        flash('You successfully created a new post!')
        return render_template("entry_form.html", form=form_1, errors=errors)
    else:
        entry = Entry.query.filter_by(id=entry_id).first_or_404()
        form = EntryForm(obj=entry)
        if request.method == 'POST':
            if form.validate_on_submit():
                form.populate_obj(entry)
                db.session.commit()
            else:
                errors = form.errors
        flash('You successfully changed your post!')
        return render_template("entry_form.html", form=form, errors=errors)

def login_required(view_func):
    @functools.wraps(view_func)
    def check_permissions(*args, **kwargs):
        if session.get('logged_in'):
            return view_func(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return check_permissions

@app.route("/new-post/", methods=["GET", "POST"])
@login_required
def create_entry():
    return work_on_entry()

@app.route("/edit-post/<int:entry_id>", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
    return work_on_entry(entry_id)

@app.route("/delete-post/<int:entry_id>", methods=["GET", "POST"])
@login_required
def delete_entry(entry_id):
    errors = None
    if entry_id:
        entry = Entry.query.filter_by(id=entry_id).first_or_404()
        if request.method == 'POST':
                db.session.delete(entry)
                db.session.commit()  
        flash('You successfully deleted your post!')
        return redirect(url_for('index'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    errors = None
    next_url = request.args.get('next')
    if request.method == 'POST':
        if form.validate_on_submit():
            session['logged_in'] = True
            session.permanent = True
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('index'))
        else:
            errors = form.errors
    return render_template("login_form.html", form=form, errors=errors)

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        flash('You are now logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/drafts/', methods=['GET', 'POST'])
def list_drafts():
    draft_posts = Entry.query.filter_by(is_published=False).order_by(Entry.pub_date.desc())
    return render_template("table.html", draft_posts=draft_posts)