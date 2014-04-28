import re
import urllib2
import csv

CECA_URL = "http://www.ceca.uwaterloo.ca/students/sessions.php?month_num=%d&year_num=%d"
sessions = []

HTML_REGEX = '<p><a href="sessions_details.*?</a></p>'
SESSION_REGEX = "<p><a href=\"sessions_details\.php\?id=(\d+?)\" onmouseover=\"return overlib\('<p align=left><b>Employer</b>:.*?<br><b>Date</b>: (.+?)<br><b>Time</b>: (.+?) - (.+?)<br><b>Location</b>: (.+?)<br><b>Web Site:</b> (.*?)<br><i>For (.+?) - (.+?)</i></p><p align=left>(.*?)</p><p align=left><b>Click to RSVP\.</b></p>',CAPTION,'<div class=wstitle><font size=2>Information Session Details</font></div>',.*?\);\" onmouseout=\"return nd\(\);\">(.+?)</a></p>"
SESSION_REGEX_INDICES = ["id", "date", "start_time", "end_time", "location", "website", "audience", "programs", "description", "employer"]

sessions = []
year = 2014
term = "spring"
for month in [5, 6, 7, 8]:
	html = urllib2.urlopen(CECA_URL%(month, year)).read()

	for session_html in re.findall(HTML_REGEX, html):
		m = re.match(SESSION_REGEX, session_html)
		if m:
			session = {}
			for i in range(0, len(SESSION_REGEX_INDICES)):
				session[SESSION_REGEX_INDICES[i]] = re.sub(r"</?.+/?>", "", m.group(i+1))
			sessions.append(session)
		else:
			print "Warning: found session html but could not parse (if the following is not a proper info session, please ignore this warning):"
			print session_html

# sessions object is complete here and can be exported as needed
# import json
# print json.dumps(sessions)

with open('%d_%s_infosessions.csv'%(year, term), 'wb') as f:
	writer = csv.writer(f)
	writer.writerow(["id", "employer", "date", "start_time", "end_time", "location", "website", "audience", "programs", "description"])
	for session in sessions:
		writer.writerow([session["id"], session["employer"], session["date"], session["start_time"], session["end_time"], session["location"], session["website"], session["audience"], session["programs"], session["description"]])
