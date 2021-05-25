# Builtin Imports
from http.server import HTTPServer, SimpleHTTPRequestHandler
from random import randint
import json
import hashlib
import binascii
import os
import re
from datetime import datetime, timedelta

# Third-Party Imports
from sqlalchemy import create_engine

# Project Imports
import db_details as db
from create_db import engine

LOGIN_SESSION_TIMEOUT = 5
sessions = {}


class UserAPIHandler(SimpleHTTPRequestHandler):

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

handler = UserAPIHandler
httpd = HTTPServer(("", 8080), handler)
httpd.serve_forever()
