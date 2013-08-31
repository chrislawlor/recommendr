"""
Similarity functions. All functions return a score from 0 to 1, where 1
means most similar and 0 means least similar.
"""
from math import sqrt


def sim_distance(ratings):
    """
    Given a list of ratings as two-tuples, returns the Euclidean distance score
    """
    sum_of_squares = sum([pow(rating1 - rating2, 2)
                          for rating1, rating2 in ratings])
    return 1/(1+sqrt(sum_of_squares))


def sim_pearson(ratings):
    """
    Given a list of ratings as two-tuples, returns the Pearson Correlation score
    """
    num_ratings = len(ratings)
    
    if num_ratings == 0:
        return 0
    
    ratings_1, ratings_2 = zip(*ratings)
    sum_1 = sum(ratings_1)
    sum_2 = sum(ratings_2)
    
    sum_1_sq = sum([rating**2 for rating in ratings_1])
    sum_2_sq = sum([rating**2 for rating in ratings_2])
    
    sum_of_products = sum([rating_1 * rating_2
                           for rating_1, rating_2 in ratings])
    
    numerator = sum_of_products - (sum_1 * sum_2/num_ratings)
    denominator = sqrt((sum_1_sq - sum_1**2/num_ratings) *
                       (sum_2_sq - sum_2**2/num_ratings))
    
    if denominator == 0: return 0
    
    return numerator / denominator

