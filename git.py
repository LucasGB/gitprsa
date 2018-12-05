import requests

user = ''
token = ''
with open('auth.txt', 'r') as file:
	user, token = file.read().split(':')

def get_repositories_by_forks(n):
	print 'Fetching repositories by most forks...'
	
	r = requests.get('https://api.github.com/search/repositories?q=forks%3A%3E0&sort=forks&per_page=' + str(n))
	
	print 'Done'

	return r.json()

def get_closed_pull_request_numbers_from_repo(repositry):
	print 'Fetching pull requests from %s' % (repositry)

	full_name = repositry.split('/')
	pull_requests = []

	print ('https://api.github.com/repos/{}/{}/pulls?state=closed&page=1&per_page=100').format(full_name[0], full_name[1])	
	response = requests.get( ('https://api.github.com/repos/{}/{}/pulls?state=closed&page=1&per_page=100').format(full_name[0], full_name[1]), auth=(user,token))

	while True:
		if response.ok:
			for pr in response.json():
				pull_requests.append(str(pr["number"]))
				with open('repositories/{}_{}.txt'.format(full_name[0], full_name[1]), 'w') as output:
					output.write(pull_requests)
		else:
			return response.raise_for_status()

		try:
			print response.links['next']['url']
			response = requests.get(response.links['next']['url'], auth=('lucasgb','0c123d1e252bee8bda1227b83606f5ccf483fa9c'))
		except:
			print 'KeyError: next link not found. Returning results'
			break

	print 'Done.'

	

	return pull_requests

def filter_by_presence_of_changed_files(pull_requests):
	filtered_pull_requests = []

	print 'Filtering pull requests by presence of changed files'

	for pull_request in pull_requests:
		response = requests.get('https://api.github.com/repos/rails/rails/pulls/' + pull_request, auth=(user,token))

		if response.ok:
			if response.json()["changed_files"] > 0:
				filtered_pull_requests.append(response.json())
		else:
			return response.raise_for_status()

	print 'Done'
	
	return filtered_pull_requests

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