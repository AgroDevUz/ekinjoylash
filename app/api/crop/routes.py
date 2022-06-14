from flask import Blueprint, jsonify, request
from flask_login import current_user, login_remembered, login_required

from geoalchemy2.functions import ST_AsGeoJSON
from app.main.models import Crop, CropName, District, LandType, PlantingMethod, PlantingType, Province
from geomet import wkt
from app import db
import json
import pyproj
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
import shapely.ops as ops
from functools import partial
crop = Blueprint("crop",__name__, url_prefix='/crop')

@crop.route("/", methods=['POST', "GET"])
@login_required
def crop_main():
    if request.method == 'POST':
        try:
            data = request.get_json()
        except Exception as e:
            return jsonify({"error": str(e)})
        print(data)
        if not data:
            return jsonify({"error": "No data"}), 400
        crop_name = data.get('crop_name')
        crop_id = CropName.query.filter_by(code=crop_name).first().id
        geometry = data.get('geom')
        print(type(geometry), geometry)
        polygon = Polygon(geometry[0])
        geom_area = ops.transform(
            partial(
                pyproj.transform,
                pyproj.Proj(init='EPSG:4326'),
                pyproj.Proj(
                    proj='aea',
                    lat_1=polygon.bounds[1],
                    lat_2=polygon.bounds[3]
                )
            ),
            polygon)
        area = geom_area.area / 10000
        district_id = data.get('district_id')
        farm_tax_number = data.get('farm_tax_number')
        farm_cad_number = data.get('farm_cad_number')
        productivity = data.get('productivity')
        contour_number = data.get('contour_number')
        land_type_id = data.get('land_type_id')
        planting_type_id = data.get('planting_type_id')
        planting_method_id = data.get('planting_method_id')
        geometry = {'type': 'MultiPolygon', 'coordinates': [geometry]}
        try:

            geometry = wkt.dumps(geometry)
            geometry = "SRID=4326;%s"%geometry
            print(geometry)
        except Exception as E:
            return jsonify({'error': str(E), "key" : "geometry"}), 400
        
        if not District.query.get(district_id):
            return jsonify({'error': 'District not found'})
        
        crop = Crop(
            crop_id = crop_id,
            area = area,
            geometry = geometry,
            district_id = district_id,
            farm_tax_number = farm_tax_number,
            farm_cad_number = farm_cad_number,
            user_id = current_user.id,
            productivity = productivity,
            contour_number = contour_number,
            land_type_id = land_type_id,
            planting_type_id = planting_type_id,
            planting_method_id = planting_method_id
        )
        try:
            db.session.add(crop)
            db.session.commit()
        except Exception as E:
            print(E)
            db.session.rollback()
            return jsonify({'error': str(E)})
        return jsonify({'success': 'Crop added'})
    crops = db.session.query(ST_AsGeoJSON(Crop.geometry), Crop.crop_id, Crop.area, Crop.district_id, Crop.farm_tax_number, Crop.farm_cad_number, Crop.user_id, Crop.created_at, Crop.updated_at, Crop.ball_bonitet, Crop.contour_number).all()
    collection = {
        "type": "FeatureCollection",
        "features": []
        }
    for crop_geo, crop_name, crop_area, crop_district_id, crop_farm_tax_number, crop_farm_cad_number, user_id, created_at, updated_at, ball_bonitet, contour_number in crops:
        
        
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
            'farm_cad_number': crop_farm_cad_number,
            'user_id': user_id,
            'created_at': created_at,
            'updated_at': updated_at,
            'ball_bonitet': ball_bonitet,
            'contour_number': contour_number
        }
        collection['features'].append(feature)
    return jsonify(collection)

@crop.route('/getby_prefix')
def getby_prefix():
    prefix = request.args.get('prefix')
    if not prefix:
        return jsonify({'msg' : 'error: prefix not defined'}), 400
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
        return jsonify({'msg' : 'error: cadastral_number not defined'}), 400
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

@crop.route('/get-crop-geojson')
def get_crop_geojson():
    # crops = Crop.query.all()
    crop_names = CropName.query.all()
    crops = {}
    for crop_name in crop_names:
        crops[crop_name.code] = {
            'name': crop_name.name,
            'color': crop_name.color,
            'feature_collection': {
                'type': "FeatureCollection",
                'features': []
            }
        }
    crops_obj = db.session.query(Crop.crop_id, ST_AsGeoJSON(Crop.geometry), Crop.area, Crop.district_id, Crop.farm_tax_number, Crop.farm_cad_number, Crop.user_id, Crop.created_at, Crop.updated_at, Crop.productivity, Crop.contour_number, CropName.name, Crop.land_type_id, Crop.planting_type_id, Crop.planting_method_id)\
        .join(CropName, CropName.id == Crop.crop_id)\
        .join(LandType, LandType.id == Crop.land_type_id)\
        .join(PlantingType, PlantingType.id == Crop.planting_type_id)\
        .join(PlantingMethod, PlantingMethod.id == Crop.planting_method_id)\
        .filter(Crop.farm_cad_number==request.args.get('cadastral_number')).all()
    collection = {
        "type": "FeatureCollection",
        "features": []
    }
    for crop_id, crop_geo, crop_area, crop_district_id, crop_farm_tax_number, crop_farm_cad_number, user_id, created_at, updated_at, ball_bonitet, contour_number, cropname in crops_obj:

        feature = {
            "type": "Feature"
        }
        crop_geo = json.loads(crop_geo)
        feature['geometry'] = crop_geo
        feature['properties'] = {
            'area': crop_area,
            'district_id': crop_district_id,
            "cropname" : cropname,
            'farm_tax_number': crop_farm_tax_number,
            'farm_cad_number': crop_farm_cad_number,
            'user_id': user_id,
            'created_at': created_at,
            'updated_at': updated_at,
            'ball_bonitet': ball_bonitet,
            'contour_number': contour_number
        }
        code = CropName.query.get(int(crop_id)).code
        crops[code]['feature_collection']['features'].append(feature)
    return jsonify(crops)

@crop.route('/get-select-data')
def get_select_data():
    data = {
        'crops': [],
        'land_types': [],
        'planting_types': [],
        'planting_methods': [],
    }
    crops = CropName.query.all()
    for crop in crops:
        data['crops'].append({
            'id': crop.code,
            'name': crop.name,
        })
    land_types = LandType.query.all()
    for land_type in land_types:
        data['land_types'].append({
            'id': land_type.id,
            'name': land_type.name,
        })
    planting_types = PlantingType.query.all()
    for planting_type in planting_types:
        data['planting_types'].append({
            'id': planting_type.id,
            'name': planting_type.name,
        })
    planting_methods = PlantingMethod.query.all()
    for planting_method in planting_methods:
        data['planting_methods'].append({
            'id': planting_method.id,
            'name': planting_method.name,
        })

    return jsonify(data)

@crop.route("/calc-area", methods=['POST'])
def calc_area():
    if request.method == 'POST':
        try:
            data = request.get_json()
        except Exception as e:
            return jsonify({"error": str(e)})
        geometry = data.get('geom')
        print(type(geometry))
        polygon = Polygon(geometry[0])
        geom_area = ops.transform(
            partial(
                pyproj.transform,
                pyproj.Proj(init='EPSG:4326'),
                pyproj.Proj(
                    proj='aea',
                    lat_1=polygon.bounds[1],
                    lat_2=polygon.bounds[3]
                )
            ),
            polygon)
        area = geom_area.area / 10000
        return jsonify({"area": area})
    return jsonify({"error": "Method not allowed"}), 405
