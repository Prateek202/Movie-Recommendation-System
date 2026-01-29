from flask import Flask, render_template, request
import pickle
import requests
import os




app = Flask(__name__)

# ===============================
# TMDB API KEY
# ===============================
# ⚠️ For production, use environment variables
#API_KEY = "75c3387a1b299a0927c5e78ee5f7df8d"
API_KEY = os.getenv("TMDB_API_KEY")

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
