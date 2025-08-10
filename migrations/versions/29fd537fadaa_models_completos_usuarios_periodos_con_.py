"""models completos: usuarios, periodos con estado, actas

Revision ID: 29fd537fadaa
Revises: 4303c54eaddb
Create Date: 2025-08-09 20:36:13.678252
"""
from alembic import op
import sqlalchemy as sa
from datetime import date

# revision identifiers, used by Alembic.
revision = '29fd537fadaa'
down_revision = '4303c54eaddb'
branch_labels = None
depends_on = None

# Defaults seguros para SQLite al agregar NOT NULL a tablas existentes
_YEAR = str(date.today().year)
_MONTH = str(date.today().month)


def upgrade():
    # === Nueva tabla: periodos_remunerativos ===
    op.create_table(
        'periodos_remunerativos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('anio', sa.Integer(), nullable=False),
        sa.Column('mes', sa.Integer(), nullable=False),
        sa.Column('fecha_inicio', sa.Date(), nullable=False),
        sa.Column('fecha_corte', sa.Date(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.Column('estado', sa.String(length=10), nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("estado IN ('abierto','cerrado')", name='ck_periodo_estado'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('anio', 'mes', name='uq_periodo_anio_mes')
    )

    # === Alteraciones en actas (tabla existente) ===
    with op.batch_alter_table('actas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rut_titular_reemplazo', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('nombre_titular_reemplazo', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('cargo', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('jornada', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('horario_jornada', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('lugar_trabajo', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('motivo', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('observaciones', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('fecha_acta', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('fecha_inicio_contratacion', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('fecha_termino_contratacion', sa.Date(), nullable=True))

        # NOT NULL nuevos -> requieren server_default en SQLite
        batch_op.add_column(sa.Column('periodo_anio', sa.Integer(), nullable=False, server_default=sa.text(_YEAR)))
        batch_op.add_column(sa.Column('periodo_mes', sa.Integer(), nullable=False, server_default=sa.text(_MONTH)))
        batch_op.add_column(sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))

        batch_op.add_column(sa.Column('modificado_en', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('firma_path', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('nombre_encargado', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('cargo_encargado', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('fecha_envio_fisico', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('usuario_envio_fisico', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('correlativo', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('direccion', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('fecha_nacimiento', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('telefono', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('estado_civil', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('nacionalidad', sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column('lugar_nacimiento', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('email', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('categoria', sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column('estado', sa.String(length=20), nullable=True))

        batch_op.alter_column('nombres',
            existing_type=sa.VARCHAR(length=128),
            type_=sa.String(length=120),
            nullable=False)
        batch_op.alter_column('apellidos',
            existing_type=sa.VARCHAR(length=128),
            type_=sa.String(length=120),
            nullable=False)
        batch_op.alter_column('rut',
            existing_type=sa.VARCHAR(length=20),
            nullable=False)
        batch_op.alter_column('tipo_contrato',
            existing_type=sa.VARCHAR(length=64),
            type_=sa.String(length=40),
            nullable=False)
        batch_op.alter_column('convenio',
            existing_type=sa.VARCHAR(length=128),
            type_=sa.String(length=120),
            existing_nullable=True)
        batch_op.alter_column('responsable',
            existing_type=sa.VARCHAR(length=128),
            type_=sa.String(length=120),
            existing_nullable=True)
        batch_op.alter_column('salud',
            existing_type=sa.VARCHAR(length=64),
            type_=sa.String(length=20),
            existing_nullable=True)
        batch_op.alter_column('plan_isapre',
            existing_type=sa.VARCHAR(length=128),
            type_=sa.String(length=120),
            existing_nullable=True)
        batch_op.alter_column('afp',
            existing_type=sa.VARCHAR(length=128),
            type_=sa.String(length=60),
            existing_nullable=True)
        batch_op.alter_column('usuario_id',
            existing_type=sa.INTEGER(),
            nullable=False)
        batch_op.alter_column('cesfam',
            existing_type=sa.VARCHAR(length=128),
            type_=sa.String(length=120),
            nullable=False)

        batch_op.create_index('ix_acta_cesfam_periodo', ['cesfam', 'periodo_anio', 'periodo_mes'], unique=False)
        batch_op.create_index(batch_op.f('ix_actas_correlativo'), ['correlativo'], unique=False)
        batch_op.create_index(batch_op.f('ix_actas_estado'), ['estado'], unique=False)
        batch_op.create_index(batch_op.f('ix_actas_rut'), ['rut'], unique=False)

        # columnas viejas que se eliminan
        batch_op.drop_column('fecha_creacion')
        batch_op.drop_column('rut_reemplazo')
        batch_op.drop_column('nombre_reemplazo')
        batch_op.drop_column('numero_correlativo')
        batch_op.drop_column('fecha_contratacion')
        batch_op.drop_column('firma_filename')
        batch_op.drop_column('periodo_remunerativo')

    # === Alteraciones en usuarios (tabla existente) ===
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
        batch_op.add_column(sa.Column('actualizado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
        batch_op.create_index(batch_op.f('ix_usuarios_username'), ['username'], unique=True)


def downgrade():
    # === usuarios ===
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_usuarios_username'))
        batch_op.drop_column('actualizado_en')
        batch_op.drop_column('creado_en')
        batch_op.drop_column('email')

    # === actas ===
    with op.batch_alter_table('actas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('periodo_remunerativo', sa.VARCHAR(length=10), nullable=True))
        batch_op.add_column(sa.Column('firma_filename', sa.VARCHAR(length=120), nullable=True))
        batch_op.add_column(sa.Column('fecha_contratacion', sa.DATE(), nullable=True))
        batch_op.add_column(sa.Column('numero_correlativo', sa.VARCHAR(length=64), nullable=True))
        batch_op.add_column(sa.Column('nombre_reemplazo', sa.VARCHAR(length=128), nullable=True))
        batch_op.add_column(sa.Column('rut_reemplazo', sa.VARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('fecha_creacion', sa.DATETIME(), nullable=True))

        batch_op.drop_index(batch_op.f('ix_actas_rut'))
        batch_op.drop_index(batch_op.f('ix_actas_estado'))
        batch_op.drop_index(batch_op.f('ix_actas_correlativo'))
        batch_op.drop_index('ix_acta_cesfam_periodo')

        batch_op.alter_column('cesfam',
            existing_type=sa.String(length=120),
            type_=sa.VARCHAR(length=128),
            nullable=True)
        batch_op.alter_column('usuario_id',
            existing_type=sa.INTEGER(),
            nullable=True)
        batch_op.alter_column('afp',
            existing_type=sa.String(length=60),
            type_=sa.VARCHAR(length=128),
            existing_nullable=True)
        batch_op.alter_column('plan_isapre',
            existing_type=sa.String(length=120),
            type_=sa.VARCHAR(length=128),
            existing_nullable=True)
        batch_op.alter_column('salud',
            existing_type=sa.String(length=20),
            type_=sa.VARCHAR(length=64),
            existing_nullable=True)
        batch_op.alter_column('responsable',
            existing_type=sa.String(length=120),
            type_=sa.VARCHAR(length=128),
            existing_nullable=True)
        batch_op.alter_column('convenio',
            existing_type=sa.String(length=120),
            type_=sa.VARCHAR(length=128),
            existing_nullable=True)
        batch_op.alter_column('tipo_contrato',
            existing_type=sa.String(length=40),
            type_=sa.VARCHAR(length=64),
            nullable=True)
        batch_op.alter_column('rut',
            existing_type=sa.VARCHAR(length=20),
            nullable=True)
        batch_op.alter_column('apellidos',
            existing_type=sa.String(length=120),
            type_=sa.VARCHAR(length=128),
            nullable=True)
        batch_op.alter_column('nombres',
            existing_type=sa.String(length=120),
            type_=sa.VARCHAR(length=128),
            nullable=True)

        batch_op.drop_column('estado')
        batch_op.drop_column('categoria')
        batch_op.drop_column('email')
        batch_op.drop_column('lugar_nacimiento')
        batch_op.drop_column('nacionalidad')
        batch_op.drop_column('estado_civil')
        batch_op.drop_column('telefono')
        batch_op.drop_column('fecha_nacimiento')
        batch_op.drop_column('direccion')
        batch_op.drop_column('correlativo')
        batch_op.drop_column('usuario_envio_fisico')
        batch_op.drop_column('fecha_envio_fisico')
        batch_op.drop_column('cargo_encargado')
        batch_op.drop_column('nombre_encargado')
        batch_op.drop_column('firma_path')
        batch_op.drop_column('modificado_en')
        batch_op.drop_column('creado_en')
        batch_op.drop_column('periodo_mes')
        batch_op.drop_column('periodo_anio')
        batch_op.drop_column('fecha_termino_contratacion')
        batch_op.drop_column('fecha_inicio_contratacion')
        batch_op.drop_column('fecha_acta')
        batch_op.drop_column('observaciones')
        batch_op.drop_column('motivo')
        batch_op.drop_column('lugar_trabajo')
        batch_op.drop_column('horario_jornada')
        batch_op.drop_column('jornada')
        batch_op.drop_column('cargo')
        batch_op.drop_column('nombre_titular_reemplazo')
        batch_op.drop_column('rut_titular_reemplazo')

    # === tabla periodos_remunerativos ===
    op.drop_table('periodos_remunerativos')
