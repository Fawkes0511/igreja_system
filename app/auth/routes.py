from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.models import db
from app.models.usuario import Usuario
from werkzeug.security import check_password_hash, generate_password_hash

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('membros.membros_page'))

    if request.method == 'POST':
        username = request.form.get('email')  # Campo é "usuário" no HTML
        senha = request.form.get('senha')

        # Buscar usuário pelo email (que é o campo username)
        usuario = Usuario.query.filter_by(email=username).first()

        if usuario and check_password_hash(usuario.senha_hash, senha):
            if usuario.ativo:
                login_user(usuario)
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('membros.membros_page'))
            else:
                flash('Conta desativada.', 'danger')
        else:
            flash('Usuário ou senha incorretos.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/')
def root_redirect():
    return redirect(url_for('auth.login'))

# ==========================================
# ROTAS DE GESTÃO DE USUÁRIOS (ACESSOS)
# ==========================================

@auth_bp.route('/usuarios', methods=['GET'])
@login_required
def listar_usuarios():
    # Lista todos os usuários cadastrados
    usuarios = Usuario.query.all()
    return render_template('auth/usuarios.html', usuarios=usuarios)

@auth_bp.route('/usuarios/novo', methods=['POST'])
@login_required
def novo_usuario():
    nome = request.form.get('nome')
    email = request.form.get('email') # Funciona como o 'username' no sistema
    senha = request.form.get('senha')

    # Verifica se o usuário já existe
    if Usuario.query.filter_by(email=email).first():
        flash('Erro: Já existe um usuário com este login.', 'danger')
        return redirect(url_for('auth.listar_usuarios'))

    # Cria o novo usuário como administrador (criptografando a senha)
    novo_user = Usuario(
        nome=nome,
        email=email,
        senha_hash=generate_password_hash(senha),
        tipo='admin', # Todos recebem admin conforme a regra de negócio
        ativo=True
    )
    db.session.add(novo_user)
    db.session.commit()
    
    flash('Usuário administrador criado com sucesso!', 'success')
    return redirect(url_for('auth.listar_usuarios'))

@auth_bp.route('/usuarios/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_usuario(id):
    # Proteção: Impede o administrador de apagar a própria conta acidentalmente
    if current_user.id == id:
        flash('Erro: Você não pode deletar a conta que está usando no momento.', 'danger')
        return redirect(url_for('auth.listar_usuarios'))
        
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    
    flash('Acesso revogado com sucesso!', 'success')
    return redirect(url_for('auth.listar_usuarios'))