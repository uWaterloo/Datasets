import re
import urllib2
import csv

CECA_URL = "http://www.ceca.uwaterloo.ca/students/sessions_details.php?id=%s"
sessions = []

# messy regex scraping was required. see source of above page for more info. :(

def get_by_label(label, html):
	# regex is very slow if it doesn't exist (too many wildcards); prevent that.
	if label in html:
		return re.findall("<td.*?>.*?%s.*?</td>.*?<td.*?>(.*?)</td>"%label, html, re.DOTALL)
	else:
		return []

def get_others(html):
	return re.findall('<tr><td width="60%" colspan="2"><i>For (.+?) - (.*?)</i></td></tr>.+?<tr><td width="60%" colspan="2"><i>(.*?)</i></td></tr>', html, re.DOTALL)

def get_ids(html):
	return re.findall('<a href=".+id=(\d+).+?">RSVP \(students\)</a>', html)

def parse_link(html):
	link = re.findall('<a href="(.+?)".*?>', html)[0]
	if link == "http://": # this is the default on the ceca site when no url is entered
		link = ""
	return link

def parse_time(html):
	return html.split(" - ")

# parsing Fall 2013
for month in ["2013Sep", "2013Oct"]:
	html = urllib2.urlopen(CECA_URL%month).read()

	# find all the fields individually. note the order matters.
	ids = get_ids(html)
	employers = get_by_label("Employer:", html)
	dates = get_by_label("Date:", html)
	times = map(parse_time, get_by_label("Time:", html))
	locations = get_by_label("Location:", html)
	websites = map(parse_link, get_by_label("Web Site:", html))
	others = get_others(html)

	# make sure each session has all the required fields
	if not (len(ids) == len(employers) == len(dates) == len(times) == len(locations) == len(websites) == len(others)):
		raise Exception, 'Some sessions are missing info'

	# merge/zipper all the fields together per info sessions
	for i in range(0, len(employers)):
		session = {}
		session["id"] = ids[i]
		session["employer"] = employers[i]
		session["date"] = dates[i]
		session["start_time"] = times[i][0]
		session["end_time"] = times[i][1]
		session["location"] = locations[i]
		session["website"] = websites[i]
		session["coop/grad"] = others[i][0]
		session["programs"] = others[i][1]
		session["info"] = others[i][2]
		sessions.append(session)

# sessions object is complete here and can be exported as needed
# import json
# print json.dumps(sessions)

with open('sessions.csv', 'wb') as f:
	writer = csv.writer(f)
	writer.writerow(["id", "employer", "date", "start_time", "end_time", "location", "website", "coop/grad", "programs", "info"])
	for session in sessions:
		writer.writerow([session["id"], session["employer"], session["date"], session["start_time"], session["end_time"], session["location"], session["website"], session["coop/grad"], session["programs"], session["info"]])
