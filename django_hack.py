from google.appengine.ext import webapp

register = webapp.template.create_template_register()

def hash(h,key):
    if key in h:
        return h[key]
    else:
        return None

register.filter(hash)