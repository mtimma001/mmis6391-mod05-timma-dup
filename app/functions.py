from app.db_connect import get_db

# Function to filter movies by genre
def filter_movies_by_genre(genre_id):
    db = get_db()
    cursor = db.cursor()
    query = '''
        SELECT m.movie_id, m.title, m.release_year, GROUP_CONCAT(g.genre_name) AS genres
        FROM movies m
        JOIN movie_genres mg ON m.movie_id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.genre_id
        WHERE g.genre_id = %s
        GROUP BY m.movie_id
    '''
    cursor.execute(query, (genre_id,))
    filtered_movies = cursor.fetchall()
    return filtered_movies

# Function to filter movies by title
def filter_movies_by_title(title):
    db = get_db()
    cursor = db.cursor()
    query = '''
        SELECT m.movie_id, m.title, m.release_year, GROUP_CONCAT(g.genre_name) AS genres
        FROM movies m
        LEFT JOIN movie_genres mg ON m.movie_id = mg.movie_id
        LEFT JOIN genres g ON mg.genre_id = g.genre_id
        WHERE m.title LIKE %s
        GROUP BY m.movie_id
    '''
    cursor.execute(query, ('%' + title + '%',))
    filtered_movies = cursor.fetchall()
    return filtered_movies

# Function to filter movies by year
def filter_movies_by_year(release_year):
    db = get_db()
    cursor = db.cursor()
    query = '''
        SELECT m.movie_id, m.title, m.release_year, GROUP_CONCAT(g.genre_name) AS genres
        FROM movies m
        LEFT JOIN movie_genres mg ON m.movie_id = mg.movie_id
        LEFT JOIN genres g ON mg.genre_id = g.genre_id
        WHERE m.release_year = %s
        GROUP BY m.movie_id
    '''
    cursor.execute(query, (release_year,))
    filtered_movies = cursor.fetchall()
    return filtered_movies
