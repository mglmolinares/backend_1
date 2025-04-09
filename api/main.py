from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import pymysql
from datetime import datetime, timedelta
import jwt
import os
# mysql://root:yBsbbewWkjWDnGYlGgacUHSlgNtXzvky@autorack.proxy.rlwy.net:54667/railway
# Inicialización de la app FastAPI
app = FastAPI()


# Configurar CORS para permitir el acceso desde dominios externos
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Permitir todos los orígenes. Cambia a una lista específica de dominios si lo prefieres
    allow_credentials=True,
    allow_methods=[
        "*"
    ],  # Permitir todos los métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)


# mysql://root:yBsbbewWkjWDnGYlGgacUHSlgNtXzvky@autorack.proxy.rlwy.net:54667/railway
# Función para obtener conexión a la base de datos
def get_db_connection():
    return pymysql.connect(
        host="sql10.freesqldatabase.com",
        user="sql10772255",
        password="GlgTY9zwsF",
        database="sql10772255",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,



class LoginRequest(BaseModel):
    usuario: str
    contraseña: str
# Modelo Pydantic para los datos del contacto
class Usuario(BaseModel):
    id_usuario: int
    nombres: str
    apellidos: str
    usuario: str
    contraseña: str
    id_rol: int
    edad: int
    sexo: str


class EstadoTarea(BaseModel):
    estado: str  # El estado a actualizar


class Alerta(BaseModel):
    id_alertas: int
    fecha: str


class AlertUser(BaseModel):
    id_alertas: int
    id_usuario: int


class DatosClimaticos(BaseModel):
    id_dato: int
    humedad: float
    temperatura: float
    fecha: str
    id_galpon: int


class Galpon(BaseModel):
    # id_galpon: int
    capacidad: int
    aves: int


class Granja(BaseModel):
    id_granja: int
    nombre_granja: str
    contraseña: str


class GranGalpon(BaseModel):
    id_granja: int
    id_galpon: int


class Huevos(BaseModel):
    # id_recoleccion: int
    cantidad: int
    fecha: str
    id_lote: int


class Lote(BaseModel):
    # id_lote: int
    num_aves: int
    fecha_ingreso: str
    id_galpon: int


class Reporte(BaseModel):
    # id_reporte: int
    fecha_registro: str
    id_lote: int
    diagnostico: str = None
    tratamiento_prescrito: str = None
    fecha_inicio_tratamiento: str = None
    fecha_fin_tratamiento: str = None
    id_usuario: int
    estado_general: str = None
    dosis: str = None
    frecuencia_tratamiento: str = None


class Rol(BaseModel):
    id_rol: int
    tipo_usuario: str  # Puede ser 'administrador', 'trabajador' o 'veterinario'


class Tarea(BaseModel):
    # id_tareas: int
    descripcion: str
    fecha_asignacion: str
    estado: str  # Puede ser 'Pendiente', 'En progreso' o 'Completado'
    id_usuario: int


class EditarTarea(BaseModel):
    descripcion: str
    fecha_asignacion: str
    estado: str  # Puede ser 'Pendiente', 'En progreso' o 'Completado'
    id_usuario: int

@app.get("/verificar_conexion")
def verificar_conexion():
    try:
        connection = get_db_connection()
        connection.ping()  # Verifica si la conexión es válida
        connection.close()
        return {"mensaje": "Conexión exitosa a la base de datos"}
    except Exception as e:
        return {"mensaje": f"Error al conectar con la base de datos: {e}"}
        
@app.get("/")
def welcome():
    return {"mensaje": "Hello world"}

SECRET_KEY="DJEJFKJLSFK"
# Función para crear un token de acceso
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    else:
        to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=10)})  # Default 30 minutos
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# Función para verificar el token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


@app.post("/login")
async def login(login_request: LoginRequest):
    try:
        usuario = login_request.usuario
        contraseña = login_request.contraseña

        print(f"Usuario recibido: {usuario}")
        print(f"Contraseña recibida: {contraseña}")

        # Verificar las credenciales del usuario
        connection = get_db_connection()
        print("Conexión a la base de datos exitosa")

        cursor = connection.cursor()
        cursor.execute("""
            SELECT usuarios.id_usuario,usuarios.usuario, usuarios.contraseña, roles.tipo_usuario 
            FROM usuarios 
            JOIN roles ON usuarios.id_rol = roles.id_rol 
            WHERE usuarios.usuario = %s
        """, (usuario,))
        
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        print(f"Resultado de la consulta SQL: {user}")

        if user:
            id_usuario = user['id_usuario']  # Acceder usando la clave del diccionario
            stored_password = user['contraseña'].strip()  # La contraseña almacenada está en la segunda columna
            user_role = user['tipo_usuario']  # El rol está en la tercera columna
            usuario=user["usuario"]

            print(f"ID Usuario: {id_usuario}")
            print(f"Contraseña almacenada: {stored_password}")
            print(f"Rol del usuario: {user_role}")
            print(f"Rol del usuario: {usuario}")

            # Verificar si la contraseña coincide
            if stored_password == contraseña.strip():
                print("Las contraseñas coinciden, creando token...")
                payload = {
                    'usuario': usuario,
                    'id': id_usuario,
                    'rol': user_role,
                }
                token = create_access_token(payload)
                
                print(f"Token generado: {token}")
                return {"token": token, "rol": user_role}
            else:
                print("La contraseña no coincide")
                raise HTTPException(status_code=401, detail="Credenciales inválidas")
        else:
            print("No se encontró el usuario")
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
    except Exception as e:
        print(f"Error en login: {e}")
        raise HTTPException(status_code=500, detail=f"Error en login: {str(e)}")
    
# Ruta para crear un nuevo contacto
@app.post("/nuevo_usuario")
def nuevo_usuario(new_contact: Usuario):

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """INSERT INTO usuarios (id_usuario, nombres, apellidos, edad, sexo, usuario, contraseña, id_rol) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(
                sql,
                (
                    new_contact.id_usuario,
                    new_contact.nombres,
                    new_contact.apellidos,
                    new_contact.edad,
                    new_contact.sexo,
                    new_contact.usuario,
                    new_contact.contraseña,
                    new_contact.id_rol,
                ),
            )
        connection.commit()
        connection.close()
        return {"informacion": "Registro exitoso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para obtener todos los contactos
@app.get("/obtener_usuarios")
def obtener_usuarios():
    try:
        connection = get_db_connection()  # Se obtiene la conexión a la base de datos
        with connection.cursor() as cursor:
            # Se realiza la consulta de los usuarios y sus roles
            cursor.execute(
                """
                SELECT u.id_usuario, u.nombres, u.apellidos, u.usuario, u.contraseña, r.tipo_usuario, u.edad, u.sexo 
                FROM usuarios u 
                JOIN roles r ON u.id_rol = r.id_rol
                """
            )
            datos = cursor.fetchall()  # Se obtienen todos los registros

        connection.close()  # Se cierra la conexión a la base de datos

        return datos
    except Exception as e:
        print(f"Error: {e}")  # Se imprime el error en el servidor
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para obtener el conteo de los registros
@app.get("/total_usuarios")
def total_usuarios():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            count = cursor.fetchone()
        connection.close()
        return count
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# obtiene un usuario en especifico de la tabla usuarios
@app.get("/obtener_usuario/{id_usuario}")
def obtener_usuario(id_usuario: int):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,)
            )
            user = cursor.fetchone()
        connection.close()
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Obtiene un usuario por su usuario con rol de trabajador
@app.get("/buscar_usuario_tb/{nombre}")
def buscar_usuario_tb(nombre: str):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM usuarios WHERE nombres LIKE %s and id_rol=2;",
                ("%" + nombre + "%",),
            )
            user = cursor.fetchall()
        connection.close()
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/buscar_usuario_vt/{nombre}")
def buscar_usuario_vt(nombre: str):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM usuarios WHERE nombres LIKE %s and id_rol=3;",
                ("%" + nombre + "%",),
            )
            user = cursor.fetchall()
        connection.close()
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.put("/editar_usuario/{id_usuario}")
def editar_usuario(id_usuario: int, usuario: Usuario):
    try:
        connection = get_db_connection()
        with connection:
            with connection.cursor() as cursor:
                sql = """
                UPDATE usuarios
                SET
                    nombres = %s,
                    apellidos = %s,
                    edad = %s,
                    sexo = %s,
                    usuario = %s,
                    contraseña = %s,
                    id_rol = %s
                WHERE id_usuario = %s
                """
                cursor.execute(
                    sql,
                    (
                        usuario.nombres,
                        usuario.apellidos,
                        usuario.edad,
                        usuario.sexo,
                        usuario.usuario,
                        usuario.contraseña, 
                        usuario.id_rol,
                        id_usuario,  # Este es el id_usuario del WHERE
                    ),
                )
            connection.commit()
        return {"informacion": "Registro actualizado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# obtiene un reporte especifico por id
@app.get("/obtener_reporte/{id_reporte}")
def obtener_reporte(id_reporte: int):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM reportes WHERE id_reporte = %s", (id_reporte,)
            )
            rv = cursor.fetchone()
        connection.close()

        if rv is None:
            raise HTTPException(status_code=404, detail="Reporte no encontrado")
        return rv
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/obtener_tareas")
def obtener_tareas():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT t.id_tareas,t.descripcion,t.fecha_asignacion, t.estado,u.nombres, u.id_usuario FROM  tareas t JOIN usuarios u  ON t.id_usuario = u.id_usuario ORDER BY t.fecha_asignacion ASC"
            )
            rv = cursor.fetchall()
        connection.close()
        return rv
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/obtener_tareas_trabajador/{id}")
def obtener_tareas(id: int):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id_tareas, descripcion, fecha_asignacion, estado FROM tareas WHERE id_usuario = %s  ORDER BY estado desc, fecha_asignacion asc",
                (id,),
            )
            rv = cursor.fetchall()
        connection.close()
        return rv
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# obtener todas las tareas por trabajador
@app.get("/obtener_tareas_id/{id}")
def obtener_tareas_id(id: int):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM tareas WHERE id_tareas= %s",
                (id,),
            )
            rv = cursor.fetchone()
        connection.close()

        if rv is None:
            raise HTTPException(status_code=404, detail="Reporte no encontrado")
        return rv
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#### ruta para crear una tarea
@app.post("/agregar_tarea")
def agregar_tarea(new_task: Tarea):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "INSERT INTO tareas (descripcion, fecha_asignacion, estado, id_usuario) VALUES (%s, %s, %s, %s)"
            cursor.execute(
                sql,
                (
                    new_task.descripcion,
                    new_task.fecha_asignacion,
                    new_task.estado,
                    new_task.id_usuario,
                ),
            )
        connection.commit()
        connection.close()
        return {"informacion": "Tarea asignada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# eliminar tareas  por id
@app.delete("/eliminar_tarea/{id}")
def eliminar_tarea(id: int):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM tareas WHERE id_tareas = %s", (id,))
        connection.commit()
        connection.close()
        return {"informacion": "Registro eliminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para eliminar un usuario
@app.delete("/eliminar_usuario/{id}")
def eliminar_usuario(id: int):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id,))
        connection.commit()
        connection.close()
        return {"informacion": "Registro eliminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/editar_tarea/{id_tareas}")
def editar_tarea(id_tareas: int, task: Tarea):
    try:
        connection = get_db_connection()
        with connection:
            with connection.cursor() as cursor:
                sql = """
                UPDATE tareas
                SET descripcion = %s,
                    fecha_asignacion = %s,
                    estado = %s,
                    id_usuario = %s
                WHERE id_tareas = %s
                """
                cursor.execute(
                    sql,
                    (
                        task.descripcion,
                        task.fecha_asignacion,
                        task.estado,
                        task.id_usuario,
                        id_tareas,  # Se usa el id_tareas recibido en la URL
                    ),
                )
            connection.commit()
        return {"informacion": "Registro actualizado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para crear reporte del veterinario
@app.post("/crear_reporte")
def crear_reporte(new_report: Reporte):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """INSERT INTO reportes (
                    fecha_registro, id_lote, estado_general, diagnostico, tratamiento_prescrito,
                    dosis, frecuencia_tratamiento, fecha_inicio_tratamiento, fecha_fin_tratamiento, id_usuario
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(
                sql,
                (
                    new_report.fecha_registro,  # Asegúrate de incluir todos los campos necesarios
                    new_report.id_lote,
                    new_report.estado_general,
                    new_report.diagnostico,
                    new_report.tratamiento_prescrito,
                    new_report.dosis,
                    new_report.frecuencia_tratamiento,
                    new_report.fecha_inicio_tratamiento,
                    new_report.fecha_fin_tratamiento,
                    new_report.id_usuario,
                ),
            )
        connection.commit()
        connection.close()
        return {"informacion": "Registro exitoso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para obtener todos los reportes
@app.get("/obtener_reportes")
def obtener_reportes():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT r.id_reporte, r.id_lote, r.fecha_registro, u.nombres 
            FROM reportes r
            JOIN usuarios u ON r.id_usuario = u.id_usuario
            ORDER BY r.fecha_registro ASC """
            )
            reportes = cursor.fetchall()

        connection.close()

        # Convertir los resultados a una lista de diccionarios
        return reportes

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/editar_reporte/{id_reporte}")
def editar_reporte(id_reporte: int, reporte: Reporte):
    try:
        connection = get_db_connection()
        with connection:
            with connection.cursor() as cursor:
                sql = """
                UPDATE reportes
                SET id_usuario = %s,
                    fecha_registro = %s,
                    id_lote = %s,
                    estado_general = %s,
                    diagnostico = %s,
                    tratamiento_prescrito = %s,
                    dosis = %s,
                    frecuencia_tratamiento = %s,
                    fecha_inicio_tratamiento = %s,
                    fecha_fin_tratamiento = %s
                WHERE id_reporte = %s
                """
                cursor.execute(
                    sql,
                    (
                        reporte.id_usuario,
                        reporte.fecha_registro,
                        reporte.id_lote,
                        reporte.estado_general,
                        reporte.diagnostico,
                        reporte.tratamiento_prescrito,
                        reporte.dosis,
                        reporte.frecuencia_tratamiento,
                        reporte.fecha_inicio_tratamiento,
                        reporte.fecha_fin_tratamiento,
                        id_reporte,
                    ),
                )
            connection.commit()
        return {"informacion": "Reporte actualizado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# editar estado de las tareas del trabajador
@app.put("/actualizar_estado/{id_tareas}")
def actualizar_estado(id_tareas: int, estado_tarea: EstadoTarea):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                UPDATE tareas
                SET estado = %s
                WHERE id_tareas = %s
            """
            cursor.execute(sql, (estado_tarea.estado, id_tareas))
        connection.commit()
        connection.close()
        return {"informacion": "Estado actualizado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para contar los galpones del administrador
@app.get("/contar_galpones")
def contar_galpones():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM galpon")
            count = cursor.fetchone()
        connection.close()
        return count
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para contar los lotes del administrador
@app.get("/contar_lotes")
def contar_lotes():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM lote")
            count = cursor.fetchone()
        connection.close()
        return count
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#### ruta para crear un galpon ########
@app.post("/crear_galpon")
def crear_galpon(galpon: Galpon):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO galpon (capacidad, aves) 
                VALUES (%s, %s)
            """
            cursor.execute(sql, (galpon.capacidad, galpon.aves))
        connection.commit()
        connection.close()
        return {"informacion": "Galpón agregado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para crear un lote
@app.post("/crear_lote")
def crear_lote(lote: Lote):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO lote (num_aves, fecha_ingreso, id_galpon) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (lote.num_aves, lote.fecha_ingreso, lote.id_galpon))
        connection.commit()
        connection.close()
        return {"informacion": "Lote agregado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para agregar huevos
@app.post("/agregar_huevos")
def agregar_huevos(huevos: Huevos):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO huevos (cantidad, fecha, id_lote) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (huevos.cantidad, huevos.fecha, huevos.id_lote))
        connection.commit()
        connection.close()
        return {"informacion": "Registro de huevos agregado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add_datos_climaticos")
def add_datos_climaticos(datos: DatosClimaticos):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO datos_climaticos (humedad, temperatura, fecha, id_galpon) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(
                sql, (datos.humedad, datos.temperatura, datos.fecha, datos.id_galpon)
            )
        connection.commit()
        connection.close()
        return {"informacion": "Datos climáticos agregados exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/obtener_galpones")
def obtener_galpones():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM galpon")
            galpones = cursor.fetchall()
        connection.close()
        return galpones
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/obtener_lotes")
def obtener_lotes():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM lote")
            lotes = cursor.fetchall()
        connection.close()
        return lotes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/obtener_huevos")
def obtener_huevos():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM huevos")
            huevos = cursor.fetchall()
        connection.close()
        return huevos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para actualizar un lote
@app.put("/actualizar_lote/{id_lote}")
def actualizar_lote(id_lote: int, lote: Lote):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                UPDATE lote
                SET num_aves = %s, fecha_ingreso = %s, id_galpon = %s
                WHERE id_lote = %s
            """
            cursor.execute(
                sql, (lote.num_aves, lote.fecha_ingreso, lote.id_galpon, id_lote)
            )
        connection.commit()
        connection.close()
        return {"informacion": "Lote actualizado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para actualizar un galpón
@app.put("/actualizar_galpon/{id_galpon}")
def actualizar_galpon(id_galpon: int, galpon: Galpon):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                UPDATE galpon
                SET capacidad = %s, aves = %s
                WHERE id_galpon = %s
            """
            cursor.execute(sql, (galpon.capacidad, galpon.aves, id_galpon))
        connection.commit()
        connection.close()
        return {"informacion": "Galpón actualizado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para obtener la cantidad total de huevos por fecha
@app.get("/total_huevos")
def total_huevos():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT fecha, SUM(cantidad) AS total_huevos FROM huevos GROUP BY fecha"
            )
            datos = cursor.fetchall()
        connection.close()
        return datos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para obtener el total de aves por galpón
@app.get("/total_aves_por_galpon")
def total_aves_por_galpon():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id_galpon, SUM(aves) AS total_aves FROM galpon GROUP BY id_galpon"
            )
            datos = cursor.fetchall()
        connection.close()
        return datos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para obtener la cantidad de lotes y aves por galpón
@app.get("/lotes_y_aves_por_galpon")
def lotes_y_aves_por_galpon():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id_galpon, COUNT(id_lote) AS numero_lotes, SUM(num_aves) AS total_aves FROM lote GROUP BY id_galpon"
            )
            datos = cursor.fetchall()
        connection.close()
        return datos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para obtener el número de tareas pendientes por usuario
@app.get("/tareas_pendientes_por_usuario")
def tareas_pendientes_por_usuario():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.nombres, COUNT(*) AS tareas_pendientes
                FROM tareas t
                JOIN usuarios u ON t.id_usuario = u.id_usuario
                WHERE t.estado = %s
                GROUP BY u.id_usuario, u.nombres
            """,
                ("Pendiente",),
            )
            datos = cursor.fetchall()
        connection.close()
        return datos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para obtener la frecuencia de diagnósticos en los reportes
@app.get("/frecuencia_diagnostico")
def frecuencia_diagnostico():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT diagnostico, COUNT(*) AS frecuencia
                FROM reportes
                GROUP BY diagnostico
                ORDER BY frecuencia DESC
            """
            )
            datos = cursor.fetchall()
        connection.close()
        return datos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Comando para correr la aplicación usando Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=3000)
