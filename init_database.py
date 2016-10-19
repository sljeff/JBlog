import os

def main(database):
    """
    :type database: db.BlogDB
    """
    if not os.path.isfile('blog.db'):
        database.init()
