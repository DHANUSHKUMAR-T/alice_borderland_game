from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app.auth import auth
from app.auth.forms import LoginForm, SignupForm
from app import db
from app.models import User, GameProgress


# -----------------------------
# CREATE DEFAULT TEST USER
# -----------------------------
def create_default_user():
    username = "dhanush"
    password = "kumar"

    user = User.query.filter_by(username=username).first()

    if not user:
        hashed = generate_password_hash(password)
        new_user = User(username=username, password=hashed)
        db.session.add(new_user)
        db.session.commit()

        progress = GameProgress(user_id=new_user.id)
        db.session.add(progress)
        db.session.commit()


# -----------------------------
# LOGIN
# -----------------------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid username or password!", "error")
            return redirect(url_for("auth.login"))

        login_user(user)
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html")


# -----------------------------
# SIGNUP
# -----------------------------
@auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("auth.signup"))

        hashed = generate_password_hash(password)
        user = User(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()

        progress = GameProgress(user_id=user.id)
        db.session.add(progress)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html")


# -----------------------------
# LOGOUT
# -----------------------------
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))
