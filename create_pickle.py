import pandas as pd
import ast
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv("tmdb_5000_movies.csv")
credits = pd.read_csv("tmdb_5000_credits.csv")
movies = movies.merge(credits, on='title')

movies = movies[['movie_id','title','overview','genres','keywords','cast','crew']]
movies.dropna(inplace=True)

def parse(x): return [i['name'] for i in ast.literal_eval(x)]
def cast(x): return [i['name'] for i in ast.literal_eval(x)][:3]
def director(x):
    for i in ast.literal_eval(x):
        if i['job']=='Director': return i['name']
    return ''

movies['genres']=movies['genres'].apply(parse)
movies['keywords']=movies['keywords'].apply(parse)
movies['cast']=movies['cast'].apply(cast)
movies['director']=movies['crew'].apply(director)
movies['overview']=movies['overview'].apply(lambda x:x.split())

movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['director'].apply(lambda x:[x])
movies['tags'] = movies['tags'].apply(lambda x:" ".join(x).lower())

cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(movies['tags']).toarray()
similarity = cosine_similarity(vectors)

pickle.dump(movies, open("movies.pkl","wb"))
pickle.dump(similarity, open("similarity.pkl","wb"))

print("Pickle files created")
