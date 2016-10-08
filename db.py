# coding: utf-8
import sqlite3
import datetime
from functools import partial


class DB:
    def __init__(self, loop, dbpath='blog.db', executor=None):
        """
        :param asyncio.AbstractEventLoop loop: event loop
        :param str dbpath: database path
        :param concurrent.futures.Executor executor: executor for sqlite operate
        """
        self._dbpath = dbpath
        self._loop = loop
        self._executor = executor

    def _do(self, func, *args, **kwargs):
        """
        :param callable func: arrange func to be called in self._executor
        :rtype: asyncio.Future
        """
        func = partial(func, *args, **kwargs)
        future = self._loop.run_in_executor(self._executor, func)
        return future

    async def _connect(self):
        """
        :rtype: sqlite3.Connection
        """
        conn = await self._do(sqlite3.connect, self._dbpath, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    async def _commit(self, conn):
        await self._do(conn.commit)

    async def _rollback(self, conn):
        await self._do(conn.rollback)

    async def _close(self, conn):
        await self._do(conn.close)

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
        get_symbol = lambda tp: tp[1]
        inner = ' AND '
        if isinstance(conditions, dict):
            conditions = [x for x in conditions.items()]
            get_symbol = lambda tp: '='
            inner = ','
        for tp in conditions:
            if ' ' in tp[0]:
                # SQL injection
                return None, None
            cdt_arr.append(tp[0] + ' ' + get_symbol(tp) + ' ' + '?')
            cdt_value_arr.append(tp[-1])
        cdt_str = inner.join(cdt_arr)
        return cdt_str, tuple(cdt_value_arr)

    async def insert(self, table, value_dict):
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

        conn = await self._connect()
        try:
            await self._do(conn.execute, sql, v_tuple)
            await self._commit(conn)
            result = True
        except BaseException as e:
            await self._rollback(conn)
        finally:
            await self._close(conn)
            return result

    async def select(self, columns, table, conditions):
        """
        SELECT columns FROM table WHERE condition AND condition
        note that: columns should not be a string!
        :param tuple|list columns: if columns is (), [] or None, it will be translated to '*'.
        :param str table: table to select
        :param list[tuple[str]] conditions: list of 3-tuple; ex: [('author', '=', 'jeff'), ('time', '<', '20160501')]
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

        conn = await self._connect()
        try:
            cursor = conn.cursor()
            await self._do(cursor.execute, sql, cdt_value)
            result = await self._do(cursor.fetchall)
        except BaseException as e:
            await self._rollback(conn)
        finally:
            await self._close(conn)
            return result

    async def update(self, table, value_dict, conditions):
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

        conn = await self._connect()

        try:
            await self._do(conn.execute, sql, value_tuple + cdt_value)
            await self._commit(conn)
            result = True
        except:
            await self._rollback(conn)
        finally:
            await self._close(conn)
            return result

    async def delete(self, table, conditions):
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

        conn = await self._connect()
        try:
            await self._do(conn.execute, sql, cdt_value)
            await self._commit(conn)
            result = True
        except:
            await self._rollback(conn)
        finally:
            await self._close(conn)
            return result


class BlogDB(DB):
    """
    :param dict table_name: tables in database. need 'articles', .. attributes
    :param list selection: columns to select in self.select_article and self.select_articles
    """

    def __init__(self, loop, dbpath='blog.db', executor=None):
        super(BlogDB, self).__init__(loop, dbpath, executor)
        self.table_name = {'articles': 'articles', 'category': 'cat'}
        self.selection = []

    async def add_article(self, slug, title, md_content, html_content, author, time=None):
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
        result = await self.insert(self.table_name['articles'], {
            'slug': slug,
            'title': title,
            'md_content': md_content,
            'html_content': html_content,
            'author': author,
            'time': time or datetime.datetime.now()
        })
        return result

    async def delete_article(self, slug):
        """
        delete an article
        :param str slug: slug of the article
        :rtype: bool
        """
        result = await self.delete(self.table_name['articles'], [('slug', '=', slug)])
        return result

    async def delete_articles(self, conditions):
        """
        delete articles
        :param list[tuple[str]] conditions: list of 3-tuple; ex: [('author', '=', 'jeff'), ('time', '<', '20160501')]
        :rtype: bool
        """
        result = await self.delete(self.table_name['articles'], conditions)
        return result

    async def update_article(self, value_dict, slug):
        """
        update an article
        :param dict value_dict: values to update
        :param str slug: slug of the article
        :rtype: bool
        """
        result = await self.update(self.table_name['articles'], value_dict, [('slug', '=', slug)])
        return result

    async def select_article(self, slug):
        """
        :param str slug: slug of the article
        :rtype: sqlite3.Row
        """
        result = await self.select(self.selection, self.table_name['articles'], [('slug', '=', slug)])
        return result[0]

    async def select_articles(self, conditions):
        """
        :param list[tuple[str]] conditions: list of 3-tuple; ex: [('author', '=', 'jeff'), ('time', '<', '20160501')]
        :rtype: list[sqlite3.Row]
        """
        result = await self.select(self.selection, self.table_name['articles'], conditions)
        return result

    async def select_articles_by_time(self, begin=None, end=None):
        """
        :param datetime.datetime begin: begin *begin*
        :param datetime.datetime end: to *end*
        :rtype: list[sqlite3.Row]
        """
        if begin is None:
            begin = datetime.datetime.min
        if end is None:
            end = datetime.datetime.max
        result = await self.select_articles([('time', '>', begin), ('time', '<', end)])
        return result

    async def select_articles_by_category(self, cat_slug):
        """
        :param str cat_slug: slug of category
        :rtype: list[sqlite3.Row]
        """
        rows = await self.select_articles([('slug', '=', cat_slug)])
        row = rows[0]
        cat_id = row['id']
        result = await self.select_articles([('cat_id', '=', cat_id)])
        return result

    async def init(self):
        """
        :rtype: bool
        """
        sqls = []
        sql_create_articles = 'CREATE TABLE {} '.format(self.table_name['article']) +\
                              '(id INT PRIMARY KEY NOT NULL AUTOINCREMENT, slug CHAR(100) NOT NULL, cat_id INT NOT NULL, ' +\
                              'title NCHAR(100) NOT NULL, md_content TEXT NOT NULL, html_content TEXT NOT NULL, ' +\
                              'author NCHAR(30) NOT NULL, time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)'
        sql_create_category = 'CREATE TABLE {} '.format(self.table_name['category']) +\
                              '(id INT PRIMARY KEY NOT NULL AUTOINCREMENT, slug CHAR(50) NOT NULL, name NCHAR(50) NOT NULL)'
        sqls.append(sql_create_articles)
        sqls.append(sql_create_category)

        result = False
        for sql in sqls:
            conn = await self._connect()
            try:
                await self._do(conn.execute(sql))
                await self._commit(conn)
                result = True
            except:
                await self._rollback(conn)
            finally:
                await self._close(conn)
                return result
