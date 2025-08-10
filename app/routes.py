from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, date
from werkzeug.utils import secure_filename
import os

from .models import db, Usuario, Acta, PeriodoRemunerativo
from .forms import LoginForm, RegistrarActaForm

# =========================
# Blueprint
# =========================
bp = Blueprint('main', __name__)


# =========================
# Helpers
# =========================
def require_superuser():
    if getattr(current_user, "rol", "") != "superusuario":
        abort(403)


# =========================
# Inicio / Autenticación
# =========================
@bp.route('/')
def index():
    # Si ya está autenticado, al listado; si no, al login

     return redirect(url_for('main.login'))
 #   if current_user.is_authenticated:
    #    return redirect(url_for('main.listar_actas'))
  # return redirect(url_for('main.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Usa tu LoginForm existente
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(username=form.username.data).first()
        if usuario and usuario.check_password(form.password.data):
            login_user(usuario)
            return redirect(url_for('main.listar_actas'))
        flash('Nombre de usuario o contraseña incorrectos', 'danger')
    return render_template('login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


# =========================
# Períodos (solo superusuario)
# =========================
@bp.route("/periodos", methods=["GET"])
@login_required
def periodos_list():
    require_superuser()
    items = PeriodoRemunerativo.query.order_by(
        PeriodoRemunerativo.anio.desc(), PeriodoRemunerativo.mes.desc()
    ).all()
    return render_template("periodos_list.html", periodos=items)


@bp.route("/periodos/nuevo", methods=["POST"])
@login_required
def periodos_nuevo():
    require_superuser()
    try:
        anio = int(request.form["anio"])
        mes = int(request.form["mes"])
        fecha_inicio = datetime.strptime(request.form["fecha_inicio"], "%Y-%m-%d").date()
        fecha_corte = datetime.strptime(request.form["fecha_corte"], "%Y-%m-%d").date()
    except Exception:
        flash("Datos de período inválidos.", "danger")
        return redirect(url_for("main.periodos_list"))

    # Evitar duplicados (por unique anio+mes)
    ya = PeriodoRemunerativo.query.filter_by(anio=anio, mes=mes).first()
    if ya:
        flash("Ese período ya existe.", "warning")
        return redirect(url_for("main.periodos_list"))

    p = PeriodoRemunerativo(
        anio=anio, mes=mes,
        fecha_inicio=fecha_inicio, fecha_corte=fecha_corte,
        activo=True, estado="abierto"
    )
    db.session.add(p)
    db.session.commit()
    flash("Período creado.", "success")
    return redirect(url_for("main.periodos_list"))


@bp.route("/periodos/<int:pid>/estado", methods=["POST"])
@login_required
def periodos_estado(pid):
    require_superuser()
    p = PeriodoRemunerativo.query.get_or_404(pid)
    nuevo = request.form.get("estado")
    if nuevo in ("abierto", "cerrado"):
        p.estado = nuevo
        db.session.commit()
        flash(f"Período marcado como {nuevo}.", "success")
    return redirect(url_for("main.periodos_list"))


# =========================
# Actas
# =========================
@bp.route('/actas')
@login_required
def listar_actas():
    q = Acta.query
    if getattr(current_user, "rol", "administrativo") != "superusuario":
        q = q.filter_by(cesfam=current_user.cesfam)
    actas = q.order_by(Acta.creado_en.desc()).limit(100).all()
    return render_template('listar_actas.html', actas=actas)


@bp.route('/actas/<int:acta_id>')
@login_required
def ver_acta(acta_id):
    a = Acta.query.get_or_404(acta_id)
    # solo dueño o superusuario
    if current_user.rol != 'superusuario' and a.usuario_id != current_user.id:
        abort(403)
    return render_template('ver_acta.html', acta=a)


@bp.route('/registrar_acta', methods=['GET', 'POST'])
@login_required
def registrar_acta():
    # ---- Período automático (no editable) ----
    hoy = date.today()
    periodo, _pasa_siguiente = PeriodoRemunerativo.periodo_vigente_para_fecha(hoy)
    if not periodo:
        flash("No existe período remunerativo activo configurado. Solicita al superusuario crearlo.", "warning")
        return redirect(url_for("main.periodos_list") if getattr(current_user, "rol", "") == "superusuario"
                        else url_for("main.listar_actas"))

    # El helper YA devuelve el periodo correcto (actual o siguiente). No sumar de nuevo.
    periodo_anio, periodo_mes = periodo.anio, periodo.mes
    periodo_label = f"{periodo_mes:02d}/{periodo_anio}"

    # ---- Tu WTForm ----
    form = RegistrarActaForm()

    # GET: si el usuario tiene cesfam, preseleccionar en Establecimiento
    if request.method == 'GET':
        user_cesfam = (getattr(current_user, 'cesfam', '') or '').strip()
        if user_cesfam:
            values = [v for (v, _l) in form.lugar_trabajo.choices]
            if user_cesfam in values:
                form.lugar_trabajo.data = user_cesfam

    # POST
    if form.validate_on_submit():
        # Datos base
        nombres = form.nombres.data
        apellidos = form.apellidos.data
        rut = form.rut.data
        tipo_contrato = form.tipo_contrato.data
        establecimiento = form.lugar_trabajo.data  # único campo de establecimiento
        cargo = form.cargo.data
        jornada = form.jornada.data
        horario_jornada = form.horario_jornada.data
        motivo = form.motivo.data
        observaciones = form.observaciones.data
        salud = form.salud.data
        plan_isapre = form.plan_isapre.data if (salud or '').upper() == 'ISAPRE' else None
        afp = form.afp.data
        categoria = form.categoria.data
        rut_rep = form.rut_reemplazo.data
        nom_rep = form.nombre_reemplazo.data
        convenio = form.convenio.data
        responsable = form.responsable.data

        # Fechas
        fecha_acta = form.fecha_contratacion.data         # rotulada como “Fecha de acta”
        f_inicio = form.fecha_inicio.data
        f_termino = form.fecha_termino.data

        # Datos personales
        direccion = form.direccion.data
        fecha_nacimiento = form.fecha_nacimiento.data
        telefono = form.telefono.data
        estado_civil = form.estado_civil.data
        nacionalidad = form.nacionalidad.data
        lugar_nacimiento = form.lugar_nacimiento.data
        email = form.email.data

        # Firma (opcional)
        firma_file = request.files.get('firma')
        firma_path = None
        if firma_file and getattr(firma_file, "filename", ""):
            ext = firma_file.filename.rsplit('.', 1)[-1].lower()
            if ext in {"png", "jpg", "jpeg", "webp"}:
                fname = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{firma_file.filename}")
                destino = os.path.join(current_app.root_path, 'static', 'uploads', 'firmas', fname)
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                firma_file.save(destino)
                firma_path = os.path.join('static', 'uploads', 'firmas', fname).replace('\\', '/')
            else:
                flash("Formato de firma no permitido. Usa png/jpg/jpeg/webp.", "warning")

        # Cesfam final: usa el del usuario si existe; si no, el Establecimiento elegido
        cesfam_final = (getattr(current_user, "cesfam", "") or establecimiento or "").strip()

        # Crear Acta (ojo: correlativo es el nombre del campo en el modelo)
        acta = Acta(
            correlativo=form.numero_correlativo.data or None,

            nombres=nombres, apellidos=apellidos, rut=rut,
            tipo_contrato=tipo_contrato,
            rut_titular_reemplazo=rut_rep or None,
            nombre_titular_reemplazo=nom_rep or None,
            convenio=convenio or None,
            responsable=responsable or None,

            salud=salud, plan_isapre=plan_isapre, afp=afp,

            cargo=cargo, jornada=jornada, horario_jornada=horario_jornada,
            lugar_trabajo=establecimiento, motivo=motivo, observaciones=observaciones,

            fecha_acta=fecha_acta,
            fecha_inicio_contratacion=f_inicio,
            fecha_termino_contratacion=f_termino,

            periodo_anio=periodo_anio, periodo_mes=periodo_mes,

            usuario_id=current_user.id, cesfam=cesfam_final,

            firma_path=firma_path,

            nombre_encargado=form.nombre_encargado.data,
            cargo_encargado=form.cargo_encargado.data,

            direccion=direccion, fecha_nacimiento=fecha_nacimiento, telefono=telefono,
            estado_civil=estado_civil, nacionalidad=nacionalidad,
            lugar_nacimiento=lugar_nacimiento, email=email, categoria=categoria,

            estado='borrador'
        )
        db.session.add(acta)
        db.session.commit()

        flash(f"Acta registrada para el período {periodo_mes:02d}/{periodo_anio}.", "success")
        return redirect(url_for('main.registrar_envio_fisico', acta_id=acta.id))

    # Si falla la validación, mostrar errores
    if request.method == 'POST' and not form.validate():
        for campo, errs in form.errors.items():
            for e in errs:
                flash(f"Error en {campo}: {e}", "danger")

    # GET o validación fallida
    return render_template('registrar_acta.html',
                           periodo_label=periodo_label,
                           usuario=current_user,
                           form=form)


@bp.route('/registrar_envio_fisico/<int:acta_id>', methods=['GET', 'POST'])
@login_required
def registrar_envio_fisico(acta_id):
    acta = Acta.query.get_or_404(acta_id)

    # Solo el dueño o superusuario
    if current_user.rol != 'superusuario' and acta.usuario_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        v = request.form.get('fecha_envio_fisico')
        if not v:
            flash('Debes seleccionar una fecha.', 'warning')
            return render_template('registrar_envio_fisico.html', acta=acta)
        acta.fecha_envio_fisico = datetime.strptime(v, "%Y-%m-%d").date()
        acta.usuario_envio_fisico = current_user.id
        acta.estado = 'enviado'
        db.session.commit()
        flash('Fecha de envío físico registrada.', 'success')
        return redirect(url_for('main.ver_acta', acta_id=acta.id))

    return render_template('registrar_envio_fisico.html', acta=acta)
