from peewee import *
from datetime import date
db=MySQLDatabase("spider",host="192.168.43.200",port=3306,user="root",password="root")



class Person(Model):
    name=CharField()
    birthdate=DateTimeField()

    class Meta:
        database=db
        table_name="persons"

if __name__=="__main__":
   # db.create_tables([Person])

    #生成数据
    #bob=Person(name="Bob",birthdate=date(1960,1,15))
    #bob.save()
    #获取数据
   # bob=Person.select().where(Person.name=='Bob').get()
   # print(bob.name)
   # grandma = Person.get(Person.name == 'Bob')
   #query是modelSelect对象  可以当做list操作
   query= Person.select().where(Person.name=="bob")
   for p in query:
       p.delete_instance()
       # print(p.name)
       # p.birthdate=date(1960,1,18)
       # p.save()#存在数据进行更新，不存在新增