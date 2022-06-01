from flask import Blueprint, jsonify, request
import requests

kadastr = Blueprint("kadastr",__name__, url_prefix='/kadastr')

@kadastr.route('/getby_prefix')
def getby_prefix():
    prefix = request.args.get('prefix')
    if not prefix:
        return jsonify({'msg' : 'error: prefix not defined'})
    url = 'https://api.agro.uz/gis_bridge/eijara?prefix=%s'%(prefix)
    data = requests.get(url)
    return data.text

@kadastr.route('/getby_kadastr')
def getby_kadastr():
    prefix = request.args.get('prefix')
    if not prefix:
        return jsonify({'msg' : 'error: cadastral number not defined'})
    url = 'https://api.agro.uz/gis_bridge/eijara_all?prefix=%s'%(prefix)
    data = requests.get(url)
    return data.text