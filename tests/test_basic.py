import pytest
from app import create_app

@pytest.fixture
def app():
    """Fixture que crea y configura una instancia de la app para pruebas."""
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Cliente de pruebas HTTP de Flask."""
    return app.test_client()

def test_app_exists(app):
    """Verifica que la instancia de la aplicación se cree correctamente."""
    assert app is not None
    assert app.config['TESTING'] is True

def test_home_page_status(client):
    """Verifica que la ruta principal '/' responda con HTTP 200 OK."""
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'EduReport' in html
    assert 'Primer Ciclo' in html
    assert 'Segundo Ciclo' in html
    assert '3 Ausencias' in html

def test_arquitectura_page_status(client):
    """Verifica que la ruta '/arquitectura' responda con HTTP 200 OK."""
    response = client.get('/arquitectura')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Arquitectura de Software EduReport' in html
    assert 'Application Factory' in html

def test_api_status_endpoint(client):
    """Verifica que el endpoint '/api/status' devuelva JSON válido y estado OK."""
    response = client.get('/api/status')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'OK'
    assert data['application'] == 'EduReport'
    assert data['rule_3_absences'] == 'Active'
