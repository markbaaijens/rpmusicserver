# TODO logging: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-error-handling
# TODO - create logs folders runtime (delete info.txt files)
#        if not os.path.exists('logs'):
#           os.mkdir('logs')
# TODO - choose console-logging OR file-logging based on debug-modus
#        if not app.debug:
# TODO Exception handling API-calls (based on return codes op calls) 
# TODO see: https://flask.palletsprojects.com/en/1.1.x/patterns/apierrors/
# TODO Error when page (or id) not found
# TODO Error when service not found when doing a request

from flask import Flask, render_template, jsonify, request, redirect, flash
import requests
import json
import logging
from logging.handlers import RotatingFileHandler
import traceback

from config import Config
from forms import EditBookForm, DeleteBookForm
from converters import ConvertToTwoDecimals, ConvertBooleanToText, ConvertEnumBookTypeToDescription
from model import Book

app = Flask(__name__)

app.config.from_object(Config)

logger = logging.getLogger()

'''
if not logger.handlers:
    logger.setLevel(logging.DEBUG)

    fileHandler = logging.handlers.RotatingFileHandler(
        app.config['LOG_FILE_NAME'], 'a', app.config['LOG_MAX_SIZE'], app.config['LOG_BACKUP_COUNT'])
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(consoleHandler)
'''

@app.route('/', methods=['GET'])
def index():
    try:
        apiInfo = json.loads(requests.get(app.config['API_ROOT_URL']).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiInfo = []

    try:
        versionInfo = json.loads(requests.get(app.config['API_ROOT_URL'] + '/api/GetVersionInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        versionInfo = []

    try:
        machineInfo = json.loads(requests.get(app.config['API_ROOT_URL'] + '/api/GetMachineInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        machineInfo = []

    return render_template(
        'details.html', 
        appTitle = app.config['APP_TITLE'], 
        apiInfo = apiInfo,
        apiUrl = app.config['API_ROOT_URL'],
        versionInfo = versionInfo,
        machineInfo = machineInfo
    )

# GET /books
@app.route('/books', methods=['GET'])
def listBook():
    global apiInfo

    try:
        # Using eval to convert string to a dictionairy
        bookList = json.loads(requests.get(app.config['API_ROOT_URL'] + '/books').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        bookList = []

    nrOfBooks = len(bookList)  # Count books client-side

    # Some formatting 
    for book in bookList:
        book['price'] = ConvertToTwoDecimals(book['price'])
        book['isObsolete'] = ConvertBooleanToText(book['isObsolete'])
        book['bookType'] = ConvertEnumBookTypeToDescription(book['bookType'])

    return render_template('books/list.html', appTitle = app.config['APP_TITLE'], api = apiInfo, books = bookList, 
        nrOfBooks = nrOfBooks)

# GET /books/<id>
@app.route('/books/<int:id>', methods=['GET'])
def detailsBook(id):
    global apiInfo

    try:
        # Using eval to convert string to a dictionairy
        bookList = json.loads(requests.get(app.config['API_ROOT_URL'] + '/books' + '/' + str(id)).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())        
        bookList = []  

    for book in bookList:  
        # There is one and only one book
        orgBook = Book (
            book['id'], 
            book['name'],
            book['price'],  # Two decimals
            book['isbn'],
            book['isObsolete'],
            book['bookType']
        )    

    orgBook.price = ConvertToTwoDecimals(orgBook.price)
    orgBook.isObsolete = ConvertBooleanToText(orgBook.isObsolete)
    orgBook.bookType = ConvertEnumBookTypeToDescription(orgBook.bookType)

    return render_template('books/details.html', actionTitle = 'Book details', appTitle = app.config['APP_TITLE'], api = apiInfo, book = vars(orgBook))

# GET/POST /books/edit/<id>
@app.route('/books/edit/<int:id>', methods=['GET', 'POST'])
def editBook(id):
    global apiInfo

    try:
        # Using eval to convert string to a dictionairy
        bookList = json.loads(requests.get(app.config['API_ROOT_URL'] + '/books' + '/' + str(id)).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        bookList = []  

    for book in bookList:  
        # There is one and only one book
        # Use constructor b/c mutating members directly result in unpredictable data
        orgBook = Book(
            book['id'], 
            book['name'],
            book['price'],
            book['isbn'],
            book['isObsolete'],
            book['bookType']
        )  

    form = EditBookForm()

    if request.method == 'GET':
        form.id.data = orgBook.id
        form.name.data = orgBook.name
        form.price.data = orgBook.price
        form.isbn.data = orgBook.isbn
        form.isObsolete.data = orgBook.isObsolete
        form.bookType.data = orgBook.bookType

    if request.method == 'POST' and form.validate():  # Equivalent to validate_on_submit()
        newName = request.form['name']
        newIsbn = request.form['isbn']
        newPrice = request.form['price']
        newObsolete = form.isObsolete.data  # TODO (bug) request.form['<booelan>'] does not return
        newBookType = request.form['bookType']

        deltaBook = {}

        if newName.strip() != orgBook.name.strip():
            deltaBook['name'] = newName
        if int(newIsbn) != int(orgBook.isbn):  # Convert to int to have a precise comparison
            deltaBook['isbn'] = newIsbn
        if float(newPrice) != float(orgBook.price):  # Convert to float to have a precise comparison
            deltaBook['price'] = newPrice
        if newObsolete != orgBook.isObsolete: 
            deltaBook['isObsolete'] = newObsolete
        if int(newBookType) != int(orgBook.bookType):  # Convert to int to have a precise comparison
            deltaBook['bookType'] = newBookType

        if deltaBook != {}:
            try:
                requests.patch(app.config['API_ROOT_URL'] + '/books' + '/' + str(id), json = deltaBook)
                flash('Saved book {}'.format(deltaBook))
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
            
        # TODO After insert, redirect to book-details            
        return redirect('/books/' + str(id))     

    return render_template('books/edit.html', actionTitle = 'Edit book', appTitle = app.config['APP_TITLE'], api = apiInfo, book = orgBook, form = form)

# GET/POST /books/add
@app.route('/books/add', methods=['GET', 'POST'])
def addBook():
    global apiInfo

    orgBook = Book()  

    form = EditBookForm()

    if request.method == 'GET':
        form.id.data = orgBook.id
        form.name.data = orgBook.name
        form.price.data = orgBook.price
        form.isbn.data = orgBook.isbn
        form.isObsolete.data = orgBook.isObsolete
        form.bookType.data = orgBook.bookType

    if request.method == 'POST' and form.validate():  # Equivalent to validate_on_submit()
        newBook = Book()
        newBook.name = request.form['name']
        newBook.isbn = request.form['isbn']
        newBook.price = request.form['price']
        newBook.isObsolete = form.isObsolete.data # TODO (bug) request.form['<booelan>'] does not return
        newBook.bookType = request.form['bookType']

        try:
            addedBook = json.loads(requests.post(app.config['API_ROOT_URL'] + '/books', json = vars(newBook)).content)
            newBook.id = addedBook['id']
            flash('Added book {}'.format(vars(newBook)))
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())

        return redirect('/books')      

    return render_template('books/edit.html', actionTitle = 'Add book', appTitle = app.config['APP_TITLE'], api = apiInfo, book = vars(orgBook), form = form)

# DELETE /books/<id>
@app.route('/books/delete/<int:id>', methods=['GET', 'POST'])
def deleteBook(id):
    global apiInfo

    try:
        bookList = json.loads(requests.get(app.config['API_ROOT_URL'] + '/books' + '/' + str(id)).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        bookList = []  

    for book in bookList:  
        # There is one and only one book
        # Use constructor b/c mutating members directly result in unpredictable data
        orgBook = Book(book['id'], book['name'])
        
    form = DeleteBookForm()     

    if form.validate_on_submit():
        requests.delete(app.config['API_ROOT_URL'] + '/books' + '/' + str(id))

        flash('Deleted book id = {}'.format(id))
        return redirect('/books')  

    return render_template('books/delete.html', actionTitle = 'Delete book', appTitle = app.config['APP_TITLE'], api = apiInfo, book = vars(orgBook), form = form)

if __name__ == '__main__':
    logger.debug('App Started')
    app.run(port=5001, debug=True)  # auto-reload, only localhoast
#    app.run(host='0.0.0.0', port=5001)  # public server, reachable from remote
    logger.debug('App Stopped')

