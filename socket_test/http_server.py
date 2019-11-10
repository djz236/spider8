#soccket 服务端
import socket
import threading
server=socket.socket()
#绑定到0.0.0.0：8000端口
server.bind(('0.0.0.0',8000))
server.listen()

def handle_sock(sock,addr):
    while True:
        tmp_data = sock.recv(1024)
        print(tmp_data.decode("utf8"))
        # input_data = input()
        response_template='''HTTP/1.1 200 OK

        
        <html_test>
        <body>adsasdfasdf</body>
        </html_test>
        
        '''
        sock.send(response_template.encode("utf8"))
while True:
    #阻塞等待连接
    sock,addr=server.accept()
    client_thread=threading.Thread(target=handle_sock,args=(sock,addr))
    client_thread.start()
