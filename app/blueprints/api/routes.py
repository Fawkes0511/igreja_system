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


def _build_membros_base(tipo=None, congregacao_id=None, ministerio_id=None, funcao_id=None, ativo=None):
    """
    Retorna subquery de membro_ids que atendem aos filtros.
    ativo: True = só ativos, False = só inativos, None = todos.
    """
    q = db.session.query(Membro.id)
    if ativo is True:
        q = q.filter(Membro.ativo == True)
    elif ativo is False:
        q = q.filter(Membro.ativo == False)
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
    ativo_arg = request.args.get('ativo', '').strip().lower()
    if ativo_arg in ('1', 'true', 'ativos', 'ativo'):
        ativo = True
    elif ativo_arg in ('0', 'false', 'inativos', 'inativo'):
        ativo = False
    else:
        ativo = None

    base = _build_membros_base(tipo, congregacao_id, ministerio_id, funcao_id, ativo=ativo)
    base_select = select(base.c.id)

    if eixo == 'por_congregacao':
        rows = (
            db.session.query(
                Congregacao.id,
                Congregacao.nome,
                func.count(distinct(membro_congregacao.c.membro_id)),
            )
            .select_from(membro_congregacao)
            .join(Congregacao, Congregacao.id == membro_congregacao.c.congregacao_id)
            .filter(membro_congregacao.c.membro_id.in_(base_select))
            .filter(Congregacao.ativa == True)
            .group_by(Congregacao.id, Congregacao.nome)
            .order_by(func.count(distinct(membro_congregacao.c.membro_id)).desc())
            .all()
        )
        labels = [r[1] for r in rows]
        values = [r[2] for r in rows]
        members_by_label = []
        for cong_id, _nome, _count in rows:
            nomes = (
                db.session.query(Membro.nome, Membro.tipo)
                .join(membro_congregacao, membro_congregacao.c.membro_id == Membro.id)
                .filter(
                    membro_congregacao.c.congregacao_id == cong_id,
                    Membro.id.in_(base_select),
                )
                .order_by(Membro.nome)
                .all()
            )
            members_by_label.append([{'nome': n[0], 'tipo': n[1] or '-'} for n in nomes])
    elif eixo == 'por_ministerio':
        rows = (
            db.session.query(
                Ministerio.id,
                Ministerio.nome,
                func.count(distinct(MembroMinisterio.membro_id)),
            )
            .select_from(MembroMinisterio)
            .join(Ministerio, Ministerio.id == MembroMinisterio.ministerio_id)
            .filter(MembroMinisterio.membro_id.in_(base_select))
            .group_by(Ministerio.id, Ministerio.nome)
            .order_by(func.count(distinct(MembroMinisterio.membro_id)).desc())
            .all()
        )
        labels = [r[1] for r in rows]
        values = [r[2] for r in rows]
        members_by_label = []
        for min_id, _nome, _count in rows:
            mid_list = (
                db.session.query(MembroMinisterio.membro_id)
                .filter(
                    MembroMinisterio.ministerio_id == min_id,
                    MembroMinisterio.membro_id.in_(base_select),
                )
                .distinct()
                .all()
            )
            ids = [x[0] for x in mid_list]
            nomes = (
                db.session.query(Membro.nome, Membro.tipo)
                .filter(Membro.id.in_(ids))
                .order_by(Membro.nome)
                .all()
            ) if ids else []
            members_by_label.append([{'nome': n[0], 'tipo': n[1] or '-'} for n in nomes])
    elif eixo == 'por_funcao':
        rows = (
            db.session.query(
                Funcao.id,
                Funcao.nome,
                func.count(distinct(MembroMinisterio.membro_id)),
            )
            .select_from(MembroMinisterio)
            .join(Funcao, Funcao.id == MembroMinisterio.funcao_id)
            .filter(MembroMinisterio.membro_id.in_(base_select))
            .group_by(Funcao.id, Funcao.nome)
            .order_by(func.count(distinct(MembroMinisterio.membro_id)).desc())
            .all()
        )
        labels = [r[1] for r in rows]
        values = [r[2] for r in rows]
        members_by_label = []
        for func_id, _nome, _count in rows:
            mid_list = (
                db.session.query(MembroMinisterio.membro_id)
                .filter(
                    MembroMinisterio.funcao_id == func_id,
                    MembroMinisterio.membro_id.in_(base_select),
                )
                .distinct()
                .all()
            )
            ids = [x[0] for x in mid_list]
            nomes = (
                db.session.query(Membro.nome, Membro.tipo)
                .filter(Membro.id.in_(ids))
                .order_by(Membro.nome)
                .all()
            ) if ids else []
            members_by_label.append([{'nome': n[0], 'tipo': n[1] or '-'} for n in nomes])
    else:
        return jsonify({'error': 'eixo inválido'}), 400

    return jsonify({
        'labels': labels,
        'values': values,
        'members_by_label': members_by_label,
        'eixo': eixo,
    })
