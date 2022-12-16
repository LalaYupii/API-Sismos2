from fastapi import FastAPI, Depends
from .models import Sismos, Tsunamis, Volcanes, Pais
from .database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from Funciones import *
from typing import Union


app = FastAPI(title='Sismos', description='En esta APi podras encontrar información acerca de eventos sísmicos y tsunamis ocurridos en Chile, Japón y Estados Unidos. Adicionalmente, permite hacer consultas de los volcanes en dichos paises.\n Para filtrar por país se deberá escribir el nombre del país de la siguiente manera: Chile, Japón, USA')
Base.metadata.create_all(bind = engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get('/',tags=['Sismos'])
def inicio(db: Session = Depends(get_db)):
    return {'Hola':'Bienvenido a la API de EARTH DATA, por favor dirigite a la página: '}

@app.get('/sismos/all',tags=['Sismos'], description='Petición para obtener todos los registros de sismos.')
def sismos_todos(db: Session = Depends(get_db)):
    sismos_todos = obtener_sismos(db)
    return sismos_todos

# Obtener los registros de sismos filtrando por características.
@app.get('/sismos/',tags=['Sismos'], description='Petición para obtener los registros  de sismos filtrados según sus características.')
def sismos_filtrados(max_depth: Union[float, None] = 800, min_depth: Union[float, None] = 0, min_mag: Union[float, None] = 0, max_mag: Union[float, None] = 9.9,
         min_lat: Union[float, None] = -90, max_lat: Union[float, None] = 90, min_long: Union[float, None] = -180, max_long:Union[float, None] = 180,
         min_anio: Union[float, None] = 2000, max_anio:Union[float, None] = 2022, pais : Union[str, None] = 'Japón',
         db: Session = Depends(get_db)):
    pais_valor = pais(pais)
    sismos = db.query(Sismos).filter(Sismos.depth >= min_depth).filter(Sismos.depth <= max_depth).\
            filter(Sismos.mag <= max_mag).filter(Sismos.mag >= min_mag).\
                filter(Sismos.lat <= max_lat).filter(Sismos.lat >= min_lat).\
                    filter(Sismos.lng <= max_long).filter(Sismos.lng >= min_long).\
                        filter(Sismos.year <= max_anio).filter(Sismos.year >= min_anio).\
                            filter(Sismos.idpais == pais_valor).limit(100).all()
    return sismos


# Sismo mas fuerte para el año deseado en el pais de interes.
@app.get('/sismos/evento_maximo', tags=['Sismos'], description='Petición que retorna el sismo mas fuerte para el año deseado en el pais de interes.')
def sismo_maximo(pais_i : str,anio: int, db: Session = Depends(get_db)):
    pais_valor = pais(pais_i)
    max_sismo = db.query(Sismos).select_from(Sismos).join(Pais, Sismos.idpais == Pais.idpais,).\
        filter(Pais.idpais == pais_valor).filter(Sismos.year == anio).order_by(Sismos.mag.desc()).limit(1).all()
    return max_sismo
    

# # TSUNAMIS

# Obtener todos los registros de tsunamis
@app.get('/tsunamis/all',tags=['Tsunamis'], description='Petición para obtener todos los registros de tsunamis.')
def tsunamis_todos(db: Session = Depends(get_db)):
    tsunamis = db.query(Tsunamis).all()
    return tsunamis

# Obtener los registros de intento filtrando por características.
@app.get('/tsunamis/',tags=['Tsunamis'], description='Petición para obtener los registros  de tsunamis filtrados según sus características.')
def tsunamis_filtrados(altura_olas_max: Union[float, None] = 100, altura_olas_min: Union[float, None] = 0, max_depth: Union[float, None] = 800, min_depth: Union[float, None] = 0, min_mag: Union[float, None] = 0, max_mag: Union[float, None] = 9.9,
         min_lat: Union[float, None] = -90, max_lat: Union[float, None] = 90, min_long: Union[float, None] = -180, max_long:Union[float, None] = 180,
         min_anio: Union[float, None] = 2000, max_anio:Union[float, None] = 2022,
         db: Session = Depends(get_db)):
    tsunamis = db.query(Tsunamis).filter(Tsunamis.lat <= max_lat).filter(Tsunamis.lat >= min_lat).\
        filter(Tsunamis.lng <= max_long).filter(Tsunamis.lng >= min_long).\
            filter(Tsunamis.altura_oleaje <= altura_olas_max).filter(Tsunamis.altura_oleaje >= altura_olas_min).\
                filter(Tsunamis.depth >= min_depth).filter(Tsunamis.depth <= max_depth).\
                    filter(Tsunamis.mag <= max_mag).filter(Tsunamis.mag >= min_mag).\
                        filter(Tsunamis.year <= max_anio).filter(Tsunamis.year >= min_anio).limit(100).all()
    return tsunamis

# Top 5 Tsunami mas fuertes para el año deseado en el pais de interes
@app.get('/Tsunamis/eventos_maximos', tags=['Tsunamis'], description='Petición para obtener los 5 tsunamis con mayor elevación de marea filtrados según pais y año.')
def tsunamis_maximos(pais_i: str, anio: int, db: Session = Depends(get_db)):
    pais_valor = pais(pais_i)
    tsunami_maximo = db.query(Tsunamis).select_from(Tsunamis).join(Pais, Tsunamis.idpais == Pais.idpais).\
        filter(Tsunamis.year == anio).filter(Pais.idpais == pais_valor).order_by(Tsunamis.altura_oleaje.desc()).limit(5).all()
    return tsunami_maximo

# VOLCANES

# Obtener todos los registros de volcanes.
@app.get('/volcanes/all', tags=['Volcanes'], description='Petición para obtener los volcanes de los paises de interes')
def volcanes_todos(db: Session = Depends(get_db)):
    volcanes_todos = db.query(Volcanes).all()
    return volcanes_todos

# Obtener todos los registros de volcanes segun el pais.
@app.get('/volcanes/', tags=['Volcanes'], description='Petición para obterner los volcanes filtrados por pais.')
def volcanes_filtrados(pais_i: str,db: Session = Depends(get_db)):
    pais_valor = pais(pais_i)
    volcanes_filtrados = db.query(Volcanes).select_from(Volcanes).join(Pais, Volcanes.idpais == Pais.idpais).\
        filter(Pais.idpais == pais_valor).all()
    return volcanes_filtrados
        


# Crear registros
# @app.post('/intento',tags=['Intento'], description='Crear registros')
# def create(request: schemas.Intento, db: Session = Depends(get_db)):
#     new_intento = models.Intento(mag=request.mag, depth=request.depth, peligro = request.peligro)
#     db.add(new_intento)
#     db.commit()
#     db.refresh(new_intento)
#     return new_intento
