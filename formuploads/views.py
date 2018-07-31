from django.shortcuts import render
from django.http import HttpResponse
from xml.etree import ElementTree as ET
from django.http import JsonResponse
import urllib
import os
import shutil
import json
from dicttoxml import dicttoxml
from .vacants import get_vacants
from django.views.decorators.csrf import csrf_exempt
cv_summary = {}


def home(request):
	return render(request, 'formuploads/index.html', {'what': 'Upload your CV'})


def show_json(request):
	summary = "HEER"
	if 'cv_summary' in request.session:
		cv = request.session['cv_summary']
	# return render(request, 'formuploads/show_json.html', {'cv_summary':cv})
	return HttpResponse(json.dumps(cv, ensure_ascii = False), content_type = "application/json")

def show_xml(request):
	summary = "HEER"
	if 'cv_summary' in request.session:
		cv = request.session['cv_summary']
	# return render(request, 'formuploads/show_json.html', {'cv_summary':cv})
	return HttpResponse(dicttoxml(cv, custom_root='cv_summary', attr_type=False), content_type = "application/xml")


@csrf_exempt
def upload(request):
#try:
	all_vacants_info = [{}]
	vacants_ids = []
	vacants_ids, cv_summary = handle_uploaded_file(request.FILES['file'], str(request.FILES['file']))
	request.session['cv_summary'] = cv_summary
	all_vacants_info = analyse_file(all_vacants_info, vacants_ids)
#except:
	#return render(request, 'formuploads/failed.html')
	if request.method == 'POST':
		#return HttpResponse(json.dumps(cv_summary, ensure_ascii=False), content_type="application/json")
		return render(request, 'formuploads/success.html', {'vacants':all_vacants_info, 'cv_summary':cv_summary})
	return render(request, 'formuploads/failed.html')


def handle_uploaded_file(file, filename):
	if not os.path.exists('upload/'):
		os.mkdir('upload/')
	with open('upload/' + filename, 'wb+') as destination: 
		for chunk in file.chunks():
			destination.write(chunk)
	dir_path = 'upload/' + filename
	results = []
	results, cv_summary = get_vacants(dir_path)
	if os.path.exists('upload/'):
		shutil.rmtree('upload/')
	return results, cv_summary


def analyse_file(all_vacants_info, vacants_ids):
	requestURL = "https://www.enbek.kz/ru/xml/jooble"
	root = ET.parse(urllib.request.urlopen(requestURL)).getroot()
	for key in vacants_ids:
		for job in root.iter('job'):
			if(job.attrib.get('id') == key):
				all_vacants_info.append({
				
						'job_name': str(job.find('name').text).replace(", ", "",1),
						'job_region': str(job.find('region').text),
						"job_salary": str(job.find('salary').text),
						"job_description": str(job.find('description').text).replace("p&gt;", " ")
						.replace("li", " ").replace("ul", " ")
						.replace("/", " ").replace("&gt;", " ")
						.replace("&lt;", " ").replace("ul&gt;", " ")
						.replace("/li&gt;", " ").replace("li&gt;", " ")
						.replace("-&amp;", " ").replace("nbsp;", " ")
						.replace("&amp;", " ").replace("quot;"," ")
						.replace("br"," ").replace("strong"," ")
						.replace("strong"," ").replace("ol"," "),
						"job_email": str(job.find('email').text),
						"job_phone": str(job.find('phone').text),
						"job_link": str(job.find('link').text),
				
				})
	return all_vacants_info

