import pandas as pd
from flask.helpers import send_from_directory
from flask_cors import CORS, cross_origin
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify
import os
import requests

# Initialize the Flask app with static folder configuration
app = Flask(__name__, static_folder='movie-recommender-app/build', static_url_path='/')
CORS(app)

# Use a valid environment variable to store your TMDb API key
API_KEY = os.getenv('9bd3b509b567015b50c99c50eb204a57')

@app.route('/api/genres', methods=['GET'])
def get_genres():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}"
    response = requests.get(url)
    return jsonify(response.json())

@app.route('/api/movies', methods=['GET'])
def get_movies():
    url = f"https://api.themoviedb.org/3/discover/movie?sort_by=popularity.desc&api_key={API_KEY}"
    response = requests.get(url)
    return jsonify(response.json())

@app.route('/api/search_movie', methods=['GET'])
def search_movie():
    query = request.args.get('query')
    if query:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}"
        response = requests.get(url)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Unable to fetch data from TMDb"}), response.status_code
    return jsonify({"error": "No query parameter provided"}), 400

# Recommendation functionality using local dataset
def createSimilarity():
    data = pd.read_csv('main_data.csv')
    cv = CountVectorizer()
    countMatrix = cv.fit_transform(data['comb'])
    similarity = cosine_similarity(countMatrix)
    return (data, similarity)

def getAllMovies():
    data = pd.read_csv('main_data.csv')
    return list(data['movie_title'].str.capitalize())

def Recommend(movie):
    movie = movie.lower()
    try:
        data.head()
        similarity.shape
    except:
        (data, similarity) = createSimilarity()
    if movie not in data['movie_title'].unique():
        return 'Sorry! The movie you requested is not present in our database.'
    else:
        movieIndex = data.loc[data['movie_title'] == movie].index[0]
        lst = list(enumerate(similarity[movieIndex]))
        lst = sorted(lst, key=lambda x: x[1], reverse=True)
        lst = lst[1:20]
        movieList = [data['movie_title'][i[0]] for i in lst]
        return movieList

@app.route('/api/similarity/<name>')
@cross_origin()
def similarity(name):
    recommendations = Recommend(name)
    if isinstance(recommendations, str):
        return jsonify({"movies": recommendations.split('---')})
    return jsonify({"movies": recommendations})

@app.route('/')
@cross_origin()
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
