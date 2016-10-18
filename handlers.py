import datetime
import tornado.web
import db
import os
import markdown2
from functools import lru_cache


def get_overview(whole_article):
    """
    :param str whole_article: article
    :rtype: str
    """
    end_index = whole_article.index('</p>', 200) + 4
    return whole_article[0:end_index]


class BaseHandler(tornado.web.RequestHandler):
    pass


class ArticleHandler(BaseHandler):
    async def get(self, slug):
        d = db.BlogDB(self.application.loop)
        row = await d.select_article(slug)
        if row is None:
            row = {'title': '', 'html_content': '', 'author': '', 'time': ''}
        article_options = {
            'mainTitle': row['title'],
            'content': row['html_content'],
            'pageTitle': self.application.get_site_title(row['title']),
            'articleAuthor': row['author'],
            'articleDate': row['time']
        }
        self.render('article.html', **article_options, **self.application.opts)


class TimeHandler(BaseHandler):
    async def get(self, begin=None, end=None, page_num=0):
        page_num = int(page_num)
        if begin is not None:
            begin = datetime.datetime.fromtimestamp(float(begin))
        if end is not None:
            end = datetime.datetime.fromtimestamp(float(end))
        d = db.BlogDB(self.application.loop)
        rows = await d.select_articles_by_time(begin, end, self.application.article_num, page_num)
        archives = []
        next_link = None
        pre_link = page_num - 1 if page_num > 0 else None
        if rows:
            for row in rows:
                title = row['title']
                overview = get_overview(row['html_content'])
                archives.append({'title': title, 'overview': overview})
            next_link = page_num + 1 if len(rows) >= 20 else None
        page_title = '{0} to {1}'.format(str(begin), str(end)) if begin or end else None
        category_options = {
            'archives': archives,
            'preLink': pre_link,
            'nextLink': next_link,
            'pageTitle': self.application.get_site_title(page_title)
        }
        self.render('articles.html', **category_options, **self.application.opts)


class AddHandler(BaseHandler):
    def get(self):
        self.render('add.html', cat=self.application.opts['categories'])
    async def post(self):
        slug = self.get_body_arguments('slug')[0]  # type: str
        md_file_name = os.path.join('md', slug.strip() + '.md')
        if not os.path.isfile(md_file_name):
            self.write('fail')
            return
        with open(md_file_name, 'r', encoding='utf-8') as f:
            md_content = await self.application.loop.run_in_executor(None, f.read)
            html_content = markdown2.markdown(md_content)
        try:
            title = self.get_body_arguments('title')[0]
            author = self.get_body_arguments('author')[0]
            time = datetime.datetime.now()
        except:
            self.write('fail')
            return

        d = db.BlogDB(self.application.loop)
        result = await d.add_article(slug, title, md_content, html_content, author, time)
        if result:
            self.write('success')
        else:
            self.write('fail')
