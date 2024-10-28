from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.db_connect import get_db

movies = Blueprint('movies', __name__)


# Add a new route to handle movie data
@movies.route('/movies', methods=['GET', 'POST'])
def movie():
    db = get_db()
    cursor = db.cursor()

    # Handle POST request to add a new movie
    if request.method == 'POST':
        title = request.form['title']
        release_year = request.form['release_year']
        movie_genres = request.form.getlist('genres')  # Get a list of movie genres

        # Fetch all genre IDs from the database
        cursor.execute('SELECT genre_id FROM genres')
        fetched_genres = cursor.fetchall()
        valid_genres = [str(fetched_genre['genre_id']) for fetched_genre in fetched_genres]

        # Debugging output: print movie genres and valid genres
        print(f"Selected genres from form: {movie_genres}")
        print(f"Valid genres from database: {valid_genres}")

        # Insert the new movie into the database
        cursor.execute('INSERT INTO movies (title, release_year) VALUES (%s, %s)', (title, release_year))
        movie_id = cursor.lastrowid  # Get the ID of the last inserted movie

        # Insert the genres into the movie_genres table
        for movie_genre in movie_genres:
            if movie_genre in valid_genres:  # Check if the genre is valid
                cursor.execute('INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s)', (movie_id, movie_genre))
            else:
                flash(f"Invalid genre ID: {movie_genre}", 'danger')
                db.rollback()  # Roll back the transaction if an invalid genre is detected
                print(f"Invalid genre ID: {movie_genre}")  # Debug message for invalid genres
                return redirect(url_for('movies.movie'))

        db.commit()

        flash('New movie added successfully!', 'success')
        return redirect(url_for('movies.movie'))

    # Handle GET request to display all movies
    cursor.execute('''
        SELECT m.movie_id, m.title, m.release_year, GROUP_CONCAT(g.genre_name) AS genres
        FROM movies m
        LEFT JOIN movie_genres mg ON m.movie_id = mg.movie_id
        LEFT JOIN genres g ON mg.genre_id = g.genre_id
        GROUP BY m.movie_id
        ''')
    all_movies = cursor.fetchall()

    # Get all genres
    cursor.execute('SELECT * FROM genres')
    all_genres = cursor.fetchall()
    return render_template('movies.html', all_movies=all_movies, all_genres=all_genres)


# Add a new route to handle updating a movie
@movies.route('/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(movie_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        title = request.form['title']
        release_year = request.form['release_year']
        movie_genres = request.form.getlist('genres')  # Get a list of movie genres

        # Update the movie in the database
        cursor.execute('UPDATE movies SET title=%s, release_year=%s WHERE movie_id=%s', (title, release_year, movie_id))

        # Fetch valid genre IDs from the database
        cursor.execute('SELECT genre_id FROM genres')
        fetched_genres = cursor.fetchall()
        valid_genres = [str(fetched_genre['genre_id']) for fetched_genre in fetched_genres]

        # Delete the existing genres for the movie to avoid duplication
        cursor.execute('DELETE FROM movie_genres WHERE movie_id=%s', (movie_id,))

        # Insert the selected genres into the movie_genres table
        for movie_genre in movie_genres:
            if movie_genre in valid_genres:
                cursor.execute('INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s)', (movie_id, movie_genre))
            else:
                flash(f"Invalid genre ID: {movie_genre}", 'danger')
                db.rollback()  # Roll back the transaction if an invalid genre is detected
                print(f"Invalid genre ID: {movie_genre}")  # Debug message for invalid genres
                return redirect(url_for('movies.update_movie', movie_id=movie_id))

        db.commit()

        flash('Movie updated successfully!', 'success')
        return redirect(url_for('movies.movie'))

    # Handle GET request to display the current movie and its genres
    cursor.execute('SELECT movie_id, title, release_year FROM movies WHERE movie_id = %s', (movie_id,))
    one_movie = cursor.fetchone()

    cursor.execute('SELECT genre_id FROM movie_genres WHERE movie_id = %s', (movie_id,))
    fetched_genres = cursor.fetchall()
    selected_genres = [str(fetched_genre['genre_id']) for fetched_genre in fetched_genres]

    cursor.execute('SELECT genre_id, genre_name FROM genres')
    all_genres = cursor.fetchall()

    return render_template('update_movie.html', movie=one_movie, selected_genres=selected_genres, all_genres=all_genres)


# Add a new route to handle deleting a movie
@movies.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    db = get_db()
    cursor = db.cursor()

    # Delete the movie and its associated genres
    cursor.execute('DELETE FROM movies WHERE movie_id=%s', (movie_id,))
    cursor.execute('DELETE FROM movie_genres WHERE movie_id=%s', (movie_id,))
    db.commit()

    flash('Movie deleted successfully!', 'success')
    return redirect(url_for('movies.movie'))


# Add a new route to handle genre data
@movies.route('/genres', methods=['GET', 'POST'])
def genre():
    db = get_db()
    cursor = db.cursor()

    # Handle POST request to add a new genre
    if request.method == 'POST':
        genre_name = request.form['genre_name']

        # Insert the new genre into the database
        cursor.execute('INSERT INTO genres (genre_name) VALUES (%s)', (genre_name,))
        db.commit()

        flash('New genre added successfully!', 'success')
        return redirect(url_for('movies.genre'))

    # Handle GET request to display all genres
    cursor.execute('SELECT * FROM genres')
    all_genres = cursor.fetchall()
    return render_template('genres.html', all_genres=all_genres)


# Add a new route to handle updating a genre
@movies.route('/update_genre/<int:genre_id>', methods=['GET', 'POST'])
def update_genre(genre_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        genre_name = request.form['genre_name']

        # Update the genre in the database
        cursor.execute('UPDATE genres SET genre_name=%s WHERE genre_id=%s', (genre_name, genre_id))
        db.commit()

        flash('Genre updated successfully!', 'success')
        return redirect(url_for('movies.genre'))

    # Get the genre to update
    cursor.execute('SELECT * FROM genres WHERE genre_id=%s', (genre_id,))
    movie_genre = cursor.fetchone()
    return render_template('update_genre.html', genre=movie_genre)


# Add a new route to handle deleting a genre
@movies.route('/delete_genre/<int:genre_id>', methods=['POST'])
def delete_genre(genre_id):
    db = get_db()
    cursor = db.cursor()

    # Delete the genre and the associated movie_genres
    cursor.execute('DELETE FROM genres WHERE genre_id=%s', (genre_id,))
    cursor.execute('DELETE FROM movie_genres WHERE genre_id=%s', (genre_id,))
    db.commit()

    flash('Genre deleted successfully!', 'success')
    return redirect(url_for('movies.genre'))
