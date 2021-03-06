import json
import logging

from apps.controlpanel.mixings import NavbarReusableMixinMF
from apps.controlpanel.views.ipolwebservices import ipolservices
from apps.controlpanel.views.ipolwebservices.ipoldeserializers import (
    DeserializeArchiveStatus, DeserializeDemoinfoStatus, DeserializeDemoList,
    DeserializeProxyStatus)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from ipol_webapp.settings import (IPOL_SERVICES_MODULE_ACHIVE,
                                  IPOL_SERVICES_MODULE_BLOBS,
                                  IPOL_SERVICES_MODULE_DEMO,
                                  IPOL_SERVICES_MODULE_DEMOINFO,
                                  IPOL_SERVICES_MODULE_PROXY)

__author__ = 'josearrecio'
logger = logging.getLogger(__name__)



#View

class StatusView(NavbarReusableMixinMF,TemplateView):
    template_name = "stats.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.request.session['menu'] = 'menu-status'
        return super(StatusView, self).dispatch(*args, **kwargs)

    def get_demoinfo_module_stats(self):

        try:
            # Demoinfo Stats
            response = ipolservices.demoinfo_get_stats()
            json_response = json.loads(response)
        except Exception , e:
            msg="Error get_demoinfo_module_stats %s"%e
            print(msg)
            logger.error(msg)
            return {'status': 'KO'}

        return json_response


    def get_archive_module_stats(self):
        try:
            # Archive Stats
            response = ipolservices.archive_get_stats()
            json_response = json.loads(response)
        except Exception , e:
            msg="Error get_archive_module_stats %s"%e
            print(msg)
            logger.error(msg)
            return {'status': 'KO'}

        return json_response


    def get_blobs_module_stats(self):

        try:

            response = ipolservices.get_blobs_stats()
            json_response = json.loads(response)
        except Exception , e:
            msg="Error get_blobs_module_stats %s"%e
            print(msg)
            logger.error(msg)
            return {'status': 'KO'}

        return json_response

    def core_ping(self):
        try:

            response = ipolservices.core_ping()
            json_response = json.loads(response)
        except Exception, e:
            msg = "Error core_ping %s" % e
            print(msg)
            logger.error(msg)
            return {'status': 'KO'}

        return json_response


    def dispatcher_ping(self):
        try:

            response = ipolservices.dispatcher_ping()
            json_response = json.loads(response)
        except Exception, e:
            msg = "Error dispatcher_ping %s" % e
            print(msg)
            logger.error(msg)
            return {'status':'KO'}

        return json_response

    def demorunners_stats(self):
        data = {'status': 'KO'}
        try:
            # DR stats
            response = ipolservices.http_request('/api/dispatcher/get_demorunners_stats')
            json_response = json.loads(response)
            for dr in json_response.get('demorunners'):
                if dr.get('status') == 'OK':
                    data['status'] = 'OK'
                    break
            data['demorunners'] = json_response.get('demorunners')
        except Exception as ex:
            msg = "Error get_archive_module_stats %s" % ex
            logger.error(msg)
            print(msg)
            return {'status': 'KO'}

        return data

    def conversion_ping(self):
        try:

            response = ipolservices.conversion_ping()
            json_response = json.loads(response)
        except Exception, e:
            msg = "Error conversion_ping %s" % e
            print(msg)
            logger.error(msg)
            return {'status':'KO'}

        return json_response
