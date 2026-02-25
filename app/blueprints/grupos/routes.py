from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from app.models import db
from app.models.igreja import Ministerio, Funcao, MembroMinisterio, Membro
from . import grupos_bp


@grupos_bp.route('/grupos', methods=['GET', 'POST'])
@login_required
def grupos():
    if request.method == 'POST':
        t = request.form.get('tipo_acao')
        i = request.form.get('item_id')

        if t == 'novo_ministerio':
            m = Ministerio.query.get(i) if i else Ministerio()
            if not i:
                db.session.add(m)
            m.nome = request.form.get('nome')
            m.descricao = request.form.get('descricao')
            flash(f"Ministério '{m.nome}' salvo com sucesso!", 'success')

        elif t == 'nova_funcao':
            f = Funcao.query.get(i) if i else Funcao()
            if not i:
                db.session.add(f)
            f.nome = request.form.get('nome')
            flash(f"Função '{f.nome}' salva com sucesso!", 'success')

        db.session.commit()
        return redirect(url_for('grupos.grupos'))

    return render_template(
        'main/grupos.html',
        ministerios=Ministerio.query.all(),
        funcoes=Funcao.query.all()
    )


@grupos_bp.route('/ministerio/deletar/<int:id>')
@login_required
def deletar_ministerio(id):
    m = Ministerio.query.get_or_404(id)
    
    try:
        # Remove vínculos primeiro (FK safe) para não dar Erro 500
        MembroMinisterio.query.filter_by(ministerio_id=id).delete(synchronize_session=False)
        
        nome = m.nome
        db.session.delete(m)
        db.session.commit()
        flash(f"Ministério '{nome}' excluído com sucesso.", "danger")
        
    except Exception as e:
        db.session.rollback()
        flash("Erro ao excluir ministério.", "danger")

    return redirect(url_for('grupos.grupos'))


@grupos_bp.route('/funcao/deletar/<int:id>', methods=['GET', 'POST'])
@login_required
def deletar_funcao(id):
    f = Funcao.query.get_or_404(id)

    try:
        # remove vínculos primeiro (FK safe)
        MembroMinisterio.query.filter_by(funcao_id=id).delete(synchronize_session=False)

        nome = f.nome
        db.session.delete(f)
        db.session.commit()
        flash(f"Função '{nome}' excluída com sucesso.", "danger")

    except Exception as e:
        db.session.rollback()
        flash("Erro ao excluir função.", "danger")

    return redirect(url_for('grupos.grupos'))
