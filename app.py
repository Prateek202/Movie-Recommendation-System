from flask import Flask, render_template, request
import pickle
import requests
import os
import sys

app = Flask(__name__)

# ===============================
# TMDB API KEY
# ===============================
# ⚠️ For production, use environment variables
#API_KEY = "75c3387a1b299a0927c5e78ee5f7df8d"
API_KEY = os.getenv("TMDB_API_KEY")

# ===============================
# GENERATE PICKLE FILES IF MISSING
# ===============================
def generate_pickle_files():
    """Generate pickle files from CSV if they don't exist"""
    if not os.path.exists("movies.pkl") or not os.path.exists("similarity.pkl"):
        print("Generating pickle files from CSV...")
        try:
            import pandas as pd
            import ast
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            movies_df = pd.read_csv("tmdb_5000_movies.csv")
            credits = pd.read_csv("tmdb_5000_credits.csv")
            movies_df = movies_df.merge(credits, on='title')
            
            movies_df = movies_df[['movie_id','title','overview','genres','keywords','cast','crew']]
            movies_df.dropna(inplace=True)
            
            def parse(x): return [i['name'] for i in ast.literal_eval(x)]
            def cast(x): return [i['name'] for i in ast.literal_eval(x)][:3]
            def director(x):
                for i in ast.literal_eval(x):
                    if i['job']=='Director': return i['name']
                return ''
            
            movies_df['genres']=movies_df['genres'].apply(parse)
            movies_df['keywords']=movies_df['keywords'].apply(parse)
            movies_df['cast']=movies_df['cast'].apply(cast)
            movies_df['director']=movies_df['crew'].apply(director)
            movies_df['overview']=movies_df['overview'].apply(lambda x:x.split())
            
            movies_df['tags'] = movies_df['overview'] + movies_df['genres'] + movies_df['keywords'] + movies_df['cast'] + movies_df['director'].apply(lambda x:[x])
            movies_df['tags'] = movies_df['tags'].apply(lambda x:" ".join(x).lower())
            
            cv = CountVectorizer(max_features=5000, stop_words='english')
            vectors = cv.fit_transform(movies_df['tags']).toarray()
            similarity_matrix = cosine_similarity(vectors)
            
            pickle.dump(movies_df, open("movies.pkl","wb"))
            pickle.dump(similarity_matrix, open("similarity.pkl","wb"))
            print("✓ Pickle files generated successfully")
        except Exception as e:
            print(f"✗ Error generating pickle files: {e}")
            sys.exit(1)

# Generate pickle files before loading
generate_pickle_files()

# ===============================
# LOAD PICKLE FILES
# ===============================
movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ===============================
# FETCH MOVIE DETAILS
# ===============================
def fetch_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    poster_path = data.get("poster_path")
    poster_url = (
        f"https://image.tmdb.org/t/p/w500{poster_path}"
        if poster_path else
        "https://via.placeholder.com/500x750?text=No+Image"
    )

    return {
        "title": data.get("title", "N/A"),
        "overview": data.get("overview", "No overview available."),
        "rating": data.get("vote_average", "N/A"),
        "poster": poster_url
    }

# ===============================
# RECOMMENDATION LOGIC
# ===============================
def recommend(movie):
    movie = movie.lower()
    titles = movies['title'].str.lower()

    if movie not in titles.values:
        return []

    index = titles[titles == movie].index[0]
    scores = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommendations = []
    for i in scores:
        movie_id = movies.iloc[i[0]].movie_id
        recommendations.append(fetch_details(movie_id))

    return recommendations

# ===============================
# ROUTES
# ===============================
@app.route("/", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        movie = request.form.get("movie")
    else:
        movie = "Avatar"

    recommendations = recommend(movie) if movie else []

    return render_template(
        "index.html",
        movies=movies['title'].values,
        recommendations=recommendations
    )


# ===============================
# RUN APP
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
