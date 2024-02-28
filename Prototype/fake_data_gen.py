'''# Define Books Table
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

    # Define Publishers Table
    class Publishers(db.Model):
        PublisherID = db.Column(db.Integer, primary_key=True)
        PublisherName = db.Column(db.String(255))
        PublisherEmail = db.Column(db.String(255))'''
    # do all above steps in the database_setup.py as python code

    # To open prolib database in postgresql shell
    # psql -U postgres -d prolib

    # (raised as a result of Query-invoked autoflush; consider using a session.no_autoflush block if this flush is occurring prematurely)


def generate_fake_data(reset = False):
    from app import app, db, Books, Users, Ratings, UserLibrary, Publishers
    from faker import Faker
    from random import randint
    # Create all tables
    with app.app_context():
        if reset:
            db.drop_all()  # if you want to clear the database or when u want to change the schema when not running via docker
        db.create_all() # uncomment this when not running via docker
        db.session.no_autoflush # uncomment this when not running via docker
        # Generate and add random sample data
        fake = Faker()

        # Add Publishers
        for _ in range(5):
            publisher = Publishers(
                PublisherID=randint(1000, 9999),
                PublisherName=fake.company(),
                PublisherEmail=fake.email()
            )
            db.session.add(publisher)
        db.session.commit()

        # Add Books
        for _ in range(100):
            book = Books(
                ISBN=fake.random_int(min=1000000000000, max=9999999999999), # 13 digit ISBN
                BookTitle=fake.sentence(nb_words=4, variable_nb_words=True, ext_word_list=None),
                BookAuthor=fake.name(),
                YearOfPublication=fake.random_int(min=1900, max=2020),
                PublisherID=fake.random_element(elements=[publisher.PublisherID for publisher in Publishers.query.all()]),
                ImageURL=fake.image_url(),
            )
            db.session.add(book)
        db.session.commit()

        # add test publisher with id 21159 if that id doesnt exist already
        if Publishers.query.filter_by(PublisherID=21159).first() is None:
            db.session.add(Publishers(PublisherID=21159, PublisherName='test', PublisherEmail="test@test"))
        db.session.commit()

        # adding lot of books to our test publisher with id 21159
        for _ in range(100):
            book = Books(
                ISBN=fake.random_int(min=1000000000000, max=9999999999999), # 13 digit ISBN
                BookTitle=fake.sentence(nb_words=4, variable_nb_words=True, ext_word_list=None),
                BookAuthor=fake.name(),
                YearOfPublication=fake.random_int(min=1900, max=2020),
                PublisherID=21159,
                ImageURL=fake.image_url(),
            )
            db.session.add(book)
        db.session.commit()

        # Add Users
        for _ in range(50):
            user = Users(
                UserName = fake.name().replace(' ', '').lower(),
                Location=fake.city(),
                Age=fake.random_int(min=18, max=80),
            )
            db.session.add(user)
        db.session.commit()

        # Adding a test user with UserID=59, Location='test', Age=20 if user id 59 doesnt exist
        if Users.query.filter_by(UserID=59).first() is None:
            db.session.add(Users(UserID=59, UserName = 'prop', Location='test', Age=20))
        db.session.commit()

        # Add Ratings (assuming you have at least 5 users and 10 books)
        for _ in range(10):
            rating = Ratings(
                UserID=fake.random_int(min=1, max=5),
                ISBN=fake.random_element(elements=[book.ISBN for book in Books.query.all()]),
                BookRating=randint(1, 5),
            )
            # change the user if and isbn if that pair already exists
            while Ratings.query.filter_by(UserID=rating.UserID, ISBN=rating.ISBN).first() is not None:
                rating.UserID = fake.random_int(min=1, max=5)
                rating.ISBN = fake.random_element(elements=[book.ISBN for book in Books.query.all()])
            db.session.add(rating)
        db.session.commit()
        # Add UserLibrary (assuming you have at least 5 users and 10 books)
        # we will add random 300 records of people adding books to personal library
        for _ in range(100):
            library = UserLibrary(
                user_id=fake.random_element(elements=[user.UserID for user in Users.query.all()]),
                isbn=fake.random_element(elements=[book.ISBN for book in Books.query.all()]),
                date_added=fake.date_between(start_date='-6y', end_date='today')
            )
            # change the isbn if that pair already exists
            while UserLibrary.query.filter_by(user_id=library.user_id, isbn=library.isbn).first() is not None:
                library.isbn = fake.random_element(elements=[book.ISBN for book in Books.query.all()])
            db.session.add(library)
        db.session.commit()
        

        # Commit the changes to the database

        # replace all the values of the imageurl coloumn with "https://static.vecteezy.com/system/resources/previews/017/205/140/original/plain-book-logo-icon-free-vector.jpg"
        Books.query.update({Books.ImageURL: 'https://static.vecteezy.com/system/resources/previews/017/205/140/original/plain-book-logo-icon-free-vector.jpg'})
        db.session.commit()

        # print the schema of all 3 tables
        #print("\n\nBooks Table Schema:")
        #print(Books.query.first(), Books.query.first().ImageURL)
        #print("\n\nUsers Table Schema:")
        #print(Users.query.first(), Users.query.first().Location, Users.query.first().Age)
        #print("\n\nRatings Table Schema:")
        #print(Ratings.query.first(), Ratings.query.first().BookRating)
        #print("\n\nUserLibrary Table Schema:")
        #print(UserLibrary.query.first())
        #print("\n\nPublisher Table Schema:")
        #print(Publishers.query.first())

# When this file is run directly, execute the code below
if __name__ == '__main__':
    generate_fake_data(reset=True) # set reset to True if you want to clear the database or when u want to change the schema when not running via docker