from recommendr.db import RedisBackend

from recommendr.config import REDIS_TEST_HOST, REDIS_TEST_PORT, REDIS_TEST_DB


class TestRedisBackend:

    @classmethod
    def setup_class(cls):
        backend = RedisBackend(host=REDIS_TEST_HOST,
                               port=REDIS_TEST_PORT,
                               db=REDIS_TEST_DB)

        # Start with a clean DB
        backend.clear()
        cls.backend = backend

    def setup(self):
        self.backend.clear()

    def test_add_genre(self):
        genre_id = self.backend.add_genre('Comedy')
        assert self.backend.get_genre_id_by_name("Comedy") == genre_id

    def test_retrieve_missing_genre(self):
        assert self.backend.get_genre_id_by_name('Missing') is None

    def test_get_or_create_genre(self):
        # This time, it should create the genre
        genre_id = self.backend.get_or_create_genre('Drama')
        assert self.backend.get_genre_id_by_name('Drama') == genre_id
        # This time, it should retrieve the genre
        genre_id_2 = self.backend.get_or_create_genre('Drama')
        assert genre_id_2 == genre_id

    def test_add_movie_with_no_genres(self):
        self.backend.add_movie(1, 'Shawshank Redemption')
        movies = self.backend.get_movies()
        assert len(movies) == 1
        assert 1 in movies

    def test_get_name_for_movie(self):
        self.backend.add_movie(1, "Cujo")
        name = self.backend.get_name_for_movie(1)
        assert name == "Cujo"

    def test_get_reviewers(self):
        self.backend.add_movie(1, "Cujo")
        self.backend.add_rating(10, 1, 3)
        reviewers = self.backend.get_reviewers()
        assert 10 in reviewers

    def test_get_unrated_movies_for(self):
        self.backend.add_movie(1, "Cujo")
        self.backend.add_movie(2, "The Shining")
        self.backend.add_rating(10, 1, 3)
        # User 10 hasn't rated The Shining
        unrated = self.backend.get_unrated_movies_for(10)
        assert len(unrated) == 1
        assert 2 in unrated

    def test_get_reviewers_for_movie(self):
        self.backend.add_movie(1, "Cujo")
        self.backend.add_rating(10, 1, 3)
        reviewers = self.backend.get_reviewers_for_movie(1)
        assert 10 in reviewers

    def test_get_reviewer_rating_for_movie(self):
        self.backend.add_movie(1, "Cujo")
        self.backend.add_rating(10, 1, 3)
        rating = self.backend.get_reviewer_rating_for_movie(10, 1)
        assert rating == 3

    def test_get_common_ratings_for_reviewers(self):
        self.backend.add_movie(1, "Cujo")
        self.backend.add_movie(2, "The Shining")
        # User 10 gives Cujo a 3
        self.backend.add_rating(10, 1, 3)
        # User 11 gives Cujo a 4
        self.backend.add_rating(11, 1, 4)
        # User 10 gives The Shining a 5
        self.backend.add_rating(10, 2, 5)
        # User 11 gives The Shining a 2
        #self.backend.add_rating(11, 2, 2)
        ratings = self.backend.get_common_ratings_for_reviewers(10, 11)
        assert len(ratings) == 1
        rating = ratings[0]
        assert rating == (3, 4)

    def test_get_common_ratings_for_movies(self):
        self.backend.add_movie(1, "Cujo")
        self.backend.add_movie(2, "The Shining")
        # User 10 gives Cujo a 3
        self.backend.add_rating(10, 1, 3)
        # User 11 gives Cujo a 4
        self.backend.add_rating(11, 1, 4)
        # User 10 gives The Shining a 5
        self.backend.add_rating(10, 2, 5)
        # User 11 gives The Shining a 2
        self.backend.add_rating(11, 2, 2)
        ratings = self.backend.get_common_ratings_for_movies(1, 2)
        assert len(ratings) == 2
        assert (3, 5) in ratings
        assert (4, 2) in ratings

    def test_ignore_duplicate_ratings(self):
        self.backend.add_movie(1, "Cujo")
        self.backend.add_rating(10, 1, 3)
        