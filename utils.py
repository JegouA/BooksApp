import os
import zipfile
import tempfile
import xml.dom.minidom as xd
import shutil
import sqlFunctions as sqF
import time

__ratings__ = {'diamant': 5, 'or': 4, 'argent':3, 'bronze':2, 'neutral':1, 'dislike':0}


def extract_epubook(bookfile, path=None, parsefile=None):
    if path is None:
        path = os.path.join(os.getcwd(), 'data', 'covers')
        if not os.path.exists(path):
            os.makedirs(path)
    temp_dir = tempfile.TemporaryDirectory()
    with zipfile.ZipFile(bookfile, 'r') as zip_ref:
        zip_ref.extractall(temp_dir.name)
    #Find the opf file
    metadata, cover = read_epub_content(temp_dir.name, path)
    metadata['rating'] = 0
    metadata['read'] = 'No'
    if parsefile is not None:
        bookname = os.path.basename(bookfile)
        value = [livre for livre in parsefile if livre[4] == bookname]
        if len(value) > 0:
            try:
                metadata['rating'] = __ratings__[value[0][7]]
                metadata['read'] = value[0][6]
            except:
                metadata['rating'] = 0
                metadata['read'] = 'No'

    temp_dir.cleanup()
    return metadata, cover


def read_epub_content(temp_dir, path, metadata=None, cover=None):
    header = ['language', 'title', 'creator', 'description', 'publisher', 'subject']
    if metadata is None:
        metadata = {}
    if cover is None:
        cover = ''
    with os.scandir(temp_dir) as it:
        for file in it:
            if file.is_file() and file.name.endswith('.opf'):
                xml_doc = xd.parse(file.path)
                packages = xml_doc.getElementsByTagName('package')
                meta = packages[0].getElementsByTagName('metadata')
                for child in meta[0].childNodes:
                    idx = [elt for elt in header if child.localName == elt]
                    if len(idx) == 1 and len(child.childNodes) > 0:
                        data = child.childNodes[0].data
                        if idx[0] == 'description':
                            try:
                                deb = data.find('<span')
                                fin = data.find('</span>')
                                data = data[deb:fin]
                                interm = data.find('>')
                                data = data[interm+1::]
                            except:
                                data = 'No description'
                        if "'" in data:
                            data = data.replace("'", " ")
                        metadata[idx[0]] = data
            elif file.name.startswith('cover') and file.name.endswith('.jpg'):
                if 'title' not in metadata.keys():
                    titname = file.name + '_' + str(round(time.time()))
                else:
                    titname = metadata['title']
                cover = os.path.join(path, titname + '.jpg')
                shutil.copyfile(file.path, cover)
            elif file.is_dir():
                metadata, cover = read_epub_content(file.path, path, metadata=metadata, cover=cover)

    return metadata, cover


def read_parsefile(filename):
    parsefile = []
    with open(filename, 'r') as file:
        for line in file:
            temp_header = line.replace('\n', '').split('\t')
            parsefile.append(temp_header)

    return parsefile


def parsing_directory(path, connect, userID, basepath=None, parsefile=None):
    if basepath is None:
        basepath = path
    if userID[1] == 'Aaude' and parsefile is None:
        parsefile = read_parsefile(os.path.join(path, 'parsing.tsv'))
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir():
                parsing_directory(entry.path, connect, userID, basepath=basepath, parsefile=parsefile)
            elif entry.is_file() and entry.name.endswith('.epub'):
                meta, cover = extract_epubook(entry.path, parsefile=parsefile)
                # Change the header, to fit the books elements
                # Also add for Aude user the value of the hierarchy
                header_books = sqF.get_header_table(connect, 'books')
                if header_books is None:
                    header_books = ['title', 'publisher', 'language']
                elt = {v: meta[v] for v in header_books if v in meta.keys()}
                if 'creator' in meta.keys():
                    elt['author'] = meta['creator']
                # First check if it is in book tables
                res = sqF.get_elements(connect, '*', ['books'], wher=elt)
                if res is None or len(res) == 0:
                    # Add the books to the database
                    if cover:
                        elt['cover'] = cover
                    sqF.insert_elements_table(connect, 'books', elt)
                    res = sqF.get_elements(connect, 'id', ['books'], wher=elt)
                    if res is None:
                        continue
                subtype=None
                if 'subject' in meta.keys():
                    subtype = meta['subject']
                elif'subject' not in meta.keys() and userID[1] == 'Aaude':
                    value = entry.path.replace(basepath, '')
                    elem = value.split(os.sep)
                    subtype = elem[1]
                # have to check if theme in tables
                if subtype is not None or subtype:
                    resT = sqF.get_elements(connect, '*', ['themes'], wher={'subtype':subtype})
                    # if not do updates
                    if resT is None or len(resT) == 0:
                        sqF.insert_elements_table(connect, 'themes', {'subtype':subtype})
                    sqF.update_table_elt(connect, 'books', {'theme':subtype}, {'id': res[0][0]})
                if userID[1] == 'Aaude':
                    tome = entry.name.split(' - ')
                    if tome[0].startswith('Tome'):
                        tome = tome[0]
                    else:
                        tome = []
                    # update info
                    sqF.update_table_elt(connect, 'books', {'tome': tome}, {'id': res[0][0]})
                # then check if it is in library of the user
                resL = sqF.get_elements(connect, '*', ['library'], wher={'book_id': res[0][0], 'user_id':userID[0]})
                if resL is None or len(resL) == 0:
                    libBook = {}
                    libBook['book_id'] = res[0][0]
                    libBook['rating'] = meta['rating']
                    libBook['read'] = meta['read']
                    libBook['user_id'] = userID[0]

                    sqF.insert_elements_table(connect, 'library', libBook)


def booksApp_connection(user, password):
    error = ""
    userID = []
    path = os.getcwd()
    subpath = os.path.join(path, 'data')
    if not os.path.exists(subpath):
        os.makedirs(subpath)
    dbpath = os.path.join(subpath, 'booksApp.db')
    connect = sqF.create_connection(dbpath)
    res = sqF.get_elements(connect, '*', ['users'], wher={'username':user})
    if res is None or len(res) == 0:
        # create user
        username = {'username':user, 'password':password}
        sqF.insert_elements_table(connect, "users", username)
        # get the user id
        res = sqF.get_elements(connect, '*', ['users'], wher=username)
        userID = res[0]
    else:
        #check password
        userID = [item for item in res if item[2] == password]
        if userID is None or len(userID) == 0:
            error = 'Wrong password'
            return connect, userID, error
        userID = userID[0]
    return connect, userID, error

# Go throught the theme to update the type