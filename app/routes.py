from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, Usuario, Acta #FechaLimite
from .forms import LoginForm, FechaEnvioForm, RegistrarActaForm
from datetime import datetime, date
import os
from werkzeug.utils import secure_filename


bp = Blueprint('main', __name__)

# Ruta de inicio
@bp.route('/')
def index():
    return redirect(url_for('main.login'))

# Login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(username=form.username.data).first()
        if usuario and usuario.check_password(form.password.data):
            login_user(usuario)
            return redirect(url_for('main.registrar_acta'))  # o la vista que corresponda
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')
    return render_template('login.html', form=form)

# Logout
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# Menú principal
@bp.route('/menu')
@login_required
def menu():
    return render_template('menu.html')

# Registrar acta
@bp.route('/registrar_acta', methods=['GET', 'POST'])
@login_required
def registrar_acta():
    form = RegistrarActaForm()  # ← ESTA LÍNEA FALTABA
    if request.method == 'POST':
        data = request.form

        # Validar fecha límite para el período ingresado
        periodo = data.get('periodo_remunerativo')
        if periodo:
            mes, anio = map(int, periodo.split('-'))
            fecha_limite = FechaLimite.query.filter_by(mes=mes, anio=anio).first()
            ahora = date.today()
            if fecha_limite and ahora > fecha_limite.fecha_limite:
                # Cambiar el período automáticamente al mes siguiente
                if mes == 12:
                    mes, anio = 1, anio + 1
                else:
                    mes += 1
                periodo = f"{mes:02d}-{anio}"
                flash("El período ha superado la fecha límite. El acta se registrará para el mes siguiente.", 'warning')

        # Firma (opcional)
        firma_file = request.files.get('firma')
        filename = None
        if firma_file and firma_file.filename:
            filename = secure_filename(firma_file.filename)
            firma_path = os.path.join('static', 'firmas', filename)
            firma_file.save(firma_path)

        nueva_acta = Acta(
            numero_correlativo=data.get('numero_correlativo'),
            nombres=data.get('nombres'),
            apellidos=data.get('apellidos'),
            rut=data.get('rut'),
            tipo_contrato=data.get('tipo_contrato'),
            rut_reemplazo=data.get('rut_reemplazo') if 'reemplazo' in data.get('tipo_contrato', '').lower() else None,
            nombre_reemplazo=data.get('nombre_reemplazo') if 'reemplazo' in data.get('tipo_contrato', '').lower() else None,
            salud=data.get('salud'),
            plan_isapre=data.get('plan_isapre') if data.get('salud') == 'isapre' else None,
            afp=data.get('afp'),
            convenio=data.get('convenio') if 'convenio' in data.get('tipo_contrato', '').lower() else None,
            responsable=data.get('responsable') if 'convenio' in data.get('tipo_contrato', '').lower() else None,
            fecha_contratacion=data.get('fecha_contratacion'),
            periodo_remunerativo=periodo,
            fecha_creacion=datetime.now(),
            cesfam=current_user.cesfam,
            usuario_id=current_user.id,
            firma_filename=filename
        )
        db.session.add(nueva_acta)
        db.session.commit()

        # Guardar fecha de envío físico después
        return redirect(url_for('main.registrar_envio_fisico', acta_id=nueva_acta.id))
    
    return render_template('registrar_acta.html', form=form, usuario=current_user)

# Registrar fecha de envío físico (post-guardar)
@bp.route('/registrar_envio_fisico/<int:acta_id>', methods=['GET', 'POST'])
@login_required
def registrar_envio_fisico(acta_id):
    acta = Acta.query.get_or_404(acta_id)

    # Solo permitir que el usuario dueño de la acta la edite
    if current_user.rol != 'superusuario' and acta.usuario_id != current_user.id:
        abort(403)

    form = FechaEnvioFisicoForm()

    if form.validate_on_submit():
        acta.fecha_envio_fisico = form.fecha_envio.data
        db.session.commit()
        flash('Fecha de envío físico registrada.', 'success')
        return redirect(url_for('main.registrar_acta'))  # O redirige a listado si prefieres

    return render_template('registrar_envio_fisico.html', form=form, acta=acta)
