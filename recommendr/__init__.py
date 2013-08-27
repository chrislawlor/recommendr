import sys

from eventlet import GreenPool

from .similarity import sim_pearson, sim_distance
from .db import RedisBackend
from .config import REDIS_HOST, REDIS_PORT, REDIS_DB

db = RedisBackend(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


def get_reviewer_similarity(reviewer_1, reviewer_2, sim_function=sim_pearson):
    return sim_function(db.get_common_ratings_for_reviewers(reviewer_1,
                                                            reviewer_2))


def get_movie_similarity(movie_1, movie_2, sim_function=sim_pearson):
    return sim_function(db.get_common_ratings_for_movies(movie_1, movie_2))


def closest_reviewers(reviewer_id, n=5, similarity=sim_pearson):
    others = db.get_reviewers()
    scores = [(get_reviewer_similarity(reviewer_id, other, sim_function=similarity), other)
              for other in others if other != reviewer_id]
    scores.sort()
    scores.reverse()
    return scores[:n]


def closest_movies(movie_id, n=5, similarity=sim_pearson):
    movies = db.get_movies()
    scores = [(get_movie_similarity(movie_id, other, sim_function=similarity), other)
              for other in movies if other != movie_id]
    scores.sort()
    scores.reverse()
    return scores[:n]


def do_movie_similarity_calculation(movie_id, n=10, similarity=sim_pearson):
    sys.stdout.write("Processing {0}\n".format(movie_id))
    scores = closest_movies(movie_id, n=n, similarity=similarity)
    db.save_similarity_scores(movie_id, scores)


def calculate_similar_movies(n=10, similarity=sim_pearson):
    pool = GreenPool(size=30)
    movies = db.get_movies()
    movie_count = len(movies)
    sys.stdout.write("Processing {0} movies\n".format(movie_count))
    for movie in movies:
        pool.spawn_n(do_movie_similarity_calculation, movie, n=n, similarity=sim_distance)
    pool.waitall()


def get_user_based_recommendations(reviewer_id, num=20, similarity=sim_distance):
    totals = {}  # where totals[movie_id] = sum of (ratings * similarity)
    sim_sums = {}

    # get movies reviewer hasn't rated
    unrated_movie_ids = db.get_unrated_movies_for(reviewer_id)

    movie_idx = 0
    for movie_id in unrated_movie_ids:

        movie_idx += 1

        reviewer_ids = db.get_reviewers_for_movie(movie_id)
        for reviewer in reviewer_ids:
            sim = get_reviewer_similarity(reviewer_id, reviewer, sim_function=similarity)

            # ignore scores of zero or lower
            if sim <= 0:
                continue

            rating = db.get_reviewer_rating_for_movie(reviewer, movie_id)

            # similarity * score
            totals.setdefault(movie_id, 0)
            totals[movie_id] += rating * sim
            # sum of similarities
            sim_sums.setdefault(movie_id, 0)
            sim_sums[movie_id] += sim

    # create the normalized list
    rankings = [(total / sim_sums[movie_id], movie_id)
                for movie_id, total in totals.items()]

    # return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings[:20]
