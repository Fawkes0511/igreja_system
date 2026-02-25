import sys
sys.path.insert(0, '.')

from app import create_app

app = create_app()

with app.app_context():
    print("=== TESTANDO ROTAS DE CONGREGAÇÕES ===")
    
    # Listar todas as rotas registradas
    with app.test_client() as client:
        print("\nRotas disponíveis:")
        for rule in app.url_map.iter_rules():
            if 'congreg' in rule.rule:
                print(f"  {rule.rule} -> {rule.endpoint}")
        
        print("\nTestando acesso às rotas (sem login):")
        routes_to_test = ['/congregacoes', '/congregacao/1/detalhes']
        
        for route in routes_to_test:
            try:
                response = client.get(route, follow_redirects=True)
                print(f"  {route}: {response.status_code}")
            except Exception as e:
                print(f"  {route}: ERRO - {e}")
    
    print("\n=== TESTE CONCLUÍDO ===")
