import urllib.request
import os
import sys
import re
from optparse import OptionParser
from bs4 import BeautifulSoup
from gpo_zugaina_dl.colors import color

def get(url):
	with urllib.request.urlopen(url) as response: 
		return response.read()

def get_inherit(ebuild):
    lines = ebuild.splitlines()
    inheritFound = False
    eclasses = ""
    for line in lines:
        if inheritFound and line.find('\\') != -1:
            eclasses = eclasses + line.replace("\\", "").strip() + " "
        elif inheritFound and line.find('\\') == -1:
            eclasses = eclasses + line.strip() + " "
            break
        if line.startswith("inherit"):
            eclasses = line.replace("inherit", "").replace("\\", "").strip() + " "
            inheritFound = True
    return eclasses.strip().split(" ")

def sanitize(path):
	if path.endswith("/"):
		return path
	else:
		return path+"/"

def download_rec(prefix,overlay,package,path):
	eclasses = []
	url = "https://data.gpo.zugaina.org/"+overlay+"/"+package
	if path is not None:
		url = url + "/" + path
	else:
		path = "/"

	html = get(url)
	parsed_html = BeautifulSoup(html, "lxml")
	items = parsed_html.body.find_all('a')
	index = 5
	while index < len(items):
		href = items[index]['href']
		if OPTIONS.verbose or OPTIONS.pretend:
			decors="│   │   │   ├── "
			for _ in range(len(path.split("/"))-2):
				decors="│   " + decors
			print(decors[:-4]+"│")
			

		if href.find('/') != -1:
			#print(href + ' is dir ' + path)
			if OPTIONS.verbose or OPTIONS.pretend:
				print(decors+sanitize(href))
			if not OPTIONS.pretend:
				os.makedirs(prefix+package+path+href, exist_ok=True)
			download_rec(prefix,overlay,package,path+href)
		else:
			if OPTIONS.verbose or OPTIONS.pretend:
				print(decors+href)

			txt = get(url+"/"+href) 
			if not OPTIONS.pretend:
				file = open(prefix+package+path+href,"w")
				file.write(txt.decode("utf-8")) 
				file.close()
				
			if href.endswith(".ebuild"):
				eclasses.extend(get_inherit(txt.decode("utf-8")))
		index = index + 1
	return eclasses

def get_matches(html):
	 matches = html.body.find('div', attrs={'class':'pager'}).find('span').text
	 return int(matches.split("of ")[1])

def calc_page_to_show(html):
	res = [1]
	if OPTIONS.limit != 0 and OPTIONS.limit <= GPO_MATCH_PER_PAGE:
		return res
	pager = html.body.find('div', attrs={'class':'pager'}).find_all('a')
	count = GPO_MATCH_PER_PAGE

	for page in pager:
		if page.text.strip():
			res.append(int(page.text.strip()))
		count = count + GPO_MATCH_PER_PAGE
		if OPTIONS.limit != 0 and OPTIONS.limit <= count:
			break;
	return res

def print_matches(matches):
	print("Found {0} matches".format(matches))
	if matches > OPTIONS.limit and OPTIONS.limit != 0:
		print("Only {0} matches displayed on terminal".format(OPTIONS.limit))
		print("Set --limit=0 option to show all matches")

def download(prefix,overlay,package):
	if OPTIONS.verbose or OPTIONS.pretend:
		print(prefix)
		print("│")
		print("├── " +  sanitize(package.split("/")[0]))
		print("│   │")
		print("│   ├── " + sanitize(package.split("/")[1]))
	if not OPTIONS.pretend:
		os.makedirs(prefix+package, exist_ok=True)
	return list(set(download_rec(prefix,overlay,package,None)))

def download_required_eclasses(prefix, overlay, eclasses):
	eclassExists = False
	for eclass in eclasses:
		try:
			txt = get('https://data.gpo.zugaina.org/' + overlay + 'eclass/' + eclass + ".eclass")

			if not eclassExists and (OPTIONS.verbose or OPTIONS.pretend):
				print("│")
				print("├── eclass")
				eclassExists = True
			if OPTIONS.verbose or OPTIONS.pretend:
				print("│   │")
				print("│   ├── "+eclass)
			
			if not OPTIONS.pretend:
				os.makedirs(prefix+"eclass", exist_ok=True)
				file = open(prefix+"eclass/"+eclass,"w")
				file.write(txt.decode("utf-8")) 
				file.close()
		except Exception:
			continue

def view_package_overlays(package):
	try:
		html = get('https://gpo.zugaina.org/' + package)
	except Exception:
		print(color("*", bold=True, fg_light_red=True) + ' Category or package ' + color(package, bold=True) + ' not exists')
		sys.exit(1)

	parsed_html = BeautifulSoup(html, "lxml")
	packages = parsed_html.body.find('div', attrs={'id':'ebuild_list'}).ul.find_all('div',recursive=False)
	category = package.split('/')[0]
	matches = 0
	for package in packages:
		overlay = package['id']
		infos = package.li.find_all('div')
		name = infos[0].text
		keywords = infos[1].text
		use_flags = infos[2].text
		license = "";

		directTexts = package.li.findAll(text=True, recursive=False)
		for directText in directTexts:
			if directText.find('License') != -1:
				license = directText.strip();

		matches = matches + 1
		print(color("*", bold=True, fg_green=True) + " " + color(category + "/" + name, bold=True))
		print("\t" +color("Keywords: ",fg_green=True) + keywords)
		print("\t" +color("Use flags: ",fg_green=True) + use_flags)
		print("\t" +color("License: ",fg_green=True) + license)
		print("\t" +color("Overlay: ",fg_green=True) + color(overlay, bold=True)+"\n")
	print("Found {0} matches".format(matches))
	
def search(text):
	html = get('https://gpo.zugaina.org/Search?search='+text)
	parsed_html = BeautifulSoup(html, "lxml")
	matches = get_matches(parsed_html)
	pages = calc_page_to_show(parsed_html);
	
	search_items = []
	for page in pages:
		searchItem = parsed_html.body.find('div', attrs={'id':'search_results'}).find('a')
		if searchItem is None:
			print(color("*", bold=True, fg_yellow=True) + ' No results are found for ' + color(text, bold=True))
			sys.exit(0)
		while searchItem is not None:
			search_items.append(searchItem.text.strip())
			if OPTIONS.limit > 0 and len(search_items) >= OPTIONS.limit:
			        break
			searchItem = searchItem.find_next_sibling('a')

	if OPTIONS.limit == 0:
		search_items.sort()

	for strippedItem in search_items:
		fields = strippedItem.split(' ', 1)
		print(color("*", bold=True, fg_green=True) + " " + color(fields[0], bold=True))
		print("\t" +color("Description: ",fg_green=True) + fields[1]+"\n")

	print_matches(matches)

def main():
	global OPTIONS 
	global GPO_MATCH_PER_PAGE
	usage = "usage: gpo-zugaina-dl [options]"
	parser = OptionParser(usage=usage)
	parser.add_option("-s", "--search", dest="search",
					help="search a package", metavar="TEXT|CATEGORY/PACKAGE")
	parser.add_option("-l", "--limit", dest="limit", type="int", 
					default=50, help="set max limit matches to display (only available with -s option)")
	parser.add_option("-d", "--download", dest="download", nargs=3,
					help="download package from overlay", metavar="PREFIX OVERLAY CATEGORY/PACKAGE")
	parser.add_option("-p", "--pretend", action="store_true", dest="pretend", 
					default=False, help="display what will downloaded (only available with -d option)")
	parser.add_option("-v", "--verbose", action="store_true", dest="verbose", 
					default=False, help="run in verbose mode (only available with -d option)")
	(OPTIONS, args) = parser.parse_args()
	GPO_MATCH_PER_PAGE=50

	if OPTIONS.search:
		if OPTIONS.search.find("/") == -1:
			search(OPTIONS.search)
		else:
			view_package_overlays(OPTIONS.search)
	elif OPTIONS.download:
		eclasses = download(sanitize(OPTIONS.download[0]),OPTIONS.download[1],OPTIONS.download[2])
		download_required_eclasses(sanitize(OPTIONS.download[0]),sanitize(OPTIONS.download[1]),eclasses)
	else:
		parser.print_help()
		sys.exit(1)

if __name__ == "__main__":
        main()
