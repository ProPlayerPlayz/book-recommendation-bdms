from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import fake_data_gen as fdg
import os

global app
app = Flask(__name__)

# Setting Secret key for session
app.secret_key = 'BatchBGroup17EbookStore'

# CREATE DATABASE prolib;
# CREATE USER prop WITH PASSWORD '12345678';
# ALTER ROLE prop SET client_encoding TO 'utf8';
# ALTER ROLE prop SET default_transaction_isolation TO 'read committed';
# ALTER ROLE prop SET timezone TO 'UTC';
# GRANT ALL PRIVILEGES ON DATABASE prolib TO prop;

# Create new database with name testlib
# CREATE DATABASE testlib;

# Setting up Databases
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@db:5432/prolib'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost:5432/prolib'
# format: postgresql://username:password@hostname:port/database_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Books Table
class Books(db.Model):
    ISBN = db.Column(db.String(255), primary_key=True)
    BookTitle = db.Column(db.String(255))
    BookAuthor = db.Column(db.String(255))
    YearOfPublication = db.Column(db.Integer)
    PublisherID = db.Column(db.Integer, db.ForeignKey('publishers.PublisherID'))
    ImageURL = db.Column(db.String(255))
    
# Define Users Table
class Users(db.Model):
    UserID = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(255))
    Location = db.Column(db.String(255))
    Age = db.Column(db.Integer)
    
# Define Ratings Table
class Ratings(db.Model):
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), primary_key=True)
    ISBN = db.Column(db.String(255), db.ForeignKey('books.ISBN'), primary_key=True)
    BookRating = db.Column(db.Integer)

# Define UserLibrary Table
class UserLibrary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.UserID'))
    isbn = db.Column(db.String(255), db.ForeignKey('books.ISBN'))
    date_added = db.Column(db.DateTime, server_default=func.now())

# Define Publishers Table
class Publishers(db.Model):
    PublisherID = db.Column(db.Integer, primary_key=True)
    PublisherName = db.Column(db.String(255))
    PublisherEmail = db.Column(db.String(255))


fdg.generate_fake_data(reset=True)

def add_new_user(username, location, age):
    """
    Add a new user to the database.

    Parameters:
    - username (str): The username of the user.
    - location (str): The location of the user.
    - age (int): The age of the user.

    Returns:
    None
    """
    user = Users(
                UserName = str(username),
                Location= str(location),
                Age=int(age),
                )
    db.session.add(user)

# Index page with Login button and publish button
@app.route('/')
def index():
    return render_template('index.html')

# Login page to login using user id
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        userid = request.form.get('userid')
        username = Users.query.filter_by(UserID=userid).first()
        if username is None:
            return redirect('/login')
        username = username.UserName
        session['user_id'] = userid
        session['username'] = username
        return redirect('/home/' + userid)
    else:
        return render_template('login.html')

# Publisher Login page to login using publisher id
@app.route('/publisher_login', methods=['GET', 'POST'])
def publisher_login_page():
    if request.method == 'POST':
        pid = request.form.get('pid')
        session['pid'] = pid
        return redirect('/publish/' + pid)
    else:
        return render_template('publisher_login.html')
    
# Publish page to add new books
@app.route('/publish/<pid>', methods=['GET', 'POST'])
def publish_page(pid):
    if Publishers.query.filter_by(PublisherID=pid).first() is None:
        return redirect('/publisher_login')
    pname = Publishers.query.filter_by(PublisherID=pid).first().PublisherName
    if request.method == 'POST':
        # get book details from form
        isbn = request.form.get('isbn')
        book_title = request.form.get('book_title')
        book_author = request.form.get('book_author')
        year_of_publication = request.form.get('year_of_publication')
        publisher_name = pname
        image_url = request.form.get('image_url')
        # add book to database
        new_book = Books(ISBN=int(isbn), BookTitle=book_title, BookAuthor=book_author, YearOfPublication=year_of_publication, PublisherID=publisher_name, ImageURL=image_url)
        db.session.add(new_book)
        db.session.commit()
        return render_template('publish.html',status = "Your Book has been Added!", pid=pid, publisherName=pname)
    else:
        return render_template('publish.html',status = "Ready to Add E-book to System!", pid=pid, publisherName=pname)

# Analytics page to view analytics
@app.route('/analytics/<pid>/<time_period>', methods=['GET', 'POST'])
def analytics_page(pid, time_period):
    if request.method == 'POST':
        form_time_period = request.form.get('form_time_period')
        if form_time_period in ['1','12','60']:
            return redirect('/analytics/' + pid + '/' + time_period)
        else:
            return redirect('analytics/'+ pid + '/1')
    else:
        # get query results for sales of the past 1 month, 12 months and 60 months
        # the result is a list of tuples with each tuple containing the time and sales count over that time period
        # for month we need atleast 30 points, for year we need atleast 12 points, for 5 years we need atleast 60 points
        sales_1 = db.session.query(func.date_trunc('day', UserLibrary.date_added).label('time'), func.count(UserLibrary.isbn).label('sales')).filter(Books.PublisherID==pid, UserLibrary.isbn==Books.ISBN, func.date_part('month', UserLibrary.date_added)==func.date_part('month', func.now())).group_by(func.date_trunc('day', UserLibrary.date_added)).order_by(func.date_trunc('day', UserLibrary.date_added)).all()
        sales_12 = db.session.query(func.date_trunc('month', UserLibrary.date_added).label('time'), func.count(UserLibrary.isbn).label('sales')).filter(Books.PublisherID==pid, UserLibrary.isbn==Books.ISBN, func.date_part('year', UserLibrary.date_added)==func.date_part('year', func.now())).group_by(func.date_trunc('month', UserLibrary.date_added)).order_by(func.date_trunc('month', UserLibrary.date_added)).all()
        sales_60 = db.session.query(func.date_trunc('year', UserLibrary.date_added).label('time'), func.count(UserLibrary.isbn).label('sales')).filter(Books.PublisherID==pid, UserLibrary.isbn==Books.ISBN, func.date_part('year', UserLibrary.date_added)>=func.date_part('year', func.now())-5).group_by(func.date_trunc('year', UserLibrary.date_added)).order_by(func.date_trunc('year', UserLibrary.date_added)).all()
        # top books of same three time periods
        top_1 = db.session.query(Books.ISBN, Books.BookTitle, Books.BookAuthor, func.count(UserLibrary.isbn).label('sales')).join(UserLibrary).filter(Books.PublisherID==pid, UserLibrary.isbn==Books.ISBN, func.date_part('month', UserLibrary.date_added)==func.date_part('month', func.now())).group_by(Books.ISBN).order_by(func.count(UserLibrary.isbn).desc()).limit(5).all()
        top_12 = db.session.query(Books.ISBN, Books.BookTitle, Books.BookAuthor, func.count(UserLibrary.isbn).label('sales')).join(UserLibrary).filter(Books.PublisherID==pid, UserLibrary.isbn==Books.ISBN, func.date_part('year', UserLibrary.date_added)==func.date_part('year', func.now())).group_by(Books.ISBN).order_by(func.count(UserLibrary.isbn).desc()).limit(5).all()
        top_60 = db.session.query(Books.ISBN, Books.BookTitle, Books.BookAuthor, func.count(UserLibrary.isbn).label('sales')).join(UserLibrary).filter(Books.PublisherID==pid, UserLibrary.isbn==Books.ISBN, func.date_part('year', UserLibrary.date_added)>=func.date_part('year', func.now())-5).group_by(Books.ISBN).order_by(func.count(UserLibrary.isbn).desc()).limit(5).all()
        
        if time_period == '1':
            # x_data is time, y_data is sales
            # need to extract time and sales from sales_1
            x_data =[]
            y_data = []
            sales_data = sales_1
            x = 1
            for i in sales_data:
                x_data.append(x)
                x += 1
                y_data.append(i.sales)
            top_books = top_1
        elif time_period == '12':
            x_data =[]
            y_data = []
            sales_data = sales_12
            x = 1
            for i in sales_data:
                x_data.append(x)
                x += 1
                y_data.append(i.sales)
            top_books = top_12
        elif time_period == '60':
            x_data =[]
            y_data = []
            sales_data = sales_60
            x = 1
            for i in sales_data:
                x_data.append(x)
                x += 1
                y_data.append(i.sales)
            top_books = top_60
        else:
            x_data = []
            y_data = []
            top_books = []
        return render_template('analytics.html', pid = pid, top_books = top_books, sales_data = sales_data, x_data = x_data, y_data=y_data, time_period=time_period)

# Data analysis page that shows the images
@app.route('/data_analysis/<id>', methods=['GET', 'POST'])
def data_analysis_page(id):
    pid = session['pid']
    if request.method == 'POST':
        return redirect('/data_analysis/' + id)
    else:
        if id == '1':
            image_path = 'images/PopularAuthorsChart.jpg'
            name_of_analysis = 'Popular Authors'

        elif id == '2':
            image_path = 'images/PublicationTrendsChart.png'
            name_of_analysis = 'Publication Trends'

        elif id == '3':
            image_path = 'images/PublisherPerformanceChart.png'
            name_of_analysis = 'Publisher Performance'

        elif id == '4':
            image_path = 'images/PublisherStatusChart.png'
            name_of_analysis = 'Publisher Status'

        elif id == '5':
            image_path = 'images/RatingDistributionChart.png'
            name_of_analysis = 'Rating Distribution'

        elif id == '6':
            image_path = 'images/TopRatedBooksChart.png'
            name_of_analysis = 'Top Rated Books'

        elif id == '7':
            image_path = 'images/UserActivityChart.png'
            name_of_analysis = 'User Activity'

        elif id == '8':
            image_path = 'images/UserEngagementChart.png'
            name_of_analysis = 'User Engagement'

        elif id == '9':
            image_path = 'images/UserLocationsChart.png'
            name_of_analysis = 'User Locations'

        else:
            image_path = 'images/SelectAnalysis.png'
            name_of_analysis = 'Select a Analysis to Display'

        return render_template('data_analysis.html',pid = pid, image_path = image_path, name_of_analysis = name_of_analysis)

# homepage after user logs in using login-page, contains list of books and search bar
@app.route('/home/<userid>', methods=['GET', 'POST'])
def home_page(userid):
    username = session['username']
    num_books = 21 # number of books to be displayed on each page
    total_pages = int(Books.query.count()/num_books) + 1 # total number of pages
    page = 1 # current page
    if request.method == 'POST':
        page = request.form.get('page')
        page = page.split()
        if page[0] == 'Next':
            page = int(page[1]) + 1
        elif page[0] == 'Back':
            page = int(page[1]) - 1

        if int(page) < 1:
            page = "1"
        elif int(page) > total_pages:
            page = str(total_pages)

        books = db.session.query(Books.ISBN, Books.BookTitle, Books.BookAuthor, Publishers.PublisherName, Books.ImageURL).join(Publishers).limit(num_books).offset((int(page)-1)*num_books).all()

        # send "book isbn", "book title","book author","publisher name","book image url" to render template with respective datatypes for the html to use
        return render_template('home.html', username = username, books = books, user_id = userid, page = page)
        
    else:
        # get books from database
        books = db.session.query(Books.ISBN, Books.BookTitle, Books.BookAuthor, Publishers.PublisherName, Books.ImageURL).join(Publishers).limit(num_books).all()
        return render_template('home.html', username = username, books = books, user_id = userid, page = page)
    
# book page after user clicks on a book, contains book details and reviews
@app.route('/book/<isbn>', methods=['GET', 'POST'])
def book_page(isbn):
    username = session['username']
    user_id = session['user_id']
    if request.method == 'POST':
        # there are 2 buttons, one for adding review and one for adding book to personal library
        # if add review button is pressed
        if request.form.get('add_rating'):
            # get user id
            user_id = session['user_id']
            # get book rating
            book_rating = request.form.get('book_rating')
            # if user has already reviewed the book, update the review
            if Ratings.query.filter_by(UserID=user_id, ISBN=isbn).first() is not None:
                Ratings.query.filter_by(UserID=user_id, ISBN=isbn).update({Ratings.BookRating: book_rating})
            else:
                # add review to database
                new_rating = Ratings(UserID=user_id, ISBN=isbn, BookRating=book_rating)
                db.session.add(new_rating)
            
            db.session.commit()
            return redirect('/book/' + isbn)
        # if add to library button is pressed
        elif request.form.get('add_to_library'):
            # if book already exists in personal library, do nothing
            if UserLibrary.query.filter_by(user_id=user_id, isbn=isbn).first() is not None:
                return redirect('/profile')
            # add book to database
            new_library_entry = UserLibrary(user_id=user_id, isbn=isbn)
            db.session.add(new_library_entry)
            db.session.commit()
            # redirect to personal library
            return redirect('/profile')
    else:
        # retrieve book details from database
        book = Books.query.filter_by(ISBN=isbn).first()
        publisher = Publishers.query.filter_by(PublisherID=book.PublisherID).first().PublisherName
        # retrieve book reviews from database
        reviews = Ratings.query.filter_by(ISBN=isbn).all()
        # get overall rating of book
        overall_rating = 0
        for review in reviews:
            overall_rating += review.BookRating
        if len(reviews) != 0:
            overall_rating /= len(reviews)
        else:
            overall_rating = 0
        # round to 2 decimal places
        overall_rating = round(overall_rating, 2)

        # send it all to render template with respective datatypes for the html to use
        return render_template('book.html', book=book, publisher = publisher, reviews=reviews, overall_rating=overall_rating, username=username, user_id=user_id)

# search page without search query, contains list of books and search bar
@app.route('/search/', methods=['GET', 'POST'])
def search_page_no_query():
    username = session['username']
    userid = session['user_id']
    if request.method == 'POST':
        # get search query
        search = request.form.get('search')
        # if search query is empty, redirect to home page
        if search.strip() == '':
            return redirect('/search/')
        # redirect to search page with search query
        return redirect('/search/' + search + '/1')
    else:
        # get books from database
        books = db.session.query(Books.ISBN, Books.BookTitle, Books.BookAuthor, Publishers.PublisherName, Books.ImageURL).join(Publishers).limit(21).all()
        # send it all to render template with respective datatypes for the html to use
        return render_template('search.html', userid = userid, username = username, found="Ready to Search!", books=books, search='', page = 1)

# need to redirect /search//1 to /search/
@app.route('/search//<int:page>', methods=['GET', 'POST'])
def search_page_no_query_redirect(page):
    return redirect('/search/')

# search page after user searches for a book, contains list of books and search bar
@app.route('/search/<search>/<page>', methods=['GET', 'POST'])
def search_page(search,page):
    username = session['username']
    userid = session['user_id']
    num_books = 21 # number of books to be displayed on each page
    total_results = Books.query.filter(func.lower(Books.BookTitle).contains(func.lower(search)) | func.lower(Books.BookAuthor).contains(func.lower(search)) | func.lower(Books.ISBN).contains(func.lower(search))).count()
    total_pages = int(total_results/num_books) + 1 # total number of pages
    if request.method == 'POST':
        # get search query
        search = request.form.get('search')
        page = request.form.get('page')
        page = page.split()
        if page[0] == 'Next':
            page = int(page[1]) + 1
        elif page[0] == 'Back':
            page = int(page[1]) - 1
        if int(page) < 1:
            page = "1"
        elif int(page) > total_pages:
            page = str(total_pages)
        # if search query is empty, redirect to home page
        if search == '':
            return redirect('/search/')
        # redirect to search page with search query
        return redirect('/search/' + search + '/' + str(page))
    else:
        # get search query
        if search == '':
            redirect('/search/')
        # get books from database that match search query (case insensitive) match it with book title, author or isbn
        
        books = db.session.query(Books.ISBN, Books.BookTitle, Books.BookAuthor, Publishers.PublisherName, Books.ImageURL).join(Publishers).filter(func.lower(Books.BookTitle).contains(func.lower(search)) | func.lower(Books.BookAuthor).contains(func.lower(search)) | func.lower(Books.ISBN).contains(func.lower(search))).offset((int(page)-1)*num_books).limit(num_books).all()
        if len(books) == 0:
            return render_template('search.html', userid = userid, username = username, found = f'No Books Found for "{search}"!', books=[], search=search, page = page)
        # send it all to render template with respective datatypes for the html to use
        return render_template('search.html', userid = userid, username = username, found=f'{total_results} book(s) found for "{search}"', books=books, search=search, page = page)
        
# profile page after user clicks on profile, contains user details and reviews
@app.route('/profile', methods=['GET', 'POST'])
def profile_page():
    username = session['username']
    userid = session['user_id']
    if request.method == 'POST':
        return redirect('/profile')
    else:
        # retrieve user details from database
        user = Users.query.filter_by(UserID=userid).first()
        # retrieve personal library from database using user id foriegn key query
        library = UserLibrary.query.filter_by(user_id=userid).all()
        if len(library) == 0:
            return render_template('profile.html', user=user, books=[])
        # retrieve book details from database
        books = []
        for book in library:
            books.append(Books.query.filter_by(ISBN=book.isbn).first())

        # send it all to render template with respective datatypes for the html to use
        return render_template('profile.html', userid = userid, username = username, user=user, books=books)

# remove book from personal library
@app.route('/remove_book/<isbn>', methods=['GET', 'POST'])
def remove_book(isbn):
    if request.method == 'POST':
        # get user id
        user_id = session['user_id']
        # remove book from database
        UserLibrary.query.filter_by(user_id=user_id, isbn=isbn).delete()
        db.session.commit()
        # redirect to personal library
        return redirect('/profile')

    return redirect('/profile')

# logout user
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # remove user id from session
    session.clear()
    # redirect to login page
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
