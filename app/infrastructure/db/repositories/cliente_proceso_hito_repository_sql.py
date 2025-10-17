# app/infrastructure/db/repositories/cliente_proceso_hito_repository_sql.py

from app.domain.entities.cliente_proceso_hito import ClienteProcesoHito
from app.domain.repositories.cliente_proceso_hito_repository import ClienteProcesoHitoRepository
from app.infrastructure.db.models.cliente_proceso_hito_model import ClienteProcesoHitoModel
from datetime import date, datetime

class ClienteProcesoHitoRepositorySQL(ClienteProcesoHitoRepository):
    def __init__(self, session):
        self.session = session

    def guardar(self, relacion: ClienteProcesoHito):
        modelo = ClienteProcesoHitoModel(**vars(relacion))
        self.session.add(modelo)
        self.session.commit()
        self.session.refresh(modelo)
        return modelo

    def listar(self):
        return self.session.query(ClienteProcesoHitoModel).all()

    def obtener_por_id(self, id: int):
        return self.session.query(ClienteProcesoHitoModel).filter_by(id=id).first()

    def eliminar(self, id: int):
        relacion = self.obtener_por_id(id)
        if not relacion:
            return False
        self.session.delete(relacion)
        self.session.commit()
        return True

    def obtener_por_cliente_proceso_id(self, cliente_proceso_id: int):
        return self.session.query(ClienteProcesoHitoModel).filter_by(cliente_proceso_id=cliente_proceso_id).all()

    def listar_habilitados(self):
        """Lista solo los hitos habilitados (habilitado=True)"""
        return self.session.query(ClienteProcesoHitoModel).filter_by(habilitado=True).all()

    def obtener_habilitados_por_cliente_proceso_id(self, cliente_proceso_id: int):
        """Obtiene solo los hitos habilitados de un proceso de cliente específico"""
        return self.session.query(ClienteProcesoHitoModel).filter_by(
            cliente_proceso_id=cliente_proceso_id,
            habilitado=True
        ).all()

    def deshabilitar_desde_fecha_por_hito(self, hito_id: int, fecha_desde):
        """Deshabilita todos los ClienteProcesoHito para un hito_id con fecha_limite >= fecha_desde"""
        from app.infrastructure.db.models.cliente_proceso_model import ClienteProcesoModel

        # Normalizar fecha_desde a date
        if isinstance(fecha_desde, str):
            try:
                fecha_desde = datetime.fromisoformat(fecha_desde).date()
            except ValueError:
                fecha_desde = date.fromisoformat(fecha_desde)

        # Obtener todos los registros a deshabilitar
        query = self.session.query(ClienteProcesoHitoModel).filter(
            ClienteProcesoHitoModel.hito_id == hito_id,
            ClienteProcesoHitoModel.fecha_limite >= fecha_desde
        )

        # Obtener los cliente_proceso_id únicos que serán afectados
        cliente_proceso_ids_afectados = set()
        afectados = 0
        cliente_procesos_deshabilitados = []

        # Primero, obtener los registros que se van a deshabilitar
        registros_a_deshabilitar = query.all()

        for registro in registros_a_deshabilitar:
            registro.habilitado = False
            cliente_proceso_ids_afectados.add(registro.cliente_proceso_id)
            afectados += 1

        # Hacer flush para que los cambios se reflejen en la sesión antes de contar
        self.session.flush()

        # Ahora verificar cada cliente_proceso afectado
        for cliente_proceso_id in cliente_proceso_ids_afectados:
            # Contar TODOS los hitos habilitados para este cliente_proceso
            hitos_habilitados = self.session.query(ClienteProcesoHitoModel).filter(
                ClienteProcesoHitoModel.cliente_proceso_id == cliente_proceso_id,
                ClienteProcesoHitoModel.habilitado == True
            ).count()

            # Si no quedan hitos habilitados, deshabilitar el cliente_proceso
            if hitos_habilitados == 0:
                cliente_proceso = self.session.query(ClienteProcesoModel).filter_by(
                    id=cliente_proceso_id
                ).first()
                if cliente_proceso:
                    cliente_proceso.habilitado = False
                    cliente_procesos_deshabilitados.append({
                        'id': cliente_proceso.id,
                        'cliente_id': cliente_proceso.cliente_id,
                        'proceso_id': cliente_proceso.proceso_id
                    })

        self.session.commit()
        return {
            'hitos_afectados': afectados,
            'cliente_procesos_deshabilitados': cliente_procesos_deshabilitados
        }

    def sincronizar_estado_cliente_proceso(self, cliente_proceso_id: int):
        """Verifica y actualiza el estado de habilitado de un cliente_proceso basado en sus hitos"""
        from app.infrastructure.db.models.cliente_proceso_model import ClienteProcesoModel

        # Contar hitos habilitados para este cliente_proceso
        hitos_habilitados = self.session.query(ClienteProcesoHitoModel).filter(
            ClienteProcesoHitoModel.cliente_proceso_id == cliente_proceso_id,
            ClienteProcesoHitoModel.habilitado == True
        ).count()

        # Obtener el cliente_proceso
        cliente_proceso = self.session.query(ClienteProcesoModel).filter_by(
            id=cliente_proceso_id
        ).first()

        if not cliente_proceso:
            return False

        # Determinar el estado correcto: habilitado si tiene al menos un hito habilitado
        nuevo_estado = hitos_habilitados > 0
        estado_anterior = cliente_proceso.habilitado

        if cliente_proceso.habilitado != nuevo_estado:
            cliente_proceso.habilitado = nuevo_estado
            self.session.commit()
            return {
                'actualizado': True,
                'estado_anterior': estado_anterior,
                'estado_nuevo': nuevo_estado,
                'hitos_habilitados': hitos_habilitados
            }

        return {
            'actualizado': False,
            'estado_actual': cliente_proceso.habilitado,
            'hitos_habilitados': hitos_habilitados
        }

    def actualizar(self, id: int, data: dict):
        from datetime import datetime, date
        from app.infrastructure.db.models.cliente_proceso_model import ClienteProcesoModel

        hito = self.obtener_por_id(id)
        if not hito:
            return None

        # Guardar el cliente_proceso_id antes de actualizar
        cliente_proceso_id = hito.cliente_proceso_id

        for key, value in data.items():
            # Manejar conversión de tipos específicos
            if key == 'fecha_estado' and isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    value = datetime.fromisoformat(value)
            elif key == 'fecha_limite' and isinstance(value, str):
                try:
                    value = date.fromisoformat(value)
                except ValueError:
                    value = value
            elif key == 'habilitado' and isinstance(value, str):
                value = value.lower() in ('true', '1', 'yes', 'on')

            setattr(hito, key, value)

        # Hacer flush para que los cambios se reflejen
        self.session.flush()

        # Si se cambió el estado de habilitado del hito, verificar si debe actualizar el cliente_proceso
        if 'habilitado' in data:
            # Contar hitos habilitados para este cliente_proceso
            hitos_habilitados = self.session.query(ClienteProcesoHitoModel).filter(
                ClienteProcesoHitoModel.cliente_proceso_id == cliente_proceso_id,
                ClienteProcesoHitoModel.habilitado == True
            ).count()

            # Obtener el cliente_proceso
            cliente_proceso = self.session.query(ClienteProcesoModel).filter_by(
                id=cliente_proceso_id
            ).first()

            if cliente_proceso:
                # Si hay hitos habilitados, el cliente_proceso debe estar habilitado
                # Si no hay hitos habilitados, el cliente_proceso debe estar deshabilitado
                nuevo_estado = hitos_habilitados > 0
                if cliente_proceso.habilitado != nuevo_estado:
                    cliente_proceso.habilitado = nuevo_estado

        self.session.commit()
        self.session.refresh(hito)
        return hito

    def verificar_registros_por_hito(self, hito_id: int):
        """Verifica si existe algún registro para un hito específico"""
        from app.infrastructure.db.models import ProcesoHitoMaestroModel

        # Buscar cualquier registro en cliente_proceso_hito que referencie al hito a través de proceso_hito_maestro
        resultado = self.session.query(ClienteProcesoHitoModel).join(
            ProcesoHitoMaestroModel,
            ClienteProcesoHitoModel.hito_id == ProcesoHitoMaestroModel.hito_id
        ).filter(
            ProcesoHitoMaestroModel.hito_id == hito_id
        ).first()

        return resultado is not None

    def eliminar_por_hito_id(self, hito_id: int):
        """Elimina todos los registros de cliente_proceso_hito asociados a un hito específico"""
        from app.infrastructure.db.models import ProcesoHitoMaestroModel

        # Obtener los IDs de proceso_hito_maestro que referencian al hito
        proceso_hito_ids = self.session.query(ProcesoHitoMaestroModel.id).filter(
            ProcesoHitoMaestroModel.hito_id == hito_id
        ).all()

        if proceso_hito_ids:
            # Extraer solo los IDs
            ids_list = [phm_id[0] for phm_id in proceso_hito_ids]

            # Eliminar registros de cliente_proceso_hito que referencien estos IDs
            eliminados = self.session.query(ClienteProcesoHitoModel).filter(
                ClienteProcesoHitoModel.hito_id.in_(ids_list)
            ).delete(synchronize_session=False)

            self.session.commit()
            return eliminados

        return 0
