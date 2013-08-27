"""
Split ratings.dat into a total of three files, as follows:

From the set of all ratings, divide the set into two files:

* ratings_training.dat

* ratings_test.dat

The ratings are divided by taking approximately 20 percent of a given user's
ratings for testing, and the rest go to training, using random sampling.

Thus, all users should have ratings in both ``ratings_training.dat`` and
``ratings_test.dat``.

Since the training data set is quite large, a smaller file ``ratings_dev.dat``
is created by taking a random sample comprising 20 percent of the user
population, and copying all of the sample population's ratings to
``ratings_dev.dat``. Thus, not all users are represented in
``ratings_dev.dat``, and no rating contained in ``ratings_test.dat`` is
included in any other dataset.
"""

import random
import os

DEV_SAMPLE_SIZE = 200


DIR = os.path.dirname(os.path.abspath(__file__))


def split_ratings():
    """
    For each user, save 20 percent of their ratings to the test dataset.
    """
    test_count = 0
    training_count = 0
    dev_count = 0

    user_ratings = {}  # all ratings, keyed by user
    movie_ratings = {}  # ratings in training dataset, keyed by movie id
    movies = {}  # movie info, keyed by movie id

    # Divide ratings.dat into training and test datasets

    with open(os.path.join(DIR, 'ratings.dat'), 'r') as ratingsfile:
        for line in ratingsfile.readlines():
            user_id = line.split("::", 1)[0]
            if user_id not in user_ratings:
                user_ratings[user_id] = [line]
            else:
                user_ratings[user_id].append(line)

    with open(os.path.join(DIR, 'ratings_test.dat'), 'w') as test_ratings_file:
        with open(os.path.join(DIR, 'ratings_training.dat'), 'w') as training_ratings_file:
            for user in user_ratings.keys():
                ratings = user_ratings[user]
                num_ratings = len(ratings) / 5
                test_data = random.sample(ratings, num_ratings)
                test_data = set(test_data)
                ratings = set(ratings)
                training_data = ratings.difference(test_data)

                for rating in test_data:
                    test_ratings_file.write(rating)
                    test_count += 1

                for rating in training_data:
                    training_ratings_file.write(rating)
                    movie_id = rating.split('::', 2)[1]
                    if movie_id not in movie_ratings:
                        movie_ratings[movie_id] = [rating]
                    else:
                        movie_ratings[movie_id].append(rating)
                    training_count += 1

    # Load all movie data into memory
    with open(os.path.join(DIR, 'movies.dat'), 'r') as movies_file:
        for movie in movies_file:
            movie_id = movie.split('::')[0]
            movies[movie_id] = movie

    # Write out a sample set of movies for development use.
    with open(os.path.join(DIR, 'movies_dev.dat'), 'w') as movies_dev_file:
        with open(os.path.join(DIR, 'ratings_dev.dat'), 'w') as ratings_dev_file:
            sample_movies = random.sample(movies.keys(), DEV_SAMPLE_SIZE)
            for movie_id in sample_movies:
                movies_dev_file.write(movies[movie_id])

                if movie_id in movie_ratings:
                    for rating in movie_ratings[movie_id]:
                        ratings_dev_file.write(rating)
                        dev_count += 1

    print("Added {0} ratings to ratings_test.dat".format(test_count))
    print("Added {0} ratings to ratings_training.dat".format(training_count))
    print("Added {0} ratings to ratings_dev.dat".format(dev_count))


if __name__ == '__main__':
    split_ratings()
