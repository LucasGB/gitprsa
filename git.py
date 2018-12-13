import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os

user = ''
token = ''
with open('auth.txt', 'r') as file:
	user, token = file.read().split(':')

def get_repositories_by_forks(n):
	print 'Fetching repositories by most forks...'
	
	r = requests.get('https://api.github.com/search/repositories?q=forks%3A%3E0&sort=forks&per_page=' + str(n))
	
	print 'Done'

	return r.json()

def get_closed_pull_request_numbers_from_repo(repository):
	print 'Fetching pull requests from %s' % (repository)

	full_name = repository.split('/')

	s = requests.Session()
	retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
	s.mount('https://', HTTPAdapter(max_retries=retries))

	print ('https://api.github.com/repos/{}/{}/pulls?state=closed&page=1&per_page=100').format(full_name[0], full_name[1])	
	response = s.get( ('https://api.github.com/repos/{}/{}/pulls?state=closed&page=1&per_page=100').format(full_name[0], full_name[1]), auth=(user,token))

	directory = 'repositories/{}_{}'.format(full_name[0], full_name[1])
	if not os.path.exists(directory):
		os.makedirs(directory)
	
	while True:
		for pr in response.json():
			if not verify_presence_of_changed_files(repository, str(pr["number"])):
				print 'No changed files'
				continue

			with open('{}/{}_{}_pull_request_numbers.txt'.format(directory, full_name[0], full_name[1]), 'a') as output:
				output.write(str(pr["number"]) + '\n')
		try:
			print response.links['next']['url']
			response = s.get(response.links['next']['url'], auth=(user,token))
		except:
			print 'KeyError: next link not found. Returning results'
			break

	print 'Done.'

def verify_presence_of_changed_files(repository, pull_request):
	print 'Verifying presence of changed files in pull request: {}'.format(pull_request)

	s = requests.Session()
	retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
	s.mount('https://', HTTPAdapter(max_retries=retries))

	response = s.get('https://api.github.com/repos/{}/pulls/{}'.format(repository, pull_request), auth=(user,token))

	if response.json()["changed_files"] > 0:
		return True

	print 'No presence of changed files'
	return False

def verify_acceptance(repository, pull_request):
	print 'Verifying acceptance of pull request #{}'.format(pull_request)

	s = requests.Session()
	retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
	s.mount('https://', HTTPAdapter(max_retries=retries))

	response = s.get('https://api.github.com/repos/{}/pulls/{}'.format(repository, pull_request), auth=(user,token))

	if response.json()["merged_at"] != None:
		status = verify_presence_of_review_comments(response.json()["review_comments_url"])
		print 'MERGED'
		
		if status == True:
			return True
		else:
			return None
	else:
		print 'NOT MERGED'
		status = verify_presence_of_review_comments(response.json()["review_comments_url"])

		if status == True:
			print 'HAS REVIEWS'
			return False
		else:
			print 'DOESNT HAVE REVIEWS'
			return None

def verify_presence_of_review_comments(url):
	print 'Verifying presence of review comments'

	print url

	s = requests.Session()
	retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
	s.mount('https://', HTTPAdapter(max_retries=retries))

	response = s.get(url, auth=(user,token))

	if len(response.json()) == 0:
		return False

	return True

def verify_merged_at_attr_from_pull_request(repository, pull_request):
	print 'Verifying if pull request #{} was merged'.format(pull_request)

	s = requests.Session()
	retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
	s.mount('https://', HTTPAdapter(max_retries=retries))

	response = s.get('https://api.github.com/repos/{}/pulls/{}'.format(repository, pull_request), auth=(user,token))

	if response.json()["merged_at"] != None:
		return True
	else:
		return False

def get_comments_from_pull_request(pull_request):
	r = requests.get('https://api.github.com/repos/rails/rails/issues/' + pull_request + '/comments')

	return r.json

def get_review_comments_from_pull_request(pull_request):
	print 'Fetching comments from pull request #' + pull_request

	comments = []

	response = requests.get('https://api.github.com/repos/rails/rails/pulls/' + pull_request + '/comments')

	if response.ok:
		
		for comment in response.json():
			comments.append(comment['body'])

		print 'Done.'

		return comments
	else:
		return response.raise_for_status()



#if __name__ == '__main__':
#	pull_requests = []
	#data = get_repositories_by_forks(1)

	#for entry in data['items']:		
	#	pull_requests = get_pull_requests_from_repo(entry['full_name'])

	#pull_requests = get_closed_pull_requests_from_repo('rails/rails')

	#comments = get_review_comments_from_pull_request(str(pull_requests[25]['number']))

#	review_comments = get_review_comments_from_pull_request(str(34227))
#	pull_request_comments = get_comments_from_pull_request(str(34227))

#	print comments