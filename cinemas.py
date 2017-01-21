import bs4
import requests
import time

ARTHOUSE_CINEMAS_NUMBER = 10
TIME_OF_TIMEOUT = 15
TOP = 10
KINOPOISK_SEARCH_URL = 'https://www.kinopoisk.ru/index.php'
AFISHA_URL = 'http://www.afisha.ru/msk/schedule_cinema/'


def fetch_afisha_page():
    request_to_afisha = requests.get(AFISHA_URL).content
    return request_to_afisha


def parse_afisha_list(raw_html):
    soup = bs4.BeautifulSoup(raw_html, 'html.parser')
    movies = []
    for film in soup.find_all('div', {'class': 'object s-votes-hover-area collapsed'}):
        if not is_arthouse(film):
            movies.append((film.find('div', {'class': "m-disp-table"})).find('a').text)
    return movies[:TOP]


def is_arthouse(soup_film):
    return len(soup_film.find_all('tr')) < ARTHOUSE_CINEMAS_NUMBER


def fetch_movie_info(movie_title):
    payload = {'first': 'yes', 'kp_query': '{}'.format(movie_title)}
    raw_html = requests.get(KINOPOISK_SEARCH_URL, params=payload).content
    return raw_html


def parse_kinopoisk(raw_html, movie_title):
    soup = bs4.BeautifulSoup(raw_html, 'html.parser')
    average_rating = soup.find('span', {'class': 'rating_ball'}).text
    voters_amount = soup.find('span', {'class': 'ratingCount'}).text
    return {'movie_name': movie_title,
            'movie_rating': float(average_rating),
            'voters_amount': voters_amount}


def output_movies_to_console(movies):
    top_rating_films = sorted(movies, key=lambda movie: movie[1], reverse=True)
    for movie in top_rating_films[:TOP]:
        print('Фильм {} имеет {} голосов со средней оценкой {}'.format(**movie))


if __name__ == '__main__':
    movies = parse_afisha_list(fetch_afisha_page())
    movies_info = []
    for movie in movies:
        kinopoisk_raw_html = fetch_movie_info(movie)
        movies_info.append(parse_kinopoisk(kinopoisk_raw_html, movie))
        time.sleep(TIME_OF_TIMEOUT)
    output_movies_to_console(movies_info)
