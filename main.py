# Copyright 2024 by Aude Jegou.
# All rights reserved.
# This file is part of the BooksApp project,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# This is a sample Python script.
import utils as ut
# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    user = ''
    password = ''
    connect, userID, error = ut.booksApp_connection(user, password)
    path = r'C:\Users\pimou\OneDrive\livres'
    ut.parsing_directory(path, connect, userID)
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# Ebook metadata in DC
# title, creator, description, publisher, subject