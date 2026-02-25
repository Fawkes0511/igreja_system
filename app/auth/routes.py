from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.models import db
from app.models.usuario import Usuario
from werkzeug.security import check_password_hash

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
