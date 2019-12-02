#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from decouple import config
import json
import logging

# Configure and create a logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 

def send_notification(text):
	logger.info("Sending slack notification, data=%s", text)
	slack_endpoint = config('SLACK_ENDPOINT')
	headers = {
        	'Content-type': 'application/json',
    	}
	data = dict(
		text = text,
	)
	data = json.dumps(data)
	response = requests.post(slack_endpoint, headers=headers, data=data)
	return response.status_code


def main():
	logger.info("Starting run")
	urls = ["https://yst.am/", "https://yts.vc/", "https://yts.lt/"]
	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'
	}
	stored_movie_list_filename = "yts_movie_list.txt"

	for url in urls:
		response = requests.get(url, headers = headers)
		
		logger.info("Received respose=%s for URL=%s", response.status_code, url)

		# retrieve content from website
		if response.status_code == 200:
			soup = BeautifulSoup(response.content, 'html.parser')
			popular_downloads_div = soup.find(id='popular-downloads')
			second_row = popular_downloads_div.find_all('div', class_="row")[1]
			all_top_movies = second_row.find_all('div', class_="browse-movie-wrap")

			extracted_movies_dict = dict()
			
			for each_movie in all_top_movies:
				title = each_movie.find('a', class_="browse-movie-title").get_text()
				movie_link = "%s%s" % (url.strip("/"), each_movie.find('a', class_="browse-movie-title").get('href'))
				img_link = "%s%s" % (url.strip("/"), each_movie.find('img').get('src'))
				
				extracted_movies_dict.update(
					{
						title : dict(
							movie_link = movie_link,
							img_link = img_link,
						)
					}
				)
			
			logger.info("Extracted movies=%s", extracted_movies_dict.keys())

			# retrieve existing movies
			try:
				with open(stored_movie_list_filename) as f:
					existing_movie_list = [ x.strip() for x in f.readlines() ]
			except FileNotFoundError:
				existing_movie_list = list()

			extracted_movies_title_list = extracted_movies_dict.keys()
			new_movies_list	= set(extracted_movies_title_list) - set(existing_movie_list)

			# send notification if new movies available
			notification_response_dict = dict()
			if new_movies_list:
				for new_movie in new_movies_list:
					text = """Hey found new movie on YTS\n\n*%s* `<%s|view>`\n\n%s""" % (
							new_movie, 
							extracted_movies_dict.get(new_movie, {}).get("movie_link"),
							extracted_movies_dict.get(new_movie, {}).get("img_link")
						)

					response_code = send_notification(text)
					logger.info("Received notification respose=%s for movie=%s", response_code, new_movie)

					if str(response_code).startswith(('2')):
						notification_response_dict.update({
							new_movie: response_code
						})

				# update the tracker file
				logger.info("Updating tracker file with movies=%s", notification_response_dict.keys())
				if notification_response_dict:
					with open(stored_movie_list_filename, 'a') as f:
						movie_names = notification_response_dict.keys()
						f.write("\n".join(movie_names))
						f.write("\n")

			else:	
				logger.info("No new movies found")
			
		else:
			logger.info("Got response %s" % (response.status_code))

if __name__ == "__main__":
	main()
