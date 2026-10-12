from typing import List, Optional, Union

from src.dominio.administrador import Administrador
from src.dominio.usuario import Usuario
from src.persistencia.conexion import abrir_conexion
from src.persistencia.dao_util import DAOError, marcador


class UsuarioDAO:
    """
    Data Access Object para la persistencia de Usuario y Administrador.
    Aplica encapsulamiento de consultas SQL y manejo de excepciones (Criterio 2.1.4).
    """

    def guardar(self, usuario: Union[Usuario, Administrador]) -> int:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        es_admin = isinstance(usuario, Administrador)
        tipo = "ADMIN" if es_admin else "USUARIO"

        try:
            cursor.execute(
                f"INSERT INTO usuario (nombre, correo, contrasena_hash, tipo_usuario) "
                f"VALUES ({p}, {p}, {p}, {p})",
                (usuario.nombre, usuario.correo, usuario.contrasena_hash, tipo),
            )
            usuario_id = cursor.lastrowid
            usuario.id = usuario_id

            if es_admin:
                cursor.execute(
                    f"INSERT INTO administrador (id_usuario, nivel_acceso) VALUES ({p}, {p})",
                    (usuario_id, getattr(usuario, "nivel_acceso", "ADMIN")),
                )

            conexion.commit()
            return usuario_id
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al guardar usuario '{usuario.correo}': {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_id(self, id_usuario: int) -> Optional[Union[Usuario, Administrador]]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"SELECT u.id_usuario, u.nombre, u.correo, u.contrasena_hash, u.tipo_usuario, a.nivel_acceso "
                f"FROM usuario u LEFT JOIN administrador a ON u.id_usuario = a.id_usuario "
                f"WHERE u.id_usuario = {p}",
                (id_usuario,),
            )
            fila = cursor.fetchone()
            if not fila:
                return None

            id_u, nombre, correo, c_hash, tipo, nivel = fila
            if tipo == "ADMIN":
                admin = Administrador(id_u, nombre, correo, c_hash, nivel or "ADMIN")
                return admin
            return Usuario(id_u, nombre, correo, c_hash)
        except Exception as err:
            raise DAOError(f"Error al buscar usuario por ID {id_usuario}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_correo(self, correo: str) -> Optional[Union[Usuario, Administrador]]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"SELECT u.id_usuario, u.nombre, u.correo, u.contrasena_hash, u.tipo_usuario, a.nivel_acceso "
                f"FROM usuario u LEFT JOIN administrador a ON u.id_usuario = a.id_usuario "
                f"WHERE LOWER(u.correo) = LOWER({p})",
                (correo.strip(),),
            )
            fila = cursor.fetchone()
            if not fila:
                return None

            id_u, nombre, c_correo, c_hash, tipo, nivel = fila
            if tipo == "ADMIN":
                return Administrador(id_u, nombre, c_correo, c_hash, nivel or "ADMIN")
            return Usuario(id_u, nombre, c_correo, c_hash)
        except Exception as err:
            raise DAOError(f"Error al buscar usuario por correo '{correo}': {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def autenticar(self, correo: str, contrasena_plana: str) -> Optional[Union[Usuario, Administrador]]:
        """
        Valida las credenciales comparando con el hash seguro almacenado.
        Retorna la instancia si es válido, None si falla.
        """
        usuario = self.buscar_por_correo(correo)
        if usuario and usuario.autenticar(contrasena_plana):
            return usuario
        return None

    def listar(self) -> List[Union[Usuario, Administrador]]:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "SELECT u.id_usuario, u.nombre, u.correo, u.contrasena_hash, u.tipo_usuario, a.nivel_acceso "
                "FROM usuario u LEFT JOIN administrador a ON u.id_usuario = a.id_usuario ORDER BY u.id_usuario"
            )
            resultado = []
            for fila in cursor.fetchall():
                id_u, nombre, correo, c_hash, tipo, nivel = fila
                if tipo == "ADMIN":
                    resultado.append(Administrador(id_u, nombre, correo, c_hash, nivel or "ADMIN"))
                else:
                    resultado.append(Usuario(id_u, nombre, correo, c_hash))
            return resultado
        except Exception as err:
            raise DAOError(f"Error al listar usuarios: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def actualizar(self, usuario: Union[Usuario, Administrador]) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(
                f"UPDATE usuario SET nombre={p}, correo={p}, contrasena_hash={p} WHERE id_usuario={p}",
                (usuario.nombre, usuario.correo, usuario.contrasena_hash, usuario.id),
            )
            if isinstance(usuario, Administrador):
                cursor.execute(
                    f"UPDATE administrador SET nivel_acceso={p} WHERE id_usuario={p}",
                    (usuario.nivel_acceso, usuario.id),
                )
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al actualizar usuario ID {usuario.id}: {err}") from err
        finally:
            cursor.close()
            conexion.close()

    def eliminar(self, id_usuario: int) -> bool:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        p = marcador()
        try:
            cursor.execute(f"DELETE FROM usuario WHERE id_usuario = {p}", (id_usuario,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as err:
            conexion.rollback()
            raise DAOError(f"Error al eliminar usuario ID {id_usuario}: {err}") from err
        finally:
            cursor.close()
            conexion.close()
