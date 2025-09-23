from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from .models import User, TeamMember
from . import google, db
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import csv
from werkzeug.utils import secure_filename
import os


main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        if not google.authorized:
            flash("Please log in first.", "warning")
            return redirect(url_for("main.index"))

        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            flash("Failed to fetch user info. Please login again.", "danger")
            return redirect(url_for("main.index"))

        user_info = resp.json()
        user = User.query.filter_by(google_id=user_info["id"]).first()
        if not user:
            user = User(
                google_id=user_info["id"],
                name=user_info.get("name"),
                email=user_info.get("email")
            )
            db.session.add(user)
            db.session.commit()

        session["user_id"] = user.id

    user = User.query.get(session["user_id"])
    return render_template("dashboard.html", user=user)

@main_bp.route("/team")
def team():
    members = TeamMember.query.all()
    if not members:
        flash("No team members found.", "info")
    return render_template("team.html", members=members)



@main_bp.route("/team/add", methods=["GET", "POST"])
def add_team_member():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        date_of_joining = request.form.get("date_of_joining")
        details = request.form.get("details")

        try:
            member = TeamMember(
                name=name,
                email=email,
                date_of_joining=datetime.strptime(date_of_joining, "%Y-%m-%d").date(),
                details=details
            )
            db.session.add(member)
            db.session.commit()
            flash("Team member added successfully!", "success")
            return redirect(url_for("main.team"))

        except IntegrityError:
            db.session.rollback()
            flash("Error: Team member email already exists. Please use a different email.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")

    return render_template("add_team.html")

#####################
# Bulk upload Team Members via CSV  
#####################

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.route("/team/import", methods=["GET", "POST"])
def import_team():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part", "danger")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No selected file", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            errors = []
            success_count = 0

            with open(filepath, newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row_num, row in enumerate(reader, start=2):  # start=2 (skip header)
                    try:
                        # Check duplicate email
                        if TeamMember.query.filter_by(email=row["email"]).first():
                            errors.append(f"Row {row_num}: Email {row['email']} already exists")
                            continue

                        member = TeamMember(
                            name=row["name"],
                            email=row["email"],
                            date_of_joining=datetime.strptime(row["date_of_joining"], "%Y-%m-%d").date(),
                            details=row.get("details", "")
                        )
                        db.session.add(member)
                        success_count += 1

                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")

                # Commit once at the end
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    errors.append(f"Database commit failed: {str(e)}")

            if success_count > 0:
                flash(f"Successfully imported {success_count} team members!", "success")
            if errors:
                flash("Some errors occurred:<br>" + "<br>".join(errors), "danger")

            return redirect(url_for("main.team"))

    return render_template("import_team.html")