from datetime import datetime

from app.models import db

# Tabela de associação (Membro <-> Congregacao)
membro_congregacao = db.Table(
    'membro_congregacao',
    db.Column('membro_id', db.Integer, db.ForeignKey('membros.id'), primary_key=True),
    db.Column('congregacao_id', db.Integer, db.ForeignKey('congregações.id'), primary_key=True),
)


class Congregacao(db.Model):
    __tablename__ = 'congregações'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    endereco = db.Column(db.String(200))
    ativa = db.Column(db.Boolean, default=True)

    membros = db.relationship('Membro', secondary=membro_congregacao, backref='congregações')
    eventos = db.relationship('Evento', backref='congregação', lazy=True)


class Membro(db.Model):
    __tablename__ = 'membros'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)

    data_nascimento = db.Column(db.Date)
    data_batismo = db.Column(db.Date)  # OK: você já criou no banco

    tipo = db.Column(db.String(20), default='Adulto')
    ativo = db.Column(db.Boolean, default=True)

    observacoes = db.Column(db.Text)

    responsaveis = db.Column(db.String(200))  # OK: você já criou no banco
    alergias = db.Column(db.String(200))      # OK: você já criou no banco
    foto_path = db.Column(db.String(255))     # OK: você já criou no banco

    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    inscricoes = db.relationship('Inscricao', backref='membro', lazy=True)


class Ministerio(db.Model):
    __tablename__ = 'ministérios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200))

    # IMPORTANTE:
    # Não use backref='ministerio' aqui, porque o MembroMinisterio já tem a property "ministerio".
    # Usa back_populates para ligar os dois lados sem conflito.
    membros_vinculados = db.relationship(
        'MembroMinisterio',
        back_populates='ministerio',
        lazy=True,
        cascade='all, delete-orphan'
    )


class Funcao(db.Model):
    __tablename__ = 'funções'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)


class MembroMinisterio(db.Model):
    __tablename__ = 'membro_ministerio'

    membro_id = db.Column(db.Integer, db.ForeignKey('membros.id'), primary_key=True)
    ministerio_id = db.Column(db.Integer, db.ForeignKey('ministérios.id'), primary_key=True)
    funcao_id = db.Column(db.Integer, db.ForeignKey('funções.id'), primary_key=True)

    membro = db.relationship('Membro', backref='ministerios_vinculados')

    # Já existe "ministerio" aqui → por isso NÃO pode criar backref com o mesmo nome lá em cima.
    ministerio = db.relationship('Ministerio', back_populates='membros_vinculados')

    funcao = db.relationship('Funcao')


class Evento(db.Model):
    __tablename__ = 'eventos'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)

    data_evento = db.Column(db.DateTime, nullable=False)
    congregacao_id = db.Column(db.Integer, db.ForeignKey('congregações.id'))

    permite_inscricao = db.Column(db.Boolean, default=False)
    ativa = db.Column(db.Boolean, default=True)

    # usado no checkin por QR nas suas rotas
    codigo_checkin = db.Column(db.String(80), unique=True, index=True)

    inscritos = db.relationship('Inscricao', backref='evento', lazy=True)


class Inscricao(db.Model):
    __tablename__ = 'inscricoes'

    id = db.Column(db.Integer, primary_key=True)
    membro_id = db.Column(db.Integer, db.ForeignKey('membros.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)

    presenca = db.Column(db.Boolean, default=False)
    data_inscricao = db.Column(db.DateTime, default=datetime.utcnow)


class Agenda(db.Model):
    __tablename__ = 'agenda'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)

    dia_semana = db.Column(db.Integer)
    horario = db.Column(db.Time, nullable=False)

    tipo = db.Column(db.String(50))
    congregacao_id = db.Column(db.Integer, db.ForeignKey('congregações.id'))


class Presenca(db.Model):
    __tablename__ = 'presencas'

    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    membro_id = db.Column(db.Integer, db.ForeignKey('membros.id'), nullable=False)

    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    presente = db.Column(db.Boolean, default=False)

    checkin_time = db.Column(db.DateTime)
    checkout_time = db.Column(db.DateTime)

    observacoes = db.Column(db.Text)

    evento = db.relationship('Evento', backref=db.backref('presencas_registradas', lazy='dynamic'))
    membro = db.relationship('Membro', backref=db.backref('presencas', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('evento_id', 'membro_id', name='uq_evento_membro'),
    )
