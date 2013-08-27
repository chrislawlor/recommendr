import random

from recommendr import db, calculate_similar_movies, get_user_based_recommendations


def init():
    calculate_similar_movies()


def main():
    initialized = raw_input("Initialize the database?")
    if initialized.lower() == 'y':
        init()

    user_id = raw_input("What is your user id? Enter 10000 if you don't know:")

    unrated = list(db.get_unrated_movies_for(user_id))
    asked = []

    # Have the user review 5 movies
    rated = 0
    while rated < 5:
        movie_id = random.choice(unrated)
        if movie_id in asked:
            continue
        asked.append(movie_id)
        print("Have you seen %s" % db.get_name_for_movie(movie_id))
        confirm = raw_input("y or n?")
        if confirm.lower() == 'n':
            continue
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
        rated += 1

    print("OK, let me think...")

    recommendations = get_user_based_recommendations(user_id, num=10)

    print("Based on your ratings, I recommend the following movies:")

    for score, movie_id in recommendations:
        print("{0}: ({1})".format(db.get_name_for_movie(movie_id), score))


if __name__ == '__main__':
    main()
