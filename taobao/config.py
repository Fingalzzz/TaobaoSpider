# -*- coding: utf-8 -*-

# Redis
# REDIS_HOST = '127.0.0.1'
# REDIS_PORT = 6379
# REDIS_DATABASE_NAME = 0

# MongoDB
MONGO_URI = 'mongodb://localhost:27017'
MONGO_DB = 'taobao'

# 图片保存路径
IMAGES_STORE = 'C:/scrapy'

# search keywords
KEYWORDS = [
    '短袖', '长袖', '同款', '森系', '日系', '小清新',
    '风衣', '大衣', '西装', '连衣裙', '半身裙', '针织衫',
    '高腰裤', '毛呢外套', '衬衫', '卫衣', '短裤', 'T恤'
]

# Abu proxy settings
PROXIES = {
    'ip_port': 'http-dyn.abuyun.com:9020',
    'user': 'HE307V7G720N643D',
    'passwd': '50B19E042761C968'
}
