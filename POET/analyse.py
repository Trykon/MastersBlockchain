
f = open('thechain.txt', 'r')
lines = f.readlines()
starttime = float(0)
lastaddition = float(0)
countadditions = 0
totaltransactions = 0
delayssummed = float(0)
blockdelayssummed = float(0)
for idx, val in enumerate(lines):
    words = val.split()
    if(idx == 0):
        for word in words:
            if(len(word) == 13):
                starttime = float(word)
                lastaddition = float(word)
    elif(idx % 3 == 0):
        countadditions += 1
        for word in words:
            if(len(word) == 13):
                temptimestamp = float(word)
                delay = temptimestamp - lastaddition
                blockdelayssummed += delay
                lastaddition = temptimestamp
    elif(idx % 3 == 2):
        for word in words:
            if(len(word) == 15):
                totaltransactions += 1
                transtimestamp = float(int(word[:-2]))
                delay = lastaddition - transtimestamp
                delayssummed += delay
print("total time running: ", str(lastaddition - starttime), "miliseconds")
print("amount of blocks passed: ", countadditions)
print("amount of blocks per second: ",
      int(countadditions/(lastaddition - starttime)*1000))
print("amount of transactions passed: ", totaltransactions)
print("amount of transactions per second: ",
      int(totaltransactions/(lastaddition - starttime)*1000))
print("avg delay between blocks: ",
      int(blockdelayssummed / countadditions), "miliseconds")
print("avg delay transaction to chain: ",
      int(delayssummed / totaltransactions), "miliseconds")
f.close()
input()
