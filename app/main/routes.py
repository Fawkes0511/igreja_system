from PIL import Image
import os, secrets
from datetime import datetime
from flask import redirect, url_for, render_template, request, flash, jsonify, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.main import main_bp
from app.models import db
from app.models.igreja import (
    Membro, Congregacao, Ministerio, Funcao, MembroMinisterio,
    Evento, Inscricao, Agenda, Presenca
)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {
        'png',
        'jpg',
        'jpeg',
        'gif',
    }


def _get_attr(obj, name, default=None):
    return getattr(obj, name, default)


def _set_if_exists(obj, name, value):
    if hasattr(obj, name):
        setattr(obj, name, value)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Página inicial de visão geral do sistema.
    Mostra alguns números agregados para o administrador.
    Eventos: mesma lógica da aba Eventos (exclui FIXO, CANCELADO e passados).
    """
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    total_eventos = Evento.query.filter(
        Evento.descricao.is_distinct_from('[FIXO]'),
        Evento.descricao.is_distinct_from('[CANCELADO]'),
        Evento.data_evento >= hoje,
    ).count()

    stats = {
        'total_membros_adultos': Membro.query.filter_by(tipo='Adulto').count(),
        'total_membros_criancas': Membro.query.filter_by(tipo='Criança').count(),
        'total_membros_ativos': Membro.query.filter_by(ativo=True).count(),
        'total_congregacoes': Congregacao.query.count(),
        'total_ministerios': Ministerio.query.count(),
        'total_funcoes': Funcao.query.count(),
        'total_eventos': total_eventos,
    }

    congregacoes = Congregacao.query.filter_by(ativa=True).order_by(Congregacao.nome).all()
    ministerios = Ministerio.query.order_by(Ministerio.nome).all()
    funcoes = Funcao.query.order_by(Funcao.nome).all()

    return render_template('main/dashboard.html', stats=stats,
                          congregacoes=congregacoes, ministerios=ministerios, funcoes=funcoes)

