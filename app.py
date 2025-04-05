from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///torremal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Asegurar que existe la carpeta de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar la base de datos
db = SQLAlchemy(app)

# Configurar el sistema de login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Definir modelos de la base de datos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    lugar = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(200), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'fecha': self.fecha.isoformat(),
            'lugar': self.lugar,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'imagen': self.imagen
        }

class Peregrinacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    lugar = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(200), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'fecha': self.fecha.isoformat(),
            'lugar': self.lugar,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'imagen': self.imagen,
            'url': self.url
        }

class Inscripcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=True)
    peregrinacion_id = db.Column(db.Integer, db.ForeignKey('peregrinacion.id'), nullable=True)
    nombre = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    num_asistentes = db.Column(db.Integer, nullable=False)
    asistentes = db.Column(db.Text, nullable=False)  # JSON con los nombres
    pagado = db.Column(db.Boolean, default=False)
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Inscripcion {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'evento_id': self.evento_id,
            'peregrinacion_id': self.peregrinacion_id,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'num_asistentes': self.num_asistentes,
            'asistentes': json.loads(self.asistentes),
            'pagado': self.pagado,
            'fecha_inscripcion': self.fecha_inscripcion.isoformat()
        }

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    estado_civil = db.Column(db.String(20), nullable=False)
    profesion = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Registro {self.dni}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'dni': self.dni,
            'nombre': self.nombre,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat(),
            'estado_civil': self.estado_civil,
            'profesion': self.profesion,
            'direccion': self.direccion,
            'email': self.email,
            'telefono': self.telefono,
            'fecha_registro': self.fecha_registro.isoformat()
        }

class Noticia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    imagen = db.Column(db.String(200), nullable=True)
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Noticia {self.titulo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'contenido': self.contenido,
            'imagen': self.imagen,
            'fecha_publicacion': self.fecha_publicacion.isoformat()
        }

# Callback para cargar usuario
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Función para verificar extensiones permitidas
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        
        flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Rutas de API
@app.route('/api/eventos')
def api_eventos():
    eventos = Evento.query.all()
    return jsonify([evento.to_dict() for evento in eventos])

@app.route('/api/peregrinaciones')
def api_peregrinaciones():
    peregrinaciones = Peregrinacion.query.all()
    return jsonify([p.to_dict() for p in peregrinaciones])

@app.route('/api/noticias')
def api_noticias():
    noticias = Noticia.query.all()
    return jsonify([noticia.to_dict() for noticia in noticias])

@app.route('/api/inscripcion', methods=['POST'])
def api_inscripcion():
    data = request.json
    
    # Validar los datos
    if not data or not data.get('nombre') or not data.get('email') or not data.get('telefono'):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    # Crear la inscripción
    inscripcion = Inscripcion(
        evento_id=data.get('evento_id'),
        peregrinacion_id=data.get('peregrinacion_id'),
        nombre=data.get('nombre'),
        email=data.get('email'),
        telefono=data.get('telefono'),
        num_asistentes=data.get('num_asistentes', 1),
        asistentes=json.dumps(data.get('asistentes', []))
    )
    
    db.session.add(inscripcion)
    db.session.commit()
    
    # Enviar correo de confirmación
    enviar_correo_confirmacion(inscripcion)
    
    return jsonify({'success': True, 'id': inscripcion.id})

@app.route('/api/registro', methods=['POST'])
def api_registro():
    data = request.json
    
    # Validar los datos
    if not data or not data.get('dni') or not data.get('nombre') or not data.get('email'):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    # Verificar si ya existe un registro con ese DNI
    if Registro.query.filter_by(dni=data.get('dni')).first():
        return jsonify({'error': 'Ya existe un registro con ese DNI'}), 400
    
    # Crear el registro
    registro = Registro(
        dni=data.get('dni'),
        nombre=data.get('nombre'),
        fecha_nacimiento=datetime.strptime(data.get('fecha_nacimiento'), '%Y-%m-%d'),
        estado_civil=data.get('estado_civil'),
        profesion=data.get('profesion', ''),
        direccion=data.get('direccion'),
        email=data.get('email'),
        telefono=data.get('telefono')
    )
    
    db.session.add(registro)
    db.session.commit()
    
    return jsonify({'success': True, 'id': registro.id})

@app.route('/api/contacto', methods=['POST'])
def api_contacto():
    data = request.json
    
    # Validar los datos
    if not data or not data.get('nombre') or not data.get('email') or not data.get('motivo'):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    # Enviar el correo
    enviar_correo_contacto(data)
    
    return jsonify({'success': True})

# Panel de administración
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('No tienes permiso para acceder al panel de administración', 'danger')
        return redirect(url_for('index'))
    
    return render_template('admin/dashboard.html')

@app.route('/admin/eventos')
@login_required
def admin_eventos():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    eventos = Evento.query.all()
    return render_template('admin/eventos.html', eventos=eventos)

@app.route('/admin/evento/nuevo', methods=['GET', 'POST'])
@login_required
def admin_evento_nuevo():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        fecha = datetime.strptime(request.form.get('fecha'), '%Y-%m-%dT%H:%M')
        lugar = request.form.get('lugar')
        descripcion = request.form.get('descripcion')
        precio = float(request.form.get('precio'))
        
        evento = Evento(
            titulo=titulo,
            fecha=fecha,
            lugar=lugar,
            descripcion=descripcion,
            precio=precio
        )
        
        # Procesar la imagen si se ha subido
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                evento.imagen = filename
        
        db.session.add(evento)
        db.session.commit()
        
        flash('Evento creado correctamente', 'success')
        return redirect(url_for('admin_eventos'))
    
    return render_template('admin/evento_form.html')

@app.route('/admin/evento/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_evento_editar(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    evento = Evento.query.get_or_404(id)
    
    if request.method == 'POST':
        evento.titulo = request.form.get('titulo')
        evento.fecha = datetime.strptime(request.form.get('fecha'), '%Y-%m-%dT%H:%M')
        evento.lugar = request.form.get('lugar')
        evento.descripcion = request.form.get('descripcion')
        evento.precio = float(request.form.get('precio'))
        
        # Procesar la imagen si se ha subido
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                evento.imagen = filename
        
        db.session.commit()
        
        flash('Evento actualizado correctamente', 'success')
        return redirect(url_for('admin_eventos'))
    
    return render_template('admin/evento_form.html', evento=evento)

@app.route('/admin/evento/eliminar/<int:id>', methods=['POST'])
@login_required
def admin_evento_eliminar(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    evento = Evento.query.get_or_404(id)
    db.session.delete(evento)
    db.session.commit()
    
    flash('Evento eliminado correctamente', 'success')
    return redirect(url_for('admin_eventos'))

# Rutas de administración de peregrinaciones (similares a eventos)
@app.route('/admin/peregrinaciones')
@login_required
def admin_peregrinaciones():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    peregrinaciones = Peregrinacion.query.all()
    return render_template('admin/peregrinaciones.html', peregrinaciones=peregrinaciones)

@app.route('/admin/peregrinacion/nueva', methods=['GET', 'POST'])
@login_required
def admin_peregrinacion_nueva():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    # Similar a admin_evento_nuevo pero para peregrinaciones
    return render_template('admin/peregrinacion_form.html')

@app.route('/admin/peregrinacion/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_peregrinacion_editar(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    # Similar a admin_evento_editar pero para peregrinaciones
    peregrinacion = Peregrinacion.query.get_or_404(id)
    return render_template('admin/peregrinacion_form.html', peregrinacion=peregrinacion)

# Rutas de administración de noticias
@app.route('/admin/noticias')
@login_required
def admin_noticias():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    noticias = Noticia.query.all()
    return render_template('admin/noticias.html', noticias=noticias)

@app.route('/admin/noticia/nueva', methods=['GET', 'POST'])
@login_required
def admin_noticia_nueva():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    # Código para crear una nueva noticia
    return render_template('admin/noticia_form.html')

# Rutas para administrar inscripciones
@app.route('/admin/inscripciones')
@login_required
def admin_inscripciones():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    inscripciones = Inscripcion.query.all()
    return render_template('admin/inscripciones.html', inscripciones=inscripciones)

@app.route('/admin/inscripciones/evento/<int:id>')
@login_required
def admin_inscripciones_evento(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    evento = Evento.query.get_or_404(id)
    inscripciones = Inscripcion.query.filter_by(evento_id=id).all()
    return render_template('admin/inscripciones_evento.html', evento=evento, inscripciones=inscripciones)

# Rutas para administrar registros
@app.route('/admin/registros')
@login_required
def admin_registros():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    registros = Registro.query.all()
    return render_template('admin/registros.html', registros=registros)

# Exportar inscripciones a Excel
@app.route('/admin/exportar/inscripciones')
@login_required
def admin_exportar_inscripciones():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    # Código para exportar inscripciones a Excel
    # Esta funcionalidad requeriría una biblioteca como openpyxl o pandas
    # Para este ejemplo, simplemente redireccionamos
    
    flash('Exportación a Excel no implementada en esta versión', 'warning')
    return redirect(url_for('admin_inscripciones'))

# Exportar registros a Excel
@app.route('/admin/exportar/registros')
@login_required
def admin_exportar_registros():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    # Código para exportar registros a Excel
    # Esta funcionalidad requeriría una biblioteca como openpyxl o pandas
    
    flash('Exportación a Excel no implementada en esta versión', 'warning')
    return redirect(url_for('admin_registros'))

# Funciones de utilidad
def enviar_correo_confirmacion(inscripcion):
    # Configurar el correo
    msg = MIMEMultipart()
    msg['From'] = 'asociacion@torremal.org'
    msg['To'] = inscripcion.email
    
    if inscripcion.evento_id:
        evento = Evento.query.get(inscripcion.evento_id)
        msg['Subject'] = f'Confirmación de inscripción - {evento.titulo}'
        body = f"""
        Hola {inscripcion.nombre},
        
        Te confirmamos tu inscripción al evento "{evento.titulo}" que se celebrará el {evento.fecha.strftime('%d/%m/%Y')} en {evento.lugar}.
        
        Número de asistentes: {inscripcion.num_asistentes}
        
        ¡Gracias por tu interés! Nos vemos pronto.
        
        Un saludo,
        Asociación Amigos de Torreciudad en Málaga
        """
    else:
        peregrinacion = Peregrinacion.query.get(inscripcion.peregrinacion_id)
        msg['Subject'] = f'Confirmación de inscripción - {peregrinacion.titulo}'
        body = f"""
        Hola {inscripcion.nombre},
        
        Te confirmamos tu inscripción a la peregrinación "{peregrinacion.titulo}" que se celebrará el {peregrinacion.fecha.strftime('%d/%m/%Y')} en {peregrinacion.lugar}.
        
        Número de asistentes: {inscripcion.num_asistentes}
        
        ¡Gracias por tu interés! Nos vemos pronto.
        
        Un saludo,
        Asociación Amigos de Torreciudad en Málaga
        """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Configuración del servidor SMTP (esto debe ajustarse según tu proveedor)
        server = smtplib.SMTP('smtp.tudominio.com', 587)
        server.starttls()
        server.login('asociacion@torremal.org', 'tu_contraseña')
        text = msg.as_string()
        server.sendmail('asociacion@torremal.org', inscripcion.email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

def enviar_correo_contacto(data):
    # Configurar el correo
    msg = MIMEMultipart()
    msg['From'] = 'asociacion@torremal.org'
    msg['To'] = 'contacto@torremal.org'  # Correo de la asociación
    msg['Subject'] = f'Consulta: {data.get("motivo")}'
    
    body = f"""
    Nueva consulta de {data.get('nombre')}:
    
    Motivo: {data.get('motivo')}
    Descripción: {data.get('descripcion', '')}
    Teléfono: {data.get('telefono', '')}
    Email: {data.get('email')}
    
    -----------------------------
    Enviado desde el formulario de contacto de la web.
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Configuración del servidor SMTP (esto debe ajustarse según tu proveedor)
        server = smtplib.SMTP('smtp.tudominio.com', 587)
        server.starttls()
        server.login('asociacion@torremal.org', 'tu_contraseña')
        text = msg.as_string()
        server.sendmail('asociacion@torremal.org', 'contacto@torremal.org', text)
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

# Inicializar la base de datos y crear un usuario admin si no existe
@app.before_first_request
def create_tables():
    db.create_all()
    
    # Crear usuario admin si no existe
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@torremal.org',
            is_admin=True
        )
        admin.set_password('admin123')  # Cambia esta contraseña en producción
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
