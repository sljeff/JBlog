def main(database):
    """
    :type database: db.BlogDB
    """
    sqls = []
    sql_create_articles = 'CREATE TABLE {} '.format(database.table_name['articles']) + \
                          '(id INTEGER PRIMARY KEY AUTOINCREMENT, slug CHAR(100) NOT NULL UNIQUE, cat_id INT,' + \
                          'title NCHAR(100) NOT NULL, md_content TEXT NOT NULL, html_content TEXT NOT NULL, ' + \
                          'author NCHAR(30) NOT NULL, time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)'
    sql_create_cat = 'CREATE TABLE {} '.format(database.table_name['category']) + \
                     '(id INTEGER PRIMARY KEY AUTOINCREMENT, slug CHAR(100) UNIQUE, name NCHAR(100) NOT NULL)'
    sqls.append(sql_create_articles)
    sqls.append(sql_create_cat)
    print('INIT...')
    import pprint
    pprint.pprint(sqls)

    result = False
    conn = database.connect()
    for sql in sqls:
        try:
            conn.execute(sql)
            result = True
        except Exception as e:
            print(e)
            conn.rollback()
    conn.commit()
    conn.close()
    return result
