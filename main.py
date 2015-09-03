from google.appengine.ext import ndb
import webapp2
import jinja2
import os
import json

class Class_Name(ndb.Model):
    class_title = ndb.JsonProperty()
class Class_checking(ndb.Model):
    classC_array = ndb.JsonProperty()
class Graph_info(ndb.Model):
    graph_info = ndb.JsonProperty()

class gettingclasses(webapp2.RequestHandler):
    #homepage
    def get(self):
        #class_data lists current class added
        class_data = Class_checking.query().fetch()
        graph_info = Graph_info.query().fetch()
        graph_info_fetch = Graph_info.get_by_id('onlygraph')
        #if statement for normal printing
        #will have Graph_info information
        if graph_info:
            graph_info_fetch_onlyarray = graph_info_fetch.graph_info
            graph_info_send = json.dumps(graph_info_fetch_onlyarray)
            template_vars = {'class_data': class_data,'json_data': graph_info_send}
            template = jinja2_environment.get_template('template/enter.html')
            self.response.write(template.render(template_vars ))
        #if statement if just deleted the file
        #would return empty entity so can't send in NONETYPE
        else:
        #fetch the script to send to Javascript cola.js
            #if none, cola.js prints empty graph --> deletes the graph
            none = ''
            template_vars = {'class_data': class_data, 'json_data': none}
            template = jinja2_environment.get_template('template/enter.html')
            self.response.write(template.render(template_vars ))
    def post(self):
        classname = self.request.get('classname')
        prereq = self.request.get('prereq')
        new_dictionary = {}
        new_dictionary [classname] = prereq
        #stores Class_Name entities
        new_class = Class_Name(class_title = new_dictionary)
        new_class.put()
        new_array = []
        new_array.append(classname)
        new_array.append(prereq )
        class_data_JSON = json.dumps(new_array)
        #stores class_checking entities
        class_checking = Class_checking(classC_array = class_data_JSON)
        class_checking.put()
        continueForm = self.request.get('user_input')
        if continueForm == 'yes':
            self.redirect('/')
        else:
            #if no, compiles the script to Javascript
            self.redirect('/print')

class printingclasses(webapp2.RequestHandler):
        def get(self):
            #format to send to index.html
            Class_data = Class_Name.query().fetch()
            nodes_array = []
            links_array = []
            graph_array = []
            graph = {}
            counter_link = 1
            for a in Class_data:
                jsonprop = a.class_title
                extracted_before = json.dumps(jsonprop)
                extracted_output = json.loads(extracted_before)
                #check all the entities of Class_Name
                is_key_there = 0
                is_key_there_pre = 0
                for c_class, prereq in extracted_output.iteritems():
                # for each dictionary item in nodes array
                    for a in nodes_array:
                        #if the current class name is equal to the key
                        if a['id'] == c_class:
                            #set is_key_there to 1
                            is_key_there = 1
                        if a['id'] == prereq:
                            is_key_there_pre = 1
                #if is_key_there is 0, then never went to ^ if loop, so never had instance where class was in dictionary key
                if is_key_there == 0:
                    nodes_dict = {}
                    nodes_dict['id'] = c_class
                    nodes_array.append(nodes_dict)
                #need to make a prereq node if the name never esited before
                if is_key_there_pre == 0:
                    nodes_dict = {}
                    nodes_dict['id'] = prereq
                    nodes_array.append(nodes_dict)
                #javascript format
                links_dict = {}
                links_dict['id'] = counter_link
                links_dict['source'] = prereq
                links_dict['target'] = c_class
                links_array.append(links_dict)
                counter_link += 1
            #cola.js requried format
            graph['nodes'] = nodes_array
            graph['links'] = links_array
            updated_array = Graph_info(graph_info =graph, id = 'onlygraph')
            updated_array.put()
            #go back to homepage to let page stay 'same'
            self.redirect('/')

class deleteall(webapp2.RequestHandler):
    def post(self):
        #deletes entities of all classes
        class_data = Class_Name.query().fetch()
        class_data2 = Class_checking.query().fetch()
        print_data = Graph_info.query().fetch()
        for classx in class_data2:
            classx.key.delete()
        for classy in class_data:
            classy.key.delete()
        for data in print_data:
            data.key.delete()

        self.redirect('/')

jinja2_environment = jinja2.Environment(autoescape=True,
    extensions=['jinja2.ext.autoescape'],loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))


app = webapp2.WSGIApplication([
    ('/', gettingclasses),
    ('/print', printingclasses),
    ('/deleteall', deleteall)
], debug=True)
