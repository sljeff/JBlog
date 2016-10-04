# coding: utf-8
import sqlite3
import asyncio
from functools import partial


class DB:
    def __init__(self, loop, dbpath='blog.db', executor=None):
        """
        :type loop: asyncio.AbstractEventLoop
        :type dbpath: str
        :type executor: concurrent.futures.Executor
        """
        self._dbpath = dbpath
        self._loop = loop
        self._executor = executor
        self._conn = None

    def _do(self, func, *args, **kwargs):
        """
        :type func: callable
        """
        func = partial(func, *args, **kwargs)
        future = self._loop.run_in_executor(self._executor, func)
        return future

    async def _connect(self):
        f = self._do(sqlite3.connect(self._dbpath))
        conn = await f
        """:type : sqlite3.Connection"""
        conn.row_factory = sqlite3.Row
        return conn

    async def _commit(self, conn):
        """
        :type conn: sqlite3.Connection
        """
        await self._do(conn.commit)

    async def _close(self, conn):
        """
        :type conn: sqlite3.Connection
        """
        await self._d(conn.close)

    async def _insert(self, table, columns, values):
        """
        :type table: str
        :type columns: list
        :type values: list
        :rtype: bool
        """
        qstr = ', '.join(['?'] * len(columns))
        vstr = ', '.join(values)
        conn = await self._connect()
        try:
            await self._do(conn.execute, 'INSERT INTO ? (?) VALUES (?)', (table, qstr, vstr))
            await self._commit(conn)
            await self._close(conn)
            return True
        except:
            await self._do(conn.rollback)
            return False

    async def _select(self, columns, table, conditions):
        """
        :type columns: str
        :type table: str
        :type 
        """
