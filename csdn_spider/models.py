from peewee import *
from datetime import date
db=MySQLDatabase("spider",host="192.168.43.200",port=3306,user="root",password="root")

class BaseModedel(Model):
    class Meta:
        database=db


class Topic(BaseModedel):
    title=CharField()
    content=TextField(default="")
    id=IntegerField(primary_key=True)
    author=CharField()
    create_time=DateTimeField()
    answer_nums=IntegerField(default=0)
    click_nums=IntegerField(default=0)
    praised_nums=IntegerField(default=0)
    jtl_nums=FloatField(default=0.0)#结贴率
    score=IntegerField(default=0)#赏分
    status=CharField()#状态
    last_answer_time=DateTimeField()

class Answer(BaseModedel):
    topic_id=IntegerField()
    author=CharField()
    content=TextField(default="")
    create_time=DateTimeField()
    parised_nums=IntegerField(default=0)#点赞数量
    
   
class Author(BaseModedel): 
    name=CharField()
    id=CharField(primary_key=True)
    click_nums=IntegerField(default=0)#访问数量
    original_nums=IntegerField(default=0)#原创数量
    forward_nums=IntegerField(default=0)#转发数
    rate=IntegerField(default=1)#排名
    answer_nums=IntegerField(default=0)#评论数
    parised_nums=IntegerField(default=0)#获赞数
    desc=TextField(null=True)
    industry=CharField(null=True)
    location=CharField(null=True)
    follower_nums=IntegerField(default=0)#粉丝数
    following_nums=IntegerField(default=0)#关注数


if __name__ == "__main__":
    db.create_tables([Topic,Answer,Author])
