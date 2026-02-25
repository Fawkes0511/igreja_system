import sys
sys.path.insert(0, '.')

from app import create_app
from app.models import db
from app.models.igreja import Congregacao, Membro, Funcao

app = create_app()

with app.app_context():
    print("=== ATUALIZANDO BANCO DE DADOS ===")
    
    # Criar/atualizar todas as tabelas
    db.create_all()
    print("✓ Tabelas criadas/atualizadas")
    
    # Verificar se as novas colunas existem
    from sqlalchemy import inspect
    
    inspector = inspect(db.engine)
    
    # Verificar colunas da tabela congregações
    columns_cong = [col['name'] for col in inspector.get_columns('congregações')]
    print(f"\nColunas em 'congregações': {columns_cong}")
    
    # Verificar se existe ao menos uma congregação
    total_cong = Congregacao.query.count()
    print(f"\nTotal de congregações: {total_cong}")
    
    if total_cong == 0:
        print("Criando congregação principal...")
        principal = Congregacao(
            nome="Congregação Principal",
            ativa=True,
            endereco="Endereço da sede principal",
            observacoes="Congregação matriz do sistema"
        )
        db.session.add(principal)
        db.session.commit()
        print("✓ Congregação principal criada")
    
    # Verificar membros
    total_membros = Membro.query.count()
    print(f"\nTotal de membros: {total_membros}")
    
    print("\n=== BANCO PRONTO PARA USO ===")
