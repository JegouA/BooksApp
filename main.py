# This is a sample Python script.
import utils as ut
# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    user = 'Aaude'
    password = 'admin'
    connect, userID, error = ut.booksApp_connection(user, password)
    path = r'C:\Users\pimou\OneDrive\livres'
    ut.parsing_directory(path, connect, userID)
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# Ebook metadata in DC
# title, creator, description, publisher, subject