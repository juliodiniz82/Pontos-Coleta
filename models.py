from sqlite3 import connect
from pickle import dumps, loads
from scipy.spatial.distance import euclidean
from statistics import mean, stdev
from base import dict_factory
from flask_login import UserMixin
from werkzeug.security import generate_password_hash


banco = connect('coleta.db')


class PontoDeColeta():
    
    def __init__(self, lat, lon, endereco=None, cep=None):
        
        self.__lat = lat
        self.__lon = lon
        self.__endereco = endereco
        
        if isinstance(cep, str):
            self.__cep = cep
        else:
            self.__cep = None
    
    def get_coordenadas(self):
        
        return (self.__lat, self.__lon)
    
    def get_endereco(self):

        return self.__endereco

    def get_cep(self):
        
        return self.__cep
    
    def to_dict(self):
        
        return {'endereco': self.__endereco, 'latitude': self.__lat, 
                'longitude': self.__lon, 'cep': self.__cep}


class Rota():
    
    def __init__(self, pontos):
        
        self.__pontos = pontos
    
    def get_pontos(self):
        
        return self.__pontos


class Avaliador():
    
    @staticmethod
    def calcula_relevancia(ponto):
        
        cursor = banco.cursor()
        cursor.row_factory = dict_factory
        item = cursor.execute("SELECT * FROM coleta WHERE tipo = 'pontos_coleta'").fetchone()
        pontos_coleta = loads(item['dado'])
        
        localizacao = ponto.get_coordenadas()
        proximos_localizacao = [localizacao]
        proximos_distancia = [0]
        
        for p in pontos_coleta:
            dist = euclidean(localizacao, p.get_coordenadas())
            if dist > max(proximos_distancia):
                if len(proximos_distancia) == 3:
                    del proximos_distancia[0]
                    del proximos_localizacao[0]
                proximos_distancia.append(dist)
                proximos_localizacao.append(p)
        
        if stdev(proximos_distancia) >= 1:
            pontos_coleta.append(ponto)
            cursor.execute("UPDATE coleta SET dado = ? WHERE tipo = 'pontos_coleta'", (dumps(pontos_coleta),))
            banco.commit()
        cursor.close()
    
    @staticmethod
    def ativa_rota(rota):
        
        cursor = banco.cursor()
        cursor.row_factory = dict_factory
        cursor.execute("UPDATE coleta SET dado = ? WHERE tipo = 'rota_ativa'", (dumps(rota),))
        banco.commit()
        cursor.close()
    
    @staticmethod
    def exclui_pontos_sugeridos(pontos_a_excluir):
        
        cursor = banco.cursor()
        cursor.row_factory = dict_factory
        item = cursor.execute("SELECT * FROM coleta WHERE tipo = 'pontos_sugeridos'").fetchone()
        pontos_sugeridos = loads(item['dado'])
        
        for p in pontos_a_excluir:
            pontos_sugeridos.remove(p)
        
        cursor.execute("UPDATE coleta SET dado = ? WHERE tipo = 'pontos_sugeridos'", (dumps(pontos_sugeridos),))
        banco.commit()
        cursor.close()


# Classe Usuario é necessária para a operação de login padrão do FLask
class Usuario(UserMixin):

    def __init__(self, **data):

        self.id = data['id']
        self.nome = data['nome']
        self.nascimento = data['nascimento']
        self.cpf = data['cpf']
        self.cep = data['cep']
        self.email = data['email']
        # Criptografa a senha antes de armazená-la no banco
        self.senha = generate_password_hash(data['senha'])
