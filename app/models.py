from . import db
from datetime import date

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)

class TeamMember(db.Model):
    __tablename__ = "team_members"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    date_of_joining = db.Column(db.Date, nullable=False)
    details = db.Column(db.Text, nullable=True)

    @property
    def total_years(self):
        today = date.today()
        return (today - self.date_of_joining).days // 365
