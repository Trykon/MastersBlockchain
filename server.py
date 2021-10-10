import socket
import threading
import json
from typing import List
import random
import time
import math
from hashlib import blake2b

HOST = '127.0.0.1'
PORT = 50000
# step 1 Create a server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CONSENSUS = "POET"
file1 = open("thechain.txt", "a")


def convertTupleToString(t):
    outString = ''
    for item in t:
        outString = outString + str(item)
    return outString


class Header:
    def __init__(self, prev_hash, timestamp, this_hash):
        self.prev_hash = prev_hash
        self.timestamp = timestamp
        self. this_hash = this_hash

    def __hash__(self):
        return hash((self.prev_hash, self.timestamp, self.this_hash))


class Block:
    def __init__(self, header,  data):
        self.header = Header(header.prev_hash,
                             header.timestamp,
                             header.this_hash)
        self.data = data

    def toString(self):
        returnTuple = ("Header: ", self.header.prev_hash, " ",
                       self.header.timestamp, " ",
                       self.header.this_hash, " \n", "Data: ", self.data, "\n")
        return convertTupleToString(returnTuple)


class Miner:
    def __init__(self, Id):
        self.ID = Id
        self.block = Block(Header(0, 0, 0), "")

    def add_block(self, block):
        self.block = block


class Transaction:
    def __init__(self, sender, receiver, value, timestamp):
        self.sender = sender
        self.receiver = receiver
        self.value = value
        self.timestamp = timestamp

    def compare(self, trans):
        if(self.sender != trans.sender):
            return False
        if(self.receiver != trans.receiver):
            return False
        if(self.value != trans.value):
            return False
        if(self.timestamp != trans.timestamp):
            return False
        return True


chain: List[Block] = []
miners: List[Miner] = []
transactions: List[Transaction] = []
LOCK_MINERS = False
LOCK_SELECTION = True
MINER_READY = False


def on_new_client(clientsocket, address, ID):
    global transactions
    trans_amount = len(transactions)
    json_msg = {"id": ID}
    msg = json.dumps(json_msg)
    clientsocket.send(msg.encode())
    recmsg = clientsocket.recv(1024)
    msg = json.loads(recmsg.decode())
    if(msg["status"] != "ok"):
        print("something is wrong")
    while True:
        if(trans_amount == len(transactions)):
            continue
        if(len(chain) > 0):
            h = blake2b(digest_size=10)
            temp = (chain[-1].header.prev_hash, chain[-1].header.timestamp,
                    chain[-1].header.this_hash)
            h.update(temp)
            msg = {"transactions": [tr.__dict__ for tr in transactions],
                   "lastHash": str(h.hexdigest().encode())}
            print(h.hexdigest().encode())
        else:
            msg = {"transactions": [tr.__dict__ for tr in transactions],
                   "lastHash": hash(000)}
        jmsg = json.dumps(msg)
        # print(msg)
        clientsocket.send(jmsg.encode())
        msg = clientsocket.recv(1024)
        json_msg = json.loads(msg.decode())
        # print(json_msg)
        msg_id = json_msg["id"]
        msg_header = Header(json_msg["header_prevtime"],
                            json_msg["header_timestamp"],
                            json_msg["header_curtime"])
        msg_data = json.dumps(json_msg["data"])
        received_block = Block(msg_header, msg_data)
        miners[msg_id-1].add_block(received_block)
        # print(miners[msg_id-1].block.toString())
    clientsocket.close()


def checkAndRemoveTrans(d):
    global transactions
    # print("printing d: ", d)
    # print("printing transactions: ", [tr.__dict__ for tr in transactions])
    if(d == ""):
        return False
    transToCheck = json.loads(d)
    if(len(transToCheck) == 0):
        return False
    for transTC in transToCheck:
        asTrans = Transaction(transTC['sender'],
                              transTC['receiver'],
                              transTC['value'],
                              transTC['timestamp'])
        transIsIn = False
        for trans in transactions:
            if(trans.compare(asTrans)):
                transIsIn = True
        if(transIsIn is not True):
            # print("found inexistant transition")
            return False
    for transTC in transToCheck:
        asTrans = Transaction(transTC['sender'],
                              transTC['receiver'],
                              transTC['value'],
                              transTC['timestamp'])
        for trans in range(0, len(transactions)):
            if(transactions[trans].compare(asTrans)):
                del transactions[trans]
                break
    return True


def select_new_block():
    global miners
    global LOCK_MINERS
    global LOCK_SELECTION
    global MINER_READY
    chain.append(Miner(0).block)
    file1.write("Miner ID: " + str(Miner(0).ID) +
                " Current timestamp: " +
                str(current_milli_time()) + "\n" +
                Miner(0).block.toString())
    file1.flush()
    GaFitFat = []
    while True:
        if(len(miners) > 0):
            # add fitness and fatigue to miners
            if(len(miners) > len(GaFitFat)):
                GaFitFat.append([miners[len(GaFitFat)], 10, 100])
                # print(GaFitFat[-1][0].block.toString())
            # refill fatigue + add up fitness
            max_fitness = 0
            for miner in GaFitFat:
                miner[2] = min(miner[2]+(1/math.sqrt(len(GaFitFat))), 100)
                if(miner[2] == 100):
                    max_fitness += miner[1]
            # roulette wheel selection based on fitness
            # add (or not) block from the chosen miner
            # add/remove fitness to/from chosen miner
            # empty fatigue from chosen miner
            rouletteRandom = random.randint(0, max_fitness)
            for miner in GaFitFat:
                if(miner[2] == 100):
                    rouletteRandom -= miner[1]
                    if(rouletteRandom <= 0):
                        if(chain[-1].header.this_hash ==
                           miner[0].block.header.prev_hash):
                            if(checkAndRemoveTrans(miner[0].block.data)):
                                chain.append(miner[0].block)
                                file1.write("Miner ID: " + str(miner[0].ID) +
                                            " Current timestamp: " +
                                            str(current_milli_time()) + "\n" +
                                            miner[0].block.toString())
                                file1.flush()
                                miner[1] += (1 + len(miner[0].block.data))
                                miner[2] = 0
                            else:
                                miner[1] = max(1, miner[1]-1)
                                miner[2] = 0
                        else:
                            miner[1] = max(1, miner[1]-1)
                            miner[2] = 0

        if(MINER_READY):
            LOCK_SELECTION = True
            LOCK_MINERS = False
            while(LOCK_SELECTION):
                continue
            LOCK_MINERS = True


def current_milli_time():
    return round(time.time() * 1000)


def create_random_transactions():
    while True:
        global transactions
        trans = Transaction(random.randint(0, 1000),
                            random.randint(0, 1000),
                            random.randint(0, 100000),
                            current_milli_time())
        transactions.append(trans)
        time.sleep(0.003)


server_socket.bind((HOST, PORT))
server_socket.listen(10)
counter = 1
create_trans = threading.Thread(target=create_random_transactions)
POET_thread = threading.Thread(target=select_new_block)
POET_thread.start()
while True:
    c, addr = server_socket.accept()
    MINER_READY = True
    while(LOCK_MINERS):
        continue
    LOCK_SELECTION = True
    minerThread = threading.Thread(name="Thread-{}".format(counter),
                                   target=on_new_client,
                                   args=(c, addr, counter))
    miners.append(Miner(counter))
    if(counter == 1):
        create_trans.start()
    counter = counter+1
    minerThread.start()
    LOCK_MINERS = True
    MINER_READY = False
    LOCK_SELECTION = False
