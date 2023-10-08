import ast 
import csv
import random
from faker import Faker
from app.models import *
from app.database import Session 
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date

fake = Faker()
Faker.seed(0)
unique_isbns = set()


def generate_unique_isbn():
    while True:
        isbn = fake.isbn13()
        if isbn not in unique_isbns:
            unique_isbns.add(isbn)
            return isbn

def main():
    imprints = [fake.company() for _ in range(5)]

    with Session() as session:
        with session.begin():
            session.execute(sa.delete(BookGenre))
            session.execute(sa.delete(BookInstance))
            session.execute(sa.delete(Book))
            session.execute(sa.delete(Author))
            session.execute(sa.delete(Genre))
            session.execute(sa.delete(Language))

    with Session() as session:
        with session.begin():
            with open('books.csv', encoding="utf-8") as f:
                reader = csv.DictReader(f)
                all_genres = {}
                all_authors = {}
                all_books = {}
                all_languages = {}
                rows = 0

                for row in reader:

                    if rows >= 100:
                        break

                    genres = ast.literal_eval(row.pop('genres'))
                    authors = row.pop('author').split(",")
                    languages = row.pop('language')

                    if len(genres) == 0:
                        continue

                    if row['title'] not in all_books:
                        book = Book(
                            title=row['title'][:128], 
                            summary=row['summary'][:1000],
                            isbn=generate_unique_isbn(),
                            img_url=row['coverImg']
                        )

                        all_books[row['title']] = book

                        for i in range(random.randint(1, 5)):
                            bk = BookInstance(
                                imprint=row['publisher'],
                                status=random.choice(list(StatusEnum))
                            )
                            book.book_instances.append(bk)

                        if languages not in all_languages and languages != "":
                            language = Language(
                                name=languages
                            )
                            all_languages[languages] = language

                        if languages != "":
                            all_languages[languages].books.add(book)

                        if authors[0] not in all_authors:
                            author = Author(name=authors[0])
                            session.add(author)
                            all_authors[authors[0]] = author
                        all_authors[authors[0]].books.append(book)
                        
                        for genre in genres:
                            if genre not in all_genres:
                                g = Genre(name=genre)
                                session.add(g)
                                all_genres[genre] = g
                            all_genres[genre].books.append(book)

                        rows += 1


if __name__ == '__main__':
    main()