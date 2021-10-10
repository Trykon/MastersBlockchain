import socket
import json
import time


def current_milli_time():
    return round(time.time() * 1000)


HOST = '127.0.0.1'
PORT = 50000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


client_socket.connect((HOST, PORT))
message = client_socket.recv(1024)
txtmessage = message.decode()
# print(txtmessage)
jsonMsg = json.loads(txtmessage)
MyID = jsonMsg["id"]
FILENAME = 'id'
FILENAME += str(MyID)
FILENAME += '.txt'
file = open(FILENAME, 'a')
newmsg = {"status": "ok"}
jmsg = json.dumps(newmsg)
# print(jmsg)
file.write(jmsg + "\n")
file.flush()
# print("written")
client_socket.send(jmsg.encode())
while True:
    # print("in while")
    msg = client_socket.recv(1024)
    # print("received")
    jmsg = msg.decode()
    # print(jmsg)
    file.write(jmsg + "\n")
    file.flush()
    # print("written again")
    jmessage = json.loads(jmsg)
    # print("loaded")
    curtime = current_milli_time()
    # hash_last = hash(str(jmessage["lastHash"]))
    # print(hash_last)
    block = {"id": MyID,
             "header_prevtime": jmessage["lastHash"],
             "header_timestamp": curtime,
             "header_curtime": hash(curtime),
             "data": jmessage["transactions"]}
    # print("block created")
    jnewmsg = json.dumps(block)
    # print("dumped")
    # print(jnewmsg)
    file.write(jnewmsg + "\n")
    file.flush()
    client_socket.send(jnewmsg.encode())
client_socket.close()
