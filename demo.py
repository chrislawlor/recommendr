import argparse
import random

from recommendr import db, get_user_based_recommendations


def rate_movie(user_id, movie_id):
    print("Have you seen %s" % db.get_name_for_movie(movie_id))
    confirm = raw_input("'y' for yes: ")
    if confirm.lower() != 'y':
        return False
    print("How would you rate it (1-5)?")
    rating = None
    while rating is None:
        rating = raw_input()
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                print("Please enter a number between 1 and 5")
                rating = None
        except ValueError:
            print("Please enter a whole number between 1 and 5")
            rating = None
    db.add_rating(user_id, movie_id, rating)
    return True


def rate_movies(user_id):
    unrated = list(db.get_unrated_movies_for(user_id))
    asked = []

    # Have the user review 5 movies
    rated = 0
    while rated < 5:
        movie_id = random.choice(unrated)
        if movie_id in asked:
            continue
        asked.append(movie_id)
        seen = rate_movie(user_id, movie_id)
        if seen:
            rated += 1


def get_recommendations(user_id):
    print("OK, let me think...")

    recommendations = get_user_based_recommendations(user_id, num=10)

    print("Based on your ratings, I recommend the following movies:")
    print("\n")
    print("Guess\tID\tMovie")
    for score, movie_id in recommendations:
        print("{1:0.2f}\t{2}\t{0}".format(db.get_name_for_movie(movie_id), score, movie_id))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--movie", type=int,
                        help="Rate a particular movie ID.")
    parser.add_argument("-r", "--recommendations", action="store_true",
                        help="Recommendations only.")
    parser.add_argument('-u', '--user', type=int, default=10000,
                        help="User id. Defaults to 10000")
    args = parser.parse_args()

    if args.movie:
        rate_movie(args.user, args.movie)
    else:
        if not args.recommendations:
            rate_movies(args.user)
        get_recommendations(args.user)
