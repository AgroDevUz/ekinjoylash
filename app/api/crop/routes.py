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
    crops_obj = db.session.query(Crop.id, Crop.crop_id, ST_AsGeoJSON(Crop.geometry), Crop.area, Crop.district_id, Crop.farm_tax_number, Crop.farm_cad_number, Crop.user_id, Crop.created_at, Crop.updated_at, Crop.productivity, Crop.contour_number, CropName.name, LandType.name, PlantingType.name, PlantingMethod.name)\
        .join(CropName, CropName.id == Crop.crop_id)\
        .join(LandType, LandType.id == Crop.land_type_id)\
        .join(PlantingType, PlantingType.id == Crop.planting_type_id)\
        .join(PlantingMethod, PlantingMethod.id == Crop.planting_method_id)\
        .filter(Crop.farm_cad_number==request.args.get('cadastral_number')).all()
    collection = {
        "type": "FeatureCollection",
        "features": []
    }
    for id, crop_id, crop_geo, crop_area, crop_district_id, crop_farm_tax_number, crop_farm_cad_number, user_id, created_at, updated_at, ball_bonitet, contour_number, cropname, crop_land_type, crop_planting_type, crop_planting_method in crops_obj:

        feature = {
            "type": "Feature"
        }
        crop_geo = json.loads(crop_geo)
        feature['geometry'] = crop_geo
        feature['properties'] = {
            'id': id,
            'area': crop_area,
            'district_id': crop_district_id,
            "cropname" : cropname,
            'farm_tax_number': crop_farm_tax_number,
            'farm_cad_number': crop_farm_cad_number,
            'user_id': user_id,
            'created_at': created_at,
            'updated_at': updated_at,
            'ball_bonitet': ball_bonitet,
            'contour_number': contour_number,
            'land_type': crop_land_type,
            'planting_type': crop_planting_type,
            'planting_method': crop_planting_method
        }
        code = CropName.query.get(int(crop_id)).code
        crops[code]['feature_collection']['features'].append(feature)
    return jsonify(crops)

@crop.route('/get-select-data')
def get_select_data():
    data = {
        'crops': {
            'name': "Ekin nomi",
            'key': "crop_name",
            'items': []
        },
        'land_types': {
            'name': "Yer turi",
            'key': "land_type_id",
            'items': []
        },
        'planting_types': {
            'name': "Ekish turi",
            'key': "planting_type_id",
            'items': []
        },
        'planting_methods': {
            'name': "Ekish usuli",
            'key': "planting_method_id",
            'items': []
        },
    }
    crops = CropName.query.all()
    for crop in crops:
        data['crops']['items'].append({
            'id': crop.code,
            'name': crop.name,
        })
    land_types = LandType.query.all()
    for land_type in land_types:
        data['land_types']['items'].append({
            'id': land_type.id,
            'name': land_type.name,
        })
    planting_types = PlantingType.query.all()
    for planting_type in planting_types:
        data['planting_types']['items'].append({
            'id': planting_type.id,
            'name': planting_type.name,
        })
    planting_methods = PlantingMethod.query.all()
    for planting_method in planting_methods:
        data['planting_methods']['items'].append({
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


@crop.route("/get-crop-data-by-farmer", methods=['POST'])
def get_crop_data_by_farmer():
    if request.method == 'POST':
        try:
            req = request.get_json()
        except Exception as e:
            return jsonify({"error": str(e)})
        cadastral_number = req.get('cadastral_number')
        # crops = Crop.query.filter(Crop.farm_cad_number==cadastral_number).all()
        crops = db.session.query(Crop.area, Crop.contour_number, CropName.code, Crop.land_type_id, Crop.planting_type_id, Crop.planting_method_id)\
            .join(CropName, CropName.id == Crop.crop_id)\
            .filter(Crop.farm_cad_number==req.get('cadastral_number')).all()
        temp = {
            "contour_number": "",
            "jami": 0,
            "texnik": {
                "jami": 0,
                "guza": 0,
                "kannabis": 0,
                "tamaki": 0
            },
            "boshokli": {
                "jami": 0,
                "102010000": 0,
                "arpa": 0,
                "tritikale": 0
            },
            "sholi": 0,
            "dukkakli": {
                "jami": 0,
                "nuxat": 0,
                "mosh": 0,
                "loviya": 0,
                "qizil_loviya": 0,
                "yeryongoq": 0
            },
            "moyli": {
                "jami": 0,
                "soya": 0,
                "kungaboqar": 0,
                "kunjut": 0,
                "sedana": 0,
                "raps": 0
            },
            "sabzavot": 0,
            "poliz": {
                "jami": 0,
                "tarvuz": 0,
                "qovun": 0,
                "qovoq": 0
            },
            "107010000": 0,
            "ozuqa": {
                "jami": 0,
                "beda": 0,
                "xashaki_lavlagi": 0,
                "oq_joxori": 0,
                "makka_don": 0,
                "makka_silos": 0
            },
            "dorivor": 0,
            "supurgi": 0,
            "past_ball_bonitet": {
                "jami": 0,
                "intensiv": 0,
                "danakli": 0,
                "uruglik": 0,
                "yongoq": 0,
                "anor": 0,
                "zaytun": 0,
                "malina": 0,
                "uzumzorlar": 0,
                "tutzorlar": 0
            }
        }
        data = []
        for area, contour_number, code, land_type_id, planting_type_id, planting_method_id in crops:
            temp_ = temp
            temp_['contour_number'] = contour_number
            if str(code) in temp.keys():
                temp_[str(code)] += area
                temp_['jami'] += area
            else:
                for key, value in temp_.items():
                    if isinstance(value, dict):
                        if str(code) in value.keys():
                            temp_[key][str(code)] += area
                            temp_[key]['jami'] += area
            new_temp = []
            for key, value in temp_.items():
                if isinstance(value, dict):
                    for key_, value_ in value.items():
                        new_temp.append(value_)
                else:
                    new_temp.append(value)
            data.append(new_temp)
        return jsonify(data)
