import argparse
import sys
import os

from recommendr.db import RedisBackend


DIR = os.path.dirname(os.path.abspath(__file__))


def import_movies(filename, db):
    with open(os.path.join(DIR, filename), 'r') as movies:
        for movie in movies.readlines():
            movie_id, title, genres = movie.split("::")
            genre_ids = []
            for genre in genres.split("|"):
                genre_ids.append(db.get_or_create_genre(genre))
            db.add_movie(movie_id, title, *genre_ids)


def import_ratings(filename, db):
    with open(os.path.join(DIR, filename), 'r') as ratings:
        for rating in ratings.readlines():
            user_id, movie_id, score, timestamp = rating.split("::")
            db.add_rating(user_id, movie_id, score)


def main(full=False):

    if full:
        movie_file = 'movies.dat'
        ratings_file = 'ratings_training.dat'
    else:
        movie_file = 'movies_dev.dat'
        ratings_file = 'ratings_dev.dat'

    db = RedisBackend()
    sys.stdout.write("Clearing database\n")
    db.clear()
    sys.stdout.write("Importing movies...\n")
    import_movies(movie_file, db)
    sys.stdout.write("Importing ratings...\n")
    import_ratings(ratings_file, db)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', help="Load the full training dataset",
                        action='store_false')
    args = parser.parse_args()
    main(args.full)
