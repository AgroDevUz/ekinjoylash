from flask import Blueprint, jsonify
from app import db, cache
from app.main.models import District, Province
from flask_login import current_user, login_required
from geoalchemy2.functions import ST_AsGeoJSON
import json
api = Blueprint("api",__name__, url_prefix='/api')

from .kadastr.routes import kadastr
api.register_blueprint(kadastr)

@api.route("/district", methods=['GET'])
@login_required
def get_district():
    @cache.memoize(3600)
    def generate_geojson(dist_id):
        dist = District.query.get(dist_id)
        prc = Province.query.get(dist.region_id)
        rest = db.session.query(ST_AsGeoJSON(District.geometry), District.nameru).filter(District.region_id==prc.id, District.district_prefix==dist.district_prefix).first()
        if not rest:
            return {}
        FeatureCollection = {
            "type" : "FeatureCollection",
            "features" : [],
            
        }
        feature = {
            "type" : "Feature"
        }
        geometry = rest[0]
        geometry = json.loads(geometry)
        feature['geometry'] = geometry
        feature['properties'] = {
            "nameru": rest[1] 
        }
        FeatureCollection['features'].append(feature)
        return FeatureCollection    
    
    
    return jsonify(generate_geojson(current_user.district_id))

