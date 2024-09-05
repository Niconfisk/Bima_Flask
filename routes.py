from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db_connection

# Criação do Blueprint
bp = Blueprint('main', __name__)

# Rota principal (index) - exibe livros com título, autor, descrição e ações
@bp.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute('''
        SELECT b.id, b.title, b.description, GROUP_CONCAT(a.name, ', ') AS authors
        FROM books b
        LEFT JOIN book_authors ba ON b.id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.id
        GROUP BY b.id
    ''').fetchall()
    conn.close()
    return render_template('index.html', books=books)

# Rota para listar todos os livros
@bp.route('/books')
def books():
    conn = get_db_connection()
    books = conn.execute('''
        SELECT b.id, b.title, b.description, GROUP_CONCAT(a.name, ', ') AS authors
        FROM books b
        LEFT JOIN book_authors ba ON b.id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.id
        GROUP BY b.id
    ''').fetchall()
    conn.close()
    return render_template('books.html', books=books)

# Rota para listar todos os autores
@bp.route('/authors')
def authors():
    conn = get_db_connection()
    authors = conn.execute('SELECT * FROM authors').fetchall()
    conn.close()
    return render_template('authors.html', authors=authors)

# Rota para adicionar um novo livro
@bp.route('/add_book', methods=['GET', 'POST'])
def add_book():
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        authors = request.form.getlist('authors')
        
        conn.execute('INSERT INTO books (title, description) VALUES (?, ?)', (title, description))
        book_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        for author_id in authors:
            conn.execute('INSERT INTO book_authors (book_id, author_id) VALUES (?, ?)', (book_id, author_id))
        
        conn.commit()
        return redirect(url_for('main.index'))
    
    authors = conn.execute('SELECT * FROM authors').fetchall()
    return render_template('add_book.html', authors=authors)

# Rota para adicionar um novo autor
@bp.route('/add_author', methods=('GET', 'POST'))
def add_author():
    if request.method == 'POST':
        name = request.form['name']

        conn = get_db_connection()
        conn.execute('INSERT INTO authors (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()

        return redirect(url_for('main.authors'))

    return render_template('add_author.html')

# Rota para editar um livro
@bp.route('/edit_book/<int:id>', methods=('GET', 'POST'))
def edit_book(id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        author_ids = request.form.getlist('authors')

        conn.execute('UPDATE books SET title = ?, description = ? WHERE id = ?',
                     (title, description, id))
        conn.execute('DELETE FROM book_authors WHERE book_id = ?', (id,))
        for author_id in author_ids:
            conn.execute('INSERT INTO book_authors (book_id, author_id) VALUES (?, ?)',
                         (id, author_id))

        conn.commit()
        conn.close()

        return redirect(url_for('main.books'))

    authors = conn.execute('SELECT id, name FROM authors').fetchall()
    selected_authors = conn.execute('SELECT author_id FROM book_authors WHERE book_id = ?', (id,)).fetchall()
    selected_authors = [author['author_id'] for author in selected_authors]
    conn.close()

    return render_template('edit_book.html', book=book, authors=authors, selected_authors=selected_authors)

# Rota para excluir um livro
@bp.route('/delete_book/<int:id>', methods=('POST',))
def delete_book(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('main.books'))

@bp.route('/delete_author/<int:id>', methods=['POST'])
def delete_author(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM authors WHERE id = ?', (id,))
    conn.execute('DELETE FROM book_authors WHERE author_id = ?', (id,))
    conn.commit()
    return redirect(url_for('main.authors'))

@bp.route('/edit_author/<int:id>', methods=['GET', 'POST'])
def edit_author(id):
    conn = get_db_connection()
    author = conn.execute('SELECT * FROM authors WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        name = request.form['name']
        
        conn.execute('UPDATE authors SET name = ? WHERE id = ?', (name, id))
        conn.commit()
        return redirect(url_for('main.authors'))
    
    return render_template('edit_author.html', author=author)


