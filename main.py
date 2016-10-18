# coding: utf-8
import os
import asyncio
import tornado.platform.asyncio
import tornado.web
from tornado.options import define, options
import handlers
import config
import init_database

tornado.platform.asyncio.AsyncIOMainLoop().install()
loop = asyncio.get_event_loop()

init_database.main(loop)

setting = {
    'static_path': os.path.join(os.path.dirname(__file__), "static"),
    'template_path': os.path.join(os.path.dirname(__file__), 'template')
}

define('favicon_link', os.path.join(setting['static_path'], 'favicon.ico'))
define('head_pic_link', os.path.join(setting['static_path'], 'head.jpg'))
define('blog_name', config.blog_name)
define('dates', config.dates)
define('article_num', config.article_num)


class BlogApplication(tornado.web.Application):
    def __init__(self, handlers=None, default_host="", transforms=None, **settings):
        super(BlogApplication, self).__init__(handlers, default_host, transforms, **settings)
        self.loop = loop
        self.article_num = options.article_num
        self.opts = {
            'faviconLink': options.favicon_link,
            'headPicLink': options.head_pic_link,
            'blogName': options.blog_name,
            'dates': options.dates
        }
        self.get_site_title = lambda title: str(title) + ' - ' + self.opts['blogName'] if title else self.opts['blogName']


app = BlogApplication([
    (r'/', handlers.TimeHandler),
    (r'/t/(.*)_to_(.*)/(.*)', handlers.TimeHandler),
    (r'/a/(.*)', handlers.ArticleHandler),
    (r'/add', handlers.AddHandler),
], **setting)
app.listen(8765)
loop.run_forever()
