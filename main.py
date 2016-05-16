#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import jinja2
import webapp2
import time
from model import Sporocilo

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


class MainHandler(BaseHandler):
    def get(self):
        sporocila = Sporocilo.query().order(Sporocilo.cas).fetch()
        parametri = {
            "sporocila": sporocila
        }
        return self.render_template("start.html", parametri)

    def post(self):
        tekst = self.request.get("tekst")
        uporabnik = self.request.get("uporabnik")
        napaka = False
        if uporabnik:
            sporocilo = Sporocilo(tekst=tekst, uporabnik=uporabnik)
            sporocilo.put()
            time.sleep(1)
        else:
            napaka = "Uporabnik ni logiran. Logiraj se :)"
        sporocila = Sporocilo.query().fetch()
        parametri = {
            "uporabnik": uporabnik,
            "sporocila": sporocila,
            "napaka" : napaka
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