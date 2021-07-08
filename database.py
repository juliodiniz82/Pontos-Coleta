import random
import sqlite3
from pickle import loads, dumps


# Criação do banco
banco = sqlite3.connect('coleta.db')
cursor = banco.cursor()
cursor.execute('CREATE TABLE coleta (dado blob, tipo text)')
cursor.execute('CREATE TABLE usuario (id integer primary key, nome text, nascimento text, \
cpf text, cep text, email text, senha text)')

cursor.close()
banco.close()
