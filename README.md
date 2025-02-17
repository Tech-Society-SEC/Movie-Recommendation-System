# Movie Recommendation System 

## Table of Contents
1. [Overview](#overview)
2. [Project Repository](#project-repository)
3. [How to Run the Project](#how-to-run-the-project)
4. [Importing Required Libraries](#1-importing-required-libraries)
5. [Load Dataset (Caching for Performance)](#2-load-dataset-caching-for-performance)
6. [Data Processing](#3-data-processing)
7. [Content-Based Recommendation System Algorithm](#4-content-based-recommendation-system-algorithm)
    - [Step 1: Data Preparation](#step-1-data-preparation)
    - [Step 2: TF-IDF Vectorization](#step-2-tf-idf-vectorization)
    - [Step 3: Computing Cosine Similarity](#step-3-computing-cosine-similarity)
    - [Step 4: Making Movie Recommendations](#step-4-making-movie-recommendations)
8. [Streamlit User Interface](#5-streamlit-user-interface)
    - [Page Setup](#page-setup)
9. [Movie Search and Filtering](#6-movie-search-and-filtering)
    - [Sidebar (Genre Filter)](#sidebar-genre-filter)
    - [Movie Search](#movie-search)
10. [Conclusion](#conclusion)
    - [Key Features](#key-features)

## Overview
This Streamlit-based movie recommendation system allows users to search, explore, and get personalized movie recommendations. It uses content-based filtering with cosine similarity based on movie genres to suggest similar films.

## Project Repository
GitHub: [Movie Recommendation System](https://github.com/Tech-Society-SEC/Movie-Recommendation-System.git)

## How to Run the Project
Follow these steps to run the project on your local machine:

### Prerequisites
Ensure you have the following installed:
- Python 3.x
- Pip (Python package manager)
- Virtual environment (optional but recommended)

### Installation Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/Tech-Society-SEC/Movie-Recommendation-System.git
   cd Movie-Recommendation-System
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the Streamlit application:
   ```sh
   streamlit run app.py
   ```
5. Open the URL displayed in the terminal (usually `http://localhost:8501/`).

## 1. Importing Required Libraries
```python
import streamlit as st
import pandas as pd
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
```

## 2. Load Dataset (Caching for Performance)
```python
@st.cache_data
def load_data():
    df = pd.read_csv("movies.csv")
    return df
```

## 3. Data Processing
```python
def process_data(df):
    df = df.dropna(subset=['title', 'backdrop_path', 'genre_ids', 'id', 'original_language', 
                           'original_title', 'overview', 'popularity', 'poster_path', 
                           'release_date', 'vote_average', 'vote_count']).copy()
    df.loc[:, "genre_ids"] = df["genre_ids"].apply(ast.literal_eval)
    df.loc[:, "genres_combined"] = df["genre_ids"].apply(lambda x: ' '.join(map(str, x)))
    df.loc[:, "title_normalized"] = df["title"].str.lower().str.strip()
    return df
```

### **4. Content-Based Recommendation System Algorithm**

A **content-based recommendation system** suggests movies based on their features (such as genres). This system uses **TF-IDF (Term Frequency-Inverse Document Frequency) vectorization** and **cosine similarity** to compare and recommend similar movies.

#### **Step 1: Data Preparation**
We first extract and preprocess genre information from the dataset:

```python
df.loc[:, "genre_ids"] = df["genre_ids"].apply(ast.literal_eval)
df.loc[:, "genres_combined"] = df["genre_ids"].apply(lambda x: ' '.join(map(str, x)))
```

- **`genre_ids`** is a list of numerical genre representations.
- **`genres_combined`** converts them into a space-separated string for text processing.

#### **Step 2: TF-IDF Vectorization**
We transform the genre data into numerical vectors using **TF-IDF**.

```python
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['genres_combined'])
```

- **TF-IDF (Term Frequency-Inverse Document Frequency)** converts text (genres) into numerical values.
- It assigns weights to words (genre IDs), giving higher importance to rare genres while downplaying common ones.

#### **Step 3: Computing Cosine Similarity**
Once we have the TF-IDF vectors, we calculate cosine similarity:

```python
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
```

- **Cosine similarity** measures the angle between two genre vectors.
- Higher similarity values indicate more similar movies.

#### **Step 4: Making Movie Recommendations**
The system finds the most similar movies to a given title:

```python
def get_recommendations(title, df, cosine_sim):
    title = title.lower().strip()
    if title not in df['title_normalized'].values:
        return pd.DataFrame()

    indices = pd.Series(df.index, index=df['title_normalized']).drop_duplicates()
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:20]
    movie_indices = [i[0] for i in sim_scores]
    return df.iloc[movie_indices]
```

- Normalizes the title and checks if it exists in the DataFrame.
- Computes cosine similarity to find similar movies.
- Sorts results by similarity and returns the top 20 recommendations.

---

### **5. Streamlit User Interface**

#### **Page Setup**

```python
st.set_page_config(page_title="NEXEN - Movie Recommendation", layout="wide")
st.title("🍿 NEXEN - Movie Recommendation System")
```

- **`st.set_page_config()`**: Configures the page title and layout.
- **`st.title()`**: Sets the app's main title.

---

### **6. Movie Search and Filtering**

#### **Sidebar (Genre Filter)**

```python
st.sidebar.subheader("🎭 Filter by Genre")
selected_genre = st.sidebar.multiselect("Select Genres", df['genres_combined'].explode().unique())
submit_sidebar_button = st.sidebar.button("Apply Genre Filter", key="submit_sidebar_button")
```

- Allows users to select multiple genres to filter movies.
- A button to apply the genre filter.

#### **Movie Search**

```python
col1, col2, col3 = st.columns([4, 1, 1])
with col1:
    search_dropdown = st.selectbox("🔍 Select a movie...", ["Select a movie"] + df['title'].tolist())
with col2:
    submit_main_button = st.button("Submit", key="submit_main_button")
```

- A search bar (`selectbox`) to search for a movie.
- A submit button to trigger movie recommendations or filtering.

---

### **Conclusion**

This system provides a user-friendly interface for exploring and discovering movies, with a combination of search, genre-based filtering, and content-based recommendations powered by cosine similarity.

### **Key Features**
- Movie search by title.
- Genre filtering.
- Random movie suggestion ("Surprise Me!").
- Content-based recommendations based on movie genres.

---

