import requests as rq
from flask import Flask, redirect, render_template, request
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from flask_restful import Api
from matplotlib import pyplot as plt

from api import Log_api, Setting_api, Tracker_api, User_api
from models import User, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_db.sqlite3'
db.init_app(app)
app.app_context().push()
api = Api(app)

login_manager = LoginManager(app)

api.add_resource(User_api, '/api/user', '/api/user/<string:uname>')
api.add_resource(Tracker_api, '/api/tracker/<int:tid>/<int:uid>',
                 '/api/tracker/<int:uid>')
api.add_resource(Log_api, '/api/log/<int:tid>', '/api/log/<int:tid>/<int:lid>')
api.add_resource(Setting_api, '/api/setting/<int:tid>')

app.config['SECRET_KEY'] = 'azaf'


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(user_id=user_id).first()


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html', error=0)
    else:
        uname = request.form['username']
        pasw = request.form['password']

        # check if username and password matches
        data = rq.get(request.url_root+'api/user/'+uname)
        if data.status_code == 200 and data.json().get('password') == pasw:
            login_user(User.query.filter_by(username=uname).first(),
                       remember=True)
            return redirect('/dashboard')
        else:
            return render_template('login.html', error=1)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/new_user', methods=["GET", "POST"])
def new_user():
    if request.method == 'GET':
        return render_template('new_user.html')
    else:
        # insert new user into DB
        form = {"username": request.form["username"],
                "password": request.form["password"]}
        rq.post(url=request.url_root+'api/user', json=form)
        return redirect('/')


@app.route('/dashboard')
@login_required
def dashboard():
    td = rq.get(url=request.url_root+'api/tracker/' +
                str(current_user.user_id)).json()
    return render_template('dashboard.html', username=current_user.username, trackers=td)


@app.route('/tracker_details/<int:tid>')
@login_required
def tracker_details(tid):
    tdl = rq.get(url=request.url_root+'api/tracker/' +
                 str(current_user.user_id)).json()
    td = None
    for i in tdl:
        if i.get('tracker_id') == tid:
            td = i
            break
    if td is None:
        return render_template('error.html', error_msg='Tracker not found')
    log = rq.get(url=request.url_root+'api/log/' + str(td.get('tracker_id')))

    if log.status_code == 200:

        plt.xlabel('Timestamp')
        plt.xticks(rotation=45)
        plt.tight_layout(pad=6)

        if td.get('t_type') == 'mcq':
            set_d = rq.get(url=request.url_root + 'api/setting/' +
                           str(tid)).json().get('options').split(',')

            ax = plt.gca()
            ax.set_yticks([i for i in range(len(set_d))],
                          labels=set_d)
            plt.scatter([L.get('timestamp') for L in log.json()],
                        [L.get('t_value')-1 for L in log.json()])
            plt.ylabel('Settings')
            plt.savefig('static/graph.jpg')
            plt.close()

            return render_template('tracker_details.html', t=td, logs=log.json(), options=set_d)
        else:

            plt.plot([L.get('timestamp') for L in log.json()],
                     [L.get('t_value') for L in log.json()])
            plt.ylabel('Value recorded')
            plt.savefig('static/graph.jpg')
            plt.close()

            return render_template('tracker_details.html', t=td, logs=log.json())
    else:
        return render_template('tracker_details.html', t=td)


@app.route('/new_tracker', methods=['GET', 'POST'])
@login_required
def new_tracker():
    if request.method == 'GET':
        return render_template('new_tracker.html', error=0)
    else:
        if request.form.get('type') == 'mcq':
            if len(request.form.get('settings')) == 0:
                return render_template('new_tracker.html', error=1)

        data = {"tracker_name": request.form.get('tname'), "description": request.form.get('description'),
                "t_type": request.form.get('type')}

        td = rq.post(url=request.url_root+'api/tracker/'+str(current_user.user_id),
                     json=data)
        if data['t_type'] == 'mcq':
            rq.post(url=request.url_root+'api/setting/'+str(td.json().get('tracker_id')),
                    json={'options': request.form.get('settings')})
        return redirect('/dashboard')


@app.route('/edit_tracker/<int:tid>', methods=['GET', 'POST'])
@login_required
def edit_tracker(tid):
    if request.method == 'GET':
        tdl = rq.get(url=request.url_root+'api/tracker/' +
                     str(current_user.user_id)).json()
        td = None
        for i in tdl:
            if i.get('tracker_id') == tid:
                td = i
                break
        if td == None:
            return render_template('error.html', error_msg='Tracker not found')

        set_d = ''
        if td.get('t_type') == 'mcq':
            set_d = rq.get(url=request.url_root + 'api/setting/' +
                           str(tid)).json().get('options')
        return render_template('edit_tracker.html', t=td, options=set_d)
    else:
        form = {"tracker_name": request.form.get('tname'),
                "description": request.form.get('description')}
        data = rq.put(url=request.url_root + 'api/tracker/' + str(tid) + '/'+str(current_user.user_id),
                      json=form)
        if data.status_code == 200:
            return redirect('/dashboard')
        else:
            return render_template('error.html', error_msg='Error occured while editing the tracker')


@app.route('/del_tracker/<int:tid>')
@login_required
def del_tracker(tid):
    data = rq.delete(url=request.url_root + 'api/tracker/' +
                     str(tid) + '/' + str(current_user.user_id))
    if data.status_code == 200:
        return redirect('/dashboard')
    else:
        return render_template('error.html', error_msg='Error occured while deleting the tracker')


@app.route('/new_log/<int:tid>', methods=['GET', 'POST'])
@login_required
def new_log(tid):
    if request.method == 'GET':
        tdl = rq.get(url=request.url_root+'api/tracker/' +
                     str(current_user.user_id)).json()
        for i in tdl:
            if i.get('tracker_id') == tid:
                td = i
                break
        if td.get('t_type') == 'mcq':
            set_d = rq.get(url=request.url_root + 'api/setting/' +
                           str(tid)).json().get('options').split(',')
            return render_template('new_log.html', t=td, options=set_d)
        else:
            return render_template('new_log.html', t=td)
    else:
        form = {"timestamp": request.form.get('timestamp').replace('T', ' '),
                "comments": request.form.get('comments'),
                "t_value": int(request.form.get('value'))}
        data = rq.post(url=request.url_root+'api/log/'+str(tid), json=form)
        if data.status_code == 201:
            return redirect('/tracker_details/'+str(tid))
        else:
            return render_template('error.html', error_msg="Error occured while logging the event")


@app.route('/edit_log/<int:tid>/<int:lid>', methods=['GET', 'POST'])
@login_required
def edit_log(tid, lid):
    if request.method == 'GET':
        log_l = rq.get(url=request.url_root+'api/log/'+str(tid))
        if log_l.status_code != 200:
            return render_template('error.html', error_msg="Invalid tracker/log id")

        log_l = log_l.json()
        for log in log_l:
            if log.get('logger_id') == lid:
                data = log

        set_d = rq.get(url=request.url_root + 'api/setting/' + str(tid))
        tdl = rq.get(url=request.url_root+'api/tracker/' +
                     str(current_user.user_id)).json()
        for i in tdl:
            if i.get('tracker_id') == tid:
                td = i
                break
        if set_d.status_code == 200:
            set_d = set_d.json().get('options').split(',')
            return render_template('edit_log.html', t=td, l=data, options=set_d)
        return render_template('edit_log.html', t=td, l=data)

    else:
        form = {"t_value": int(request.form.get('value')),
                "timestamp": request.form.get('timestamp').replace('T', ' '),
                "comments": request.form.get('comments')}
        log_l = rq.put(url=request.url_root +
                       'api/log/'+str(tid)+'/'+str(lid), json=form)
        if log_l.status_code == 200:
            return redirect('/tracker_details/'+str(tid))
        else:
            return render_template('error.html', error_msg="Error occured while logging the event")


@app.route('/del_log/<int:tid>/<int:lid>')
@login_required
def del_log(tid, lid):
    log_l = rq.delete(url=request.url_root + 'api/log/'+str(tid)+'/'+str(lid))
    if log_l.status_code == 200:
        return redirect('/tracker_details/'+str(tid))
    return render_template('error.html', error_msg="Error occured while deleting the log")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
