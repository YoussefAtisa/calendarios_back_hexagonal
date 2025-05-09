from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.db.database import Base



class ProcesoHitoMaestroModel(Base):
    __tablename__ = "proceso_hito_maestro"

    id = Column(Integer, primary_key=True, index=True)
    id_proceso = Column(Integer, ForeignKey("proceso.id"), nullable=False)
    id_hito = Column(Integer, ForeignKey("hito.id"), nullable=False)

    proceso = relationship("ProcesoModel", back_populates="hitos")
    hito = relationship("HitoModel", back_populates="procesos")
