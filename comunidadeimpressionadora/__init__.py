from flask import Flask                        ##aqui são instaladas todas as extensões e integradas ao site
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from flask_login import LoginManager

app = Flask(__name__)


app.config['SECRET_KEY'] = '14d841e9642f05874926e8a662408bec'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///comunidade.db'                                                         ##caminho local onde vai ficar o banco de dados

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = ('login')
login_manager.login_message_category = 'alert-info'

from comunidadeimpressionadora import routes                                                                            ##routes precisam do app para funcionar e o app está sendo criado
                                                                                                                        ##depois das importações




