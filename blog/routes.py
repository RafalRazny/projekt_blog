from dataclasses import dataclass
from flask import Flask, render_template, request
from blog import app
from blog.models import Entry, db
from blog.forms import EntryForm

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    all_posts = Entry.query.filter_by(is_published=True).order_by(Entry.pub_date.desc())
    return render_template("homepage.html", all_posts=all_posts)

def work_on_entry(entry_id):
    errors = None
    if entry_id == None:
        form = EntryForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                entry = Entry(
                    title=form.title.data,
                    body=form.body.data,
                    is_published=form.is_published.data
                )
                db.session.add(entry)
                db.session.commit()
            else:
                errors = form.errors
        return render_template("entry_form.html", form=form, errors=errors)
    else:
        if request.method == 'POST':
            entry = Entry.query.filter_by(id=entry_id).first_or_404()
            form = EntryForm(obj=entry)
            if form.validate_on_submit():
                form.populate_obj(entry)
                db.session.commit()
            else:
                errors = form.errors
        return render_template("entry_form.html", form=form, errors=errors)
   

@app.route("/new-post/", methods=["GET", "POST"])
def create_entry():
    return work_on_entry()

@app.route("/edit-post/<int:entry_id>", methods=["GET", "POST"])
def edit_entry(entry_id):
    return work_on_entry(entry_id)