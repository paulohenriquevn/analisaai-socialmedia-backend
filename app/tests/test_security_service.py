from services.security_service import encrypt_token, decrypt_token

def test_token_encryption():
    token = "mysecrettoken"
    encrypted_token = encrypt_token(token)
    assert token != encrypted_token
    assert token == decrypt_token(encrypted_token) 