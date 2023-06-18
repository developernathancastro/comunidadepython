from flask import render_template, redirect, url_for, flash, request, abort
from comunidadeimpressionadora import app, database
from comunidadeimpressionadora.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost
from comunidadeimpressionadora.models import Usuario, Post
from comunidadeimpressionadora import bcrypt
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image


#database.session.add
#database.session.commit


@app.route('/')                                                                                                         ##método que atrinui uma nova funcionalidade a função que vem em seguida
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)


@app.route('/contato')
def contato():
    return render_template('contato.html')


@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return  render_template('usuarios.html', lista_usuarios = lista_usuarios)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):                                #verifica se a senha que está no banco de dados é igual a que foi preenchida  o banco de dados
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login feito com sucesso no e-mail: {form_login.email.data}', 'alert-success')                       ##método.atrbuto.data pego o que o usuário preencheu
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))

        else:
            flash(f'Falha no Login. E-mail ou Senha Incorretos', 'alert-danger')
    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:                              ###quando o form é valido e clicou no botão de criar conta
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data).decode("utf-8")                                         ##transformando senha em senha criptografada
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada para o e-mail: {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('home'))
    return render_template('login.html', form_login = form_login, form_criarconta = form_criarconta )

@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash(f'Logout Feito com Sucesso', 'alert-success')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename ='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html', foto_perfil=foto_perfil)


@app.route('/post/criar', methods=['GET', 'POST'])
@login_required                                                                                                         ##garante que o usuário só vai conseguir acessar a página caso esteja logado
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo= form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post Criado com Sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form=form)

def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo


def atualizar_cursos(form):
    lista_cursos = []
    for campo in form:
        if 'curso_' in campo.name:
            if campo.data:                                                                                              ##retorna verdadeiro se estiver marcado e falso caso não esteja
                lista_cursos.append(campo.label.text)                                                                   ##.label traz o que tem na descrição do campo no site
    return  ';'.join(lista_cursos)                                                                                      ##transformando lista em texto único


@app.route('/perfil/editar',  methods=['GET', 'POST'])                                                                  ##toda página que tem formulario preciso dizer que o método post é permitido
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():                                                                                       ##validate_on_submit() roda todos os métodos que começam com o nome validate_
        current_user.email = form.email.data
        current_user.username = form.username.data                                                                      ##só estou dando update
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem

        current_user.cursos = atualizar_cursos(form)
        database.session.commit()
        flash(f'Perfil atualizado com Sucesso', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == "GET":
        form.email.data = current_user.email
        form.username.data = current_user.username


    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form=form)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form= FormCriarPost()
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post Atualizado com Sucesso', 'alert-success')
            return redirect(url_for('home'))
    else:
        form=None
    return render_template('post.html', post=post, form=form)


@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post Excluído com Sucesso', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)                                                                                                      ##Uusário tentou entrar em um link que não possui autorização para acessar



