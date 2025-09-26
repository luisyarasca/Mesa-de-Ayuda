import random, string

def crear_usuario(client, apenom="Maria Test", correo="maria@test.com"):
    correo_base = correo
    for _ in range(3):
        r = client.post("/usuarios", json={"Apenom": apenom, "Correo": correo})
        if r.status_code in (200, 201):
            return r.json()["UsuarioID"]
        if r.status_code == 409:
            suf = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
            correo = correo_base.replace("@", f"+{suf}@")
            continue
        assert False, f"Creación de usuario falló: {r.status_code} {r.text}"
    assert False, "No se pudo crear usuario único tras reintentos"


def crear_tecnico(client, apenom="Tec QA", especialidad="Soporte"):
    t = client.post("/tecnicos", json={"Apenom": apenom, "Especialidad": especialidad})
    assert t.status_code in (200, 201)
    return t.json()["TecnicoID"]

def test_crear_ticket_valido(client):
    uid = crear_usuario(client, correo="maria1@test.com")
    tec_id = crear_tecnico(client)
    payload = {
        "Titulo": "Sin internet",
        "Descripcion": "LED rojo en el router hogwarts",  # >= 10 chars
        "UsuarioID": uid,
        "TecnicoID": tec_id
    }
    r = client.post("/tickets/", json=payload)
    assert r.status_code in (200, 201)
    data = r.json()
    assert data["Titulo"] == payload["Titulo"]
    assert "TicketID" in data

def test_crear_ticket_invalido_sin_titulo(client):
    uid = crear_usuario(client, correo="maria2@test.com")
    tec_id = crear_tecnico(client, apenom="Tec 2")
    payload = {
        # "Titulo": falta a propósito
        "Descripcion": "descripcion suficientemente larga",
        "UsuarioID": uid,
        "TecnicoID": tec_id
    }
    r = client.post("/tickets/", json=payload)
    assert r.status_code in (400, 422)

def test_obtener_ticket_inexistente(client):
    r = client.get("/tickets/id/99999999")
    assert r.status_code == 404
