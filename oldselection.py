def select_new_block():
    global miners
    POET_timer: List[Miner]
    POET_timer = [None] * 1000
    POET_counter = 0
    while True:
        miners_length = len(miners)
        if(len(miners) > 0):
            print(len(miners))
            for x in miners:
                r = random.randint(0, 999)
                while POET_timer[r] is not None:
                    r = random.randint(0, 999)
                print(r)
                POET_timer[r] = x
            print("MINERS", miners_length, len(miners))
            if miners_length != len(miners):
                continue
            while True:
                if(POET_timer[POET_counter] is not None):
                    print("potato")
                    if(len(chain) > 0):
                        if(chain[-1].header.this_hash ==
                           POET_timer[POET_counter].block.header.prev_hash):
                            chain.append(POET_timer[POET_counter].block)
                    else:
                        POET_timer[POET_counter] = Miner(0)
                        chain.append(POET_timer[POET_counter].block)
                    toWrite = POET_timer[POET_counter].block.toString()
                    file1.write(toWrite)
                    file1.flush()
                    print(len(chain))
                    miner_id = POET_timer[POET_counter].ID
                    r = random.randint(0, 999)
                    while(POET_timer[r] != [Miner(0)]):
                        r = random.randint(0, 999)
                    POET_timer[r] = miners[miner_id-1]
                    POET_timer[POET_counter] = [Miner(0)]
                    block_trans = json.loads(miners[miner_id-1].block.data)
                    trans_length = len(block_trans)
                    global transactions
                    transactions = transactions[trans_length:]
                if POET_counter == 999:
                    POET_counter = 0
                else:
                    POET_counter = POET_counter+1
                if miners_length != len(miners):
                    break
