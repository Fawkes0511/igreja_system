from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.models import db
from app.models.igreja import Congregacao
from . import congregacoes_bp


@congregacoes_bp.route('/congregacoes', methods=['GET', 'POST'])
@login_required
def congregacoes():
    if request.method == 'POST':
        c_id = request.form.get('cong_id')
        c = Congregacao.query.get(c_id) if c_id else Congregacao()
        if not c_id:
            db.session.add(c)
        c.nome = request.form.get('nome')
        c.endereco = request.form.get('endereco')
        db.session.commit()
        return redirect(url_for('congregacoes.congregacoes'))

    return render_template(
        'main/congregacoes.html',
        congregacoes=db.session.query(Congregacao).all()
    )


@congregacoes_bp.route('/congregacao/deletar/<int:id>')
@login_required
def deletar_congregacao(id):
    from app.models.igreja import Congregacao, Evento, Agenda
    from app.models import db
    from sqlalchemy import text
    from flask import flash
    
    cong = Congregacao.query.get_or_404(id)
    
    # 1. O OLHEIRO: Verifica se tem eventos ou agendas atrelados
    eventos_dependentes = Evento.query.filter_by(congregacao_id=id).first()
    agendas_dependentes = Agenda.query.filter_by(congregacao_id=id).first()
    
    if eventos_dependentes or agendas_dependentes:
        flash('⚠️ Ação bloqueada: Existem eventos ou regras de agenda atrelados a esta congregação. Apague-os ou transfira-os antes de excluir este local.', 'danger')
        return redirect(url_for('congregacoes.congregacoes'))
        
    try:
        # 2. A LIMPEZA SEGURA: Solta os membros que estavam vinculados a ela e apaga
        db.session.execute(text(f"DELETE FROM membro_congregacao WHERE congregacao_id = {id}"))
        db.session.delete(cong)
        db.session.commit()
        flash('Congregação excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('⚠️ Erro interno do banco ao excluir a congregação.', 'danger')
        
    return redirect(url_for('congregacoes.congregacoes'))