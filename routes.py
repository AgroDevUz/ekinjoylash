from flask import jsonify, request
from flask_login.utils import login_required
from forms import *
from geoalchemy2.functions import ST_AsGeoJSON
import json

PERMISSIONS = ['User can edit data', 'User can view data']

@app.route("/")
@login_required
def index():
    return render_template('pages/index.html')

@app.route("/map")
@login_required 
def map():
    dist = District.query.get(current_user.district_id)
    prc = Province.query.get(dist.region_id)
    return render_template('pages/map.html', data=str(prc.region_prefix + ':' + dist.district_prefix))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))

    return jsonify(links)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user is None or not user.check_password(form.password.data):
            print('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, form.remember_me.data)
        return redirect(url_for('index'))
    else:
        print(form.errors)
    return render_template('pages/login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login_page"))

#USER CRUD
@app.route("/add_user", methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    if request.method == 'GET':
        regions = Province.query.all()
        data = {
            "regions" : regions,
            "perms" : PERMISSIONS
        }
        return render_template('pages/user/add.html',data=data)
    else:
        u_login = request.form.get('login')
        u_pass = request.form.get('pass')
        conf = request.form.get('conf')
        u_dist = request.form.get('dist')
        u_perms = request.form.getlist('perms')
        print('perms', u_perms)
        print('CONF', conf)
        u = User(
            login = u_login,
            district_id = u_dist
        )
        if conf == u_pass:
            u.set_password(u_pass)
        db.session.add(u)
        db.session.commit()

        for i in PERMISSIONS:
            if i in u_perms:
                p = Permission(
                    user_id = u.id,
                    permission = i,
                    value = True
                )
            else:
                p = Permission(
                    user_id = u.id,
                    permission = i,
                    value = False
                )
            db.session.add(p)
            db.session.commit()

        return redirect(url_for('index'))

@app.route("/all_users", methods=['GET'])
@login_required
def all_users():
    users = User.query.filter(User.role != 'admin').all()
    
    data = {
        'users' : [x.format() for x in users],
        'perms' : PERMISSIONS
    }
    print('DATA', data)
    return render_template('pages/user/all.html', data=data)

@app.route("/user", methods=['GET'])
@login_required
def read_user():
    id = int(request.args.get('id'))

    u = User.query.get_or_404(id)
    p = Permission.query.filter_by(user_id=u.id).all()

    data = {
        'userdata' : u,
        'permissions' : p
    }

    return render_template('pages/user/user.html', data=data)

@app.route("/user/edit", methods=['GET', 'POST'])
@login_required
def edit_user():
    u_id = int(request.args.get('id'))
    if request.method == 'POST':
        u_login = request.form.get('login')
        u_pass = request.form.get('pass')
        old_pass = request.form.get('old_pass')
        u_dist = request.form.get('dist')
        u_perms = request.form.getlist('perms')

        u = User.query.get_or_404(u_id)
        if u_login:
            u.login = u_login
        if old_pass and u_pass:
            if u.check_password(old_pass):
                u.password = u.set_password(u_pass)
        if u_dist:
            u.dist = u_dist
        
        for i in PERMISSIONS:
            if i in u_perms:
                p = Permission.query.filter_by(user_id=u.id, permission=i).first()
                p.value = not bool(p.value)
        
        db.session.commit()
    
        return render_template('pages/user/edit.html')

@app.route("/user/delete", methods=['GET'])
@login_required
def delete_user():
    u_id = int(request.args.get('id'))

    u = User.query.get_or_404(u_id)

    db.session.delete(u)
    db.session.commit()
    
    return render_template('pages/user/delete.html')

@app.route("/user/reg_data", methods=['GET'])
@login_required
def reg_data():
    id = int(request.args.get('id'))

    u = User.query.get_or_404(id)
    d = District.query.get(u.district_id)
    p = Province.query.get(d.region_id)

    data = {
        'district' : d,
        'region' : p
    }

    return jsonify(data)

@app.route("/dist_data/<int:id>", methods=['GET'])
@login_required
def dist_data(id):
    d = District.query.filter(District.region_id == id).all()

    return jsonify([x.format() for x in d])

@app.route("/district")
def get_district():
    dist = District.query.get(current_user.district_id)
    prc = Province.query.get(dist.region_id)
    rest = db.session.query(ST_AsGeoJSON(District.geometry), District.nameru).filter(District.region_id==prc.id, District.district_prefix==dist.district_prefix).first()
    print(rest)
    geojson = rest[0]
    geojson = json.loads(geojson)
    geojson['attributes'] = {
        "nameru": rest[1] 
    }
    return jsonify(geojson)