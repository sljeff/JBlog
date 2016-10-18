import os

def main(loop):
    if not os.path.isfile('blog.db'):
        import db
        d = db.BlogDB(loop)
        r = loop.run_until_complete(d.init())
