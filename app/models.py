# app/models.py
from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import CheckConstraint
from . import db  # usa la instancia creada en app/__init__.py


# =========================
# USUARIOS
# =========================
class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120))  # opcional
    cesfam = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(64), default="administrativo")  # "superusuario" | "administrativo"

    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


# =========================
# PERÍODOS REMUNERATIVOS
# =========================
class PeriodoRemunerativo(db.Model):
    __tablename__ = "periodos_remunerativos"

    id = db.Column(db.Integer, primary_key=True)
    anio = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)  # 1..12
    fecha_inicio = db.Column(db.Date, nullable=False)  # ventana de ingreso (informativo)
    fecha_corte = db.Column(db.Date, nullable=False)   # fecha límite para el mes vigente
    activo = db.Column(db.Boolean, default=True, nullable=False)
    estado = db.Column(db.String(10), default="abierto", nullable=False)  # "abierto" | "cerrado"

    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("anio", "mes", name="uq_periodo_anio_mes"),
        CheckConstraint("estado IN ('abierto','cerrado')", name="ck_periodo_estado"),
    )

    @property
    def etiqueta_legible(self) -> str:
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        return f"{meses[self.mes - 1]} {self.anio}"

    @staticmethod
    def periodo_vigente_para_fecha(fecha_hoy: date):
        """
        Devuelve (periodo_sugerido, es_siguiente_mes)
        - Si no hay periodo -> (None, False)
        - Si el vigente está 'cerrado' o ya pasó la fecha_corte -> sugiere el mes siguiente.
        - Si sigue dentro de la ventana -> devuelve el vigente.
        """
        periodo = (
            PeriodoRemunerativo.query.filter_by(activo=True)
            .order_by(PeriodoRemunerativo.anio.desc(), PeriodoRemunerativo.mes.desc())
            .first()
        )
        if not periodo:
            return None, False

        # Si está cerrado o ya superó fecha corte → pasar al mes siguiente
        if periodo.estado == "cerrado" or fecha_hoy > periodo.fecha_corte:
            anio, mes = periodo.anio, periodo.mes + 1
            if mes == 13:
                mes, anio = 1, anio + 1
            return (
                PeriodoRemunerativo(
                    anio=anio,
                    mes=mes,
                    fecha_inicio=date(anio, mes, 1),
                    # usamos la última fecha_corte como referencia; el superusuario definirá la real al crear el periodo
                    fecha_corte=periodo.fecha_corte,
                ),
                True,
            )

        # Sigue vigente
        return periodo, False


# =========================
# ACTAS
# =========================
class Acta(db.Model):
    __tablename__ = "actas"

    id = db.Column(db.Integer, primary_key=True)

    # Identificación funcionario
    nombres = db.Column(db.String(120), nullable=False)
    apellidos = db.Column(db.String(120), nullable=False)
    rut = db.Column(db.String(20), nullable=False, index=True)

    # Tipo de contrato y condicionales
    # Valores esperados: 'Plazo Fijo', 'Reemplazo', 'Plazo Fijo (Convenio)', 'Reemplazo (Convenio)'
    tipo_contrato = db.Column(db.String(40), nullable=False)
    rut_titular_reemplazo = db.Column(db.String(20))
    nombre_titular_reemplazo = db.Column(db.String(120))
    convenio = db.Column(db.String(120))
    responsable = db.Column(db.String(120))  # obligatorio si es "(Convenio)"

    # Salud y AFP
    salud = db.Column(db.String(20))         # 'FONASA' | 'ISAPRE'
    plan_isapre = db.Column(db.String(120))  # sólo si salud == ISAPRE
    afp = db.Column(db.String(60))           # AFP de Chile (select)

    # Datos laborales
    cargo = db.Column(db.String(120))
    jornada = db.Column(db.String(120))
    horario_jornada = db.Column(db.Text)
    lugar_trabajo = db.Column(db.String(120))  # Centros de salud Coquimbo (select)
    motivo = db.Column(db.String(200))
    observaciones = db.Column(db.Text)

    # Fechas
    fecha_acta = db.Column(db.Date)  # etiqueta en UI: "Fecha de acta"
    fecha_inicio_contratacion = db.Column(db.Date)
    fecha_termino_contratacion = db.Column(db.Date)

    # Período remunerativo (NO editable por el usuario; asignado automáticamente)
    periodo_anio = db.Column(db.Integer, nullable=False)
    periodo_mes = db.Column(db.Integer, nullable=False)

    # Metadatos
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    modificado_en = db.Column(db.DateTime, onupdate=datetime.utcnow)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    usuario = db.relationship("Usuario", backref="actas")

    cesfam = db.Column(db.String(120), nullable=False)

    # Firma y envío físico
    firma_path = db.Column(db.String(255))   # ruta relativa a /static/uploads/firmas
    nombre_encargado = db.Column(db.String(120))
    cargo_encargado = db.Column(db.String(120))
    fecha_envio_fisico = db.Column(db.Date)        # se ingresa en paso posterior
    usuario_envio_fisico = db.Column(db.Integer)   # id del usuario que registró la fecha (opcional)

    # Correlativo (editable por administrativos)
    correlativo = db.Column(db.String(30), index=True)

    # Datos personales extra
    direccion = db.Column(db.String(200))
    fecha_nacimiento = db.Column(db.Date)
    telefono = db.Column(db.String(50))
    estado_civil = db.Column(db.String(50))
    nacionalidad = db.Column(db.String(80))    # select con países LATAM
    lugar_nacimiento = db.Column(db.String(120))
    email = db.Column(db.String(120))
    categoria = db.Column(db.String(80))

    # Estado del documento (flujo)
    estado = db.Column(db.String(20), default="borrador", index=True)  # 'borrador' | 'enviado' | 'cerrado'

    # ==== PREP FIRMA DIGITAL ====
    # (Todos opcionales para no romper migración ni flujo actual)
    firma_tipo = db.Column(db.String(20))       # 'imagen' | 'FES' | 'FEA'
    firmada_en = db.Column(db.DateTime)         # cuándo se firmó
    firma_hash = db.Column(db.String(64))       # SHA-256 del archivo/PDF base
    firma_cn = db.Column(db.String(120))        # CN del certificado (FEA)
    firma_serial = db.Column(db.String(120))    # serial del certificado (FEA)
    firma_p7s_path = db.Column(db.String(255))  # ruta a .p7s o PDF firmado (FEA)

    __table_args__ = (
        # índice compuesto útil para filtro por período y CESFAM
        db.Index("ix_acta_cesfam_periodo", "cesfam", "periodo_anio", "periodo_mes"),
    )
    