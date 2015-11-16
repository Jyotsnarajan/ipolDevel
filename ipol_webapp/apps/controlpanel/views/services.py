# coding=utf-8
#GLOBAL WS LIST (todo in DB)
#LOCAL
#ARCHIVE
archive_ws_url_page ='http://127.0.0.1:9000/page'
archive_ws_url_ping = 'http://127.0.0.1:9000/ping'
archive_ws_url_stats = 'http://127.0.0.1:9000/stats'
#BLOBS


#TEST ENV
#ARCHIVE
te_archive_ws_url_page ='http://boucantrin.ovh.hw.ipol.im:9000/page'
te_archive_ws_url_ping = 'http://boucantrin.ovh.hw.ipol.im:9000/ping'
te_archive_ws_url_stats = 'http://boucantrin.ovh.hw.ipol.im:9000/stats'
te_archive_ws_url_stats = 'http://boucantrin.ovh.hw.ipol.im:9000/archive_admin'

#
# http://<localhost>:<port>/add_exp_test?demo_id=42&blobs=<json_blobs>&parameters=<json_parameters>
# The method “add experiment” takes in the entry of the id of the demo used ; a JSON string of the format :
# {
#     url_blob : name,
# ... }
# containing a description of each blob used by and produced by the experiment, with their temporary URLs and names ;
#  and a JSON string describing the parameters of the demo used for the experiment. It will add an experiment to the
#  database by creating a new entry in the experiment table. If the blobs used by and produced by the experiment aren’t
# already in the database, it will copy them in the directory given in the configuration file, and create a thumbnail
#  for the images. It will return a json string containing the status of the operation, OK if it succeeded, KO if there
#  was an error and the operation wasn’t performed, as such :
# {
#     status : OK/KO
# }
# ￼￼If status is KO, a log describing the error will be written.
# 14
# Deleting an experiment from the archive
# When removing an experiment from the database via the method “delete experiment”, every blob linked to this experiment
#  and only to this experiment is removed.
# After that, all the entries in the correspondence table referencing this experiment are removed automatically due to
#  a foreign key constraint. It return
# a json response containing the status of the operation of the same format as the return of the method “add experiment”
# . The method shouldn’t be called anywhere else than through the user interface described later.
# Deleting a blob from the archive
# Due to a many-to-many link between blobs and experiments in the database, a blob has a lot of dependencies : it has
# of course the experiments using this blobs, but also the blobs linked to these experiments. For deletion of a blob
# from the archive, the precedent service is called on each experiment the blob is part of, assuring that no orphan
# data stay in the database (e.g. experiments linked to removed blobs or blobs linked to removed experiments).
#  The method implementing this service is “delete blob w deps”. It return a json response containing the status of
# the operation in the same format as the return of the method “add experiment”. The method shouldn’t be called anywhere
# else than through the user interface described later.

# Getting data
# Example :
# http://<localhost>:<port>/page?demo_id=42&page=3
# The method “page” returns a JSON response with, for a given page of a given demo, all the data of the experiments
# that should be displayed on this page. Twelve experiments are displayed by page. For rendering the archive page in
# the browser, the JSON response should be parsed and interpreted in a dedicated template furnished by the front-end
# of another module. The JSON response is formatted this way :
# {
#     status :  OK/KO,
#     experiments : [
#         {
#             date : timestamp_example,
#             files : [
#                 {
#                     url : url_example,
# 15
# ￼￼￼￼￼￼
# } ... ],
# id : id_example,
# name : name_example,
# url_thumb : url_thumbnail_example
#             id : id_example,
#             parameters = {parameters_example...}
#     ... ],
#     id_demo : id_demo_example,
#     nb_pages : nb_pages_example
# }

# Administrator interface for removing blobs/experiments

# Example :
# http://<localhost>:<port>/archive_admin?demo_id=42&page=3
# The only user interface furnished by the archive module is for removing blobs or experiment in a convenient manner.
# It uses the json response of the precedent service and renders the “archive admin tmp.html” template displaying a
#  page of archives for given demo, allowing the deletion of both blobs and experiments by simply linking to two other
#  services calling deletion methods and updating the template. In case of error, for example when invalid data is given
#  through URL, “error.html” is rendered.


# Example :
# http://<localhost>:<port>/shutdown
# The method “Shutdown” shuts down the archive application when called. It returns a json response containing the
# status of the operation.
# Other services
# Other services features the method “ping”, simply for checking if the module is up, and the method “stats”, formatted
# this way :
# ￼￼{
#     status : OK/KO,
#     nb_experiments : x,
# nb_blobs : y }

# Example :
# http://<localhost>:<port>/ping

# Example :
# http://<localhost>:<port>/stats

#BLOBS
#view list of available demos
te_blobs_demo_list="http://boucantrin.ovh.hw.ipol.im:9010/demos_ws"

# add_blob_ws
# ￼￼
# add blob to database
# demo id path tag ext the set title credit { return:OK or KO, the hash: ... }
# ￼￼
# ￼
# add_demo_ws
# ￼￼
# add demo to database name is template template
# { return:OK or KO }
# ￼
# add_tag_to_blob_ws
# ￼￼￼￼
# add tag to database blob id tag
# { return:OK or KO }
# ￼
# delete_blob_ws
# ￼￼
# delete blob from id demo and id blob demo id blob id
# { return:OK or KO, delete: (hash, extension) }
# ￼￼
# ￼￼
# get_blob_ws
# ￼￼
# return blob information from id
# blob id
# { return:OK or KO, {id, hash, extension, credit } }
# ￼
# 10
# get_blobs_from_template_ws
# ￼￼￼￼
# list blobs from name template template
# { return:OK or KO, blobs: {id, hash, extension, format } }
# get blobs of demo- by name ws
# ￼￼￼￼￼￼
# list_blobs_from_demo_name
# demo name
# { return:OK or KO, blobs: {id, hash,
# extension, format }, use template: {id: name, is template, id template}}
# ￼
# ￼￼￼
# get_blobs_of_demo_ws
# ￼￼￼￼
# list blobs from demo id demo
# { return:OK or KO, blobs: {id, hash, extension, format }, use template: {id: name, is template, id template}}
# ￼￼￼
# get_tags_ws
# ￼￼
# return list tags from blob id blob id
# { {id: name} }
# ￼
# get_template_demo_ws
# ￼￼￼
# return list demos templated
# { return:OK or KO, list template: {id: name} }
# ￼
# op_remove_demo_ws
# ￼￼￼
# remove demo from id demo demo id
# { return:OK or KO }
# ￼
# remove_tag_from_blob_ws
# ￼￼￼￼
# remove tag for a blob from id tag and id blob
# id tag id blob id
# { return:OK or KO }
# ￼￼
# set_template_ws
# ￼￼
# change the current template used by a demo
# demo id id name
# { return:OK or KO }
import json

def is_json(myjson):
	try:
		json_object = json.loads(myjson)
	except Exception, e:
		print("e:%s"%e)
		return False
	return True

import requests
import logging
logger = logging.getLogger(__name__)

def get_page(experimentid , page='1'):
	"""
	:param experimentid:
	:param page:
	:return:
	The method “page” returns a JSON response with, for a given page of a given demo, all the data of the experiments
	that should be displayed on this page. Twelve experiments are displayed by page. For rendering the archive page in
	the browser
	"""
	import json
	result = None
	wsurl = te_archive_ws_url_page
	try:

		params = {'demo_id': experimentid, 'page': page}
		response = requests.get(wsurl,params)
		result =  response.content
		if not is_json(result):
			msg="No es un Json valido:  is_json:%s" % is_json(result)
			print(msg)
			raise ValueError(msg)

		# print("response class")
		# print(response.__class__)
		# print("result")
		# print(result.__class__)
		# import yaml
		# list_org = ['a', 'b']
		# list_dump = json.dumps(list_org)
		# print(list_dump)
		# print json.loads(list_dump)
		# print yaml.safe_load(result)



	except Exception as e:
		msg=" get_page: error=%s"%(e)
		print(msg)
		logger.error(msg)
	return result

def get_demo_list():
	"""
	list demos present in database
	{ return:OK or KO, list demos: {id:name, id template, template } }
	"""
	#todo deberia devolver demo_id, debe ser un numero
	result = None
	try:

		r = requests.get(te_blobs_demo_list)
		result = r.json()
	except Exception as e:
		msg=" get_page: error=%s"%(e)
		print(msg)
		logger.error(msg)
	return result