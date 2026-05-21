"""Testes da fatia de autenticação por matrícula."""
import pytest
from django.urls import reverse

from apps.accounts.models import User

SENHA = 'senha-forte-123'


@pytest.fixture
def usuario(db):
    return User.objects.create_user(
        matricula='OP-001', password=SENHA, nome='Operador Teste',
    )


def test_get_tela_login(client):
    resposta = client.get(reverse('accounts:login'))
    assert resposta.status_code == 200
    assert 'accounts/login.html' in {t.name for t in resposta.templates}


def test_tela_login_exibe_identidade_e_campos_acessiveis(client):
    resposta = client.get(reverse('accounts:login'))
    conteudo = resposta.content.decode()

    assert 'WMS SAEP' in conteudo
    assert 'Sistema interno de gestão de materiais' in conteudo
    assert 'Acesse com sua matrícula e senha.' in conteudo
    assert 'Acesso restrito a funcionários autorizados.' in conteudo
    assert 'for="id_username"' in conteudo
    assert 'for="id_password"' in conteudo
    assert 'autofocus' in conteudo
    assert 'role="alert"' not in conteudo
    assert 'min-h-screen' in conteudo
    assert 'max-w-5xl' not in conteudo
    assert '<header' not in conteudo


def test_login_valido_por_matricula(client, usuario):
    resposta = client.post(
        reverse('accounts:login'),
        {'username': 'OP-001', 'password': SENHA},
    )
    assert resposta.status_code == 302
    assert resposta.wsgi_request.user.is_authenticated


def test_login_preserva_next_no_formulario_e_redirect(client, usuario):
    resposta_get = client.get(reverse('accounts:login'), {'next': '/requisicoes/minhas/'})
    conteudo = resposta_get.content.decode()

    assert 'name="next" value="/requisicoes/minhas/"' in conteudo

    resposta_post = client.post(
        reverse('accounts:login'),
        {
            'username': 'OP-001',
            'password': SENHA,
            'next': '/requisicoes/minhas/',
        },
    )
    assert resposta_post.status_code == 302
    assert resposta_post['Location'] == '/requisicoes/minhas/'


def test_login_senha_invalida(client, usuario):
    resposta = client.post(
        reverse('accounts:login'),
        {'username': 'OP-001', 'password': 'errada'},
    )
    assert resposta.status_code == 200
    assert not resposta.wsgi_request.user.is_authenticated


def test_login_senha_invalida_exibe_erro_inline(client, usuario):
    resposta = client.post(
        reverse('accounts:login'),
        {'username': 'OP-001', 'password': 'errada'},
    )
    conteudo = resposta.content.decode()

    assert 'role="alert"' in conteudo
    assert 'senha corretos' in conteudo
    assert 'aria-invalid="true"' in conteudo


def test_login_usuario_inativo(client, usuario):
    usuario.is_active = False
    usuario.save()
    resposta = client.post(
        reverse('accounts:login'),
        {'username': 'OP-001', 'password': SENHA},
    )
    assert resposta.status_code == 200
    assert not resposta.wsgi_request.user.is_authenticated


def test_logout(client, usuario):
    client.force_login(usuario)
    resposta = client.post(reverse('accounts:logout'))
    assert resposta.status_code == 302
    assert not resposta.wsgi_request.user.is_authenticated
