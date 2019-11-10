import pymysql.cursors


connection=pymysql.connect(host='192.168.43.200',
                user='root',
                password='root',
                db='spider',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
try:
    with connection.cursor() as cursor:
        sql="insert into users (email,password) values(%s,%s)"
        cursor.execute(sql,('adfas','dfs'))
        connection.commit()
        with connection.cursor() as cursor:
            sql = "select id,password from users where email=%s"
            cursor.execute(sql,('adfas',))
            result=cursor.fetchone()
            print(result)
finally:
    connection.close()
