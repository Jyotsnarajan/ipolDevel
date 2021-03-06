import json
from apps.controlpanel.mixings import NavbarReusableMixinMF

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.utils.six import BytesIO

from apps.controlpanel.views.ipolwebservices.ipoldeserializers import DeserializePage, \
        DeserializeDemoList, DeserializeDemoinfoDemoList
from apps.controlpanel.views.ipolwebservices import ipolservices

import logging
from rest_framework.parsers import JSONParser

logger = logging.getLogger(__name__)

__author__ = 'josearrecio'

def has_permission(demo_id, user):
    try:
        if user.is_staff or user.is_superuser:
            return True

        editors = json.loads(ipolservices.demoinfo_editor_list_for_demo(demo_id))
        for editor in editors.get('editor_list'):
            if editor.get('mail') == user.email:
                return True
        return False

    except Exception:
        print "has_permission failed"
        return False

class ArchiveDeleteExperimentView(NavbarReusableMixinMF,TemplateView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ArchiveDeleteExperimentView, self).dispatch(*args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        #just return the JSON from the ws, this json has no interesting data, no template is needed

        try:
            experiment_id = int(self.kwargs['experiment_id'])
        except ValueError:
            msg= "Id is not an integer"
            logger.error(msg)
            raise ValueError(msg)

        result= ipolservices.archive_delete_experiment(experiment_id)
        if result is None:
            msg="DeleteExperimentView: Something went wrong using archive WS"
            logger.error(msg)
            raise ValueError(msg)


        return HttpResponse(result, content_type='application/json')


class ArchiveDeleteDemoView(NavbarReusableMixinMF,TemplateView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ArchiveDeleteDemoView, self).dispatch(*args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        #just return the JSON from the ws, no template is needed

        try:
            demo_id = int(self.kwargs['demo_id'])
        except ValueError:
            msg= "Id is not an integer"
            logger.error(msg)
            raise ValueError(msg)

        result= ipolservices.archive_delete_demo(demo_id)
        if result is None:
            msg="ArchiveDeleteDemoView: Something went wrong using archive WS"
            logger.error(msg)
            raise ValueError(msg)


        return HttpResponse(result, content_type='application/json')


class ArchiveDeleteExperimentFileView(NavbarReusableMixinMF,TemplateView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ArchiveDeleteExperimentFileView, self).dispatch(*args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        #just return the JSON from the ws, no template is needed

        try:
            demo_id = int(self.kwargs['file_id'])
        except ValueError:
            msg= "Id is not an integer"
            logger.error(msg)
            raise ValueError(msg)

        result= ipolservices.archive_delete_file(demo_id)
        if result is None:
            msg="DeleteFileView: Something went wrong using archive WS"
            logger.error(msg)
            raise ValueError(msg)


        return HttpResponse(result, content_type='application/json')


class ExperimentDetails(NavbarReusableMixinMF,TemplateView):
    template_name = "archive/experiment_details.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ExperimentDetails, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # get context
        context = super(ExperimentDetails, self).get_context_data(**kwargs)
        default_msg = 'The query did not return any results. Please make sure that you entered a valid ID.'

        try:
            # get the typed query, and cast into integer (should be an experiment ID)
            query = self.request.GET.get('search')
            demo_id = self.request.GET.get('demo_id')
            query = int(query)
            context['status'] = 'OK'
            context['query'] = query

            # Search for the asked experiment_id
            result_json = ipolservices.archive_get_experiment(query)

            try:
                # Parse a stream into Python native datatypes
                # Avoids the use of deserializer
                stream = BytesIO(result_json)
                parsed_data = JSONParser().parse(stream)

                context['status'] = parsed_data['status']
                context['results'] = parsed_data['experiment']
                context['registered'] = has_permission(demo_id, self.request.user)

            except Exception as e:
                msg = "Error on JSON parsing: %s" %e
                context['status'] = 'KO'
                context['query'] = query
                context['results'] = default_msg
                logger.error(msg)

        except Exception as e:
            context['status'] = 'KO'
            context['query'] = query
            context['results'] = default_msg
            msg = "Error while converting search criteria to integer: %s" % e
            logger.error(msg)

        return context


class ArchivePageView(NavbarReusableMixinMF,TemplateView):
    template_name = "demoinfo/manage_archives_for_demo.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ArchivePageView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        # get context
        context = super(ArchivePageView, self).get_context_data(**kwargs)
        demo_id = self.kwargs['id']
        try:
            query = self.request.GET.get('q')
            context['q'] = query

            try:
                current_page = self.request.GET.get('page')
                current_page = int(current_page)
            except:
                # If page is not an integer, deliver last page, by setting it to -1
                current_page = -1

            page_json = ipolservices.archive_get_page(int(demo_id), current_page)
            parsed_data = {}

            try:
                # Parse a stream into Python native datatypes
                # Avoids the use of deserializer
                stream = BytesIO(page_json)
                parsed_data = JSONParser().parse(stream)
                # load into context the tags from parsed_data
                for tag in parsed_data:
                    context[tag] = parsed_data[tag]

            except Exception as e:
                msg = "Error on JSON parsing: %s" %e
                logger.error(msg)

            # pagination of result
            if 'number_of_pages' in parsed_data['meta']:
                total_pages = parsed_data['meta']['number_of_pages']
            else:
                total_pages = 0

            # call the method to obtain previous/next pages numbers
            pages = set_pages(total_pages, current_page)

            # set the values of current/previous/next page, according to the values returned by the method set_pages
            context['current_page_number'] = pages['current_page']
            context['previous_page_number'] = pages['previous_page']
            context['next_page_number'] = pages['next_page']
            context['registered'] = has_permission(demo_id, self.request.user)

        except Exception as e:
            msg = "ArchivePageView Error %s "%e
            logger.error(msg)
            context['parsed_data'] = []
            logger.error(msg)
            print(msg)

        return context


# Given total_pages and current_page numbers, returns an array with current/previous/next pages numbers
# Value 0 means the current page does not have previous/next
# Also, if the current_page is out of bounds, delivers the last one
def set_pages(total_pages, current_page):
    pages = {}

    try:
        # if the asked page is out of bounds, show the last page
        if current_page < 1 or current_page > total_pages:
            current_page = total_pages

        # 0 or 1 pages
        if total_pages <= 1:
            previous_page = 0
            next_page = 0

        # more than 1 pages
        else:
            # current page is the first one
            if current_page == 1:
                previous_page = 0
                next_page = current_page + 1

            # current page is the last one
            elif current_page == total_pages:
                previous_page = current_page - 1
                next_page = 0

            # current page is between the first and the last one
            else:
                previous_page = current_page - 1
                next_page = current_page + 1

        pages['current_page'] = current_page
        pages['previous_page'] = previous_page
        pages['next_page'] = next_page

    except Exception as e:
        print "Error in set_pages: %s" % e

    return pages