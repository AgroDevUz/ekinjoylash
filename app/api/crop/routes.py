from flask import Blueprint, jsonify, request

from geoalchemy2.functions import ST_AsGeoJSON
from app.main.models import Crop, District
from geomet import wkt
from app import db
import json
crop = Blueprint("crop",__name__, url_prefix='/crop')

@crop.route("/", methods=['POST', "GET"])
def crop_main():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400
        name = data.get('name')
        area = data.get('area')
        geometry = data.get('geometry')
        district_id = data.get('district_id')
        farm_tax_number = data.get('farm_tax_number')
        farm_cad_number = data.get('farm_cad_number')
        
        try:
            geometry = wkt.dumps(geometry, decimals=4)
        except Exception as E:
            return jsonify({'error': str(E)})
        
        if not District.query.get(district_id):
            return jsonify({'error': 'District not found'})
        
        crop = Crop(
            name = name,
            area = area,
            geometry = geometry,
            district_id = district_id,
            farm_tax_number = farm_tax_number,
            farm_cad_number = farm_cad_number
        )
        try:
            db.session.add(crop)
            db.session.commit()
        except Exception as E:
            db.session.rollback()
            return jsonify({'error': str(E)})
        
    crops = db.session.query(ST_AsGeoJSON(Crop.geometry), Crop.name, Crop.area, Crop.district_id, Crop.farm_tax_number, Crop.farm_cad_number).all()
    collection = {
        "type": "FeatureCollection",
        "features": []
        }
    for crop_geo, crop_name, crop_area, crop_district_id, crop_farm_tax_number, crop_farm_cad_number in crops:
        
        
        feature = {
            "type" : "Feature"
        }
        crop_geo = json.loads(crop_geo)
        feature['geometry'] = crop_geo
        feature['properties'] = {
            'name': crop_name,
            'area': crop_area,
            'district_id': crop_district_id,
            'farm_tax_number': crop_farm_tax_number,
            'farm_cad_number': crop_farm_cad_number
        }
        collection['features'].append(feature)
    return jsonify(collection)