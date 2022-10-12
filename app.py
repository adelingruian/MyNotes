from flask import Flask, render_template, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_bootstrap import Bootstrap
from forms import CreateEntryForm, LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///mynotes.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = "Tractor"

ckeditor = CKEditor(app)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

gravatar = Gravatar(app,
                    size=40,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    entry_date = db.Column(db.String(15), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="notes")



class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    pass_hash = db.Column(db.String(50), nullable=False)
    notes = relationship("Note", back_populates="author")

db.create_all();

@app.route('/')
def index():
    try:
        all_tasks = Note.query.filter_by(author_id=current_user.id).all()
    except AttributeError:
        all_tasks = []
        return render_template("index.html", tasks=all_tasks)
    return render_template("index.html", tasks=all_tasks)


@login_required
@app.route('/add-entry', methods=['GET', 'POST'])
def add_entry():

    today = datetime.today()
    create_entry_form = CreateEntryForm(
        entry_date=today
    )
    if create_entry_form.validate_on_submit():
        if Note.query.filter_by(title=create_entry_form.title.data).first():
            flash("This title already exists.")
        else:
            new_note = Note(
                title=create_entry_form.title.data,
                description=create_entry_form.description.data,
                entry_date=create_entry_form.entry_date.data.strftime('%d/%m/%Y'),
                author=current_user
            )
            db.session.add(new_note)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template("add_entry.html", form=create_entry_form)


@login_required
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    task = Note.query.get(task_id)
    date = task.entry_date.split('/')
    edit_form = CreateEntryForm(
        title=task.title,
        description=task.description,
        entry_date=datetime(int(date[2]), int(date[1]), int(date[0]))
    )
    if edit_form.validate_on_submit():
        if task.title != edit_form.title.data:
            if Note.query.filter_by(title=edit_form.title.data).first():
                flash("This entry title already exists.")
        task.title = edit_form.title.data
        task.description = edit_form.description.data
        task.entry_date = edit_form.entry_date.data.strftime('%d/%m/%Y')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("add_entry.html", form=edit_form)


@login_required
@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = Note.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = User.query.filter_by(email=register_form.email.data).first()
        if user:
            redirect_url = url_for('login')
            flash(f"Email is already registered. <a href='{redirect_url}'>Log in</a>")
        else:
            new_user = User(
                name=register_form.name.data,
                email=register_form.email.data,
                pass_hash=generate_password_hash(register_form.password.data, "pbkdf2:sha256", 8)
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('index'))

    return render_template("register.html", form=register_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if not user:
            redirect_url = url_for('register')
            flash(f"User is not registered. <a href='{redirect_url}'>Sign up</a>")
        elif check_password_hash(user.pass_hash, login_form.password.data):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', form=login_form)


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@login_required
@app.route('/download')
def download():
    with open("export.csv", "w") as file:
        all_tasks = Note.query.filter_by(author_id=current_user.id).all()
        for task in all_tasks:
            new_line = f"{task.title},{task.description},{task.entry_date}\n"
            file.writelines(new_line)
    return send_from_directory("", "export.csv")

if __name__ == '__main__':
    app.run(debug=True)
