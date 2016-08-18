# coding: utf-8
import os
import tornado.ioloop
import tornado.web

with open('test/content.html', 'r', encoding='utf-8') as f:
    content = f.read()


class TestHandler(tornado.web.RequestHandler):
    options = {
        'mainTitle': '人的想法和意识',
        'content': content,
        'preLink': 'a',
        'nextLink': 'b',
        'pageTitle': '人的想法和意识——善良的杰夫',
        'faviconLink': 'http://7xsn8i.com2.z0.glb.clouddn.com/img/favicon.ico',
        'headPicLink': 'http://7xsn8i.com2.z0.glb.clouddn.com/img/head.jpg',
        'blogName': '善良的杰夫',
        'categories': [('/c/think', '随想'), ('/c/think', '编程'), ('/c/think', 'Node'), ('/c/think', '记录')],
        'dates': [('/t/2016', '2016冬'), ('/t/2016', '2016秋'), ('/t/2016', '2016夏'), ('/t/2016', '2016春')] * 4,
        'articleAuthor': 'Jeff',
        'articleDate': '2016-05-27 01:08:39'
    }

    def get(self):
        self.render("template/article.html", **self.options)


class CSSHandler(tornado.web.RequestHandler):
    def get(self):
        self.write()


setting = {
    'static_path': os.path.join(os.path.dirname(__file__), "static")
}

app = tornado.web.Application([
    (r'/', TestHandler),
], **setting)
app.listen(8888)
tornado.ioloop.IOLoop.current().start()
