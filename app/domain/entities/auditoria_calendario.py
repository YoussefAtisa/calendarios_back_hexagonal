from datetime import datetime
from typing import Optional


class AuditoriaCalendario:
    def __init__(self, id=None, id_cliente="", id_hito=0, campo_modificado="", valor_anterior=None, valor_nuevo=None, usuario_modificacion="", fecha_modificacion=None, observaciones=None, created_at=None, updated_at=None):
        self.id = id
        self.id_cliente = id_cliente
        self.id_hito = id_hito  # ID del ClienteProcesoHito
        self.campo_modificado = campo_modificado
        self.valor_anterior = valor_anterior
        self.valor_nuevo = valor_nuevo
        self.usuario_modificacion = usuario_modificacion
        self.fecha_modificacion = fecha_modificacion
        self.observaciones = observaciones
        self.created_at = created_at
        self.updated_at = updated_at
