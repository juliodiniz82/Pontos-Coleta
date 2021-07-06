#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, request
from flask_restful import Api
# from resources.resources import *
from sqlite3 import connect
from models import *
import pickle
import json
import pandas as pd
import geopandas as gpd


def geometry_to_tuple(geometry):
    """
    Parameters
    ---------------------------------
    geometry: GeoSeries

    Return
    ---------------------------------
    float
        latitude da endereço
    float
        longitude do endereço
    """
    return geometry._get_coords()[0][1], geometry._get_coords()[0][0]

def ajustar_endereco(endereco):
    """
    Parameters
    ---------------------------------
    endereco: string
    
    Return
    ---------------------------------
    string
        endereço alterado para evitar ambiguidades ou localizações fora de Fortaleza
    """

    if 'Fortaleza, CE' in endereco:
        return endereco
    else: 
        return endereco + ', Fortaleza, CE'


app = Flask(__name__)
app.secret_key = ''
api = Api(app)

@app.route('/sistema')
def homepage():
    return render_template('index.html')

@app.route('/sistema/cadastro_usuario')
def sign_up_user():
    return render_template('sign_up_user.html')

@app.route('/sistema/login')
def login():
    return render_template('login.html')

@app.route('/sistema/mapa.html', methods=['POST'])
def atualizar_rotas():
    data = json.loads(json.dumps(request.form))
    end = gpd.tools.geocode(ajustar_endereco(data['localizacao']), 
    provider='nominatim', user_agent='Intro Geocode')
    
    print(type(end['geometry'][0]))
    lat, lon = geometry_to_tuple(end['geometry'][0])

    p = PontoDeColeta(lat, lon, data['localizacao'])

    banco = connect('coleta.db')
    cursor = banco.cursor()

    cursor.execute('INSERT INTO coleta VALUES (?, ?) ', (pickle.dumps(p), 'pontos_sugeridos'))
    banco.commit()

    cursor.execute('SELECT * FROM coleta WHERE tipo = ?', ('pontos_coleta', ))
    ativos = cursor.fetchall()

    cursor.close()
    banco.close()

    ativos = [ pickle.loads(a[0]).to_dict() for a in ativos ]
    # print(ativos)
    
    return render_template('mapa.html', ativos=ativos)

@app.route('/sistema/mapa.html')
def visualizar_rotas():
    banco = connect('coleta.db')
    cursor = banco.cursor()

    # Pega os pontos de coleta para exibição no mapa
    cursor.execute('SELECT * FROM coleta WHERE tipo = ?', ('pontos_coleta', ))
    ativos = cursor.fetchall()

    cursor.close()
    banco.close()

    ativos = [ pickle.loads(a[0]).to_dict() for a in ativos ]

    return render_template('mapa.html', ativos=ativos, locations=json.dumps([ativos[0]]))

app.run(port=5000, debug=True)
