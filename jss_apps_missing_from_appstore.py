#!/usr/bin/env python
####################################################################################################
#
# Copyright (c) 2014, JAMF Software, LLC.  All rights reserved.
#
#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are met:
#               * Redistributions of source code must retain the above copyright
#                 notice, this list of conditions and the following disclaimer.
#               * Redistributions in binary form must reproduce the above copyright
#                 notice, this list of conditions and the following disclaimer in the
#                 documentation and/or other materials provided with the distribution.
#               * Neither the name of the JAMF Software, LLC nor the
#                 names of its contributors may be used to ENDorse or promote products
#                 derived from this software without specific prior written permission.
#
#       THIS SOFTWARE IS PROVIDED BY JAMF SOFTWARE, LLC "AS IS" AND ANY
#       EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#       WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#       DISCLAIMED. IN NO EVENT SHALL JAMF SOFTWARE, LLC BE LIABLE FOR ANY
#       DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#       (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#       LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#       ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#       SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
####################################################################################################
#
#	Date: 04/14/2017
#	Created by: Jordan Wisniewski
#
#	This script will parse a JSS Summary, or search the API for Mac and Mobile Device apps,
#	and it will check to determine if they still exist on the App Store. If they do not exist
#	a CSV will be made with the app information, and if using the API, VPP will get disabled.
#
#	NOTE: The 'requests' library is requiRED for this script. Uncomment the lines below to force
#		  the installation of 'requests' and/or 'pip'
#
#	MORE INFO: https://github.com/kennethreitz/requests, https://pypi.python.org/pypi/pip
#
####################################################################################################

from xml.etree import ElementTree as et
#from contextlib import contextmanager
from time import sleep
import requests
#import site
import sys, os
import getpass
import time
import json
import re

#@contextmanager
#def suppress_stdout():
#    with open(os.devnull, "w") as devnull:
#    	old_stderr = sys.stderr
#        old_stdout = sys.stdout
#        sys.stdout = devnull
#        sys.stderr = devnull
#        try:  
#            yield
#        finally:
#            sys.stdout = old_stdout
#            sys.stdout = old_stderr
           
#try: 
#	with suppress_stdout():
#		try:
#			import pip
#		except Exception as e:
#			from setuptools.command import easy_install
#			easy_install.main(["-U", "pip"])
#			reload(site)
#			import pip
#		try:
#			pip.main(['install', 'requests'])
#			pip.main(['install', 'requests[security]'])
#			reload(site)
#		except Exception as e:
#			print "Error: " + str(e)
#			sys.exit(1)
#	import requests
#except Exception as e:
#	print "Error: " + str(e)
#	sys.exit(1)
          			
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
  
class App:
	def __init__(self):
		self.type = ''
		self.id = 0
		self.name = ''
		self.adam_id = 0
		self.url = ''
		self.country = ''
		self.vpp = 'Unknown'
		
class Color:
	GREEN = '\033[92m\033[1m'
	RED = '\033[91m\033[1m'
	BLUE = '\033[94m\033[1m'
	END = '\033[0m'
		
#clear the command line window		
os.system('cls' if os.name == 'nt' else 'clear')

#### GLOBAL ###
ITUNES_URL = 'https://itunes.apple.com/lookup'
MOBILE_APP_URI = '/JSSResource/mobiledeviceapplications'
MAC_APP_URI = '/JSSResource/macapplications'
JSON_HEADER = {'Accept': 'application/json', 'Content-type':'application/json'}
XML_HEADER = {'Accept': 'text/xml', 'Content-type':'text/xml'}
VERIFY_SSL = False

### USER INPUT ###
JSS_URL = None
JSS_USER = None
JSS_PASS = None
FILE_PATH = None

def main():
	global JSS_URL
	global JSS_USER
	global JSS_PASS
	global FILE_PATH
	
	valid = False
	while not valid:
		input_source = raw_input('enter 1 to parse jss summary, or 2 to query api: ').strip()
		
		if input_source == '1':
			valid = True
			FILE_PATH = raw_input('Path to JSS Summary: ').strip()
			findAppsNotInAppStoreViaSummary()
		elif input_source == '2':
			valid = True
			JSS_URL = raw_input('JSS URL: ').strip()
			JSS_USER = raw_input('JSS User: ').strip()
			JSS_PASS = getpass.getpass('JSS Pass: ').strip()
			fixAppsNotInAppStoreViaApi()

def findAppsNotInAppStoreViaSummary():
	try:
		apps_not_in_appstore = []
		with open(FILE_PATH, 'rb') as f:
			content = f.readlines()
		for index, line in enumerate(content):
			if 'iTunes ID' in line.strip():
				app = App()
				for attribute in content[max(0, index - 7):min(len(content), index + 1)]:
					attribute = attribute.strip()
					if attribute.startswith('ID'):
						app.id = attribute.split()[1]
					if attribute.startswith('Name'):
						app.name = re.split('\.+', attribute)[1].strip()
					if attribute.startswith('iTunes Store URL'):
						app.url = re.split('\s{2,} | \.+', attribute, maxsplit=1)[1].strip()
						app.country = app.url.split('/')[3]
					if attribute.startswith('iTunes ID'):
						app.adam_id = re.split(r'\s{2,} | \.+', attribute)[1]
				if appInAppStore(app) is False:
					apps_not_in_appstore.append(app)
				progressBar('lines scanned', index, len(content))
		print " - done!"
		output('apps', apps_not_in_appstore)
	except Exception as e:
		print 'Error finding apps in the JSS Summary that are no longer on the App Store: ' + str(e)
def getAppDetailsFromSummary(app_list):
	print stuff
	
def fixAppsNotInAppStoreViaApi():
	try:
		checkJssAppsInAppStore('mac_apps', getListOfApps('mac'))
		checkJssAppsInAppStore('mobile_apps', getListOfApps('mobile'))
	except Exception as e:
		print 'Error processing apps: ' + str(e)

def checkJssAppsInAppStore(type, app_list):
	apps_not_in_appstore = []
	try:
		for index, app in enumerate(app_list):
			getAppDetails(app)
			progressBar('checking ' + type, index, len(app_list))
			if app.url is not None:
				if appInAppStore(app) is False:
					if app.vpp is True:
						r = disableVpp(app)
						if r == requests.codes.created:
							app.vpp = False				
					apps_not_in_appstore.append(app)	
		print " - done!"
		output(type, apps_not_in_appstore)
	except Exception as e:
		print 'Error finding and fixing apps in the JSS that are no longer on the App Store: ' + str(e)

def progressBar(title, index, total):
	chunks = 50
	current = int(chunks * (index + 1) / total)
	sys.stdout.write('\r{0} [{1}{2}] {3}/{4}'.format(
							title + ':', 
							Color.BLUE + ('*' * current) + Color.END, 
							' ' * (chunks - current), 
							(index + 1), 
							total
					 )
	)
	sys.stdout.flush()

def output(type, app_list):
	try:
		if app_list is not None and len(app_list) > 0:
			output_path = '/tmp/' + str(int(time.time() * 1000)) + '_missing_' + type + '.csv'
			with open(output_path, 'w') as out:
				out.write('"{0}", "{1}", "{2}", "{3}", "{4}", "{5}",\n'.format(
								"App ID", 
								"App Name", 
								"Adam ID", 
								"Country", 
								"URL", 
								"VPP Enabled"
							)
				)
				for app in app_list:
					out.write('"{0}", "{1}", "{2}", "{3}", "{4}", "{5}",\n'.format(
								app.id,
								app.name,
								app.adam_id,
								app.country,
								app.url, 
								app.vpp
							)
					)
					if app.vpp is True:
						print (Color.RED + "failed to disable vpp" + Color.END + " for id: {0} | adam id: {1} | name: {2}").format(
							Color.BLUE + app.id + Color.END,
							Color.BLUE + app.adam_id + Color.END,
							Color.BLUE + app.name + Color.END
						)
			print Color.RED + type + ' were found missing from app store. \n' + Color.GREEN + 'an attempt was made to disable vpp if it was enabled, and if using api query method. '
			print Color.BLUE + 'details found in: ' + output_path + '\n' + Color.END
		else:
			print Color.GREEN + 'all ' + type + ' appear to be on the App Store.' + u'\U0001F44D' + '\n' + Color.END
	except Exception as e:
		print 'Error attempting to generate output: ' + str(e)

def disableVpp(app):
	try:
		use_vpp = "false"
		vpp_account = "-1"
		if app.type == 'mac':
			app_el = et.Element('mac_application')
		elif app.type == 'mobile':
			app_el = et.Element('mobile_device_application')
		vpp_el = et.SubElement(app_el, 'vpp')
		dvpp_el = et.SubElement(vpp_el, 'assign_vpp_device_based_licenses')
		dvpp_el.text = use_vpp
		acc_el = et.SubElement(vpp_el, 'vpp_admin_account')
		acc_el.text = vpp_account
		xml = et.tostring(app_el, encoding='UTF-8')
		r = requests.put(JSS_URL + MOBILE_APP_URI + '/id/' + app.id, headers=XML_HEADER, auth=(JSS_USER, JSS_PASS), data=xml, verify=VERIFY_SSL)
		return r.status_code
	except Exception as e:
		print 'Error disabling VPP for app not found in App Store: ' + str(e)
		
def getAdamId(url):
	try:
		url_END = url.rsplit('/', 1)[-1]
		start = url_END.index('id') + len('id')
		END = url_END.index('?', start)
	except Exception as e:
		pass
	return str(url_END[start:END]).encode('utf8')

def appInAppStore(app):
	try:
		r = getJsonAppFromAppStore(app.country, app.adam_id)
		results = r['resultCount']
		if results > 0:
			return True
		else:
			return False
	except Exception as e:
		print 'Error checking App Store for app: ' + str(e)

def getJsonAppFromAppStore(country, adam_id):
	params = {'id':adam_id, 'country':country}
	try:
		r = requests.get(ITUNES_URL, headers=JSON_HEADER, params=params, verify=VERIFY_SSL)
	except Exception as e:
		print 'Error checking App Store for app: ' + str(e)	
	return r.json()
	
def getJsonAppFromJSS(uri, app_id):
	try:
		r = requests.get(JSS_URL + uri + "/id/" + str(app_id), auth=(JSS_USER, JSS_PASS), headers=JSON_HEADER, verify=VERIFY_SSL).json()
	except Exception as e:
		pass
	return r
	
def getAppDetails(app):
	try:
		if app.type == 'mac':
			json = getJsonAppFromJSS(MAC_APP_URI, app.id)
			app.url = json['mac_application']['general']['url'].encode('utf8')
			app.country = app.url.split('/')[3]
			app.adam_id = getAdamId(app.url)
			app.vpp = json['mac_application']['vpp']['assign_vpp_device_based_licenses']
		elif app.type == 'mobile':
			json = getJsonAppFromJSS(MOBILE_APP_URI, app.id)
			app.url = json['mobile_device_application']['general']['itunes_store_url'].encode('utf8')
			app.country = json['mobile_device_application']['general']['itunes_country_region'].encode('utf8')
			app.vpp = json['mobile_device_application']['vpp']['assign_vpp_device_based_licenses']
			app.adam_id = getAdamId(app.url)
	except Exception as e:
		pass
		
def getJsonAppListFromJSS(uri):
	try:
		r = requests.get(JSS_URL + uri, auth=(JSS_USER, JSS_PASS), headers=JSON_HEADER, verify=VERIFY_SSL).json()
	except Exception as e:
		print 'Error getting app list from JSS: ' + str(e)
		sys.exit(1)
	return r
	
def getListOfApps(type):
	app_list = []
	try:
		if type == 'mac':
			json = getJsonAppListFromJSS(MAC_APP_URI)
			dict = 'mac_applications'
		elif type == 'mobile':
			json = getJsonAppListFromJSS(MOBILE_APP_URI)
			dict = 'mobile_device_applications'
		for json_app in json[dict]:
			app = App()
			app.id = str(json_app['id']).encode('utf8')
			app.name = json_app['name'].encode('utf8')
			app.type = type
			app_list.append(app)
	except Exception as e:
		print 'Error parsing app list from JSS: ' + str(e)
	return app_list
	
main()