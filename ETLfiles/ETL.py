import psycopg2
import leveldb
import nbtlib
import io


conn = psycopg2.connect("host= dbname= user= password=")
cur = conn.cursor()

db = leveldb.LevelDB('C:/UNCOMPRESSED/DBFILES/PATH')

for key, value in db.iterate():
    try:
        key_str = key.decode('utf-8')

        if key_str.startswith('player_server_'):

            # Parseia o NBT sempre
            nbt_file = nbtlib.File.parse(io.BytesIO(value), byteorder='little')
            root = nbt_file['']

            
            cur.execute("""
                INSERT INTO player_data (server_id, online)
                VALUES (%s, %s)
                ON CONFLICT (server_id) DO NOTHING
            """, (key_str, False))

            # Busca o id pelo server_id — funciona pros dois casos
            cur.execute("SELECT id FROM player_data WHERE server_id = %s", (key_str,))
            player_id = cur.fetchone()[0]

            # Limpa inventário antigo
            cur.execute("DELETE FROM player_inventory WHERE player_id = %s", (player_id,))

            # Insere inventário atual
            for item in root['Inventory']:
                nome_item = str(item['Name'])
                if nome_item != '':
                    cur.execute("""
                        INSERT INTO player_inventory (player_id, item_name, quantidade)
                        VALUES (%s, %s, %s)
                    """, (player_id, nome_item, int(item['Count'])))

    except UnicodeDecodeError:
        pass
    except Exception as e:
        print("Erro:", e)

conn.commit()
cur.close()
conn.close()
db.close()
print("ETL concluído!")