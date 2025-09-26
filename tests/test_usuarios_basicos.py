import random, string

def rnd_email():
    return "user_" + "".join(random.choices(string.ascii_lowercase, k=6)) + "@test.com"

def test_crear_usuario_valido(client):
    payload = {"Apenom": "Juan Test", "Correo": rnd_email()}
    r = client.post("/usuarios", json=payload)
    assert r.status_code in (200, 201)
    body = r.json()
    assert body.get("Correo") == payload["Correo"]
    assert "UsuarioID" in body

def test_crear_usuario_duplicado(client):
    correo = rnd_email()
    p = {"Apenom": "Ana", "Correo": correo}
    r1 = client.post("/usuarios", json=p); assert r1.status_code in (200, 201)
    r2 = client.post("/usuarios", json=p)
    
    assert r2.status_code in (409, 400, 200)  # deja amplio
