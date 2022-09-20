from asyncio.windows_events import NULL
from operator import truediv
from os import curdir
import os
from flask import Flask
from flask import render_template, request, redirect, session
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory

app=Flask(__name__)
app.secret_key="llave"
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sitio'
mysql.init_app(app)

@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@app.route('/img/<imagen>')
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img/'),imagen)

@app.route("/css/<archivocss>")
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css/'),archivocss)

@app.route('/registro')
def user_registro():
    return render_template('sitio/registro.html')

@app.route('/registro',methods=['POST'])
def user_registrar_nuevo():

    _nombre = request.form['txtNombre']
    _usuario = request.form['txtUsuario']
    _email = request.form['txtEmail']
    _telefono = request.form['txtTelefono']
    _password1 = request.form['txtPassword']
    _password2 = request.form['txtPassword2']

    tiempo = datetime.now()
    horaActual1=tiempo.strftime('%X %x')

    sql="INSERT INTO `usuariosfinales` (`user`, `nombre`, `email`, `telefono`, `password`, `fecha`) VALUES (%s, %s, %s, %s, %s, %s);"
    datos=(_usuario,_nombre,_email,_telefono,_password1,horaActual1)

    conexion = mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()

    return redirect("/user/login")

@app.route('/user/')
def user_index():
    if not 'loginF' in session:
        return redirect("/user/login")
    return render_template('user/index.html')

@app.route('/user/login')
def user_login():
    if 'loginF' in session:
        return redirect("/user")
    return render_template('user/login.html')

@app.route('/user/login', methods=['POST'])
def user_login_post():
    _email=request.form['txtUsuario']
    _password=request.form['txtPassword']

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT password FROM `usuariosfinales` WHERE email=%s",_email)
    password=cursor.fetchall()
    conexion.commit()

    if cursor.rowcount !=0 :
        if _password == password[0][0]:
            session["loginF"]=True
            session["usuarioF"]=_email
            return redirect("/user")

    return render_template('user/login.html', mensaje="Acceso denegado:")

@app.route('/user/cerrar')
def user_login_cerrar():
    session.clear()
    return redirect('/user/login')


@app.route('/user/posts')
def verPosts():
    if not 'loginF' in session:
        return redirect("/user/login")
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `posts`")
    posts=cursor.fetchall()
    conexion.commit()

    return render_template('user/posts.html', posts=posts)

@app.route('/user/crearPost')
def user_crearPost():
    if not 'loginF' in session:
        return redirect("/user/login")
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `posts`")
    posts=cursor.fetchall()
    conexion.commit()

    return render_template('user/crearPost.html', posts=posts)

@app.route('/user/post/guardar',methods=['POST'])
def user_post_guardar():

    if not 'loginF' in session:
        return redirect("/user/login")

    _usuario = session["usuarioF"]
    _descripcion = request.form['txtDescripcion']
    _archivo = request.files['txtImagen']

    tiempo = datetime.now()
    horaActual=tiempo.strftime('%Y%m%d%H%M')
    horaActual2=tiempo.strftime('%X %x')

    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_usuario +".jpg"
        _archivo.save("templates/user/img/"+nuevoNombre)

    sql="INSERT INTO `posts` (`id`, `imagen`, `descripcion`, `fecha`) VALUES (NULL, %s, %s, %s);"
    datos=(nuevoNombre,_descripcion,horaActual2)

    conexion = mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()

    return redirect('/user/posts')

@app.route('/user/img/<imagen>')
def user_imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/user/img/'),imagen)

@app.route('/admin/')
def admin_index():
    if not 'loginA' in session:
        return redirect("/admin/login")
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    if 'loginA' in session:
        return redirect("/admin")
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT password FROM `usuariosadmin` WHERE usuario=%s",_usuario)
    password=cursor.fetchall()
    conexion.commit()

    if cursor.rowcount !=0 :
        if _password == password[0][0]:
            session["loginA"]=True
            session["usuarioA"]=_usuario
            return redirect("/admin")

    return render_template('admin/login.html', mensaje="Acceso denegado:")


@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login')


@app.route('/admin/habitaciones')
def admin_habitaciones():
    if not 'loginA' in session:
        return redirect("/admin/login")
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `habitaciones`")
    habitaciones=cursor.fetchall()
    conexion.commit()

    return render_template('admin/habitaciones.html', habitaciones=habitaciones)

@app.route('/admin/habitaciones/guardar',methods=['POST'])
def admin_habitaciones_guardar():

    if not 'loginA' in session:
        return redirect("/admin/login")

    _nombre = request.form['txtNombre']
    _descripcion = request.form['txtDescripcion']
    _archivo = request.files['txtImagen']

    tiempo = datetime.now()
    horaActual=tiempo.strftime('%Y%H%M%S')

    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        _archivo.save("templates/sitio/img/"+nuevoNombre)

    sql="INSERT INTO `habitaciones` (`id`, `nombre`, `imagen`, `descripcion`) VALUES (NULL, %s, %s, %s);"
    datos=(_nombre,nuevoNombre,_descripcion)

    conexion = mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()

    return redirect('/admin/habitaciones')

@app.route('/admin/habitaciones/borrar',methods=['POST'])
def admin_habitaciones_borrar():

    if not 'loginA' in session:
        return redirect("/admin/login")

    _id=request.form['txtID']

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT imagen FROM `habitaciones` WHERE id=%s",_id)
    habitacion=cursor.fetchall()
    conexion.commit()

    if os.path.exists("templates/sitio/img/"+str(habitacion[0][0])):
        os.unlink("templates/sitio/img/"+str(habitacion[0][0]))

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("DELETE FROM `habitaciones` WHERE id=%s",_id)
    conexion.commit()

    return redirect('/admin/habitaciones')



if __name__=='__main__':
    app.run(debug=True)
