import requests
from bs4 import BeautifulSoup
from decouple import config
import json

def send_notification(text):
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
	url = "https://yst.am/"
	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'
	}
	stored_movie_list_filename = "yts_movie_list.txt"

	response = requests.get(url, headers = headers)
	
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
				if str(response_code).startswith(('2')):
					notification_response_dict.update({
						new_movie: response_code
					})

			# update the tracker file
			if notification_response_dict:
				with open(stored_movie_list_filename, 'a') as f:
					movie_names = notification_response_dict.keys()
					f.write("\n".join(movie_names))
					f.write("\n")

		else:	
			print("No new movies found")
		
	else:
		print("Got response %s" % (response.status_code))

if __name__ == "__main__":
	main()
