from collections import Counter

import pymongo
import jieba.posseg as pseg

mongoDBurl = "mongodb://localhost:27017"
database_name = "redBookData"
collection_name = "RedBook"

client = pymongo.MongoClient(mongoDBurl)
db = client[database_name]
collection = db[collection_name]

user_data = ""
comments = collection.find()

for doc in comments:
    user_data += "".join(doc["user_content"])
    # # 分词处理

user_data = pseg.lcut(user_data)

# for word in user_data:
#     print(word.word,"    词性：",word.flag)

    #
    #
    # 过滤标点符号
filtered_words = [pair.word for pair in user_data if len(pair.word) > 1 and pair.flag.startswith("n")]

word_count = Counter(filtered_words)
for word,flag in word_count.most_common():
    print(word,flag)