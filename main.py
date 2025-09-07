from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Response, Query
from pydantic import BaseModel, Field
from pydantic_core import SchemaSerializer
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship, declarative_base
from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from enum import Enum
from sqlalchemy import Enum as SqlEnum
import pyodbc
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mssql+pyodbc://localhost,1433/Ticketera?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)
engine = create_engine(DATABASE_URL)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()
## Tablas
#------------------------------------------------------


class EstadoEnum(str, Enum):
    Nuevo = "Nuevo"
    Abierto = "Abierto"
    En_Progreso = "En Progreso"
    Cerrado = "Cerrado"

class Usuario(Base):
    __tablename__ = "usuarios"
    
    UsuarioID = Column(Integer, primary_key=True, autoincrement=True)
    Apenom = Column(String(100), nullable=False)
    Correo = Column("CorreoElectronico", String(255), nullable=False, unique=True)
    tickets = relationship("Ticket", back_populates="usuario")

class Tecnico(Base):
    __tablename__="Tecnicos"
    TecnicoID = Column(Integer, primary_key=True, autoincrement=True)
    Apenom = Column(String(100), nullable=False)
    Especialidad = Column(String(100), nullable=False)
    tickets = relationship("Ticket", back_populates="tecnico")



class Ticket(Base):
    __tablename__ = "tickets"
    
    TicketID = Column(Integer, primary_key=True, autoincrement=True)
    Titulo = Column(String(100), nullable=False)
    Descripcion = Column(String(500), nullable=False)
    FechaCreacion = Column(DateTime, default=datetime.utcnow)
    Estado = Column(
        SqlEnum(
            EstadoEnum,
            name="estadoenum",
            values_callable=lambda e: [m.value for m in e],  
            validate_strings=True,
            native_enum=False,  # opcional
        ),
        default=EstadoEnum.Nuevo.value, 
        nullable=False,
    )
    UsuarioID = Column(Integer, ForeignKey("usuarios.UsuarioID"))
    TecnicoID = Column(Integer, ForeignKey("Tecnicos.TecnicoID"), nullable=True)

    usuario = relationship("Usuario", back_populates="tickets")
    tecnico = relationship("Tecnico", back_populates="tickets")
    comentarios = relationship(
    "Comentario",
    back_populates="ticket",
    cascade="all, delete-orphan",
    passive_deletes=True
)


class Comentario(Base):
    __tablename__ = "Comentarios"
    ComentarioID = Column(Integer, primary_key=True, autoincrement=True)
    Contenido = Column(Text)
    Fecha = Column(DateTime, default=datetime.utcnow)
    TicketID = Column(
    Integer,
    ForeignKey("tickets.TicketID", ondelete="CASCADE")
)

    Autor = Column(String(100))  

    ticket = relationship("Ticket", back_populates="comentarios")





#---------------------------------------------------------
Base.metadata.create_all(bind = engine)

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title = "Endpoint Mesa de ayuda",
    version = "1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)




#modelos
#-----------------------------------------------------------------
class TicketCreate(BaseModel):
    Titulo: str = Field(..., min_length=3, max_length=100)
    Descripcion: str = Field(..., min_length=10, max_length=500)
    UsuarioID: int = Field(..., ge=1)
    TecnicoID: Optional[int] = Field(None, ge=1)

class TicketMostrar(BaseModel):
    TicketID: int
    Titulo: str
    Descripcion: str
    FechaCreacion: Optional[datetime] = None  
    Estado: EstadoEnum
    UsuarioID: int
    TecnicoID: Optional[int] = None

    class Config:
        from_attributes = True



class TicketActualizar(BaseModel):
    TicketID: int = Field(..., ge=1)
    Titulo: Optional[str] = Field(None, min_length=3, max_length=100)
    Descripcion: Optional[str] = Field(None, min_length=10, max_length=500)
    Estado: Optional[EstadoEnum] = None
    TecnicoID: Optional[int] = Field(None, ge=1)

#-----------------------------------------------------
class UsuarioCrear(BaseModel):
    Apenom: str
    Correo: str
class UsuarioMostrar(BaseModel):
    UsuarioID: int
    Apenom: str
    Correo: str
    class Config:
        from_attributes = True
class UsuarioACtualizar(BaseModel):
    Apenom: Optional[str] = None
    Correo: Optional[str] = None
#-----------------------------------------------------
class TecnicoCrear(BaseModel):
    Apenom: str
    Especialidad: str
class TecnicoMostrar(BaseModel):
    TecnicoID: int
    Apenom: str
    Especialidad: str

    class Config:
        from_attributes = True
#------------------------------------------------------------------

class ComentarioCreate(BaseModel):
    Contenido: str = Field(..., min_length=2, max_length=2000)
    Autor: str = Field(..., min_length=2, max_length=100)

class ComentarioMostrar(BaseModel):
    ComentarioID: int
    Contenido: str
    Fecha: Optional[datetime] = None    
    Autor: str
    TicketID: int

    class Config:
        from_attributes = True
#------------------------------------------------------------------
#TICKET

# para crear un ticket
@app.post("/tickets/", response_model=TicketMostrar)
def Crear_Ticket(ticket: TicketCreate, db: Session= Depends(get_db)):
    #si no encuentra el usuario o tecnico, lanza un error
    usuario = db.query(Usuario).filter(Usuario.UsuarioID == ticket.UsuarioID).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if ticket.TecnicoID is not None:
        tecnico = db.query(Tecnico).filter(Tecnico.TecnicoID == ticket.TecnicoID).first()
        if not tecnico:
            raise HTTPException(status_code=404, detail="Técnico no encontrado")
    
    db_ticket = Ticket(
        Titulo=ticket.Titulo,
        Descripcion=ticket.Descripcion,
        Estado=EstadoEnum.Nuevo,
        UsuarioID=ticket.UsuarioID,
        TecnicoID=ticket.TecnicoID
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

# Mostrar
@app.get("/tickets/id/{ticket_id}", response_model=TicketMostrar)
def Mostrar_Ticket(ticket_id: int, db: Session = Depends(get_db)):
    
    ticket= db.query(Ticket).filter(Ticket.TicketID == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return ticket 
#lISTAR
@app.get("/tickets", response_model=List[TicketMostrar])
def Listar_Tickets(
    response: Response,
    estado: Optional[EstadoEnum] = None,
    tecnico_id: Optional[int] = Query(None, ge=1),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Ticket)
    if estado is not None:
        q = q.filter(Ticket.Estado == estado)
    if tecnico_id is not None:
        q = q.filter(Ticket.TecnicoID == tecnico_id)

    total = q.count()
    q = q.order_by(Ticket.FechaCreacion.desc())

    if page < 1: page = 1
    if size < 1: size = 10
    offset = (page - 1) * size

    items = q.offset(offset).limit(size).all()

    response.headers["X-Total-Count"] = str(total)
    return items

#Eliminar
@app.delete("/tickets/{ticket_id}")
def Eliminar_Ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.TicketID == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    # Fallback por siaca
    db.query(Comentario).filter(Comentario.TicketID == ticket_id).delete(synchronize_session=False)

    db.delete(ticket)
    db.commit()
    return {"Status": "Ticket eliminado exitosamente"}



#por estado
@app.get("/tickets/estadisticas")
def Estadisticas_Tickets(db: Session = Depends(get_db)):
    total = db.query(Ticket).count()
    return {
        "Total": total,
        "Nuevos": db.query(Ticket).filter(Ticket.Estado == EstadoEnum.Nuevo.value).count(),
        "Abiertos": db.query(Ticket).filter(Ticket.Estado == EstadoEnum.Abierto.value).count(),
        "En Progreso": db.query(Ticket).filter(Ticket.Estado == EstadoEnum.En_Progreso.value).count(),
        "Cerrados": db.query(Ticket).filter(Ticket.Estado == EstadoEnum.Cerrado.value).count(),
        }


#actualizar

@app.put("/tickets/", response_model=TicketMostrar)
def actualizar_ticket(ticket: TicketActualizar, db: Session = Depends(get_db)):
    ticket_db = db.query(Ticket).filter(Ticket.TicketID == ticket.TicketID).first()
    if not ticket_db:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    # Validar técnico si viene en el body
    if ticket.TecnicoID is not None:
        tecnico = db.query(Tecnico).filter(Tecnico.TecnicoID == ticket.TecnicoID).first()
        if not tecnico:
            raise HTTPException(status_code=404, detail="Técnico no encontrado")
        ticket_db.TecnicoID = ticket.TecnicoID

    if ticket.Titulo is not None:
        ticket_db.Titulo = ticket.Titulo
    if ticket.Descripcion is not None:
        ticket_db.Descripcion = ticket.Descripcion

    # Regla: no se puede cerrar sin técnico
    if ticket.Estado is not None:
        if ticket.Estado == EstadoEnum.Cerrado:
            tecnico_final = ticket.TecnicoID if ticket.TecnicoID is not None else ticket_db.TecnicoID
            if tecnico_final is None:
                raise HTTPException(status_code=400, detail="No puedes cerrar un ticket sin técnico asignado")
        ticket_db.Estado = ticket.Estado  # guarda el estado

    db.commit()
    db.refresh(ticket_db)
    return ticket_db



#-----------------------------------------------------------------------
#Usuario
#Crear usuario
@app.post("/usuarios", response_model=UsuarioMostrar)
def Crear_Usuario(usuario: UsuarioCrear, db: Session = Depends(get_db)):
    db_usuario = Usuario(Apenom=usuario.Apenom, Correo=usuario.Correo)
    db.add(db_usuario)
    try:
        db.commit()
        db.refresh(db_usuario)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ese correo ya está siendo usado por otro usuario")
    return db_usuario

# Mostrar usuario ID
@app.get("/usuarios/{usuario_id}", response_model=UsuarioMostrar)
def Mostrar_Usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.UsuarioID == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


#eliminar usuario
@app.delete("/usuarios/{usuario_id}")
def Eliminar_Usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.UsuarioID == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
    return {"Status": "Usuario eliminado exitosamente"}



# Actualizar usuario
@app.put("/usuarios/{usuario_id}", response_model=UsuarioMostrar)
def Actualizar_Usuario(usuario_id: int, datos: UsuarioACtualizar, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.UsuarioID == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    #valida si el correo lo usa otro
    if datos.Correo:
        correo_existe = db.query(Usuario).filter(
            Usuario.Correo == datos.Correo,
            Usuario.UsuarioID != usuario_id
        ).first()
        if correo_existe:
            raise HTTPException(status_code=409, detail="Ese correo ya está siendo usado por otro usuario")


    if datos.Apenom is not None:
        usuario.Apenom = datos.Apenom
    if datos.Correo is not None:
        usuario.Correo = datos.Correo
    try:
        db.commit()
        db.refresh(usuario)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar el usuario")

    return usuario
#--------------------------------------------------
#Tecnico
#Crear tecnico
@app.post("/tecnicos", response_model=TecnicoMostrar)
def Crear_Tecnico(tecnico: TecnicoCrear, db: Session = Depends(get_db)):
    db_tecnico = Tecnico(
        Apenom=tecnico.Apenom,
        Especialidad=tecnico.Especialidad
    )
    db.add(db_tecnico)
    db.commit()
    db.refresh(db_tecnico)
    return db_tecnico
# Mostrar tecnico ID
@app.get("/tecnicos/{tecnico_id}", response_model=TecnicoMostrar)
def Mostrar_Tecnico(tecnico_id: int, db: Session = Depends(get_db)):
    tecnico = db.query(Tecnico).filter(Tecnico.TecnicoID == tecnico_id).first()
    if tecnico is None:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    return tecnico
#eliminar tecnico
@app.delete("/tecnicos/{tecnico_id}")
def Eliminar_Tecnico(tecnico_id: int, db: Session = Depends(get_db)):
    tecnico = db.query(Tecnico).filter(Tecnico.TecnicoID == tecnico_id).first()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    db.delete(tecnico)
    db.commit()
    return {"Status": "Técnico eliminado exitosamente"}

#Listar tecnico VItochitaaaaaaaaaaaaa

@app.get("/tecnicos", response_model=List[TecnicoMostrar])
def Listar_Tecnicos(db: Session = Depends(get_db)):
    return db.query(Tecnico).all()



#-----------------------------------------------------------------------
#Comentario
# Crear comentario en un ticket
@app.post("/tickets/{ticket_id}/comentarios", response_model=ComentarioMostrar)
def crear_comentario(ticket_id: int, comentario: ComentarioCreate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.TicketID == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    nuevo_comentario = Comentario(
        Contenido=comentario.Contenido,
        Autor=comentario.Autor,
        TicketID=ticket_id
    )
    db.add(nuevo_comentario)
    db.commit()
    db.refresh(nuevo_comentario)
    return nuevo_comentario

# Listar comentarios de un ticket



@app.get("/tickets/{ticket_id}/comentarios", response_model=List[ComentarioMostrar])
def listar_comentarios(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.TicketID == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    return (
        db.query(Comentario)
          .filter(Comentario.TicketID == ticket_id)
          .order_by(Comentario.Fecha.desc())
          .all()
    )




#aaaaaaaaaaa
# Tickets por técnico
@app.get("/tecnicos/{tecnico_id}/tickets", response_model=List[TicketMostrar])
def tickets_por_tecnico(tecnico_id: int, db: Session = Depends(get_db)):
    return db.query(Ticket).filter(Ticket.TecnicoID == tecnico_id).all()

# Tickets por estado
@app.get("/tickets/estado/{estado}", response_model=List[TicketMostrar])
def tickets_por_estado(estado: EstadoEnum, db: Session = Depends(get_db)):
    return db.query(Ticket).filter(Ticket.Estado == estado).all()
