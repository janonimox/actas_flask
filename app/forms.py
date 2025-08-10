from datetime import date  # ← para calcular el año actual
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, FileField, EmailField, TelField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Optional, ValidationError

# --- Validador de rango de año (4 dígitos) ---
def year_range(min_year=2000, max_year=2100):
    """Valida que el año tenga 4 dígitos y esté en el rango dado."""
    def _check(form, field):
        if not field.data:
            return
        y = field.data.year
        if y < 1000 or y > 9999 or not (min_year <= y <= max_year):
            raise ValidationError(f"El año de la fecha debe tener 4 dígitos y estar entre {min_year} y {max_year}.")
    return _check

YEAR_NOW = date.today().year  # año actual para fecha de nacimiento


class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')


class FechaEnvioForm(FlaskForm):
    fecha_envio = DateField('Fecha de Envío Físico', validators=[DataRequired()])
    submit = SubmitField('Guardar')


class RegistrarActaForm(FlaskForm):
    numero_correlativo = StringField('Número Correlativo', validators=[DataRequired()])

    # "Fecha de acta"
    fecha_contratacion = DateField(
        'Fecha del Acta',
        validators=[DataRequired(), year_range(2000, 2100)],
        render_kw={'min': '2000-01-01', 'max': '2100-12-31'}
    )

    # Identificación
    nombres = StringField('Nombres', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    rut = StringField('RUT', validators=[DataRequired()])
    fecha_nacimiento = DateField(
        'Fecha de Nacimiento',
        validators=[DataRequired(), year_range(1900, YEAR_NOW)],
        render_kw={'min': '1900-01-01', 'max': f'{YEAR_NOW}-12-31'}
    )
    direccion = StringField('Dirección', validators=[DataRequired()])
    telefono = TelField('Teléfono', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    estado_civil = SelectField('Estado Civil', choices=[
        ('Soltero/a', 'Soltero/a'),
        ('Casado/a', 'Casado/a'),
        ('Viudo/a', 'Viudo/a'),
        ('Divorciado/a', 'Divorciado/a')
    ], validators=[DataRequired()])

    # Nacionalidad
    nacionalidad = SelectField('Nacionalidad', choices=[
        ('', '-- Seleccione --'),
        ('Chilena','Chilena'),
        ('Peruana','Peruana'),
        ('Boliviana','Boliviana'),
        ('Colombiana','Colombiana'),
        ('Española','Española'),
        ('Argentina','Argentina'),
        ('Brasileña','Brasileña'),
        ('Ecuatoriana','Ecuatoriana'),
        ('Venezolana','Venezolana'),
        ('Uruguaya','Uruguaya'),
        ('Paraguaya','Paraguaya'),
    ], validators=[DataRequired()])

    lugar_nacimiento = StringField('Lugar de Nacimiento', validators=[DataRequired()])

    # Contrato
    tipo_contrato = SelectField('Tipo de Contrato', choices=[
        ('Plazo Fijo', 'Plazo Fijo'),
        ('Plazo Fijo (Convenio)', 'Plazo Fijo (Convenio)'),
        ('Reemplazo', 'Reemplazo'),
        ('Reemplazo (Convenio)', 'Reemplazo (Convenio)')
    ], validators=[DataRequired()])
    motivo = StringField('Motivo', validators=[Optional()])
    rut_reemplazo = StringField('RUT Titular a Reemplazar', validators=[Optional()])
    nombre_reemplazo = StringField('Nombre Titular a Reemplazar', validators=[Optional()])
    fecha_inicio = DateField(
        'Fecha Inicio Contratación',
        validators=[DataRequired(), year_range(2000, 2100)],
        render_kw={'min': '2000-01-01', 'max': '2100-12-31'}
    )
    fecha_termino = DateField(
        'Fecha Término Contratación',
        validators=[DataRequired(), year_range(2000, 2100)],
        render_kw={'min': '2000-01-01', 'max': '2100-12-31'}
    )
    jornada = StringField('Jornada', validators=[DataRequired()])

    # Establecimiento (único)
    lugar_trabajo = SelectField('Establecimiento', choices=[
        ('', '-- Seleccione --'),
        ('CESFAM Santa Cecilia', 'CESFAM Santa Cecilia'),
        ('CESFAM San Juan', 'CESFAM San Juan'),
        ('CESFAM Sergio Aguilar', 'CESFAM Sergio Aguilar'),
        ('CESFAM Tierras Blancas', 'CESFAM Tierras Blancas'),
        ('CESFAM Tongoy', 'CESFAM Tongoy'),
        ('CESFAM Pan de Azúcar', 'CESFAM Pan de Azúcar'),
        ('CESFAM El Sauce', 'CESFAM El Sauce'),
        ('CESFAM Lila Cortés Godoy', 'CESFAM Lila Cortés Godoy'),
        ('CECOSF Punta Mira', 'CECOSF Punta Mira'),
        ('PSR Guanaqueros', 'PSR Guanaqueros'),
        ('Departamento de Salud Coquimbo', 'Departamento de Salud Coquimbo'),
    ], validators=[DataRequired()])

    horario_jornada = TextAreaField('Horario Jornada', validators=[Optional()])
    cargo = StringField('Cargo', validators=[DataRequired()])

    # Salud / AFP
    salud = SelectField('Salud', choices=[
        ('FONASA', 'FONASA'),
        ('ISAPRE', 'ISAPRE')
    ], validators=[DataRequired()])
    plan_isapre = StringField('Plan Isapre', validators=[Optional()])

    afp = SelectField('AFP', choices=[
        ('', '-- Seleccione --'),
        ('AFP Capital', 'AFP Capital'),
        ('AFP Cuprum', 'AFP Cuprum'),
        ('AFP Habitat', 'AFP Habitat'),
        ('AFP Modelo', 'AFP Modelo'),
        ('AFP PlanVital', 'AFP PlanVital'),
        ('AFP Provida', 'AFP Provida'),
        ('AFP Uno', 'AFP Uno'),
    ], validators=[DataRequired()])

    categoria = StringField('Categoría', validators=[DataRequired()])

    convenio = StringField('Convenio', validators=[Optional()])
    responsable = StringField('Responsable', validators=[Optional()])

    observaciones = TextAreaField('Observaciones', validators=[Optional()])
    firma = FileField('Firma (opcional)', validators=[Optional()])

    nombre_encargado = StringField('Nombre Encargado', validators=[DataRequired()])
    cargo_encargado = StringField('Cargo Encargado', validators=[DataRequired()])
