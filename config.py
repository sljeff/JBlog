import configparser
import datetime

__all__ = ['blog_name', 'categories', 'dates', 'article_num']

config = configparser.ConfigParser()
config.read('blog.ini', encoding='utf-8')

DEFAULT = config['DEFAULT']
blog_name = DEFAULT.get('blog_name', "No Name Here")
from_date = DEFAULT.get('from_date', '201610')

# year and month from config
from_year = int(from_date[:4])
from_month = int(from_date[4:])
assert 1 <= from_month <= 12 and 1970 < from_year < 9999, 'wrong from_date'

# create from_datetime and to_datetime
from_datetime = datetime.datetime(from_year, from_month, 1)
to_datetime = datetime.datetime.now()

# add_month_num
add_month_num = 3


# a function that get year and month after add months
def add_month(year, month, add_num):
    month = month + add_num
    if month > 12:
        year += 1
        month -= 12
    elif month <= 0:
        year -= 1
        month += 12
    return year, month

# get dates
dates = []
while from_datetime < to_datetime:
    link = '/t/' + str(from_datetime.timestamp())
    name_start = '{}年{}月'.format(str(from_datetime.year), str(from_datetime.month))
    new_year, new_month = add_month(from_datetime.year, from_datetime.month, add_month_num)
    from_datetime = datetime.datetime(new_year, new_month, 1)  # new from_datetime

    to_year, to_month = add_month(from_datetime.year, from_datetime.month, -1)
    name_end = '{}年{}月'.format(str(to_year), str(to_month))
    link += '_to_' + str(from_datetime.timestamp()) + '/0'
    dates.append((link, name_start+' 至 '+name_end))

# get article_num
article_num = int(DEFAULT['article_num'])

# get categories
cat_names = []
for name in DEFAULT['cat_names'].split('|'):
    name = name.strip()
    cat_names.append(name)

cat_slugs = []
for slug in DEFAULT['cat_slugs'].split('|'):
    slug = slug.strip()
    cat_slugs.append(slug)

categories = {slug: name for slug, name in zip(cat_slugs, cat_names)}
