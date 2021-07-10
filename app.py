#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, request, flash, redirect, url_for
from flask_restful import Api
from flask_login import LoginManager, UserMixin, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
# from resources.resources import *
from sqlite3 import connect
from models import *
from base import dict_factory
import pickle
import json
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
app.secret_key = 'secret'
api = Api(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def get_user(user_id):
    banco = connect('coleta.db')
    cursor = banco.cursor()
    cursor.row_factory = dict_factory

    cursor.execute('SELECT * FROM usuario WHERE id = ?', (user_id, ))
    # Tupla que contém os atributos do registro que representa o usuário, 
    # ou None se o email não estiver cadastrado.
    usuario = cursor.fetchone()
    usuario = Usuario(**usuario)

    cursor.close()
    banco.close()
    
    return usuario

@app.route('/sistema')
def homepage():
    return render_template('index.html')

@app.route('/sistema/cadastro_usuario', methods=['GET', 'POST'])
def sign_up_user():

    banco = connect('coleta.db')
    cursor = banco.cursor()

    if request.method == 'POST':
        data = json.loads(json.dumps(request.form))
        if data['senha'] == data['confirma-senha']:

            cursor.execute('SELECT * FROM usuario WHERE email = ? OR cpf = ?', (data['email'], data['cpf']))

            if cursor.fetchone() is not None:
                cursor.close()
                banco.close()
                return render_template('Email ou CPF já cadastrado')
            
            cursor.execute('SELECT * FROM usuario')
            tam = len(cursor.fetchall())

            # Todos os cadastrados serão considerados administradores até futuras atualizações.
            cursor.execute('INSERT INTO usuario VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (tam +1 , data['nome'], 
            data['nascimento'], data['cpf'], data['cep'], data['email'], 
            generate_password_hash(data['senha']), 'administrador'))
            banco.commit()
            cursor.close()
            banco.close()
            return redirect(url_for('homepage'))
        else:
            cursor.close()
            banco.close()
            return render_template('<html>Senha incorreta</html>')

    return render_template('sign_up_user.html')

@app.route('/sistema/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        data = json.loads(json.dumps(request.form))
        banco = connect('coleta.db')
        cursor = banco.cursor()
        cursor.row_factory = dict_factory

        cursor.execute('SELECT * FROM usuario WHERE email = ?', (data['email'], ))
        
        # Dicionário que contém os atributos do registro que representa o usuário, 
        # ou None se o email não estiver cadastrado.
        usuario = cursor.fetchone()

        cursor.close()
        banco.close()

        if usuario is None:
            return render_template('<h1>Usuário não cadastrado</h1>')
        
        if check_password_hash(usuario['senha'], data['senha']):
            usuario = Usuario(**usuario)
            login_user(usuario)
            return redirect(url_for('rota'))
        else:
            return render_template('login.html', alerta=json.dumps('Senha incorreta'))
        
    return render_template('login.html')

@app.route('/sistema/mapa', methods=['GET', 'POST'])
def rota():

    banco = connect('coleta.db')
    cursor = banco.cursor()

    if request.method == 'POST':
        data = json.loads(json.dumps(request.form))
        end = gpd.tools.geocode(ajustar_endereco(data['localizacao']), 
        provider='nominatim', user_agent='Intro Geocode')
        
        lat, lon = geometry_to_tuple(end['geometry'][0])

        p = PontoDeColeta(lat, lon, data['localizacao'])

        cursor.execute('INSERT INTO coleta VALUES (?, ?) ', (pickle.dumps(p), 'pontos_sugeridos'))
        banco.commit()

    # Pega os pontos de coleta para exibição no mapa
    cursor.execute('SELECT * FROM coleta WHERE tipo = ?', ('pontos_coleta', ))
    ativos = cursor.fetchall()

    cursor.close()
    banco.close()

    ativos = [ pickle.loads(a[0]).to_dict() for a in ativos ]
    try:
        locations=json.dumps([ativos[0]])
    except IndexError:
        locations=json.dumps([])

    return render_template('mapa.html', ativos=ativos, locations=locations)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


app.run(port=5000, debug=True)
