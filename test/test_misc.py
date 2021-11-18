from cryptography.fernet import Fernet

from app import app
from app.models.endpoint import Endpoint
from app.utils.session import generate_user_key, valid_user_session


def test_generate_user_keys():
    key = generate_user_key()
    assert Fernet(key)
    assert generate_user_key() != key


def test_valid_session(client):
    assert not valid_user_session({'key': '', 'config': {}})
    with client.session_transaction() as session:
        assert valid_user_session(session)


def test_valid_translation_keys(client):
    valid_lang_keys = [_['value'] for _ in app.config['LANGUAGES']]
    en_keys = app.config['TRANSLATIONS']['lang_en'].keys()
    for translation_key in app.config['TRANSLATIONS']:
        # Ensure the translation is using a valid language value
        assert translation_key in valid_lang_keys

        # Ensure all translations match the same size/content of the original
        # English translation
        assert app.config['TRANSLATIONS'][translation_key].keys() == en_keys


def test_query_decryption(client):
    # FIXME: Handle decryption errors in search.py and rewrite test
    # This previously was used to test swapping decryption keys between
    # queries. While this worked in theory and usually didn't cause problems,
    # they were tied to session IDs and those are really unreliable (meaning
    # that occasionally page navigation would break).
    rv = client.get('/')
    cookie = rv.headers['Set-Cookie']

    rv = client.get(f'/{Endpoint.search}?q=test+1', headers={'Cookie': cookie})
    assert rv._status_code == 200

    with client.session_transaction() as session:
        assert valid_user_session(session)

    rv = client.get(f'/{Endpoint.search}?q=test+2', headers={'Cookie': cookie})
    assert rv._status_code == 200

    with client.session_transaction() as session:
        assert valid_user_session(session)
