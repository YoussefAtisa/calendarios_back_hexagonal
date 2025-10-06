from datetime import timedelta, date
from calendar import monthrange
from app.domain.entities.cliente_proceso import ClienteProceso
from app.domain.entities.proceso import Proceso
from app.domain.repositories.cliente_proceso_repository import ClienteProcesoRepository
from app.domain.repositories.proceso_hito_maestro_repository import ProcesoHitoMaestroRepository
from .base_generador import GeneradorTemporalidad

class GeneradorQuincenal(GeneradorTemporalidad):
    def generar(self, data, proceso_maestro: Proceso, repo: ClienteProcesoRepository, repo_hito_maestro: ProcesoHitoMaestroRepository) -> dict:
        procesos_creados = []
        frecuencia = 15  # Días por quincena fija

        # Obtener hitos del proceso maestro
        hitos_maestros = repo_hito_maestro.listar_por_proceso(proceso_maestro.id)

        if not hitos_maestros:
            raise ValueError(f"No se encontraron hitos para el proceso {proceso_maestro.id}")

        # Ordenar hitos por fecha límite para obtener el primero y último
        hitos_ordenados = sorted(hitos_maestros, key=lambda x: x[1].fecha_limite or date.today())
        primer_hito = hitos_ordenados[0][1]  # HitoModel
        ultimo_hito = hitos_ordenados[-1][1]  # HitoModel

        # Determinar fecha de inicio: prioridad a data.fecha_inicio (respetando el día exacto)
        if hasattr(data, 'fecha_inicio') and data.fecha_inicio:
            fecha_inicio_proceso = data.fecha_inicio
            anio = fecha_inicio_proceso.year
        else:
            # Usar año/mes/día del primer hito como base (si no, día 1)
            anio = primer_hito.fecha_limite.year if primer_hito.fecha_limite else date.today().year
            mes_inicio_proceso = primer_hito.fecha_limite.month if primer_hito.fecha_limite else 1
            dia_inicio_deseado = primer_hito.fecha_limite.day if primer_hito.fecha_limite else 1
            _, last_day_inicio = monthrange(anio, mes_inicio_proceso)
            fecha_inicio_proceso = date(anio, mes_inicio_proceso, min(dia_inicio_deseado, last_day_inicio))

        # La fecha de fin será el fin de año del año de inicio
        fecha_fin_proceso = date(anio, 12, 31)

        # Generar procesos quincenales desde la fecha de inicio hasta la fecha de fin
        fecha_actual = fecha_inicio_proceso

        while fecha_actual <= fecha_fin_proceso:
            fecha_inicio = fecha_actual
            fecha_fin = fecha_actual + timedelta(days=frecuencia - 1)

            # Si la fecha de fin excede la fecha límite del último hito, ajustarla
            if fecha_fin > fecha_fin_proceso:
                fecha_fin = fecha_fin_proceso

            cliente_proceso = ClienteProceso(
                id=None,
                cliente_id=data.cliente_id,
                proceso_id=data.proceso_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                mes=fecha_inicio.month,
                anio=fecha_inicio.year,
                anterior_id=None
            )
            procesos_creados.append(repo.guardar(cliente_proceso))

            # Avanzar 15 días para la siguiente quincena
            fecha_actual = fecha_actual + timedelta(days=frecuencia)

            # Si hemos pasado la fecha de fin, terminar
            if fecha_actual > fecha_fin_proceso:
                break

        return {
            "mensaje": "Procesos cliente generados con éxito",
            "cantidad": len(procesos_creados),
            "anio": anio,
            "procesos": procesos_creados
        }
