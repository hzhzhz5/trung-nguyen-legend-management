from app.extensions import db

class Role(db.Model):
    __tablename__ = "roles"

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    users = db.relationship("UserAccount", backref="role", lazy=True)

    def __repr__(self):
        return f"<Role {self.role_name}>"