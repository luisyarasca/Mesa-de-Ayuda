import random, string

def crear_usuario(client, apenom, correo_base):
    """
    Crea usuario con correo único, si rompe reintenta agregando sufijo.
    """
    correo = correo_base
    for _ in range(3):
        r = client.post("/usuarios", json={"Apenom": apenom, "Correo": correo})
        if r.status_code in (200, 201):
            return r.json()["UsuarioID"]
        if r.status_code == 409:
            sufijo = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
            correo = correo_base.replace("@", f"+{sufijo}@")
            continue
        assert False, f"Creación de usuario falló: {r.status_code} {r.text}"
    assert False, "No se pudo crear usuario único tras reintentos"


def crear_tecnico(client, apenom, especialidad):
    t = client.post("/tecnicos", json={"Apenom": apenom, "Especialidad": especialidad})
    assert t.status_code in (200, 201)
    return t.json()["TecnicoID"]

def test_flujo_ticket(client):
    uid = crear_usuario(client, "FlowUser", f"flow+{random.randint(1000,9999)}@test.com")
    tec_id = crear_tecnico(client, "Tec Flow", "Soporte")

    # Crear ticket
    t = client.post("/tickets/", json={
        "Titulo": "Laptop no enciende",
        "Descripcion": "No responde al botón de encendido",
        "UsuarioID": uid,
        "TecnicoID": tec_id
    })
    assert t.status_code in (200, 201)
    ticket = t.json()
    tid = ticket["TicketID"]

    # Cerrar ticket 
    upd = client.put("/tickets/", json={
        "TicketID": tid,
        "Titulo": ticket["Titulo"],
        "Descripcion": "Caso resuelto y documentado",
        "Estado": "Cerrado",
        "TecnicoID": tec_id  
    })
    assert upd.status_code in (200, 204, 201)

    # Verificar
    g = client.get(f"/tickets/id/{tid}")
    assert g.status_code == 200
    data = g.json()
    assert data.get("Estado") in ("Cerrado", "cerrado", "CERRADO")
