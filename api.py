from flask import request
from flask_restful import Resource, fields, marshal_with

from custom_error import DataError, LogicError
from models import Log, Setting, Tracker, User, db


class User_api(Resource):
    # Api code for Login_db table

    output = {"user_id": fields.Integer, "username": fields.String,
              "password": fields.String}

    @marshal_with(output)
    def get(self, uname):
        u_obj = User.query.filter_by(username=uname).first()
        if u_obj is None:
            raise DataError(status_code=404)

        return u_obj, 200

    @marshal_with(output)
    def put(self, uname):
        u_obj = User.query.filter_by(username=uname).first()

        if u_obj is None:
            raise DataError(status_code=404)

        data = request.get_json()
        u_obj.password = data.get("password")

        if u_obj.password is None or type(u_obj.password) != str:
            raise LogicError(status_code=400, error_code="USER002",
                             error_msg="Password is required and should be string.")

        db.session.commit()
        return u_obj, 200

    def delete(self, uname):
        u_obj = User.query.filter_by(username=uname).first()

        if not u_obj:
            raise DataError(status_code=404)

        db.session.delete(u_obj)
        db.session.commit()
        return '', 200

    @marshal_with(output)
    def post(self):
        data = request.get_json()
        u_obj = User(username=data.get("username"),
                     password=data.get("password"))

        if u_obj.username is None or type(u_obj.username) != str:
            raise LogicError(status_code=400, error_code="USER001",
                             error_msg="Username is required and should be string.")
        if u_obj.password is None or type(u_obj.password) != str:
            raise LogicError(status_code=400, error_code="USER002",
                             error_msg="Password is required and should be string.")
        if User.query.filter_by(username=u_obj.username).first():
            raise DataError(status_code=409)

        db.session.add(u_obj)
        db.session.commit()
        return u_obj, 201


class Tracker_api(Resource):
    # Api code for Tracker table

    output = {"tracker_id": fields.Integer, "user_id": fields.Integer,
              "tracker_name": fields.String, "description": fields.String,
              "t_type": fields.String}

    @marshal_with(output)
    def get(self, uid):
        t_obj = Tracker.query.filter_by(user_id=uid).all()

        if t_obj is None:
            raise DataError(status_code=404)

        return t_obj, 200

    @marshal_with(output)
    def put(self, tid, uid):
        t_obj = Tracker.query.filter_by(tracker_id=tid, user_id=uid).first()

        if t_obj is None:
            raise DataError(status_code=404)

        data = request.get_json()
        t_obj.tracker_name = data.get("tracker_name")
        t_obj.description = data.get("description")

        if t_obj.tracker_name is None or type(t_obj.tracker_name) != str:
            raise LogicError(status_code=400, error_code="TRACKER002",
                             error_msg="Tracker name is required and should be string.")
        if t_obj.description is None or type(t_obj.description) != str:
            raise LogicError(status_code=400, error_code="TRACKER003",
                             error_msg="Tracker description is required and should be string.")

        db.session.commit()
        return t_obj, 200

    def delete(self, tid, uid):
        t_obj = Tracker.query.filter_by(tracker_id=tid, user_id=uid).first()

        if not t_obj:
            raise DataError(status_code=404)

        db.session.delete(t_obj)

        db.session.commit()
        return '', 200

    @marshal_with(output)
    def post(self, uid):
        data = request.get_json()
        t_obj = Tracker(user_id=uid,
                        tracker_name=data.get("tracker_name"),
                        description=data.get("description"),
                        t_type=data.get("t_type"))

        if User.query.filter_by(user_id=t_obj.user_id).first() is None:
            raise DataError(status_code=404)
        if t_obj.tracker_name is None or type(t_obj.tracker_name) != str:
            raise LogicError(status_code=400, error_code="TRACKER001",
                             error_msg="Tracker name is required and should be string.")
        if t_obj.description is None or type(t_obj.description) != str:
            raise LogicError(status_code=400, error_code="TRACKER002",
                             error_msg="Tracker description is required and should be string.")
        if t_obj.t_type is None or type(t_obj.t_type) != str:
            raise LogicError(status_code=400, error_code="TRACKER003",
                             error_msg="Tracker type is required.")

        if Tracker.query.filter_by(tracker_name=t_obj.tracker_name, user_id=uid).first():
            raise DataError(status_code=409)

        db.session.add(t_obj)
        db.session.commit()
        return t_obj, 201


class Log_api(Resource):
    # Api code for Log table

    output = {"logger_id": fields.Integer, "tracker_id": fields.Integer,
              "t_value": fields.Integer, "comments": fields.String,
              "timestamp": fields.String}

    def check(self, x):
        # format = YYYY-MM-DD hh:mm
        if '.' in x or x.count('-') != 2 or x.count(':') != 1 or x.count(' ') != 1:
            return False
        if not (0 < int(x[:4]) <= 9999) or not (1 <= int(x[5:7]) <= 12) or not (1 <= int(x[8:10]) <= 31):
            return False
        return True

    @marshal_with(output)
    def get(self, tid):
        l_obj = Log.query.filter_by(tracker_id=tid).all()

        if len(l_obj) == 0:
            raise DataError(status_code=404)

        return l_obj, 200

    @marshal_with(output)
    def put(self, tid, lid):
        l_obj = Log.query.filter_by(tracker_id=tid, logger_id=lid).first()

        if l_obj is None:
            raise DataError(status_code=404)

        data = request.get_json()
        l_obj.t_value = data.get('t_value')

        if l_obj.t_value is None or type(l_obj.t_value) is not int:
            raise LogicError(status_code=400, error_code="LOGGER001",
                             error_msg="Tracker value is required and should be integer.")

        if data.get('timestamp') is not None and self.check(data.get('timestamp')):
            l_obj.timestamp = data.get('timestamp')
        else:
            raise LogicError(status_code=400, error_code="LOGGER002",
                             error_msg="Timestamp must be in the format 'YYYY-MM-DD hh:mm:ss'")

        if data.get('comments') is not None and type(data.get('comments')) is not str:
            raise LogicError(status_code=400, error_code="LOGGER003",
                             error_msg="Comments must be string")
        elif data.get('comments') is not None:
            l_obj.comments = data.get('comments')

        db.session.commit()
        return l_obj, 200

    def delete(self, tid, lid):
        l_obj = Log.query.filter_by(tracker_id=tid, logger_id=lid).first()

        if not l_obj:
            raise DataError(status_code=404)

        db.session.delete(l_obj)
        db.session.commit()
        return '', 200

    @marshal_with(output)
    def post(self, tid):
        if Tracker.query.filter_by(tracker_id=tid).first() is None:
            raise DataError(status_code=404)

        data = request.get_json()
        l_obj = Log(tracker_id=tid, t_value=data.get('t_value'),
                    comments=data.get('comments'))

        if l_obj.t_value is None or type(l_obj.t_value) is not int:
            raise LogicError(status_code=400, error_code="LOGGER001",
                             error_msg="Tracker value is required and should be integer.")

        if data.get('timestamp') is not None and self.check(data.get('timestamp')):
            l_obj.timestamp = data.get('timestamp')
        elif data.get('timestamp') is not None:
            raise LogicError(status_code=400, error_code="LOGGER002",
                             error_msg="Timestamp must be in the format 'YYYY-MM-DD hh:mm'")

        if data.get('comments') is not None and type(data.get('comments')) is not str:
            raise LogicError(status_code=400, error_code="LOGGER003",
                             error_msg="Comments must be string")

        db.session.add(l_obj)
        db.session.commit()
        return l_obj, 201


class Setting_api(Resource):
    # Api code for MCQ table

    output = {"tracker_id": fields.Integer, "options": fields.String}

    @marshal_with(output)
    def get(self, tid):
        s_obj = Setting.query.filter_by(tracker_id=tid).first()

        if s_obj is None:
            raise DataError(status_code=404)

        return s_obj, 200

    def delete(self, tid):
        s_obj = Setting.query.filter_by(tracker_id=tid).first()

        if s_obj is None:
            raise DataError(status_code=404)

        db.session.delete(s_obj)
        db.session.commit()
        return '', 200

    @marshal_with(output)
    def post(self, tid):
        if Tracker.query.filter_by(tracker_id=tid).first() is None:
            raise DataError(status_code=404)
        if Setting.query.filter_by(tracker_id=tid).first():
            raise DataError(status_code=409)

        data = request.get_json()
        s_obj = Setting(tracker_id=tid, options=data.get('options'))

        db.session.add(s_obj)
        db.session.commit()
        return s_obj, 201
