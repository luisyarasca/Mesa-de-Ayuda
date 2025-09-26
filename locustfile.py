



from locust import HttpUser, task, between
import random, string

def correo_unico(base="load@test.com"):
    suf = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return base.replace("@", f"+{suf}@")

class MesaDeAyudaUser(HttpUser):
    wait_time = between(0.5, 1.5)  # stopo

    @task(2)
    def listar_tickets(self):
        # toca lista
        self.client.get("/tickets?page=1&size=5", name="GET /tickets")

    @task(1)
    def crear_usuario(self):
        payload = {"Apenom": "Carga QA", "Correo": correo_unico()}
        with self.client.post("/usuarios", json=payload, name="POST /usuarios", catch_response=True) as res:
            if res.status_code not in (200, 201, 409):  # 409
                res.failure(f"Status inesperado: {res.status_code}")

    @task(1)
    def flujo_ticket_basico(self):
        # Crear usuario
        u = self.client.post("/usuarios", json={"Apenom": "User Load", "Correo": correo_unico()})
        if u.status_code not in (200, 201):
            return
        uid = u.json().get("UsuarioID")

        # Crear técnico
        t = self.client.post("/tecnicos", json={"Apenom": "Tec Load", "Especialidad": "Soporte"})
        if t.status_code not in (200, 201):
            return
        tec_id = t.json().get("TecnicoID")

        # Crear ticket
        ticket_payload = {
            "Titulo": "Prueba carga",
            "Descripcion": "descripcion suficientemente larga para pasar validacion",
            "UsuarioID": uid,
            "TecnicoID": tec_id
        }
        self.client.post("/tickets/", json=ticket_payload, name="POST /tickets")
