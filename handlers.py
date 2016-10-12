import datetime
import tornado.web
import db


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


class CategoryHandler(BaseHandler):
    async def get(self, cat_slug, page_num=0):
        page_num = int(page_num)
        d = db.BlogDB(self.application.loop)
        cat_rows = await d.select(['id', 'name'], d.table_name['category'], [('slug', '=', cat_slug)])
        archives = []
        next_link = None
        pre_link = None
        cat_name = ''
        if len(cat_rows) != 0:
            cat_id = cat_rows[0]['id']
            cat_name = cat_rows[0]['name']
            rows = await d.select_articles_by_category(cat_id, self.application.article_num, page_num)
            for row in rows:
                title = row['title']
                overview = get_overview(row['html_content'])
                archives.append({'title': title, 'overview': overview})
            next_link = page_num + 1 if len(rows) >= 20 else None
            pre_link = page_num - 1 if page_num > 0 else None
        category_options = {
            'archives': archives,
            'preLink': pre_link,
            'nextLink': next_link,
            'pageTitle': self.application.get_site_title(cat_name)
        }
        self.render('category.html', **category_options, **self.application.opts)


class TimeHandler(BaseHandler):
    async def get(self, begin=None, end=None, page_num=0):
        page_num = int(page_num)
        if begin is not None:
            begin = datetime.datetime.fromtimestamp(int(begin))
        if end is not None:
            end = datetime.datetime.fromtimestamp(int(end))
        d = db.BlogDB(self.application.loop)
        rows = await d.select_articles_by_time(begin, end, self.application.article_num, page_num)
        archives = []
        for row in rows:
            title = row['title']
            overview = get_overview(row['html_content'])
            archives.append({'title': title, 'overview': overview})
        next_link = page_num + 1 if len(rows) >= 20 else None
        pre_link = page_num - 1 if page_num > 0 else None
        page_title = '{0} to {1}'.format(str(begin), str(end))
        category_options = {
            'archives': archives,
            'preLink': pre_link,
            'nextLink': next_link,
            'pageTitle': self.application.get_site_title(page_title)
        }
        self.render('category.html', **category_options, **self.application.opts)
