from typing import List, Optional, Union

from src.dominio.administrador import Administrador
from src.dominio.empleado import Empleado
from src.dominio.usuario import Usuario
from src.persistencia.conexion import marcador_sql
from src.persistencia.dao_util import DAOError, exigir_guardado, exigir_nuevo, sesion_bd

_SELECT = (
    "SELECT u.id_usuario, u.nombre, u.correo, u.contrasena_hash, u.tipo_usuario, a.nivel_acceso "
    "FROM usuario u LEFT JOIN administrador a ON a.id_usuario = u.id_usuario"
)


class UsuarioDAO:
    """
    Persistencia de Usuario y su subclase Administrador (tablas usuario + administrador).
    Los Empleados se guardan con EmpleadoDAO (también usan la tabla usuario).
    """

    @staticmethod
    def _fila_a_usuario(fila) -> Union[Usuario, Administrador]:
        """Convierte una fila en el objeto del dominio que corresponda a su tipo."""
        id_usuario, nombre, correo, contrasena_hash, tipo, nivel_acceso = fila
        if tipo == "ADMIN":
            return Administrador(id_usuario, nombre, correo or "", contrasena_hash or "", nivel_acceso or "ADMIN")
        return Usuario(id_usuario, nombre, correo or "", contrasena_hash or "")

    @staticmethod
    def insertar(usuario: Union[Usuario, Administrador]) -> Union[Usuario, Administrador]:
        if isinstance(usuario, Empleado):
            raise DAOError("Los empleados se guardan con EmpleadoDAO.")
        exigir_nuevo(usuario.id_usuario, "El usuario")
        es_admin = isinstance(usuario, Administrador)
        p = marcador_sql()

        with sesion_bd() as cursor:
            cursor.execute(
                f"INSERT INTO usuario (nombre, correo, contrasena_hash, tipo_usuario) VALUES ({p}, {p}, {p}, {p})",
                (usuario.nombre, usuario.correo or None, usuario.contrasena_hash, "ADMIN" if es_admin else "USUARIO"),
            )
            nuevo_id = cursor.lastrowid  # id autoincremental generado por la BD
            if es_admin:
                cursor.execute(
                    f"INSERT INTO administrador (id_usuario, nivel_acceso) VALUES ({p}, {p})",
                    (nuevo_id, usuario.nivel_acceso),
                )
        usuario.id_usuario = nuevo_id  # solo después del COMMIT
        return usuario

    @staticmethod
    def buscar_por_id(id_usuario: int) -> Optional[Union[Usuario, Administrador]]:
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(f"{_SELECT} WHERE u.id_usuario = {p}", (id_usuario,))
            fila = cursor.fetchone()
        return UsuarioDAO._fila_a_usuario(fila) if fila else None

    @staticmethod
    def buscar_por_correo(correo: str) -> Optional[Union[Usuario, Administrador]]:
        p = marcador_sql()
        with sesion_bd() as cursor:
            # el dominio guarda los correos en minúsculas, por eso se normaliza la búsqueda
            cursor.execute(f"{_SELECT} WHERE u.correo = {p}", (correo.strip().lower(),))
            fila = cursor.fetchone()
        return UsuarioDAO._fila_a_usuario(fila) if fila else None

    @staticmethod
    def autenticar(correo: str, contrasena_plana: str) -> Optional[Union[Usuario, Administrador]]:
        """Retorna el usuario si la contraseña es correcta; None en caso contrario (sin decir cuál falló)."""
        usuario = UsuarioDAO.buscar_por_correo(correo)
        if usuario is not None and usuario.autenticar(contrasena_plana):
            return usuario
        return None

    @staticmethod
    def listar() -> List[Union[Usuario, Administrador]]:
        with sesion_bd() as cursor:
            cursor.execute(f"{_SELECT} ORDER BY u.id_usuario")
            filas = cursor.fetchall()
        return [UsuarioDAO._fila_a_usuario(fila) for fila in filas]

    @staticmethod
    def actualizar(usuario: Union[Usuario, Administrador]) -> bool:
        """True si se actualizó un registro; False si no existe un usuario con ese id."""
        exigir_guardado(usuario.id_usuario, "El usuario")
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"UPDATE usuario SET nombre = {p}, correo = {p}, contrasena_hash = {p} "
                f"WHERE id_usuario = {p} AND tipo_usuario <> 'EMPLEADO'",
                (usuario.nombre, usuario.correo or None, usuario.contrasena_hash, usuario.id_usuario),
            )
            actualizado = cursor.rowcount > 0
            if actualizado and isinstance(usuario, Administrador):
                cursor.execute(
                    f"UPDATE administrador SET nivel_acceso = {p} WHERE id_usuario = {p}",
                    (usuario.nivel_acceso, usuario.id_usuario),
                )
        return actualizado

    @staticmethod
    def eliminar(id_usuario: int) -> bool:
        """True si se eliminó; False si no existía. Los empleados se eliminan con EmpleadoDAO."""
        p = marcador_sql()
        with sesion_bd() as cursor:
            cursor.execute(
                f"DELETE FROM usuario WHERE id_usuario = {p} AND tipo_usuario <> 'EMPLEADO'", (id_usuario,)
            )
            return cursor.rowcount > 0
