# Builtin Imports
from http.server import HTTPServer, SimpleHTTPRequestHandler
from random import randint
import json
import hashlib
import binascii
import re
from datetime import datetime, timedelta

# Project Imports
import db_details as db
from create_db import engine

LOGIN_SESSION_TIMEOUT = 5
sessions = {}


class UserAPIHandler(SimpleHTTPRequestHandler):
    """ User Request handler using HTTP"""

    def do_GET(self):
        routes = {
            "/profile": self.profile
        }
        try:
            response = 200
            cookie_data = self.get_cookies(self.headers['Cookie'])
            if "sid" in cookie_data:
                self.user = cookie_data["sid"] if (cookie_data["sid"] in sessions) else False
            else:
                self.user = False
            content = routes[self.path]()
        except Exception as e:
            response = 404
            content = "Not Found"
        self.send_response(response)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(content, "utf-8"))
        return

    def profile(self):
        try:
            if self.user:
                if self.user in sessions:
                    username = sessions[self.user]['username']
                    session_validation = self.validate_login_session_time(self.user)
                    if not session_validation:
                        with engine.connect() as con:
                            ud = con.execute('SELECT username, email, phone from %s where username="%s"' % (
                            db.DB_TABLE, username))
                            user_data = ud.first()
                            data = {"username": user_data[0], "email": user_data[1], "phone_no": user_data[2]}
                            return json.dumps(data)
                    return session_validation
            return "Please login to view profile data"
        except Exception as err:
            return str(err)

    def validate_login_session_time(self, sid):
        session_time = sessions[sid]['session_time']
        if datetime.now() - timedelta(minutes=LOGIN_SESSION_TIMEOUT) > session_time:
            self.cookie = "sid="
            del sessions[self.user]
            return "Session TimedOut, Please log-in again to view your profile"
        return None

    def get_cookies(self, cookie_data):
        return dict(((cd.split("=")) for cd in cookie_data.split(";"))) \
            if cookie_data else {}

    def login(self, post_data):
        username = post_data.get('username', None)
        password = post_data.get('password', None)
        with engine.connect() as con:
            pwd = con.execute('SELECT password from %s where username="%s"' % (db.DB_TABLE, username))
            sp = pwd.first()
            if not sp:
                return "User does not exist", 400
            pwd_match = self.validate_password(sp[0], password)
            if pwd_match:
                sid = self.generate_sid()
                self.cookie = "sid={}".format(sid)
                sessions[sid] = {"username": username, "session_time": datetime.now()}
                return "User logged in successfully", 200
            else:
                return "Invalid Password", 400

    def validate_password(self, sp, pwd):
        """Verify a password against one provided by user"""
        salt = sp[:64]
        sp = sp[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha256',
                                      pwd.encode('utf-8'),
                                      salt.encode('ascii'),
                                      100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == sp

    def generate_sid(self):
        return "".join(str(randint(1, 9)) for _ in range(100))

    def logout(self):
        if not self.user:
            return "No User Logged In", 400
        self.cookie = "sid="
        del sessions[self.user]
        return "Logout Successful", 200

    def signup(self, post_data):
        required_fields = ['username', 'password', 'email', 'phone']
        missing_fields = []
        for field in required_fields:
            if not post_data.get(field, None):
                missing_fields.append(field)
        if missing_fields:
            return 'Missing fields - %s ' % (', '.join(missing_fields)), 400
        username = post_data.get('username', None)
        password = post_data.get('password', None)
        email = post_data.get('email', None)
        phone = post_data.get('phone_no', None)

        validation_errors = self.validate_signup_data(username, password, email, phone)
        if not validation_errors:
            with engine.connect() as con:
                usr = con.execute('SELECT password from %s where username="%s"' % (db.DB_TABLE, username))
                if usr.first():
                    return "User with username already exists", 200
                con.execute('INSERT INTO %s (username, password, email, phone) VALUES ("%s", "%s", "%s", "%s")' % (
                    db.DB_TABLE, username, password, email, phone))
                return "User Created Successfully", 200
        else:
            return str(validation_errors), 400

    def validate_signup_data(self, username, password, email, phone):
        """ Validate sign up data"""
        validation_errors = []
        if not re.match(r"[\w._]+\@[\w.]+", email):
            validation_errors.append('Not a valid email')
        if len(username) > 8:
            validation_errors.append('Length of username must not exceed 8 characters')
        if not re.match(r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[#_-])[A-Za-z\d#_-]{1,6}$", password):
            validation_errors.append('Password should not exceed 6 characters and it should contain one letter, '
                                     'one number')
        if not re.match(r"^(?:(?:\+|0{0,2})91(\s*[\-]\s*)?|[0]?)?[6789]\d{9}$", phone):
            validation_errors.append('Please Enter a Valid Phone Number')
        return ", ".join(validation_errors)


handler = UserAPIHandler
httpd = HTTPServer(("0.0.0.0", 8080), handler)
httpd.serve_forever()
