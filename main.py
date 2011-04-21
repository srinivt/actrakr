#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import wsgiref.handlers
import os
import datetime
import logging

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class ListItem(db.Model):
  name = db.StringProperty(required=True);
  created_at = db.DateTimeProperty(required=True, auto_now_add=True);
  completed_at = db.DateTimeProperty();
  account = db.UserProperty(required=True);
  category = db.StringProperty()
  

  # Write list item accessors 
  # ListItem.pendingItems(user)
  # ListItem.doneItems(user)
  # ListItem.create(name, user)

def renderTemplate(handler, template_name, template_values = {}):
  path = os.path.join(os.path.dirname(__file__), 'templates')
  path = os.path.join(path, template_name + '.html')
  temp_dict = dict(template_values)
  if users.get_current_user():
    cu = users.get_current_user();
    temp_dict['current_user'] = cu.nickname()
    temp_dict['logout_url'] = users.create_logout_url("/")
    query = ListItem.all().filter('account =', cu)
    if handler.request.get('done') == '1':
      query = query.filter('completed_at != ', None)
    else:
      query = query.filter('completed_at = ', None)
    temp_dict['items'] = query.fetch(1000)

    ctxs = ["important-urgent", "important-not-urgent", "unimportant-urgent", "unimportant-not-urgent"]
    temp_dict['items_by_ctx'] = dict()
    for ctx in ctxs:
      q = ListItem.all().filter('account =', cu).filter('completed_at = ', None)
      temp_dict['items_by_ctx'][ctx] = q.filter('category = ', ctx).fetch(100)
	
	  # Fix ones with no category
    temp_dict['items_by_ctx']['important-urgent'].append(query.filter('category = ', None).fetch(100))
    temp_dict['ctx_list'] = ctxs

  handler.response.out.write(template.render(path, temp_dict))

def addNewItem(item, cat):
  if item:
    i = ListItem(name = item, 
      created_at = datetime.datetime.now(), 
      account=users.get_current_user(),
      category=cat)
    i.put()
    return i.key().id()
  else:
    return ''

def homePage(self):
  renderTemplate(self, 'home')
  
def addOrUpdateItem(self):
  if self.request.get('new_item'):
    return renderTemplate(self, 'home', {
      'new_item' : addNewItem(self.request.get('new_item'), self.request.get('category'))
      })
  elif self.request.get('id'):
    item = ListItem.get_by_id(int(self.request.get('id')))
    if (self.request.get('status') == '1'):  
      item.completed_at = datetime.datetime.now()
    elif self.request.get('name'):
      item.name = self.request.get('name')
    item.put()

class MainHandler(webapp.RequestHandler):
  
  def get(self):
    homePage(self)
    
  def post(self):
    if self.request.path == '/':
      addOrUpdateItem(self)
    elif self.request.path == '/delete':
      ListItem.get_by_id(int(self.request.get('id'))).delete()
      
def main():
  application = webapp.WSGIApplication([
                                          ('/', MainHandler), 
                                          ('/delete', MainHandler)
                                       ], debug=True)
  webapp.template.register_template_library('django_hack')
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()