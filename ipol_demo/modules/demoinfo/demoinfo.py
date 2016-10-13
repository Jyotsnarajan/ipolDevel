#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
DemoInfo: an information container module

All exposed WS return JSON with a status OK/KO, along with an error
description if that's the case.

To test the POST WS use the following:
        curl -d demo_id=1  -X POST 'http://127.0.0.1:9002/demo_get_authors_list'
        curl -d editorsdemoid=777 -d title='demo1' -d abstract='demoabstract' -d zipURL='http://prueba.com' -d active=1 -d stateID=1 -X POST 'http://127.0.0.1:9002/add_demo'
        or use Ffox plugin: Poster

"""

import cherrypy
import sys
import errno
import logging
import shutil
from math import ceil

from model import *
from tools import is_json, Payload,convert_str_to_bool

# GLOBAL VARS
LOGNAME = "demoinfo_log"


class DemoInfo(object):
    
    
    def __init__(self, configfile=None):

        # Cherrypy Conf
        if not configfile:
            sys.exit(1)
        else:
            cherrypy.config.update(configfile)

        status = self.check_config()
        if not status:
            sys.exit(1)

        self.logs_dir = cherrypy.config.get("logs_dir")
        self.mkdir_p(self.logs_dir)
        self.logger = self.init_logging()
                
        self.dl_extras_dir = cherrypy.config.get("dl_extras_dir")
        self.mkdir_p(self.dl_extras_dir)
                
        self.demoExtrasFilename = cherrypy.config.get("demoExtrasFilename")
                
        self.server_address=  'http://{0}:{1}'.format(
                                  cherrypy.config['server.socket_host'],
                                  cherrypy.config['server.socket_port'])

        # Database
        self.database_dir = cherrypy.config.get("database_dir")
        self.database_name = cherrypy.config.get("database_name")
        self.database_file = os.path.join(self.database_dir, self.database_name)
                
        # check if DB already exist
        if not os.path.isfile(self.database_name):

            statuscreateDb = createDb(self.database_name)
            if not statuscreateDb:
                print "DB not created correctly"
                sys.exit(1)

            statusinitDb = initDb(self.database_name)
            if not statusinitDb:
                print "DB not initialized correctly"
                sys.exit(1)
        else:
            print ("DB already exist and is initialized")

        # db testing purposes only!, better use unittests in test folder
        # testDb(self.database_name)

    @staticmethod
    def mkdir_p(path):
        """
        Implement the UNIX shell command "mkdir -p"
        with given path as parameter.
        """
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


    @staticmethod
    def check_config():
        """
        Check if needed datas exist correctly in the config of cherrypy.
        :rtype: bool
        """
        if not (cherrypy.config.has_key("database_dir") and
            cherrypy.config.has_key("database_name") and
            cherrypy.config.has_key("logs_dir") ):
            print "Missing elements in configuration file."
            return False
        else:
            return True


    def init_logging(self):
        """
        Initialize the error logs of the module.
        """
        logger = logging.getLogger(LOGNAME)
        logger.setLevel(logging.ERROR)
        handler = logging.FileHandler(os.path.join(self.logs_dir, 'error.log'))
        formatter = logging.Formatter('%(asctime)s ERROR in %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger


    def error_log(self, function_name, error):
        """
        Write an error log in the logs_dir defined in archive.conf
        """
        error_string = function_name + ": " + error
        self.logger.error(error_string)
 

    # DEMO
    @cherrypy.expose
    def default(self, attr):
        """
        Default method invoked when asked for non-existing service.
        """
        data = {}
        data["status"] = "KO"
        data["message"] = "Unknown service '{}'".format(attr)
        return json.dumps(data)
        
    def get_compressed_file_url(self, demo_id):
        """
        :param demo_id: demo id integer
        :return:        dictionary with the url or failure if file does not exist
        """
        data = {}
        data['status']= "OK"
        
        extras_folder =  os.path.join(self.dl_extras_dir, demo_id)
        compressed_file = os.path.join(extras_folder, self.demoExtrasFilename)
        
        try:
            if os.path.isfile(compressed_file):
                
                data['url_compressed_file'] = os.path.join(self.server_address,\
                                                   self.dl_extras_dir, \
                                                   demo_id,\
                                                   self.demoExtrasFilename)
                print data['url_compressed_file']
                data['code'] = "2"
            else:
                data['code'] = "1"

        except Exception as ex:
            data['status'] = 'KO'
            self.error_log("Failure in get_compressed_file_url ",str(ex))
        
        return data

    @cherrypy.expose
    def get_compressed_file_url_ws(self, demo_id):
        """
        WS for obtaining the url for the compressed file with the demoExtras
        """
        return json.dumps(self.get_compressed_file_url(demo_id))
        
    @cherrypy.expose
    def delete_compressed_file_ws(self,demo_id):
        """
        WS for deleting the compressed demo extra file of a demo
        """
        """
        :param demo_id: demo id integer
        :return status
        """
        data = {}
        data['status']= "OK"
        
        extras_folder =  os.path.join(self.dl_extras_dir, demo_id)
        
        try:
            shutil.rmtree(extras_folder)
        except Exception as ex:
            data['status']= "KO"
            self.error_log("Failure in delete_compressed_file_ws ",str(ex))
        return json.dumps(data)


    @cherrypy.expose
    def add_compressed_file_ws(self, demo_id,**kwargs):
        """
        WS for deleting the compressed demo extra file of a demo
        """
        """
        :param demo_id: demo id integer
        :return status
        """
        data = {}
        data['status'] = "OK"
        file = None
        try:
            file = kwargs['file']
            assert isinstance(file, cherrypy._cpreqbody.Part)
            extras_folder = os.path.join(self.dl_extras_dir, demo_id)
            if(file is not None):
                name, ext = os.path.splitext(file.filename)
                data['name'] = name
                data['ext'] = ext
                if not os.path.exists(extras_folder):
                    os.makedirs(extras_folder)
                print"hola"

                with open(file.filename, 'wb') as the_file:
                    shutil.copyfileobj(file.file, the_file)
            else:
                data['status'] = "KO"
        except Exception as ex:
            data['status'] = "KO"
            # data['error'] = ex

        return json.dumps(data)

  
    
    @cherrypy.expose
    def get_file_updated_state(self, demo_id, time_of_file_in_core, size_of_file_in_core):
        """
        :param demo_id:              demo id integer
        :param time_of_file_in_core  
        :return:        dictionary with the url or failure if file does not exist
        """
        print "Entering in get_file_updated_state"
        
        data = self.get_compressed_file_url(demo_id)
        
        #The compressed_file does not exist or KO
        if data['code'] == '1' or data['status'] == 'KO':
            return json.dumps(data)      
        
        try:
            compressed_file = os.path.join(self.dl_extras_dir, demo_id + "/" + self.demoExtrasFilename)
            file_state_in_demoinfo = os.stat(compressed_file)
            time_of_file_in_demoinfo = float(file_state_in_demoinfo.st_mtime) 
            size_of_file_in_demoinfo = float(file_state_in_demoinfo.st_size)
            time_of_file_in_core     = float(time_of_file_in_core)
            size_of_file_in_core     = float(size_of_file_in_core)
            data['code'] = "2"
            if (time_of_file_in_core >= time_of_file_in_demoinfo 
                and size_of_file_in_core == size_of_file_in_demoinfo):
                    data["code"] = "0"
        except Exception as ex:
            data['status'] = 'KO'
            self.error_log("Failure in get_file_updated_state ",str(ex))
            
        return json.dumps(data)

    #todo check its not usefull any more and delete...remeber deleting from test/demoinfotest.py
    @cherrypy.expose
    def demo_list(self):
        data = {}
        data["status"] = "KO"
        demo_list = list()
        try:
            conn = lite.connect(self.database_file)
            demo_dao = DemoDAO(conn)
            for d in demo_dao.list():
                # convert to Demo class to json
                demo_list.append(d.__dict__)
            data["demo_list"] = demo_list
            data["status"] = "OK"
            conn.close()
        except Exception as ex:
            error_string = "demoinfo demo_list error %s" % str(ex)
            print error_string
            self.error_log("demo_list", error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            # raise Exception
            data["error"] = error_string

        return json.dumps(data)


    @cherrypy.expose
    def demo_list_by_demoeditorid(self,demoeditorid_list):
        """
        demoeditorid_list is a list of demo_editor_id's IN JSON FORMAT, the unique id that identifies demos across all modules
        , given this list of ids, return the demo's metinfo
        """

        data = {}
        data["status"] = "KO"
        demo_list = list()

        #get json list into python object
        if is_json(demoeditorid_list):
            demoeditorid_list=json.loads(demoeditorid_list)
        else:
            raise ValueError("demoeditorid_list is not a valid JSON")

        try:
            conn = lite.connect(self.database_file)
            demo_dao = DemoDAO(conn)
            for d in demo_dao.list():
                #convert to Demo class to json
                if d.editorsdemoid in demoeditorid_list:
                    demo_list.append(d.__dict__)

            data["demo_list"] = demo_list
            data["status"] = "OK"
            conn.close()
        except Exception as ex:
            error_string = "demoinfo demo_list_by_demoeditorid error %s" % str(ex)
            print error_string
            self.error_log("demo_list_by_demoeditorid",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string

        return json.dumps(data)

    @cherrypy.expose
    def demo_list_pagination_and_filter(self,num_elements_page,page,qfilter=None):

        data = {}
        data["status"] = "KO"
        demo_list=list()
        next_page_number = None
        previous_page_number = None

        try:

            #validate params
            num_elements_page=int(num_elements_page)
            page=int(page)
            # print "demo_list_pagination_and_filter"
            # print "num_elements_page",num_elements_page
            # print "page",page
            # print "qfilter",qfilter
            # print

            conn = lite.connect(self.database_file)
            demo_dao = DemoDAO(conn)

            complete_demo_list = demo_dao.list()

            #filter or return all
            if qfilter:
                for demo in complete_demo_list:
                    #print "demo: ",demo
                    if qfilter.lower() in demo.title.lower() or qfilter.lower() in demo.abstract.lower() :
                        demo_list.append(demo.__dict__)
            else:
                #convert to Demo class to json
                for demo in complete_demo_list:
                    demo_list.append(demo.__dict__)

            # print
            # print " demo_list",demo_list
            # print
            # print " demo_list",len(demo_list)

            #if demos found, return pagination
            if demo_list:

                # [ToDo] Check if the first float cast r=float(.) is
                # really needed. It seems not, because the divisor is
                # already a float and thus the result must be a float.
                r = float(len(demo_list)) /  float(num_elements_page)

                totalpages = int(ceil(r))

                if page is None:
                    page = 1
                else:
                    if page < 1:
                        page = 1
                    elif page > totalpages:
                        page = totalpages

                next_page_number = page + 1
                if next_page_number > totalpages:
                    next_page_number = None

                previous_page_number = page - 1
                if previous_page_number <= 0 :
                    previous_page_number = None


                start_element= (page -1) * num_elements_page

                demo_list= demo_list[start_element:start_element+num_elements_page]

                # print " totalpages: ",totalpages
                # print " page: ",page
                # print " next_page_number: ",next_page_number
                # print " previous_page_number: ",previous_page_number
                # print " start_element: ",start_element
                # print " demo_list",demo_list

            else:
                totalpages = None


            data["demo_list"] = demo_list
            data["next_page_number"] = next_page_number
            data["number"] = totalpages
            data["previous_page_number"] = previous_page_number
            data["status"] = "OK"
            conn.close()
        except Exception as ex:
            error_string = "demoinfo demo_list_pagination_and_filter error %s" % str(ex)
            print error_string
            self.error_log("demo_list_pagination_and_filter",error_string)
            try:
                conn.close() # [ToDo] It seems that this should do in a
                # finally clause, not in a nested try. Check all similar
                # cases in this file.
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    def demo_get_authors_list(self,demo_id):
        data = {}
        data["status"] = "KO"
        author_list=list()
        try:
            conn = lite.connect(self.database_file)
            da_dao = DemoAuthorDAO(conn)

            for a in da_dao.read_demo_authors(int(demo_id)):
                #convert to Demo class to json
                author_list.append(a.__dict__)


            data["author_list"] = author_list
            data["status"] = "OK"
            conn.close()
        except Exception as ex:
            error_string = "demoinfo demo_get_authors_list error %s" % str(ex)
            print error_string
            self.error_log("demo_get_authors_list",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    def demo_get_available_authors_list(self,demo_id):
        # [ToDo] Convert all comments as the following into the Python
        # format for automated documentation

        # list all authors that are not currently assigned to a demo
        data = {}
        data["status"] = "KO"
        available_author_list=list()

        try:
            conn = lite.connect(self.database_file)

            # get all available authors
            a_dao=AuthorDAO(conn)
            list_of_all_authors=a_dao.list()

            # get the authors of this demo
            da_dao = DemoAuthorDAO(conn)
            list_of_authors_assigned_to_this_demo = da_dao.read_demo_authors(int(demo_id))

            for a in list_of_all_authors:
                if not a  in list_of_authors_assigned_to_this_demo:
                    #convert to Demo class to json
                    available_author_list.append(a.__dict__)


            data["author_list"] = available_author_list
            data["status"] = "OK"
            conn.close()
        except Exception as ex:
            error_string = "demoinfo demo_get_available_authors_list error %s" % str(ex)
            print error_string
            self.error_log("demo_get_available_authors_list",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    def demo_get_editors_list(self,demo_id):
        # [ToDo] Missing docstrings for a exposed method!
        # In general, all functions should be documented

        data = {}
        data["status"] = "KO"
        editor_list=list()
        try:
            conn = lite.connect(self.database_file)
            de_dao = DemoEditorDAO(conn)

            for e in de_dao.read_demo_editors(int(demo_id)):
                #convert to Demo class to json
                editor_list.append(e.__dict__)


            data["editor_list"] = editor_list
            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string = "demoinfo demo_get_editors_list error %s" % str(ex)
            print error_string
            self.error_log("demo_list",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    def demo_get_available_editors_list(self,demo_id):
        # lista all editors that are not currently assigned to a demo
        data = {}
        data["status"] = "KO"
        available_editor_list=list()

        try:
            conn = lite.connect(self.database_file)

            # get all available editors
            a_dao = EditorDAO(conn)
            list_of_all_editors = a_dao.list()

            # get the editors of this demo
            da_dao = DemoEditorDAO(conn)
            list_of_editors_assigned_to_this_demo = da_dao.read_demo_editors(int(demo_id))

            for a in list_of_all_editors:
                if not a  in list_of_editors_assigned_to_this_demo:
                    #convert to Demo class to json
                    available_editor_list.append(a.__dict__)

            data["editor_list"] = available_editor_list
            data["status"] = "OK"
            conn.close()
        except Exception as ex:
            error_string = "demoinfo demo_get_available_editors_list error %s" % str(ex)
            print error_string
            self.error_log("demo_get_available_editors_list",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    def demo_get_demodescriptions_list(self,demo_id,returnjsons=None):
        data = {}
        data["status"] = "KO"
        demodescription_list = list()
        try:
            #read all _demodescription for this demo
            conn = lite.connect(self.database_file)
            dd_dao=DemoDemoDescriptionDAO(conn)

            if returnjsons is None:
                demodescription_list = dd_dao.read_demo_demodescriptions(int(demo_id))
            else:
                demodescription_list = dd_dao.read_demo_demodescriptions(int(demo_id),returnjsons=returnjsons)


            data["demodescription_list"] = demodescription_list
            data["status"] = "OK"
            conn.close()

        except Exception as ex:
            error_string = "demoinfo demo_get_demodescriptions_list error %s" % str(ex)
            print error_string
            self.error_log("demo_get_demodescriptions_list",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    def read_demo(self, demoid):

        demo=None
        try:
            id =int(demoid)
            conn = lite.connect(self.database_file)
            dao = DemoDAO(conn)
            demo = dao.read(id)
            conn.close()

        except Exception as ex:
            error_string=("read_demo  e:%s"%(str(ex)))
            print (error_string)
            conn.close()

        return demo


    def read_demo_by_editordemoid(self, editor_demo_id):

        demo=None
        try:
            editordemoid =int(editor_demo_id)
            conn = lite.connect(self.database_file)
            dao = DemoDAO(conn)
            demo = dao.read_by_editordemoid(editordemoid)
            conn.close()

        except Exception as ex:
            error_string=("read_demo_by_editordemoid  e:%s"%(str(ex)))
            print (error_string)
            conn.close()

        return demo


    @cherrypy.expose
    def read_demo_metainfo(self, demoid):
        data = dict()
        data["status"] = "KO"
        try:

            demo = self.read_demo(demoid)
            if demo is None:
                raise ValueError("No demo retrieved for this id")
            # data["id"] = demo.id
            data["editorsdemoid"] = demo.editorsdemoid
            data["title"] = demo.title
            data["abstract"] = demo.abstract
            data["zipURL"] = demo.zipURL
            data["active"] = demo.active
            data["stateID"] = demo.stateID
            data["creation"] = demo.creation
            data["modification"] = demo.modification
            data["status"] = "OK"

        except Exception as ex:
            error_string = "demoinfo read_demo_metainfo error %s" % str(ex)
            print error_string
            self.error_log("read_demo_metainfo",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string

        return json.dumps(data)


    @cherrypy.expose
    def read_demo_metainfo_by_editordemoid(self, editordemoid):
        data = dict()
        data["status"] = "KO"

        try:

            demo = self.read_demo_by_editordemoid(editordemoid)
            if demo is None:
                raise ValueError("No demo retrieved for this id")

            #data["id"] = demo.id
            data["editorsdemoid"] = demo.editorsdemoid
            data["title"] = demo.title
            data["abstract"] = demo.abstract
            data["zipURL"] = demo.zipURL
            data["active"] = demo.active
            data["stateID"] = demo.stateID
            data["creation"] = demo.creation
            data["modification"] = demo.modification
            data["status"] = "OK"

        except Exception as ex:
            error_string = "demoinfo read_demo_metainfo_by_editordemoid error %s" % str(ex)
            print error_string
            self.error_log("read_demo_metainfo_by_editordemoid",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string

        return json.dumps(data)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def add_demo(self, editorsdemoid, title, abstract, zipURL, active, stateID, demodescriptionID=None, demodescriptionJson=None):
        """
        Allows you to create a demo:
        - only creating the demo
        - creating the demo and assigning an existing ddl (with id demodescriptionID) to it
        - create the demo and create a ddl , whith the json passed by param (demodescriptionJson)
        """
        data = {}
        data["status"] = "KO"

        try:

            active = convert_str_to_bool(active)
            #print "active", active, type(active)

            conn = lite.connect(self.database_file)
            dao = DemoDAO(conn)

            if demodescriptionJson:
                # print "demodescriptionJson"
                #creates a demodescription and asigns it to demo
                dddao = DemoDescriptionDAO(conn)
                demodescriptionID = dddao.add(demodescriptionJson)
                d = Demo(int(editorsdemoid), title, abstract, zipURL, int(active), int(stateID))
                editorsdemoid=dao.add(d)
                dddao=DemoDemoDescriptionDAO(conn)
                dddao.add(int(editorsdemoid),int(demodescriptionID))

            elif demodescriptionID:
                # print "demodescriptionID"
                #asigns to demo an existing demodescription
                d = Demo(int(editorsdemoid), title, abstract, zipURL, int(active), int(stateID))
                editorsdemoid = dao.add(d)
                ddddao=DemoDemoDescriptionDAO(conn)
                ddddao.add(int(editorsdemoid),int(demodescriptionID))

            else:
                #demo created without demodescription
                #careful with Demo init method's validation!
                d = Demo(editorsdemoid=int(editorsdemoid), title=title, abstract=abstract, zipurl=zipURL, active=int(active), stateid=int(stateID))
                demoid = dao.add(d)

            conn.close()



            data["status"] = "OK"
            data["demoid"] = demoid
        except Exception as ex:
            error_string = " demoinfo add_demo error %s" % str(ex)
            print error_string
            self.error_log("add_demo",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string

        return json.dumps(data)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def delete_demo(self,demo_id,hard_delete = False):
        data = {}
        data["status"] = "KO"

        try:

            conn = lite.connect(self.database_file)

            # hard_delete must be converted to int!
            try:
                hard_delete=int(hard_delete)
                if hard_delete not in [0,1]:
                    msg=" hard_delete param error"
                    raise ValueError(msg)
            except Exception as ex:
                if hard_delete =='False':
                    hard_delete=0
                elif hard_delete =='True':
                    hard_delete=1
                else:
                    msg=" hard_delete param error"
                    raise ValueError(msg)


            #print "hard_delete",hard_delete
            if hard_delete:

                demo_dao = DemoDAO(conn)
                #read demo
                demo = demo_dao.read(int(demo_id))

                dd_dao = DemoDemoDescriptionDAO(conn)
                print "demo id", demo_id
                print "demo", demo.editorsdemoid
                #read demo_demodescription
                # demo_ddl_list = dd_dao.read_demo_demodescriptions(int(demo_id))
                # print
                # print "demo_ddl_list",demo_ddl_list
                # print
                # print "demoid to delete ", demo_id
                # print
                # print "demo: ",demo.__dict__

                #delete demo decription history borra ddl id 3
                #d_dd con id 2 , y demoid=2,demodescpid 3 deberia no estar
                dd_dao.delete_all_demodescriptions_for_demo(int(demo_id))
                #delete demo, and delete on cascade demodemodescription
                demo_dao.delete(int(demo_id))
                data["status"] = "OK"

            else:
                # do not delete, activate /deactivate
                demo_dao = DemoDAO(conn)
                demo_dao.set_active_flag(int(demo_id),int(False))
                data["status"] = "OK"

            conn.close()

        except Exception as ex:
            error_string = "demoinfo delete_demo error %s" % str(ex)
            print error_string
            self.error_log("delete_demo",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string

        return json.dumps(data)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def update_demo(self,demo,old_editor_demoid):
        data = {}
        data["status"] = "KO"
        #get payload from json object
        p = Payload(demo)
        # print
        # print "update_demo"
        # print "p.active" ,p.active
        # print "p " ,p
        # print "p type" ,type(p)
        # print
        #convert payload to Demo object
        if hasattr(p, 'creation'):
            #update creatio ndate

            d = Demo(p.editorsdemoid, p.title, p.abstract, p.zipURL, p.active, p.stateID, p.creation)
        else:
            d = Demo(p.editorsdemoid, p.title, p.abstract, p.zipURL, p.active, p.stateID)

        #update Demo
        try:


            conn = lite.connect(self.database_file)
            dao = DemoDAO(conn)
            dao.update(d,int(old_editor_demoid))
            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string=(" demoinfo update_demo error %s"%(str(ex)))
            print (error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string


        return json.dumps(data)


    # AUTHOR


    #todo check its not usefull any more and delete...
    @cherrypy.expose
    def author_list(self):
        data = {}
        data["status"] = "KO"
        author_list=list()
        try:
            conn = lite.connect(self.database_file)
            author_dao = AuthorDAO(conn)
            for a in author_dao.list():
                #convert to Demo class to json
                author_list.append(a.__dict__)


            data["author_list"] = author_list
            data["status"] = "OK"
            conn.close()
        except Exception as ex:
            error_string = "demoinfo author_list error %s" % str(ex)
            print error_string
            self.error_log("author_list",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    def author_list_pagination_and_filter(self,num_elements_page,page,qfilter=None):

        data = {}
        data["status"] = "KO"
        author_list=list()
        next_page_number = None
        previous_page_number = None

        try:

            #validate params
            num_elements_page=int(num_elements_page)
            page = int(page)

            conn = lite.connect(self.database_file)
            author_dao = AuthorDAO(conn)

            complete_author_list = author_dao.list()

            #filter or return all
            if qfilter:
                for a in complete_author_list:
                    #print "demo: ",demo
                    if qfilter.lower() in a.name.lower() or qfilter.lower() in a.mail.lower() :
                        author_list.append(a.__dict__)
            else:
                #convert to Demo class to json
                for a in complete_author_list:
                    author_list.append(a.__dict__)

            #if demos found, return pagination
            if author_list:

                r=float(len(author_list))/ float(num_elements_page)

                totalpages = int(ceil(r))

                if page is None:
                    page = 1
                else:
                    if page < 1:
                        page = 1
                    elif page > totalpages:
                        page = totalpages

                next_page_number = page + 1
                if next_page_number > totalpages:
                    next_page_number = None

                previous_page_number = page - 1
                if previous_page_number <= 0 :
                    previous_page_number = None

                start_element= (page -1) * num_elements_page
                author_list= author_list[ start_element:start_element+num_elements_page ]
            else:
                totalpages = None


            data["author_list"] = author_list
            data["next_page_number"] = next_page_number
            data["number"] = totalpages
            data["previous_page_number"] = previous_page_number
            data["status"] = "OK"
            conn.close()
        except Exception as ex:
            error_string = "demoinfo author_list_pagination_and_filter error %s" % str(ex)
            print error_string
            self.error_log("author_list_pagination_and_filter",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string

        return json.dumps(data)


    @cherrypy.expose
    def read_author(self, authorid):
        data = dict()
        data["status"] = "KO"

        try:

            author=None
            try:
                authorid = int(authorid)
                conn = lite.connect(self.database_file)
                dao = AuthorDAO(conn)
                author = dao.read(authorid)
                conn.close()
            except Exception as ex:
                error_string=("read_author  e:%s"%(str(ex)))
                print error_string
                #raise ValueError(error_string)

            if author is None:
                raise ValueError("No author retrieved for this id")

            data["id"] = author.id
            data["name"] = author.name
            data["mail"] = author.mail
            data["creation"] = author.creation
            data["status"] = "OK"

        except Exception as ex:
            error_string = "demoinfo read_author error %s" % str(ex)
            print error_string
            self.error_log("read_author",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string

        return json.dumps(data)


    @cherrypy.expose
    def author_get_demos_list(self,author_id):
        data = {}
        data["status"] = "KO"
        demo_list=list()
        try:
            conn = lite.connect(self.database_file)
            da_dao = DemoAuthorDAO(conn)

            for d in da_dao.read_author_demos(int(author_id)):
                #convert to Demo class to json
                demo_list.append(d.__dict__)


            data["demo_list"] = demo_list
            conn.close()
            data["status"] = "OK"

        except Exception as ex:
            error_string = "demoinfo author_get_demos_list error %s" % str(ex)
            print error_string
            self.error_log("author_get_demos_list",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST','GET']) #allow only post
    def add_author(self,name, mail):
        data = {}
        data["status"] = "KO"
        try:
            a = Author( name, mail)
            conn = lite.connect(self.database_file)
            dao = AuthorDAO(conn)
            id=dao.add(a)
            conn.close()
            data["status"] = "OK"
            data["authorid"] = id
        except Exception as ex:
            error_string = "demoinfo add_author error %s" % str(ex)
            print error_string
            self.error_log("add_author",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def add_author_to_demo(self,demo_id ,author_id):
        data = {}
        data["status"] = "KO"
        try:
            conn = lite.connect(self.database_file)
            dao = DemoAuthorDAO(conn)
            dao.add(int(demo_id),int(author_id))
            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string = "demoinfo add_author_to_demo error %s" % str(ex)
            print error_string
            self.error_log("add_author_to_demo",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def remove_author_from_demo(self,demo_id ,author_id):
        data = {}
        data["status"] = "KO"
        try:
            conn = lite.connect(self.database_file)
            dao = DemoAuthorDAO(conn)
            dao.remove_author_from_demo(int(demo_id),int(author_id))
            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string = "demoinfo remove_author_from_demo error %s" % str(ex)
            print error_string
            self.error_log("remove_author_from_demo",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def remove_author(self,author_id):
        #deletes the author, and its relation with demos
        data = {}
        data["status"] = "KO"
        try:

            authorid=int(author_id)

            conn = lite.connect(self.database_file)
            dadao = DemoAuthorDAO(conn)
            #deletes the author relation with its demos
            demolist = dadao.read_author_demos(authorid)
            if demolist:
                #remove author from demos
                for demo in demolist:
                    dadao.remove_author_from_demo(demo.editorsdemoid,authorid)

            #deletes the author
            adao = AuthorDAO(conn)
            adao.delete(authorid)

            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string = "demoinfo remove_author error %s" % str(ex)
            print error_string
            self.error_log("remove_author",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def update_author(self,author):
        data = {}
        data["status"] = "KO"
        #get payload from json object
        # #{"mail": "authoremail1@gmail.com", "creation": "2015-12-03 20:53:07", "id": 1, "name": "Author Name1"}
        p = Payload(author)

        #convert payload to Author object
        if hasattr(p,'creation'):
            a=Author(p.name,p.mail,p.id,p.creation)
        else:
            a=Author(p.name,p.mail,p.id)

        #update Author
        try:

            conn = lite.connect(self.database_file)
            dao = AuthorDAO(conn)
            dao.update(a)
            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string = "demoinfo update_author error %s" % str(ex)
            print error_string
            self.error_log("update_author",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    # EDITOR


    @cherrypy.expose
    def editor_list(self):
        data = {}
        data["status"] = "KO"
        editor_list=list()
        try:
            conn = lite.connect(self.database_file)
            editor_dao = EditorDAO(conn)
            for e in editor_dao.list():
                #convert to Demo class to json
                editor_list.append(e.__dict__)


            data["editor_list"] = editor_list
            data["status"] = "OK"
            conn.close()
        except Exception as ex:
            error_string = "demoinfo editor_list error %s" % str(ex)
            print error_string
            self.error_log("editor_list",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    def editor_list_pagination_and_filter(self,num_elements_page,page,qfilter=None):

        data = {}
        data["status"] = "KO"
        editor_list=list()
        next_page_number = None
        previous_page_number = None

        try:

            #validate params
            num_elements_page=int(num_elements_page)
            page = int(page)

            conn = lite.connect(self.database_file)
            editor_dao = EditorDAO(conn)

            complete_editor_list = editor_dao.list()

            #filter or return all
            if qfilter:
                for a in complete_editor_list:
                    #print "demo: ",demo
                    if qfilter.lower() in a.name.lower() or qfilter.lower() in a.mail.lower() :
                        editor_list.append(a.__dict__)
            else:
                #convert to Demo class to json
                for a in complete_editor_list:
                    editor_list.append(a.__dict__)

            #if demos found, return pagination
            if editor_list:

                r=float(len(editor_list))/ float(num_elements_page)

                totalpages = int(ceil(r))

                if page is None:
                    page = 1
                else:
                    if page < 1:
                        page = 1
                    elif page > totalpages:
                        page = totalpages

                next_page_number = page + 1
                if next_page_number > totalpages:
                    next_page_number = None

                previous_page_number = page - 1
                if previous_page_number <= 0 :
                    previous_page_number = None

                start_element= (page -1) * num_elements_page
                editor_list= editor_list[ start_element:start_element+num_elements_page ]
            else:
                totalpages = None


            data["editor_list"] = editor_list
            data["next_page_number"] = next_page_number
            data["number"] = totalpages
            data["previous_page_number"] = previous_page_number
            data["status"] = "OK"
            conn.close()
        except Exception as ex:
            error_string = "demoinfo editor_list_pagination_and_filter error %s" % str(ex)
            print error_string
            self.error_log("editor_list_pagination_and_filter",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string

        return json.dumps(data)


    @cherrypy.expose
    def editor_get_demos_list(self,editor_id):
        data = {}
        data["status"] = "KO"
        demo_list = list()
        try:
            conn = lite.connect(self.database_file)
            de_dao = DemoEditorDAO(conn)

            for d in de_dao.read_editor_demos(int(editor_id)):
                #convert to Demo class to json
                demo_list.append(d.__dict__)

            data["demo_list"] = demo_list
            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string = "demoinfo editor_get_demos_list error %s" % str(ex)
            print error_string
            self.error_log("editor_get_demos_list",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    def read_editor(self, editorid):
        data = dict()
        data["status"] = "KO"

        try:
            editor = None
            try:
                editorid = int(editorid)
                conn = lite.connect(self.database_file)
                dao = EditorDAO(conn)
                editor = dao.read(editorid)
                conn.close()
            except Exception as ex:
                error_string=("read_editor  e:%s"%(str(ex)))
                print error_string
                #raise ValueError(error_string)

            if editor is None:
                raise ValueError("No editor retrieved for this id")

            data["id"] = editor.id
            data["name"] = editor.name
            data["mail"] = editor.mail
            data["creation"] = editor.creation
            data["active"] = editor.active
            data["status"] = "OK"

        except Exception as ex:
            error_string = "demoinfo read_editor error %s" % str(ex)
            print error_string
            self.error_log("read_editor",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string

        return json.dumps(data)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def add_editor(self,name, mail):
        data = {}
        data["status"] = "KO"
        try:
            e = Editor( name, mail)
            conn = lite.connect(self.database_file)
            dao = EditorDAO(conn)
            id = dao.add(e)
            conn.close()
            data["status"] = "OK"
            data["editorid"] = id
        except Exception as ex:
            error_string = "demoinfo add_editor error %s" % str(ex)
            print error_string
            self.error_log("add_editor",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def add_editor_to_demo(self,demo_id ,editor_id):
        data = {}
        data["status"] = "KO"
        try:
            conn = lite.connect(self.database_file)
            dao = DemoEditorDAO(conn)
            dao.add(int(demo_id),int(editor_id))
            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string = "demoinfo add_editor_to_demo error %s" % str(ex)
            print error_string
            self.error_log("add_editor_to_demo",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def remove_editor_from_demo(self,demo_id ,editor_id):
        data = {}
        data["status"] = "KO"
        try:
            conn = lite.connect(self.database_file)
            dao = DemoEditorDAO(conn)
            dao.remove_editor_from_demo(int(demo_id),int(editor_id))
            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string = "demoinfo remove_editor_from_demo error %s" % str(ex)
            print error_string
            self.error_log("remove_editor_from_demo",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def remove_editor(self,editor_id):
        #deletes the editor, and its relation with demos
        data = {}
        data["status"] = "KO"
        try:

            editorid=int(editor_id)
            conn = lite.connect(self.database_file)
            dedao = DemoEditorDAO(conn)
            #deletes the author relation with its demos
            demolist = dedao.read_editor_demos(editorid)
            if demolist:
                #remove editor from demos
                for demo in demolist:
                    dedao.remove_editor_from_demo(demo.editorsdemoid,editorid)
            #deletes the editor
            edao = EditorDAO(conn)
            edao.delete(editorid)
            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string = "demoinfo remove_editor error %s" % str(ex)
            print error_string
            self.error_log("remove_editor",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def update_editor(self,editor):
        data = {}
        data["status"] = "KO"
        #get payload from json object
        p = Payload(editor)
        #convert payload to Editor object
        if hasattr(p,'active'):
            if hasattr(p,'creation'):
                e= Editor(p.name,p.mail,p.id,p.active,p.creation)
            else:
                e = Editor(p.name,p.mail,p.id,p.active)
        else:
            if hasattr(p,'creation'):
                #todo, if active is not provideed, we suppose its True
                e= Editor(p.name,p.mail,id=p.id,active=1,creation=p.creation)
            else:
                e = Editor(p.name,p.mail,id=p.id)

        #update Editor
        try:
            conn = lite.connect(self.database_file)
            dao = EditorDAO(conn)
            dao.update(e)
            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string = "demoinfo update_editor error %s" % str(ex)
            print error_string
            self.error_log("update_editor",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    # DDL


    @cherrypy.expose
    def read_demo_description(self, demodescriptionID):
        data = {}
        data["status"] = "KO"
        data["demo_description"] = None
        try:
            id =int(demodescriptionID)
            #print "---- read_demo_description"
            conn = lite.connect(self.database_file)
            dao = DemoDescriptionDAO(conn)

            ddl,isproduction = dao.read(id)
            # print type(ddl)
            # print ddl
            # print
            # ddl is stored in db as blob, must be converted to str before dumping
            # calling this ws from CP, dao.read(id) is buffer
            # calling directly ths ws from python code is unicode.
            # because data is serialized by request lib
            ddl = str(ddl)
            # print type(ddl)
            # print ddl

            data["demo_description"] = ddl
            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string = "demoinfo read_demo_description error %s" % str(ex)
            print error_string
            self.error_log("read_demo_description",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string

        return json.dumps(data)

    @cherrypy.expose
    def read_last_demodescription_from_demo(self,demo_id,returnjsons=None):
        data = {}
        data["status"] = "KO"
        data["last_demodescription"] = None
        try:
            #read all _demodescription for this demo
            conn = lite.connect(self.database_file)
            dd_dao = DemoDemoDescriptionDAO(conn)

            if returnjsons is None:
                last_demodescription = dd_dao.read_last_demodescription_from_demo(int(demo_id))
            else:
                last_demodescription= dd_dao.read_last_demodescription_from_demo(int(demo_id),returnjsons=returnjsons)

            data["last_demodescription"] = last_demodescription
            data["status"] = "OK"
            conn.close()

        except Exception as ex:
            error_string = "demoinfo read_last_demodescription_from_demo error %s" % str(ex)
            print error_string
            self.error_log("read_last_demodescription_from_demo",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    #todo check its not usefull any more and delete...
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def add_demodescription_to_demo(self,demo_id, demodescription_id):
        data = {}
        data["status"] = "KO"
        try:
            conn = lite.connect(self.database_file)
            dao = DemoDemoDescriptionDAO(conn)
            dao.add(int(demo_id),int(demodescription_id))
            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string = "demoinfo add_demodescription_to_demo error %s" % str(ex)
            print error_string
            self.error_log("add_demodescription_to_demo",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST']) #allow only post
    def save_demo_description(self,demoid):
        #def save_demo_description(self, demoid):
        #recieves a valid json as a string AS POST DATA
        #http://stackoverflow.com/questions/3743769/how-to-receive-json-in-a-post-request-in-cherrypy

        inproduction = 1 #This shouldn't be necessary in the demoDescription and should be removed
        data = {}
        data["status"] = "KO"

        cl = cherrypy.request.headers['Content-Length']
        demojson = cherrypy.request.body.read(int(cl))

        if not is_json(demojson):
            print
            print "save_demo_description demojson is not a valid json "
            print "+++++ demojson: ",demojson
            print "+++++ demojson type: ",type(demojson)
            raise Exception

        try:
            conn = lite.connect(self.database_file)
            demo_dao = DemoDAO(conn)
            state = demo_dao.read(int(demoid)).stateID
            print "El estado de esta demo es: ", state
            if (state==3): #If the demo is inactive the DDL is overwritten
                dao = DemoDemoDescriptionDAO(conn)
                demodescription_id = dao.read_last_demodescription_from_demo(int(demoid))['demodescriptionId']
                dao = DemoDescriptionDAO(conn)
                dao.update(int(demodescription_id),demojson)

            else:           #Otherwise it's create a new one
                dao = DemoDescriptionDAO(conn)
                demodescription_id = dao.add(demojson,inproduction=inproduction)
                dao = DemoDemoDescriptionDAO(conn)
                dao.add(int(demoid),int(demodescription_id))

            data["added_to_demo_id"] = demoid

            conn.close()
            #return id
            data["status"] = "OK"

        except Exception as ex:
            error_string = "demoinfo save_demo_description error %s" % str(ex)
            print error_string
            self.error_log("save_demo_description",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string


        return json.dumps(data)


    #For unittests and internal use, in other case you should use add_demo_description instead
    #@cherrypy.expose
    #@cherrypy.tools.allow(methods=['POST']) #allow only post
    def add_demo_description_using_param(self, demojson,inproduction = None):
        #recieves a valid json as a string AS PARAMETER
        #http://stackoverflow.com/questions/3743769/how-to-receive-json-in-a-post-request-in-cherrypy

        data = {}
        data["status"] = "KO"
        demojson=str(demojson)

        if not is_json(demojson):
            print "add_demo_description_using_param demojson is not a validjson "
            print "+++++ demojson: ",demojson
            print "+++++ demojson type: ",type(demojson)
            raise Exception

        try:
            conn = lite.connect(self.database_file)
            dao = DemoDescriptionDAO(conn)
            if inproduction is not None:
                id = dao.add(demojson,inproduction)
            else:
                id = dao.add(demojson)
            conn.close()
            #return id
            data["status"] = "OK"
            data["demo_description_id"] = id

        except Exception as ex:
            error_string=("WS add_demo_description_using_param  e:%s"%(str(ex)))
            print (error_string)
            conn.close()
            raise Exception

        return json.dumps(data)

    # MISCELLANEA


    @cherrypy.expose
    def index(self):
        return ("Welcome to IPOL demoInfo !")


    @cherrypy.expose
    def ping(self):
        data = {}
        data["status"] = "OK"
        data["ping"] = "pong"
        return json.dumps(data)


    #TODO protect THIS
    @cherrypy.expose
    def shutdown(self):
        data = {}
        data["status"] = "KO"
        try:
            cherrypy.engine.exit()
            data["status"] = "OK"
        except Exception as ex:
            self.error_log("shutdown", str(ex))
        return json.dumps(data)


    #todo hide sql
    @cherrypy.expose
    def stats(self):
        data = {}
        data["status"] = "KO"
        try:
            conn = lite.connect(self.database_file)
            cursor_db = conn.cursor()
            cursor_db.execute("""
            SELECT COUNT(*) FROM demo WHERE active = 1""")
            data["nb_demos"] = cursor_db.fetchone()[0]
            cursor_db.execute("""
            SELECT COUNT(*) FROM author""")
            data["nb_authors"] = cursor_db.fetchone()[0]
            cursor_db.execute("""
            SELECT COUNT(*) FROM editor""")
            data["nb_editors"] = cursor_db.fetchone()[0]
            conn.close()
            data["status"] = "OK"
        except Exception as ex:
            error_string = "demoinfo stats error %s" % str(ex)
            print error_string
            self.error_log("stats",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string
        return json.dumps(data)


    #todo hide sql
    @cherrypy.expose
    def read_states(self):
        data = {}
        state_list=list()
        data["status"] = "KO"
        try:
            conn = lite.connect(self.database_file)
            cursor_db = conn.cursor()
            cursor_db.execute('''SELECT  s.ID, s.name FROM state as s ''')
            conn.commit()
            for row in cursor_db.fetchall():
                s = (row[0], row[1])
                state_list.append(s)

            conn.close()

            data["status"] = "OK"
            data["state_list"] = state_list
        except Exception as ex:
            error_string = "demoinfo read_states error %s" % str(ex)
            print error_string
            self.error_log("read_states",error_string)
            try:
                conn.close()
            except Exception as ex:
                pass
            #raise Exception
            data["error"] = error_string

        return json.dumps(data)
