import leveldb

db = leveldb.LevelDB('path')

for key, value in db.iterate():
    try:
        print("Chave:", key.decode('utf-8'))
    except:
        print("Chave (bytes):", key.hex())

db.close()