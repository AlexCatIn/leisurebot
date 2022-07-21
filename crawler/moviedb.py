from peewee import *


db = SqliteDatabase('movies.db')
db2 = SqliteDatabase('cinemas.db')
db3 = SqliteDatabase('books.db')

class Movie(Model):
    movie_id = AutoField()
    name_russian = CharField()
    movie_genre = CharField(null=True)
    rate = FloatField(null=True)
    movie_url = CharField()
    

    class Meta:
        database = db
        indexes = ((("name_russian", "movie_url", ), True),)


class Cinema(Model):
    cinema_id = AutoField()
    name_russian = CharField()
    cinema_genre = CharField(null=True)
    cinema_url = CharField()


    class Meta:
        database = db2
        indexes = ((("name_russian", "cinema_url", ), True),)


class Book(Model):
    book_id = AutoField()
    name_russian = CharField()
    author = CharField()
    rate = FloatField(null=True)
    book_url = CharField()
    

    class Meta:
        database = db3
        indexes = ((("name_russian", "author"), True),)



db.connect()
db.create_tables([Movie])
db2.connect()
db2.create_tables([Cinema])
db3.connect()
db3.create_tables([Book])