#from bottle.ext.mongo import MongoPlugin
# db?
#db_uri = 'mongodb://user1:asdf5432@ds119395.mlab.com:19395/dotadb'
#db_plugin = MongoPlugin(uri=db_uri, db='dotadb')

from bottle import route, run, default_app, debug, request, static_file
from random import randrange
import csv

#scrape csv
#beautifulsoup4 thingy.
#

#static files
def static(fname):
    return static_file(fname, root='./static/')
route('/static/<fname:path>','GET',static)
#

#random icon selection
def random_icon():
    #i = randrange(1,5)
	# images are not fixed yet, it will get done later. Maybe. Who knows tbh.
	i = 4 #temporary solution
	return '"static/css/icons/' + str(i) + '.png"'
#

def htmlify(title,icon, body):
    page = """
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>%s</title>
        <link rel="stylesheet" href="static/css/stylesheet.css" type="text/css"/>
        <link rel="icon" href=%s type="image/png">
        <script src="static/sorttable.js"></script>
    </head>
    <body>
    %s
    </body>
</html>
        """ % (title,icon,body)
    return page

#

def read_csv():
	contents = []
	with open("input.csv") as input_file:
		for row in csv.reader(input_file):
			contents = contents + [row]
	return contents
contents = read_csv()
#
def get_theads():
	tableheads = "\n\t\t\t\t\t"
	for i in range(len(contents[0])):
		tableheads = tableheads + "<th>" +contents[0][i] + "</th>" + "\n\t\t\t\t\t"
	tableheads = tableheads[:tableheads.rfind('\t')]
	return tableheads
tableheads = get_theads()

def get_table(array):
	to_return = "\n\t\t\t\t"
	for row in contents:
		if(row[0] == 'Player'):
			continue
		to_return = to_return + "<tr>"
		for cell in row:
			to_return = to_return + "\n\t\t\t\t\t" + "<td>" + cell + "</td>"
		to_return = to_return + "\n\t\t\t\t" + "</tr>" + "\n\t\t\t\t"
	to_return = to_return[:to_return.rfind("<tr>")]
	to_return = to_return + "</tr>"
	to_return = to_return[:to_return.rfind("</tr>")]
	return to_return
tabledata = get_table(contents)
#

processeddata = []
with open("a2_processing.csv") as procfile:
    for row in csv.reader(procfile):
        processeddata = processeddata + [row]

avdata = "\n\t\t\t\t<tr>"
flag1 = True
for row in processeddata:
	if(flag1):
		flag1 = False
		continue
	flag = 2
	for cell in row:
		flag = flag + 1
		if(flag==7):
			avdata = avdata + "\n\t\t\t\t\t" + "<td>" + str("{0:.2f}".format( float(cell.replace(',','.') ) * 100) ) + "%" + "</td>"
			continue
		avdata = avdata + "\n\t\t\t\t\t" + "<td>" + cell + "</td>"
	break
avdata = avdata + "\n\t\t\t\t</tr>"

meddata = "\n\t\t\t\t<tr>"
flag = -1
for row in processeddata:
	flag = flag + 1
	if(flag < 2):
		continue
	for cell in row:
		flag = flag + 1
		if(flag==7):
			meddata = meddata + "\n\t\t\t\t\t" + "<td>" + str("{0:.2f}".format( float(cell.replace(',','.') ) * 100) ) + "%" + "</td>"
			continue
		meddata = meddata + "\n\t\t\t\t\t" + "<td>" + cell + "</td>"
	break
meddata = meddata + "\n\t\t\t\t</tr>"

index_content = """
    <div class="banner">
		<h1>Player Statistics</h1>
	</div>

	<section class="content">
		<h2>Statistics Of Professional Dota2 Players</h2>
		<p>Let's analyse the statistics of Dota2 player's official matches. The data got collected from <a href="https://www.datdota.com/" target="_blank">datdota</a>. To make the data recent and relevant following criterias are used.
		</p>
		<ul>
			<li>Patch 7.00 and after</li>
			<li>Players with minimum 35 matches</li>
			<li>Professional or premium matches(aka matches that actually matters)</li>
		</ul>
	</section>"""


def content(tabledata): 

	form = """
		<form action="/raw" method="post">
			<input type="text" name="search" />
			<input type="submit" value="Search Player Name" />
		</form>
	"""
	content = """
	<section class="c2">
		<h2>The Data: </h2>
		""" + form + """
		<div class="grid">
			<table class="sortable">
				<tr>"""+tableheads+"""</tr>"""+tabledata+"""	
			</table>
		</div>	
	</section>

	<section class="splitted">
		<div class="left">
			<h3>Average Stats</h3>
			<table class="grid">
				<tr>"""+tableheads+"""</tr>"""+avdata+"""	
			</table>
		</div>
		<div class="right">
			<h3>Median Player</h3>
			<table class="grid">
				<tr>"""+tableheads+"""</tr>"""+meddata+"""	
			</table>
		</div>
	</section>
	"""
	return content

def raw_content_page():
	global tabledata
	search = request.forms.get('search')

	found_rows = []
	for row in contents:
		if search.lower() in row[0].lower():
			found_rows = found_rows + row

	tabledata = get_table(found_rows)

	return htmlify("Raw stats",random_icon(),content(tabledata)+found_rows[0][0]+found_rows[0][1]+found_rows[1][0]+found_rows[1][1])
route('/raw', 'POST', raw_content_page)

def index():
    return htmlify("Statistics Of Professional Dota2 Players",random_icon(),index_content+content(tabledata))
route('/', 'GET', index)


#####################################################################
#####################################################################

# This line makes bottle give nicer error messages
debug(True)
# This line is necessary for running on Heroku
app = default_app()
# The below code is necessary for running this bottle app standalone on your computer.
if __name__ == "__main__":
  run(reloader='True')

