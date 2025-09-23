from flask import Blueprint, session, redirect, url_for, flash
from . import google_bp

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/logout")
def logout():
    session.clear()
    if google_bp.token:
        del google_bp.token
        flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))
