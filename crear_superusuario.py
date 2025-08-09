from app import create_app, db
from app.models import Usuario

app = create_app()

with app.app_context():
    username = 'admin'
    password = 'admin123'
    cesfam = 'CESFAM CENTRAL'

    # Verifica si ya existe
    existente = db.session.execute(
        db.select(Usuario).filter_by(username=username)
    ).scalar_one_or_none()

    if not existente:
        nuevo_usuario = Usuario(
            username=username,
            cesfam=cesfam,
            rol='superusuario'
        )
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        print(f"✅ Superusuario creado: {username} / {password}")
    else:
        print(f"⚠️ El usuario '{username}' ya existe.")
