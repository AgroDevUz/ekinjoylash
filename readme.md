# Crop Schedule Application

![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/AgroDevUZ/ekinjoylash?color=green&label=Python&logo=python&logoColor=white&style=flat-square)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/AgroDevUz/ekinjoylash/flask?color=green&label=Flask&logo=flask&style=flat-square)

# Before deploy

## Flask-Admin
There were some problems with leaflet in Flask-Admin
After instalation Flask-Admin go

`your_env\Lib\site-packages\flask_admin\contrib\geoa\fields.py`

Search: `self.transform_srid = self.srid`

Before this add this lines: `self.web_srid = self.srid`

```python
if self.srid == -1:
    self.transform_srid = self.web_srid
else:
    self.web_srid = self.srid
    self.transform_srid = self.srid
```

## Config
Create copy of `app/config.example.py` and rename as `config.py`
