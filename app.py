from flask import Flask, render_template, request
import pickle
import requests
import os
import sys

app = Flask(__name__)

# ===============================
# TMDB API KEY
# ===============================
API_KEY = os.getenv("TMDB_API_KEY")

# ===============================
# DOWNLOAD PICKLE FILES FROM GITHUB RELEASES
# ===============================
def download_pickle_files():
    """Download pre-generated pickle files from GitHub Releases"""
    files_to_download = ["movies.pkl", "similarity.pkl"]
    github_release_url = "https://github.com/Prateek202/Movie-Recommendation-System/releases/download/v1.0"
    
    for file_name in files_to_download:
        if not os.path.exists(file_name):
            print(f"Downloading {file_name}...")
            try:
                url = f"{github_release_url}/{file_name}"
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                    print(f"✓ {file_name} downloaded successfully")
                else:
                    print(f"✗ Failed to download {file_name}: HTTP {response.status_code}")
                    print("Make sure pickle files are uploaded to GitHub Releases as v1.0")
                    sys.exit(1)
            except Exception as e:
                print(f"✗ Error downloading {file_name}: {e}")
                sys.exit(1)

# Download pickle files on startup
download_pickle_files()

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
