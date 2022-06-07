import unittest, random, time,datetime
import json
from app import create_app, db

app = create_app('testconfig')
class TestAPI(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            db.drop_all()
            db.create_all()
    def tearDown(self):
        pass
    def test_main(self):
        with app.test_client() as client:
            res = client.get("/api/")
            d = {"msg": "Hello World"}
            self.assertEqual(res.status,"200 OK")
            self.assertEqual(json.loads(res.data),d)
    def test_district(self):
        with app.test_client() as client:
            res = client.get("/api/district")
            self.assertEqual(res.status,"302 FOUND")
    def test_crop(self):
        with app.test_client() as client:
            res = client.get("/api/crop/getby_prefix")
            self.assertEqual(res.status,"400 BAD REQUEST")
            d = {'msg' : 'error: prefix not defined'}
            self.assertEqual(json.loads(res.data),d)
    def test_crop_cad(self):
        with app.test_client() as client:
            res = client.get("/api/crop/getby_kadastr")
            self.assertEqual(res.status,"400 BAD REQUEST")
            d = {'msg' : 'error: cadastral_number not defined'}
            self.assertEqual(json.loads(res.data),d)
            
if __name__ == '__main__':
    unittest.main()