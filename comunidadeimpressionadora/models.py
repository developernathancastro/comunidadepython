from comunidadeimpressionadora import database, login_manager   ##arquivo direto no init não preciso passar o .página no from
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))                                                                           ##busca usuário pelo ID


class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)                                                            ##preeche automaticamente atribuindo um id
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)                                               ##valor único na tabela
    senha = database.Column(database.String, nullable=False)
    foto_perfil = database.Column(database.String, default='default.jpg')
    posts = database.relationship('Post', backref='autor', lazy=True)                                                   ##RECEBE VÁRIAS INFORMAÇÕES DE OUTRA TABELA
    cursos = database.Column(database.String, nullable=False, default='Não Informado')                                  ##default cria automaticamente valor padrao caso não passe nada

    def contar_posts(self):
        return len(self.posts)



class Post(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String, nullable=False)
    corpo = database.Column(database.Text, nullable=False)
    data_criacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)                   ##na chave estrangeira sempre tenho que passar o nome da minha classe como minuscula

