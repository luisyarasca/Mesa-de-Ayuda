import random, string

def crear_usuario(client, apenom, correo_base):
    """
    Crea usuario con correo único. Si choca (409), reintenta agregando un sufijo.
    """
    correo = correo_base
    for i in range(3):
        r = client.post("/usuarios", json={"Apenom": apenom, "Correo": correo})
        if r.status_code in (200, 201):
            return r.json()["UsuarioID"]
        if r.status_code == 409:
            sufijo = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
            correo = correo_base.replace("@", f"+{sufijo}@")
            continue
        # Si cae aquí, algo raro pasó (422/500/etc.)
        assert False, f"Creación de usuario falló: {r.status_code} {r.text}"
    assert False, "No se pudo crear un usuario único tras reintentos"

    
def crear_tecnico(client, apenom="Tec Extra", especialidad="Soporte"):
    t = client.post("/tecnicos", json={"Apenom": apenom, "Especialidad": especialidad})
    assert t.status_code in (200, 201)
    return t.json()["TecnicoID"]

def crear_ticket(client, uid, tec_id=None, titulo="Ping cae", desc="descripcion suficientemente larga"):
    payload = {"Titulo": titulo, "Descripcion": desc, "UsuarioID": uid}
    if tec_id is not None:
        payload["TecnicoID"] = tec_id
    r = client.post("/tickets/", json=payload)
    assert r.status_code in (200, 201)
    return r.json()["TicketID"]

def test_listar_y_estadisticas(client):
    # lista
    r = client.get("/tickets?page=1&size=5")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    e = client.get("/tickets/estadisticas")
    assert e.status_code == 200
    body = e.json()
    for k in ["Total", "Nuevos", "Abiertos", "En Progreso", "Cerrados"]:
        assert k in body

def test_cerrar_sin_tecnico_da_400(client):
    uid = crear_usuario(client, "SinTec", "sintec@test.com")
    tid = crear_ticket(client, uid, tec_id=None, titulo="Cerrar sin tec", desc="texto largo suficiente")
    # Intento cerrar sin técnico asignado deberiaaaaaa
    upd = client.put("/tickets/", json={
    "TicketID": tid,
    "Titulo": "Cerrar sin tec",
    "Descripcion": "Intento prolongado",  # >= 10 chars
    "Estado": "Cerrado"
        })
    assert upd.status_code == 400
    assert "sin técnico" in upd.json()["detail"].lower()

def test_comentarios_crear_y_listar(client):
    uid = crear_usuario(client, "Com User", "comuser@test.com")
    tec = crear_tecnico(client, "Tec Com", "Redes")
    tid = crear_ticket(client, uid, tec_id=tec, titulo="Con comentario", desc="algo largo para pasar validación")

    c = client.post(f"/tickets/{tid}/comentarios", json={"Contenido": "Todo ok", "Autor": "QA"})
    assert c.status_code in (200, 201)
    listado = client.get(f"/tickets/{tid}/comentarios")
    assert listado.status_code == 200
    arr = listado.json()
    assert isinstance(arr, list) and len(arr) >= 1
    assert arr[0]["TicketID"] == tid

def test_tecnicos_listar_y_get(client):
    tec = crear_tecnico(client, "Tec GET", "Sistemas")
    g = client.get(f"/tecnicos/{tec}")
    assert g.status_code == 200
    lista = client.get("/tecnicos")
    assert lista.status_code == 200
    assert any(item["TecnicoID"] == tec for item in lista.json())

def test_usuario_actualizar_conflicto(client):
    # provocame 409
    u1 = crear_usuario(client, "U1", "u1@test.com")
    u2 = crear_usuario(client, "U2", "u2@test.com")
    r = client.put(f"/usuarios/{u1}", json={"Correo": "u2@test.com"})
    assert r.status_code == 409

def test_eliminar_ticket(client):
    uid = crear_usuario(client, "Del User", "deluser@test.com")
    tec = crear_tecnico(client, "Tec Del", "Helpdesk")
    tid = crear_ticket(client, uid, tec_id=tec, titulo="Borrar ticket", desc="cuerpo largo para validar")
    d = client.delete(f"/tickets/{tid}")
    assert d.status_code == 200
    g = client.get(f"/tickets/id/{tid}")
    assert g.status_code == 404
