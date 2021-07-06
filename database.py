import random
import sqlite3
from pickle import loads, dumps


# Criação do banco
banco = sqlite3.connect('coleta.db')
cursor = banco.cursor()
cursor.execute('CREATE TABLE coleta (dado blob, tipo text)')

matriz = []
for i in range(10):
    matriz.append([])
    for j in range(10):
        if random.random() < 0.3:
            matriz[i].append(0)
        else:
            matriz[i].append(1)

cursor.execute("INSERT INTO coleta VALUES (?, ?)", (dumps(matriz), 'mapa'))
banco.commit()
