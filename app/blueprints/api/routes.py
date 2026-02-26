"""
API para o dashboard de vínculos (gráficos interativos).
"""
from flask import jsonify, request
from flask_login import login_required
from sqlalchemy import func, distinct, select

from app.blueprints.api import api_bp
from app.models import db
from app.models.igreja import (
    Membro, Congregacao, Ministerio, Funcao, MembroMinisterio,
    membro_congregacao
)


def _build_membros_base(tipo=None, congregacao_id=None, ministerio_id=None, funcao_id=None):
    """
    Retorna subquery de membro_ids que atendem aos filtros.
    """
    q = db.session.query(Membro.id).filter(Membro.ativo == True)
    if tipo:
        q = q.filter(Membro.tipo == tipo)
    if congregacao_id:
        q = q.join(membro_congregacao).filter(membro_congregacao.c.congregacao_id == congregacao_id)
    if ministerio_id or funcao_id:
        q = q.join(MembroMinisterio)
        if ministerio_id:
            q = q.filter(MembroMinisterio.ministerio_id == ministerio_id)
        if funcao_id:
            q = q.filter(MembroMinisterio.funcao_id == funcao_id)
    return q.distinct().subquery()


@api_bp.route('/dashboard/vinculos', methods=['GET'])
@login_required
def api_dashboard_vinculos():
    """
    Retorna dados agregados para gráficos de vínculos.
    Params: eixo (por_congregacao | por_ministerio | por_funcao),
            tipo (Adulto | Criança | Visitante | ''),
            congregacao_id, ministerio_id, funcao_id (opcionais).
    """
    eixo = request.args.get('eixo', 'por_congregacao')
    tipo = request.args.get('tipo') or None
    congregacao_id = request.args.get('congregacao_id', type=int) or None
    ministerio_id = request.args.get('ministerio_id', type=int) or None
    funcao_id = request.args.get('funcao_id', type=int) or None

    base = _build_membros_base(tipo, congregacao_id, ministerio_id, funcao_id)

    if eixo == 'por_congregacao':
        rows = (
            db.session.query(Congregacao.nome, func.count(distinct(membro_congregacao.c.membro_id)))
            .select_from(membro_congregacao)
            .join(Congregacao, Congregacao.id == membro_congregacao.c.congregacao_id)
            .filter(membro_congregacao.c.membro_id.in_(select(base.c.id)))
            .filter(Congregacao.ativa == True)
            .group_by(Congregacao.id, Congregacao.nome)
            .order_by(func.count(distinct(membro_congregacao.c.membro_id)).desc())
            .all()
        )
    elif eixo == 'por_ministerio':
        rows = (
            db.session.query(Ministerio.nome, func.count(distinct(MembroMinisterio.membro_id)))
            .select_from(MembroMinisterio)
            .join(Ministerio, Ministerio.id == MembroMinisterio.ministerio_id)
            .filter(MembroMinisterio.membro_id.in_(select(base.c.id)))
            .group_by(Ministerio.id, Ministerio.nome)
            .order_by(func.count(distinct(MembroMinisterio.membro_id)).desc())
            .all()
        )
    elif eixo == 'por_funcao':
        rows = (
            db.session.query(Funcao.nome, func.count(distinct(MembroMinisterio.membro_id)))
            .select_from(MembroMinisterio)
            .join(Funcao, Funcao.id == MembroMinisterio.funcao_id)
            .filter(MembroMinisterio.membro_id.in_(select(base.c.id)))
            .group_by(Funcao.id, Funcao.nome)
            .order_by(func.count(distinct(MembroMinisterio.membro_id)).desc())
            .all()
        )
    else:
        return jsonify({'error': 'eixo inválido'}), 400

    return jsonify({
        'labels': [r[0] for r in rows],
        'values': [r[1] for r in rows],
        'eixo': eixo,
    })
