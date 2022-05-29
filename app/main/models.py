from flask_login import UserMixin
from app import db
from datetime import datetime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from geoalchemy2 import Geometry
from app import login_manager


def Get_Load(user_id):
    return User.query.get(user_id)

@login_manager.user_loader
def load_user(user_id):
    return Get_Load(user_id)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=True, default='user')
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=True)
    permissions = relationship("Permission", backref="user", lazy=True)

    def format(self):
        return {
            'id' : self.id,
            'login' : self.login,
            'role' : self.role,
            'created_at' : self.created_at.strftime("%d-%m-%Y"),
            'last_login' : self.last_login,
            'district' : District.query.get(self.district_id).name,
            'permissions' : [x.format() for x in self.permissions]
        }

    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)



class Province(db.Model):
    __tablename__ = "province"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    nameru = db.Column(db.String, nullable=True)
    region_prefix = db.Column(db.String, nullable=False)
    geometry = db.Column(Geometry(geometry_type="MULTIPOLYGON", srid=3857), nullable = True)
    districts = relationship("District", backref="province", lazy=True)

class District(db.Model):
    __tablename__ = "district"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    nameru = db.Column(db.String, nullable=True)
    region_id = db.Column(db.Integer, db.ForeignKey("province.id"), nullable=False)
    district_prefix = db.Column(db.String, nullable=False)
    geometry = db.Column(Geometry(geometry_type="MULTIPOLYGON", srid=3857), nullable = True)
    users = relationship("User", backref="district", lazy=True)

    def format(self):
        return {
        'id' : self.id,
        'name' : self.name
        }
class Permission(db.Model):
    __tablename__ = "permission"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    permission = db.Column(db.String, nullable=False)
    value = db.Column(db.Boolean, nullable=False)

    def format(self):
        return {
            'id' : self.id,
            'permission' : self.permission,
            'value' : self.value
        }

class CropName(db.Model):
    __tablename__ = "cropname"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    code = db.Column(db.Integer, nullable=False)


    def format(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'code' : self.code
        }
        
