import requests
from bs4 import BeautifulSoup
from datetime import date
from peewee import *


from crawler.moviedb import Movie, Cinema, Book


def get_movie():
    headers = {
        "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    url = f"https://www.kinoreliz.info/index"
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    movie_cards = soup.find_all("div", class_="row mb-4")
    for movie in movie_cards:
        movie_title_russian = movie.find("h4", class_="movie-title").text.strip()
        movie_genre = movie.find("div", class_="footer-genres row-fluid").text.strip().split(sep = "|")[0]
        try:
            movie_rate = movie.find("b", class_="up40_fnt").text.strip()
        except AttributeError:
            movie_rate = None
        movie_url = f'https://www.kinoreliz.info{(movie.find("a").get("href"))}'
        try:
            Movie.create(
                name_russian=movie_title_russian,
                movie_genre=movie_genre,
                rate=movie_rate,
                movie_url=movie_url
            )
        except IntegrityError:
            print("Такой фильм уже создан")


def get_cinema():
    headers = {
        "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    url = "https://www.afisha.ru/rostov-na-donu/schedule_cinema/"
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    cinema_cards = soup.find_all("div", class_="_1kwbj lkWIA _161Om")
    for cinema in cinema_cards:
        cinema_title_russian = cinema.find("h2", class_="_3Yfoo").text.strip()
        cinema_genre = cinema.find("a", class_="_3NqYW G_0Rp").text.strip()
        cinema_url = f'https://www.afisha.ru{(cinema.find("a", class_="_3NqYW DWsHS _3lmHp wkn_c").get("href"))}'
        try:
            Cinema.create(
                name_russian=cinema_title_russian,
                cinema_genre=cinema_genre,
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
        try:
            book_author = book.find("div", class_="art__author").text.strip()
        except AttributeError:
            book_author = None 
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