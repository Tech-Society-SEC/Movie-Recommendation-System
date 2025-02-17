import streamlit as st
import pandas as pd
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random  # Import the random module for selecting a random movie

# Load dataset with caching for better performance
@st.cache_data
def load_data():
    df = pd.read_csv("movies.csv")
    return df

# Process dataset: handle missing values and extract necessary fields
def process_data(df):
    df = df.dropna(subset=['title', 'backdrop_path', 'genre_ids', 'id', 'original_language',
                           'original_title', 'overview', 'popularity', 'poster_path',
                           'release_date', 'vote_average', 'vote_count']).copy()
    
    df.loc[:, "genre_ids"] = df["genre_ids"].apply(ast.literal_eval)
    df.loc[:, "genres_combined"] = df["genre_ids"].apply(lambda x: ' '.join(map(str, x)))
    df.loc[:, "title_normalized"] = df["title"].str.lower().str.strip()
    
    return df

# Get movie recommendations based on cosine similarity
def get_recommendations(title, df, cosine_sim):
    title = title.lower().strip()
    
    if title not in df['title_normalized'].values:
        return pd.DataFrame()
    
    indices = pd.Series(df.index, index=df['title_normalized']).drop_duplicates()
    idx = indices[title]
    
    if isinstance(idx, pd.Series):  # Handle duplicate movie titles
        idx = idx.iloc[0]
    
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:20]
    movie_indices = [i[0] for i in sim_scores]
    
    return df.iloc[movie_indices]

# Streamlit UI setup
st.set_page_config(page_title="NEXEN - Movie Recommendation", layout="wide")
st.title("🍿 NEXEN - Movie Recommendation System")

df = load_data()
df = process_data(df)

# TF-IDF and Cosine Similarity for Content-Based Filtering
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['genres_combined'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Initialize session state variables
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None
if "explore_movies" not in st.session_state:
    st.session_state.explore_movies = df.sample(12)  # Initial movie list


# Genre filter section
st.sidebar.subheader("🎭 Filter by Genre")
selected_genre = st.sidebar.multiselect("Select Genres", df['genres_combined'].explode().unique())

# Submit button in the sidebar to apply genre filter
submit_sidebar_button = st.sidebar.button("Apply Genre Filter", key="submit_sidebar_button")

# Main section: Layout with Submit Button to the Right of the Search Bar
col1, col2, col3 = st.columns([4, 1, 1])  # 4 parts for search bar, 1 for submit button

# Left column: Search bar
with col1:
    search_dropdown = st.selectbox("🔍 Select a movie...", ["Select a movie"] + df['title'].tolist())

# Middle column: Submit button (main section)
with col2:
    submit_main_button = st.button("Submit", key="submit_main_button")

# Surprise Button functionality
if st.sidebar.button("🎲 Surprise Me!", key="surprise_me_button"):
    random_movie = df.sample(1).iloc[0]  # Select a random movie
    st.session_state.selected_movie = random_movie['title']  # Set the selected movie to the random one
    
    
# Handle genre filter and movie search only when the submit button is clicked
if submit_main_button:
    if search_dropdown != "Select a movie":
        st.session_state.selected_movie = search_dropdown  # Update selected movie from dropdown
    
    # Filter movies based on selected genres or show content-based recommendations
    if st.session_state.selected_movie:
        explore_movies = get_recommendations(st.session_state.selected_movie, df, cosine_sim)
    elif selected_genre:
        explore_movies = df[df['genres_combined'].apply(lambda x: any(genre in x for genre in selected_genre))]
    else:
        explore_movies = df.sample(12)  # Shuffle movies if no filter is applied
    st.session_state.explore_movies = explore_movies

# Handle genre filter separately if the sidebar button is clicked
if submit_sidebar_button and selected_genre:
    explore_movies = df[df['genres_combined'].apply(lambda x: any(genre in x for genre in selected_genre))]
    st.session_state.explore_movies = explore_movies

# Display movie details and recommendations
if st.session_state.selected_movie:
    movie_details = df[df['title'] == st.session_state.selected_movie].iloc[0]
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(f"https://image.tmdb.org/t/p/w500{movie_details['poster_path']}", use_container_width=True)
    
    with col2:
        st.subheader(f"🎮 {movie_details['title']}")
        st.markdown(f"""
        *🆔 ID:* {movie_details['id']}  
        *🌍 Original Language:* {movie_details['original_language']}  
        *📝 Original Title:* {movie_details['original_title']}  
        *⭐ Rating:* {movie_details['vote_average']} ({movie_details['vote_count']} votes)  
        *🔥 Popularity:* {movie_details['popularity']}  
        *📅 Release Date:* {movie_details['release_date']}  
        """)
        st.write(f"📖 Overview: {movie_details['overview']}")

st.subheader("🎥 Explore Movies")

# Display the recommended movies or shuffled movies
explore_movies = st.session_state.explore_movies
rec_cols = st.columns(4)

for i, movie in enumerate(explore_movies.itertuples(), start=1):
    with rec_cols[(i - 1) % 4]:
        st.image(f"https://image.tmdb.org/t/p/w500{movie.poster_path}", width=150)
        if st.button(f"🎮 {movie.title}", key=f"explore_{movie.id}"):
            st.session_state.selected_movie = movie.title
            st.session_state.explore_movies = get_recommendations(movie.title, df, cosine_sim)
            st.rerun()  # Rerun after selecting a new movie
