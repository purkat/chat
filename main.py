#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import jinja2
import webapp2
import time
from model import Sporocilo

from google.appengine.api import users

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))

    def preveriUporabnika(self):
        user = users.get_current_user()
        if user:
            logiran = True
            url = users.create_logout_url('/')
        else:
            logiran = False
            url = users.create_login_url('/')
        return logiran, url, user

class MainHandler(BaseHandler):
    def get(self):
        logiran, url, user = self.preveriUporabnika()
        '''
        user = users.get_current_user()
        if user:
            logiran = True
            url = users.create_logout_url('/')
        else:
            logiran = False
            url = users.create_login_url('/')
        '''
        parametri = {
            "logiran": logiran,
            "url": url,
            "user": user}

        sporocila = Sporocilo.query().order(-Sporocilo.cas).fetch()
        parametri["sporocila"] = sporocila
        return self.render_template("start.html", parametri)

    def post(self):
        logiran, url, user = self.preveriUporabnika()
        #user = users.get_current_user()
        if logiran:
            #logiran = True
            #url = users.create_logout_url('/')

            tekst = self.request.get("tekst")
            sporocilo = Sporocilo(tekst=tekst, uporabnik=user.nickname())
            sporocilo.put()
            time.sleep(1)
            napaka = False
        else:
            #logiran = False
            #url = users.create_login_url('/')
            napaka = "Seja je potekla. Logiraj se ponovno :)"

        sporocila = Sporocilo.query(Sporocilo.uporabnik==user.nickname()).order(-Sporocilo.cas).fetch()
        parametri = {
            "logiran": logiran,
            "sporocila": sporocila,
            "user": user,
            "napaka": napaka,
            "url" : url
        }
        return self.render_template("start.html", parametri)


class LoginHandler(BaseHandler):
    def get(self):
        uporabnik = "user"
        sporocila = Sporocilo.query().fetch()
        parametri = {
            "uporabnik" : uporabnik,
            "sporocila" : sporocila
        }
        return self.render_template("start.html", parametri)

class LogoutHandler(BaseHandler):
    def get(self):
        return self.render_template("start.html")


app = webapp2.WSGIApplication(
    [
        webapp2.Route('/', MainHandler),
        webapp2.Route('/login', LoginHandler),
        webapp2.Route('/logout', LogoutHandler),
    ],
    debug=True)
