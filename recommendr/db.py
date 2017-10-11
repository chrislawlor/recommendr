"""
Persistant storage for movies and reviews, using Redis.
"""
import redis

from . import config


def int_or_none(value):
    if value is None:
        return value
    return int(value)


def set_to_ints(values):
    """
    Redis returns all values as strings. This optimistically converts
    a set of strings to a set of integers.
    """
    ints = []
    for value in values:
        ints.append(int(value))
    return set(ints)


class RedisBackend(object):
    """
    Movie database storage and access functions, backed by Redis. Currently,
    only 'create' and 'retrieve' type functions are implemented.
    """

    def __init__(self, host=config.REDIS_HOST, port=config.REDIS_PORT,
                 db=config.REDIS_DB, client=None):
        if client:
            self.redis = client
        else:
            self.redis = redis.StrictRedis(host=host, port=port, db=db)

    def clear(self):
        """
        WARNING! Removes everything in the database.
        """
        self.redis.flushall()

    def add_genre(self, name):
        """
        Add a new genre. Returns the genre id.
        """
        name = name.lower().strip()
        genre_id = self.redis.incr("global:nextGenreId")
        with self.redis.pipeline() as pipe:
            pipe.set("genre:{0}:name".format(genre_id), name)
            pipe.sadd("genres", genre_id)
            pipe.set("genre:{0}:id".format(name), genre_id)
            pipe.execute()
        return genre_id

    def get_genre_id_by_name(self, name):
        """
        Given a genre name, return the id.
        """
        name = name.lower().strip()
        genre_id = self.redis.get("genre:{0}:id".format(name))
        #return self.redis.get("genre:{0}:name".format(genre_id))
        return int_or_none(genre_id)

    def get_or_create_genre(self, name):
        """
        Always return a genre id given a genre name. If the genre
        does not exist, create it and return the id.
        """
        name = name.lower().strip()
        if self.redis.exists("genre:{0}:id".format(name)):
            return self.get_genre_id_by_name(name)
        else:
            return self.add_genre(name)

    def add_movie(self, movie_id, name, *genres):
        """
        Add a movie. Movie IDs are not created automatically, they must be
        specified.
        """
        with self.redis.pipeline() as pipe:
            pipe.sadd("movies", movie_id)
            pipe.hset("movie_id:{0}".format(movie_id), "name", name)
            for genre in genres:
                pipe.sadd("genre:{0}:movies".format(genre), movie_id)
                pipe.sadd("movie:{0}:genres".format(movie_id), genre)
            pipe.execute()

    def get_movies(self):
        """
        Return all movie ids.
        """
        movies = self.redis.smembers("movies")
        return set_to_ints(movies)

    def get_name_for_movie(self, movie_id):
        """
        Retrieve the name of a movie for a given movie id.
        """
        return self.redis.hget("movie_id:{0}".format(movie_id), "name")

    def add_rating(self, reviewer_id, movie_id, rating):
        """
        Add a movie rating.
        """
        with self.redis.pipeline() as pipe:
            pipe.sadd("users", reviewer_id)
            pipe.sadd("uid:{0}:reviewed".format(reviewer_id), movie_id)
            pipe.zadd("uid:{0}:reviews".format(reviewer_id), rating, movie_id)
            pipe.sadd("movie:{0}:reviewers".format(movie_id), reviewer_id)
            pipe.zadd("movie:{0}:reviews".format(movie_id), rating, reviewer_id)
            pipe.execute()

    def save_similarity_scores(self, movie, scores):
        """
        Persist calculated similarity scores to Redis. Expects ``scores`` as a
        list of two tuples of (score, movie_id)
        """
        with self.redis.pipeline() as pipe:
            for score, movie_id in scores:
                pipe.zadd("movie:{0}:similarities".format(movie), score, movie_id)
            pipe.execute()

    def get_unrated_movies_for(self, reviewer_id):
        """
        Return a set of movie ids that the given reviewer has not yet rated.

        If there is no record of the given reviewer_id, returns all movies.
        """
        unrated = self.redis.sdiff("movies", "uid:{0}:reviewed".format(reviewer_id))
        return set_to_ints(unrated)

    def get_reviewers(self):
        """
        Return a set of all reviewers.
        """
        users = self.redis.smembers("users")
        return set_to_ints(users)

    def get_reviewers_for_movie(self, movie_id):
        """
        Return a set of all reviewers who have rated the given movie.
        """
        users = self.redis.smembers("movie:{0}:reviewers".format(movie_id))
        return set_to_ints(users)

    def get_reviewer_rating_for_movie(self, reviewer_id, movie_id):
        """
        Retrieve the reviewer's rating for the given movie.
        """
        return self.redis.zscore("uid:{0}:reviews".format(reviewer_id), movie_id)

    def get_common_ratings_for_reviewers(self, reviewer_id_1, reviewer_id_2):
        """
        Returns a list of ratings for all movies that both reviewer_id_1 and
        reviewer_id_2 have rated, as tuples.
        """
        common_movies = self.redis.sinter("uid:{0}:reviewed".format(reviewer_id_1),
                                  "uid:{0}:reviewed".format(reviewer_id_2))
        ratings = []
        for movie_id in common_movies:
            reviewer_1_rating = self.redis.zscore("uid:{0}:reviews".format(reviewer_id_1), movie_id)
            reviewer_2_rating = self.redis.zscore("uid:{0}:reviews".format(reviewer_id_2), movie_id)
            if reviewer_1_rating is not None and reviewer_2_rating is not None:
                ratings.append((reviewer_1_rating, reviewer_2_rating))
        return ratings

    def get_common_ratings_for_movies(self, movie_1, movie_2):
        """
        Returns a list of ratings for all reviewers that have reviewed both
        movie_1 and movie_2, as tuples
        """
        common_reviewers = self.redis.sinter("movie:{0}:reviewers".format(movie_1),
                                     "movie:{0}:reviewers".format(movie_2))
        ratings = []
        for reviewer in common_reviewers:
            movie_1_rating = self.redis.zscore("movie:{0}:reviews".format(movie_1), reviewer)
            movie_2_rating = self.redis.zscore("movie:{0}:reviews".format(movie_2), reviewer)
            if movie_1_rating is not None and movie_2_rating is not None:
                ratings.append((movie_1_rating, movie_2_rating))
        return ratings
