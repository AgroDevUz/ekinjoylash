import random
from models import *
from routes import PERMISSIONS
from  geomet import wkt
import json

def create_admin():
    u = User(
        login = 'admin',
        role = 'admin',
        district_id = District.query.filter_by(name='Qiyichirchiq').first().id
    )
    u.set_password('admin')
    db.session.add(u)
    db.session.commit()

def create_user():
    u = User(
        login = 'qwerty',
        district_id = District.query.filter_by(name='Qiyichirchiq').first().id
    )
    u.set_password('qwerty')
    db.session.add(u)
    db.session.commit()
    for p in PERMISSIONS:
        per = Permission(
            user_id = u.id,
            permission = p,
            value = bool(random.randint(0, 1))
        )
        db.session.add(per)
    db.session.commit()

def create_dis():
    with open("tuman.json", 'r', encoding='utf8') as f:
        data = json.loads(f.read())
        for d in data['features']:
            ds = District.query.filter_by(nameru=d['properties']['name']).first()
            if ds:
                continue
            else:
                poly = d['geometry']
                dump = wkt.dumps(poly)
                if 'MULTI' not in dump:
                    dump = dump.replace("GON", "GON(").replace("POL","MULTIPOL")
                    dump = dump + ")"
                dist = District(
                    nameru = d['properties']['name'],
                    district_prefix = str(d['properties']['cadastr_num']).split(':')[1],
                    region_id = Province.query.filter_by(region_prefix=str(d['properties']['cadastr_num']).split(':')[0]).first().id,
                    geometry = 'SRID=3857;' + dump
                )
                db.session.add(dist)
                db.session.commit()

def create_prs():
    with open("csvjson.json", 'r', encoding='utf8') as f:
        data = json.loads(f.read())
        for d in data:
            pr = Province.query.filter_by(name=d['viloyat']).first()
            if pr:
                continue
            else:
                p = Province(
                    name = d['viloyat'],
                    region_prefix = str(d['cad_prefix']).split(':')[0]
                )
                db.session.add(p)
                db.session.commit()

def write_geoms():
    with open("regions.json", 'r', encoding='utf8') as f:
        data = json.loads(f.read())
        for d in data['features']:
            pr = Province.query.filter_by(region_prefix=d['properties']['cadastr_num']).first()
            pr.nameru = d['properties']['name']
            poly = d['geometry']
            dump = wkt.dumps(poly)
            if 'MULTI' not in dump:
                dump = dump.replace("GON", "GON(").replace("POL","MULTIPOL")
                dump = dump + ")"
            pr.geometry = 'SRID=3857;' + dump
            db.session.commit()

def write_geoms_dists():
    with open("tuman.json", 'r', encoding='utf8') as f:
        data = json.loads(f.read())
        counter = 0
        for d in data['features']:
            counter += 1
            reg_pref, dist_pref = str(d['properties']['cadastr_num']).split(':')
            pr = Province.query.filter_by(region_prefix=reg_pref).first()
            dist = District.query.filter_by(region_id=pr.id, district_prefix=dist_pref).first()
            if not dist:
                continue
            else:
                dist.nameru = d['properties']['name']
                poly = d['geometry']
                dump = wkt.dumps(poly)
                if 'MULTI' not in dump:
                    dump = dump.replace("GON", "GON(").replace("POL","MULTIPOL")
                    dump = dump + ")"
                dist.geometry = 'SRID=3857;' + dump
                db.session.commit()

# db.create_all()
# db.drop_all()
# District.__table__.create(db.session.bind)
# create_prs()
# create_dis()
# create_admin()

# create_user()

# write_geoms_dists()import random
from models import *
from routes import PERMISSIONS
from  geomet import wkt
import j