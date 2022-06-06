from flask import Blueprint, jsonify, request

from geoalchemy2.functions import ST_AsGeoJSON
from app.main.models import Crop, CropName, District, Province
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
        crop_id = data.get('name')
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
            crop_id = crop_id,
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
        
    crops = db.session.query(ST_AsGeoJSON(Crop.geometry), Crop.crop_id, Crop.area, Crop.district_id, Crop.farm_tax_number, Crop.farm_cad_number).all()
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
            'name': CropName.query.get(int(crop_id)).name,
            'area': crop_area,
            'district_id': crop_district_id,
            'farm_tax_number': crop_farm_tax_number,
            'farm_cad_number': crop_farm_cad_number
        }
        collection['features'].append(feature)
    return jsonify(collection)

@crop.route('/getby_prefix')
def getby_prefix():
    prefix = request.args.get('prefix')
    if not prefix:
        return jsonify({'msg' : 'error: prefix not defined'})
    pr = Province.query.filter_by(region_prefix=str(prefix).split(':')[0]).first()
    dist = District.query.filter_by(region_id=pr.id, district_prefix=str(prefix).split(':')[1]).first()
    print('DIST', dist)
    crops = Crop.query.filter(Crop.district_id == dist.id).all()
    print('CROPS', crops)
    data = []
    for crop in crops:
        data.append(crop.format())

    print('CROP DATA', data)

    return jsonify(data)

@crop.route('/getby_kadastr')
def getby_kadastr():
    kadastr = request.args.get('cadastral_number')
    if not kadastr:
        return jsonify({'msg' : 'error: prefix not defined'})
    pr = Province.query.filter_by(region_prefix=str(kadastr).split(':')[0]).first()
    dist = District.query.filter_by(region_id=pr.id, district_prefix=str(kadastr).split(':')[1]).first()
    print('DIST', dist)
    crops = Crop.query.filter(Crop.district_id == dist.id, Crop.farm_cad_number == str(kadastr).split(':')[2]).all()
    print('CROPS', crops)
    data = []
    for crop in crops:
        data.append(crop.format())

    print('CROP DATA', data)

    return jsonify(data)