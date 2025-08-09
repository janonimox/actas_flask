from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, FileField, EmailField, TelField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')




class FechaEnvioForm(FlaskForm):
    fecha_envio = DateField('Fecha de Envío Físico', validators=[DataRequired()])
    submit = SubmitField('Guardar')



class RegistrarActaForm(FlaskForm):
    numero_correlativo = StringField('Número Correlativo', validators=[DataRequired()])
    fecha_contratacion = DateField('Fecha del Acta', validators=[DataRequired()])

    nombres = StringField('Nombres', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    rut = StringField('RUT', validators=[DataRequired()])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    direccion = StringField('Dirección', validators=[DataRequired()])
    telefono = TelField('Teléfono', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    estado_civil = SelectField('Estado Civil', choices=[
        ('Soltero/a', 'Soltero/a'),
        ('Casado/a', 'Casado/a'),
        ('Viudo/a', 'Viudo/a'),
        ('Divorciado/a', 'Divorciado/a')
    ], validators=[DataRequired()])
    nacionalidad = StringField('Nacionalidad', validators=[DataRequired()])
    lugar_nacimiento = StringField('Lugar de Nacimiento', validators=[DataRequired()])

    tipo_contrato = SelectField('Tipo de Contrato', choices=[
        ('Plazo Fijo', 'Plazo Fijo'),
        ('Plazo Fijo (Convenio)', 'Plazo Fijo (Convenio)'),
        ('Reemplazo', 'Reemplazo'),
        ('Reemplazo (Convenio)', 'Reemplazo (Convenio)')
    ], validators=[DataRequired()])
    motivo = StringField('Motivo', validators=[Optional()])
    rut_reemplazo = StringField('RUT Titular a Reemplazar', validators=[Optional()])
    nombre_reemplazo = StringField('Nombre Titular a Reemplazar', validators=[Optional()])
    fecha_inicio = DateField('Fecha Inicio Contratación', validators=[DataRequired()])
    fecha_termino = DateField('Fecha Término Contratación', validators=[DataRequired()])
    jornada = StringField('Jornada', validators=[DataRequired()])
    horario_jornada = TextAreaField('Horario Jornada', validators=[Optional()])
    lugar_trabajo = StringField('Lugar de Trabajo', validators=[DataRequired()])
    cargo = StringField('Cargo', validators=[DataRequired()])

    salud = SelectField('Salud', choices=[
        ('FONASA', 'FONASA'),
        ('ISAPRE', 'ISAPRE')
    ], validators=[DataRequired()])
    plan_isapre = StringField('Plan Isapre', validators=[Optional()])
    afp = SelectField('AFP', choices=[
        ('HABITAT', 'HABITAT'),
        ('MODELO', 'MODELO'),
        ('PROVIDA', 'PROVIDA'),
        ('CUPRUM', 'CUPRUM'),
        ('PLANVITAL', 'PLANVITAL')
    ], validators=[DataRequired()])
    categoria = StringField('Categoría', validators=[DataRequired()])

    convenio = StringField('Convenio', validators=[Optional()])
    responsable = StringField('Responsable', validators=[Optional()])

    periodo_remunerativo = StringField('Periodo Remunerativo (MM-YYYY)', validators=[DataRequired()])
    observaciones = TextAreaField('Observaciones', validators=[Optional()])

    firma = FileField('Firma (opcional)', validators=[Optional()])

    nombre_encargado = StringField('Nombre Encargado', validators=[DataRequired()])
    cargo_encargado = StringField('Cargo Encargado', validators=[DataRequired()])
