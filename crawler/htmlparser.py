import requests
from bs4 import BeautifulSoup
from datetime import date
from peewee import *


from crawler.moviedb import Movie, Cinema, Book


def get_movie():
    headers = {
        "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    current_month = date.today().month
    current_year = date.today().year
    url = f"https://www.kinopoisk.ru/comingsoon/digital/?month={current_month}&year={current_year}"
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    movie_cards = soup.find_all("div", class_="premier_item")
    for movie in movie_cards:
        movie_title_russian = movie.find("span", class_="name").text.strip()
        second_line = movie.find_all("span")[1].text.strip().rsplit(" (", maxsplit=1)
        if len(second_line) > 1:
            movie_title_origin = second_line[0]
            year_production = second_line[1][:4]
        else:
            movie_title_origin = movie_title_russian
            year_production = second_line[0][1:5]
        movie_genre = movie.find_all("span")[3].text.strip()[1:-1]
        try:
            try:
                rate = float(movie.find("span", class_="ajax_rating").find("u").text.strip().split(" ")[0])
            except ValueError:
                rate = None
        except AttributeError:
            rate = None
        poster = movie.find("img", class_="flap_img").get("title")
        poster = f'https://www.kinopoisk.ru{poster}'
        
        movie_url = f'https://www.kinopoisk.ru{(movie.find("a").get("href"))}'
        try:
            Movie.create(
                name_russian=movie_title_russian,
                name_origin=movie_title_origin,
                year_production=year_production,
                movie_genre=movie_genre,
                rate=rate,
                poster=poster,
                movie_url=movie_url
            )
        except IntegrityError:
            print("Такой фильм уже создан")


def get_cinema():
    headers = {
        "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    url = "https://www.afisha.ru/rostov-na-donu/cinema/"
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    cinema_cards = soup.find_all("div", class_="_2iEOq") + soup.find_all("div", class_="_3jpUB") + soup.find_all("div", class_="n4Woq")
    for cinema in cinema_cards:
        cinema_title_russian = cinema.find("div", class_="_3Yfoo").text.strip()
        cinema_description = cinema.find('div', class_='Qt8S3').text.strip()
        try:
            rate = cinema.find("div", class_="_1kq55").find("span").text
        except AttributeError:
            rate = None
        cinema_genre = cinema.find("div", class_="_1OjLF").text.strip()
        cinema_url = f'https://www.afisha.ru{(cinema.find("a", class_="AhUgj _1Mmfj _2YKQd").get("href"))}'
        try:
            Cinema.create(
                name_russian=cinema_title_russian,
                description=cinema_description,
                cinema_genre=cinema_genre,
                rate=rate,
                cinema_url=cinema_url
            )
        except IntegrityError:
            print("Такой фильм из кинотеатра уже создан")


def get_book():
    headers = {
        "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    url = "https://www.litres.ru/luchshie-knigi/"
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    book_cards = soup.find_all("div", class_="art-standart art-item mgrid cover-309")
    for book in book_cards:
        book_name = book.find("div", class_="art__name").text.strip()
        book_author = book.find("div", class_="art__author").text.strip()
        book_rate = book.find("div", class_="inline-elem bottomline-rating").text.strip()
        book_url = f'https://www.litres.ru{book.find("a", class_="img-a").get("href")}'
        try:
            Book.create(
                name_russian=book_name,
                author=book_author,
                rate=book_rate,
                book_url=book_url
            )
        except IntegrityError:
            print("Такая книга уже создана")


get_movie()
get_cinema()
get_book()