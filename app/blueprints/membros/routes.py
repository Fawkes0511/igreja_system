from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from PIL import Image

from app.models import db
from app.models.igreja import Membro, Congregacao, Ministerio, Funcao, MembroMinisterio
from . import membros_bp


@membros_bp.route('/membros', methods=['GET', 'POST'])
@login_required
def membros_page():

    if request.method == 'POST':
        try:
            membro_id = request.form.get('membro_id')

            membro = Membro.query.get(membro_id) if membro_id else Membro()

            if not membro_id:
                db.session.add(membro)

            membro.nome = request.form.get('nome')
            membro.tipo = request.form.get('tipo_membro')

            # Status ativo/inativo (dropdown: 1/ativo ou 0/inativo)
            ativo_val = request.form.get('ativo', '1')
            membro.ativo = ativo_val in ('1', 'ativo', 'true', 'sim')

            membro.observacoes = request.form.get('observacoes')
            membro.responsaveis = request.form.get('responsaveis')
            membro.alergias = request.form.get('info_medica')

            if request.form.get('data_nascimento'):
                membro.data_nascimento = datetime.strptime(
                    request.form.get('data_nascimento'),
                    '%Y-%m-%d'
                ).date()

            # Batismo: só grava data se "Batizado?" = Sim e data preenchida
            if request.form.get('batizado') == 'sim' and request.form.get('data_batismo'):
                membro.data_batismo = datetime.strptime(
                    request.form.get('data_batismo'),
                    '%Y-%m-%d'
                ).date()
            else:
                membro.data_batismo = None

            membro.congregações = Congregacao.query.filter(
                Congregacao.id.in_(request.form.getlist('congregacoes[]'))
            ).all()

            if 'foto' in request.files and request.files['foto'].filename:

                f = request.files['foto']

                fname = secure_filename(
                    f"membro_{datetime.now().timestamp()}.jpg"
                )

                up_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'static/img/membros'
                )

                os.makedirs(up_dir, exist_ok=True)

                fpath = os.path.join(up_dir, fname)

                try:
                    img = Image.open(f)

                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    img.thumbnail((500, 500))

                    img.save(fpath, optimize=True, quality=85)

                except:
                    f.seek(0)
                    f.save(fpath)

                membro.foto_path = f'img/membros/{fname}'

            db.session.flush()

            MembroMinisterio.query.filter_by(
                membro_id=membro.id
            ).delete()

            for m_id in request.form.getlist('ministerios[]'):

                for f_id in request.form.getlist('funcoes[]'):

                    db.session.add(
                        MembroMinisterio(
                            membro_id=membro.id,
                            ministerio_id=m_id,
                            funcao_id=f_id
                        )
                    )

            db.session.commit()

            flash('Membro salvo!', 'success')

        except Exception as e:

            db.session.rollback()

            flash(f'Erro: {e}', 'danger')

        return redirect(url_for('membros.membros_page'))

    membros = Membro.query.order_by(Membro.nome).all()

    membros_json = []

    for m in membros:

        vinc = []

        for v in getattr(m, 'ministerios_vinculados', []):

            vinc.append({
                'ministerio': {'id': v.ministerio.id, 'nome': v.ministerio.nome},
                'funcao': {'id': v.funcao.id, 'nome': v.funcao.nome}
            })

        membros_json.append({

            'id': m.id,
            'nome': m.nome,
            'tipo': m.tipo,
            'ativo': m.ativo,
            'foto_path': m.foto_path or '',

            'data_nascimento': (
                m.data_nascimento.isoformat()
                if m.data_nascimento else ''
            ),

            'data_batismo': (
                m.data_batismo.isoformat()
                if m.data_batismo else ''
            ),

            'congregações': [
                {'id': c.id, 'nome': c.nome}
                for c in m.congregações
            ],

            'vinculos_ministerio': vinc,

            'responsaveis': m.responsaveis or '',
            'info_medica': m.alergias or '',
            'observacoes': m.observacoes or ''
        })

    return render_template(
        'main/membros.html',
        congregacoes=Congregacao.query.all(),
        ministerios=Ministerio.query.all(),
        funcoes=Funcao.query.all(),
        membros=membros,
        membros_json=membros_json
    )


@membros_bp.route('/membro/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_membro(id):
    membro = Membro.query.get_or_404(id)

    try:
        membro.ativo = not membro.ativo
        db.session.commit()
        status = 'ativado' if membro.ativo else 'desativado'
        flash(f'Membro {status} com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao alterar status: {e}', 'danger')

    return redirect(url_for('membros.membros_page'))


@membros_bp.route('/membro/deletar/<int:id>')
@login_required
def deletar_membro(id):
    import os
    from flask import current_app
    from sqlalchemy import text
    from app.models.igreja import Membro
    from app.models import db
    
    membro = Membro.query.get_or_404(id)
    
    # 1. Deletar foto do servidor
    if membro.foto_path:
        foto_relativa = membro.foto_path.replace('/static/', '').lstrip('/')
        caminho_absoluto = os.path.join(current_app.root_path, 'static', foto_relativa)
        if os.path.exists(caminho_absoluto) and 'img' in caminho_absoluto:
            try: os.remove(caminho_absoluto)
            except: pass

    try:
        # 2. Cortar as 5 amarras reais do banco
        db.session.execute(text(f"DELETE FROM presencas WHERE membro_id = {id}"))
        db.session.execute(text(f"DELETE FROM membro_congregacao WHERE membro_id = {id}"))
        db.session.execute(text(f"DELETE FROM membro_ministerio WHERE membro_id = {id}"))
        db.session.execute(text(f"DELETE FROM inscricoes WHERE membro_id = {id}"))
        db.session.execute(text(f"UPDATE eventos SET responsavel_id = NULL WHERE responsavel_id = {id}"))
        
        # 3. Deletar Membro
        db.session.delete(membro)
        db.session.commit()
        flash('Membro excluído com sucesso!', 'danger')
    except Exception as e:
        db.session.rollback()
        return f"<h3>Erro ao excluir: {e}</h3>"
        
    return redirect(url_for('membros.membros_page'))