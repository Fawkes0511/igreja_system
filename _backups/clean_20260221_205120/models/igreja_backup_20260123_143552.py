from app.models import db
from datetime import datetime

class Congregacao(db.Model):
    __tablename__ = 'congregações'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    ativa = db.Column(db.Boolean, default=True)
    endereco = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    membros = db.relationship('Membro', backref='congregação', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'ativa': self.ativa,
            'endereco': self.endereco,
            'observacoes': self.observacoes,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'total_membros': len(self.membros)
        }

class Membro(db.Model):
    __tablename__ = 'membros'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    foto = db.Column(db.String(200))
    tipo = db.Column(db.String(20), default='Adulto')
    ativo = db.Column(db.Boolean, default=True)
    observacoes = db.Column(db.Text)
    
    congregacao_id = db.Column(db.Integer, db.ForeignKey('congregações.id'), nullable=False)
    
    data_batismo = db.Column(db.Date)
    
    responsaveis = db.Column(db.String(200))
    info_medica = db.Column(db.Text)
    
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'tipo': self.tipo,
            'ativo': self.ativo,
            'congregacao_id': self.congregacao_id,
            'data_batismo': self.data_batismo.isoformat() if self.data_batismo else None,
            'responsaveis': self.responsaveis,
            'info_medica': self.info_medica,
            'observacoes': self.observacoes,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }

class Funcao(db.Model):
    __tablename__ = 'funções'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    ativa = db.Column(db.Boolean, default=True)
    descricao = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
