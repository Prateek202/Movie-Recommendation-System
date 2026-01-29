import pandas as pd
import numpy as np
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ======================================================
# LOAD DATA
# ======================================================

movies = pd.read_csv("tmdb_5000_movies.csv")
credits = pd.read_csv("tmdb_5000_credits.csv")

movies = movies.merge(credits, on="title")

# ======================================================
# CLEAN & SELECT FEATURES
# ======================================================

movies = movies[['movie_id', 'title', 'overview',
                 'genres', 'keywords', 'cast', 'crew']]

movies.dropna(inplace=True)

# ======================================================
# HELPER FUNCTIONS
# ======================================================

def parse_names(text):
    return [i['name'] for i in ast.literal_eval(text)]

def parse_cast(text):
    return [i['name'] for i in ast.literal_eval(text)][:3]

def parse_director(text):
    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            return i['name']
    return ""

def clean_words(words):
    return [w.replace(" ", "").lower() for w in words]

# ======================================================
# APPLY PARSING
# ======================================================

movies['genres'] = movies['genres'].apply(parse_names).apply(clean_words)
movies['keywords'] = movies['keywords'].apply(parse_names).apply(clean_words)
movies['cast'] = movies['cast'].apply(parse_cast).apply(clean_words)
movies['director'] = movies['crew'].apply(parse_director).apply(lambda x: x.replace(" ", "").lower())

movies['overview'] = movies['overview'].apply(lambda x: x.lower().split())

# ======================================================
# CREATE TAGS (BAG OF WORDS)
# ======================================================

movies['tags'] = (
    movies['overview'] +
    movies['genres'] +
    movies['keywords'] +
    movies['cast'] +
    movies['director'].apply(lambda x: [x])
)

movies['tags'] = movies['tags'].apply(lambda x: " ".join(x))

final_df = movies[['movie_id', 'title', 'tags']]

# ======================================================
# VECTORIZATION (BAG OF WORDS)
# ======================================================

cv = CountVectorizer(
    max_features=5000,
    stop_words='english'
)

vectors = cv.fit_transform(final_df['tags']).toarray()

# ======================================================
# COSINE SIMILARITY
# ======================================================

similarity = cosine_similarity(vectors)

# ======================================================
# RECOMMENDATION FUNCTION
# ======================================================

def recommend(movie_title, top_n=5):
    movie_title = movie_title.lower()
    titles = final_df['title'].str.lower()

    if movie_title not in titles.values:
        print("Movie not found.")
        return

    index = titles[titles == movie_title].index[0]
    scores = list(enumerate(similarity[index]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    print(f"\nRecommendations for '{final_df.iloc[index].title}':\n")

    for i in scores[1:top_n+1]:
        print(final_df.iloc[i[0]].title)

# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":
    recommend("batman begins")
