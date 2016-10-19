# coding: utf-8
import sqlite3
import datetime
from functools import lru_cache


class DB:
    def __init__(self, dbpath='blog.db'):
        """
        :param str dbpath: database path
        """
        self._dbpath = dbpath

    @staticmethod
    def _prepare_conditions(conditions):
        """
        example:
            conditions = [('id', '=', '3'), ('name', '>', 'jeff')]
            cdt_str, cdt_value = self._prepare_conditions(conditions)
            assert cdt_str == 'id = ? AND name > ?'
            assert cdt_value == (3, 'jeff')

            conditions = {'id': 1, 'name': 'jeff'}
            cdt_str, cdt_value = self._prepare_conditions(conditions)
            assert cdt_str == 'id = ? AND name = ?'
            assert cdt_value == (3, 'jeff')
        :param list[tuple[str]]|dict conditions: list of 3-tuple
        :rtype: tuple[str, tuple]
        """
        cdt_arr = []
        cdt_value_arr = []
        get_symbol = lambda t: t[1]
        inner = ' AND '
        if isinstance(conditions, dict):
            conditions = [x for x in conditions.items()]
            get_symbol = lambda t: '='
            inner = ','
        for tp in conditions:
            if ' ' in tp[0]:
                # SQL injection
                return None, None
            cdt_arr.append('{0} {1} ?'.format(tp[0], get_symbol(tp)))
            cdt_value_arr.append(tp[-1])
        cdt_str = inner.join(cdt_arr)
        return cdt_str, tuple(cdt_value_arr)

    def _connect(self):
        """
        :rtype: sqlite3.Connection
        """
        conn = sqlite3.connect(self._dbpath, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def insert(self, table, value_dict):
        """
        INSERT INTO table (value_dict.keys()) VALUES (value_dict.values())
        :param str table: table to insert
        :param dict value_dict: dict to insert
        :rtype: bool
        """
        result = False

        qs = ','.join(['?'] * len(value_dict))
        k_tuple = ','.join(value_dict.keys())
        v_tuple = tuple(value_dict.values())
        sql = 'INSERT INTO {} ({}) VALUES ({})'.format(table, k_tuple, qs)

        conn = self._connect()
        try:
            conn.execute(sql, v_tuple)
            conn.commit()
            result = True
        except Exception as e:
            print(e)
            conn.rollback()
        finally:
            conn.close()
            return result

    def select(self, columns, table, conditions, order_by=None, desc=False, limit=None, offset=None):
        """
        SELECT columns FROM table WHERE condition AND condition
        note that: columns should not be a string!
        :param tuple|list columns: if columns is (), [] or None, it will be translated to '*'.
        :param str table: table to select
        :param list[tuple[str]] conditions: 3-tuple list; ex: [('author', '=', 'jeff'), ('time', '<', datetime.now())]
        :param str order_by: order by which column
        :param bool desc: desc
        :param int limit: limit number
        :param int offset: offset number
        :rtype: list[sqlite3.Row]
        """
        result = None

        sel_str = ','.join(columns) if columns else '*'
        cdt_str, cdt_value = self._prepare_conditions(conditions)
        if cdt_str is None or cdt_value is None:
            return result
        if len(cdt_value) == 0:
            sql = 'SELECT {} FROM {}'.format(sel_str, table)
        else:
            sql = 'SELECT {} FROM {} WHERE {}'.format(sel_str, table, cdt_str)
        if order_by is not None:
            sql += ' ORDER BY {}'.format(order_by)
        if desc:
            sql += ' DESC'
        if limit is not None:
            sql += ' LIMIT {}'.format(limit)
        if offset is not None:
            sql += ' OFFSET {}'.format(offset)

        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, cdt_value)
            result = cursor.fetchall()
        except Exception as e:
            print(sql, '\n', e)
            conn.rollback()
        finally:
            conn.close()
            return result

    def update(self, table, value_dict, conditions):
        """
        UPDATE table SET value_dict.keys() = value_dict.values() WHERE condition AND condition
        :param str table: table to update
        :param dict value_dict: values to update
        :param list[tuple[str]] conditions: list of 3-tuple; ex: [('author', '=', 'jeff'), ('time', '<', '20160501')]
        :rtype: bool
        """
        result = False

        value_str, value_tuple = self._prepare_conditions(value_dict)
        cdt_str, cdt_value = self._prepare_conditions(conditions)
        if None in (value_str, value_tuple, cdt_str, cdt_value):
            return result
        if len(cdt_value) == 0:
            sql = 'UPDATE {} SET {}'.format(table, value_str)
        else:
            sql = 'UPDATE {} SET {} WHERE {}'.format(table, value_str, cdt_str)

        conn = self._connect()

        try:
            conn.execute(sql, value_tuple + cdt_value)
            conn.commit()
            result = True
        except:
            conn.rollback()
        finally:
            conn.close()
            return result

    def delete(self, table, conditions):
        """
        DELETE FROM table WHERE conditions
        :param str table: table to delete
        :param list[tuple[str]] conditions: list of 3-tuple; ex: [('author', '=', 'jeff'), ('time', '<', '20160501')]
        :rtype: bool
        """
        result = False

        cdt_str, cdt_value = self._prepare_conditions(conditions)
        if cdt_str is None or cdt_value is None:
            return result
        if len(cdt_value) == 0:
            sql = 'DELETE FROM {}'.format(table)
        else:
            sql = 'DELETE FROM {} WHERE {}'.format(table, cdt_str)

        conn = self._connect()
        try:
            conn.execute(sql, cdt_value)
            conn.commit()
            result = True
        except:
            conn.rollback()
        finally:
            conn.close()
            return result


class BlogDB(DB):
    """
    :param dict table_name: tables in database. need 'articles', .. attributes
    :param list selection: columns to select in self.select_article and self.select_articles
    """

    def __init__(self, dbpath='blog.db'):
        super(BlogDB, self).__init__(dbpath)
        self.table_name = {'articles': 'articles', 'category': 'cat'}
        self.selection = []

    def add_article(self, slug, title, md_content, html_content, author, time=None):
        """
        add an article into database
        :param str slug: slug
        :param str title: title
        :param str md_content: markdown content of article
        :param str html_content: html content of article
        :param str author: author
        :param datetime.datetime time: time; if None, it will be datetime.datetime.now()
        :rtype: bool
        """
        result = self.insert(self.table_name['articles'], {
            'slug': slug,
            'title': title,
            'md_content': md_content,
            'html_content': html_content,
            'author': author,
            'time': time or datetime.datetime.now()
        })
        return result

    def delete_article(self, slug):
        """
        delete an article
        :param str slug: slug of the article
        :rtype: bool
        """
        result = self.delete(self.table_name['articles'], [('slug', '=', slug)])
        return result

    def delete_articles(self, conditions):
        """
        delete articles
        :param list[tuple[str]] conditions: list of 3-tuple; ex: [('author', '=', 'jeff'), ('time', '<', '20160501')]
        :rtype: bool
        """
        result = self.delete(self.table_name['articles'], conditions)
        return result

    def update_article(self, value_dict, slug):
        """
        update an article
        :param dict value_dict: values to update
        :param str slug: slug of the article
        :rtype: bool
        """
        result = self.update(self.table_name['articles'], value_dict, [('slug', '=', slug)])
        return result

    @lru_cache()
    def select_article(self, slug):
        """
        :param str slug: slug of the article
        :rtype: sqlite3.Row|None
        """
        result = self.select(self.selection, self.table_name['articles'], [('slug', '=', slug)])
        if len(result) != 0:
            return result[0]
        return None

    def select_articles(self, conditions, limit=20, offset=None):
        """
        :param list[tuple[str]] conditions: list of 3-tuple; ex: [('author', '=', 'jeff'), ('time', '<', '20160501')]
        :param int limit: limit number
        :param int offset:offset number
        :rtype: list[sqlite3.Row]
        """
        if offset == 0:
            offset = None
        result = self.select(self.selection, self.table_name['articles'], conditions,
                             order_by='time', desc=True, limit=limit, offset=offset)
        return result

    @lru_cache()
    def select_articles_by_time(self, begin=None, end=None, limit=20, page_num=0):
        """
        :param datetime.datetime begin: begin *begin*
        :param datetime.datetime end: to *end*
        :param int limit: limit number
        :param int page_num: page number
        :rtype: list[sqlite3.Row]
        """
        conditions = []
        if begin is not None:
            conditions.append(('time', '>', begin))
        if end is not None:
            conditions.append(('time', '<', end))
        result = self.select_articles(conditions, limit, limit * page_num)
        return result

    def init(self):
        """
        :rtype: bool
        """
        sqls = []
        sql_create_articles = 'CREATE TABLE {} '.format(self.table_name['articles']) + \
                              '(id INTEGER PRIMARY KEY AUTOINCREMENT, slug CHAR(100) NOT NULL UNIQUE, ' + \
                              'title NCHAR(100) NOT NULL, md_content TEXT NOT NULL, html_content TEXT NOT NULL, ' + \
                              'author NCHAR(30) NOT NULL, time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)'
        sqls.append(sql_create_articles)
        print(sqls)

        result = False
        for sql in sqls:
            conn = self._connect()
            try:
                conn.execute(sql)
                conn.commit()
                result = True
            except Exception as e:
                print(e)
                conn.rollback()
            finally:
                conn.close()
                return result
