from abc import ABC, abstractmethod
from app.domain.entities.cliente_proceso_hito import ClienteProcesoHito

class ClienteProcesoHitoRepository(ABC):

    @abstractmethod
    def guardar(self, cliente_proceso_hito: ClienteProcesoHito):
        pass

    @abstractmethod
    def listar(self):
        pass

    @abstractmethod
    def obtener_por_id(self, id: int):
        pass

    @abstractmethod
    def eliminar(self, id: int):
        pass

    @abstractmethod
    def obtener_por_cliente_proceso_id(self, cliente_proceso_id: int):
        pass

    @abstractmethod
    def listar_habilitados(self):
        pass

    @abstractmethod
    def obtener_habilitados_por_cliente_proceso_id(self, cliente_proceso_id: int):
        pass

    @abstractmethod
    def actualizar(self, id: int, data: dict):
        pass

    @abstractmethod
    def verificar_registros_por_hito(self, hito_id: int):
        pass

    @abstractmethod
    def eliminar_por_hito_id(self, hito_id: int):
        pass

    @abstractmethod
    def deshabilitar_desde_fecha_por_hito(self, hito_id: int, fecha_desde):
        """Deshabilita (habilitado=False) todos los ClienteProcesoHito de un hito concreto con fecha_limite >= fecha_desde. Devuelve cantidad afectada."""
        pass

    @abstractmethod
    def sincronizar_estado_cliente_proceso(self, cliente_proceso_id: int):
        """Verifica y actualiza el estado de habilitado de un cliente_proceso basado en sus hitos"""
        pass
