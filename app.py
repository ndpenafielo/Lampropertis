from asyncio.windows_events import NULL
from operator import truediv
from os import curdir
import os
from flask import Flask
from flask import render_template, request, redirect, session
from datetime import datetime
from flask import send_from_directory
import sqlite3


app=Flask(__name__)
app.secret_key="llave"
con = sqlite3.connect('templates/db/sitio.db', check_same_thread=False)

#    Directorios de imagenes

@app.route('/img/<imagen>')
def imagenes(imagen):
    return send_from_directory(os.path.join('templates/sitio/img/'),imagen)

@app.route('/user/userPosts/<usuario>/<imagen>')
def user_imagenes(usuario,imagen):
    directorio = usuario+"/"+imagen
    return send_from_directory(os.path.join('templates/user/userPosts/'),directorio)

#    Directorios de archivos CSS

@app.route("/sitio/css/<archivocss>")
def sitio_css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css/'),archivocss)

@app.route("/user/css/<archivocss>")
def user_css_link(archivocss):
    return send_from_directory(os.path.join('templates/user/css/'),archivocss)

#    Directorios de sitio

@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

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

    directorio = "templates/user/userPosts/"+_usuario
    if not os.path.exists(directorio):
        os.makedirs(directorio)

    tiempo = datetime.now()
    horaActual1=tiempo.strftime('%X %x')

    sql='''INSERT INTO usuariosfinales (user, nombre, email, telefono, password, fecha) VALUES (?, ?, ?, ?, ?, ?)'''
    datos=(_usuario,_nombre,_email,_telefono,_password1,horaActual1)

    cursor=con.cursor()
    cursor.execute(sql,datos)
    con.commit()

    return redirect("/user/login")

#    Directorios de usuario

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

    sql="SELECT password,user FROM usuariosfinales WHERE email=?"
    cursor=con.cursor()
    cursor.execute(sql,(_email,))
    usuario=cursor.fetchall()

    if usuario:
        if _password == usuario[0][0]:
            session["loginF"]=True
            session["usuarioF"]=usuario[0][1]
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

    sql="SELECT * FROM posts WHERE user=?"
    cursor=con.cursor()
    cursor.execute(sql,(session["usuarioF"],))
    posts=cursor.fetchall()

    return render_template('user/posts.html', posts=posts)

@app.route('/user/crearPost')
def user_crearPost():
    if not 'loginF' in session:
        return redirect("/user/login")
    return render_template('user/crearPost.html')

@app.route('/user/post/guardar',methods=['POST'])
def user_post_guardar():

    if not 'loginF' in session:
        return redirect("/user/login")

    _usuario = session["usuarioF"]
    _descripcion = request.form['txtDescripcion']
    _archivo = request.files['txtImagen']

    tiempo = datetime.now()
    horaActual=tiempo.strftime('%Y%m%d%H%M%S')
    horaActual2=tiempo.strftime('%X %x')

    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_usuario +".jpg"
        _archivo.save("templates/user/userPosts/" +_usuario +"/" + nuevoNombre)


    sql='''INSERT INTO posts (id, imagen, descripcion, fecha, user) VALUES (NULL,?, ?, ?, ?)'''
    datos=(nuevoNombre,_descripcion,horaActual2, _usuario)

    cursor=con.cursor()
    cursor.execute(sql,datos)
    con.commit()

    return redirect('/user/posts')

@app.route('/user/post/borrar',methods=['POST'])
def user_post_borrar():

    if not 'loginF' in session:
        return redirect("/user/login")
    _id=request.form['txtID']

    sql="SELECT imagen,user FROM posts WHERE id=?"
    cursor=con.cursor()
    cursor.execute(sql,(_id,))
    posts=cursor.fetchall()

    if os.path.exists("templates/user/userPosts/"+str(posts[0][1])+"/"+str(posts[0][0])):
        os.unlink("templates/user/userPosts/"+str(posts[0][1])+"/"+str(posts[0][0]))


    sql="DELETE FROM posts WHERE id=?"
    cursor=con.cursor()
    cursor.execute(sql,(_id,))
    con.commit()

    return redirect('/user/posts')

#   Directorio de Admin

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

    sql="SELECT password FROM usuariosadmin WHERE usuario=?"
    cursor=con.cursor()
    cursor.execute(sql,(_usuario,))
    password=cursor.fetchall()

    if password:
        if _password == password[0][0]:
            session["loginA"]=True
            session["usuarioA"]=_usuario
            return redirect("/admin")

    return render_template('admin/login.html', mensaje="Acceso denegado:")


@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login')


@app.route('/admin/usuariosFinales')
def admin_usuarios_finales():
    if not 'loginA' in session:
        return redirect("/admin/login")

    sql="SELECT * FROM usuariosfinales"
    cursor=con.cursor()
    cursor.execute(sql)
    usuarios=cursor.fetchall()

    return render_template('admin/usuariosFinales.html', usuarios=usuarios)

@app.route('/admin/usuariosFinales/agregar',methods=['POST'])
def admin_usuariosFinales_guardar():

    if not 'loginA' in session:
        return redirect("/admin/login")

    _usuario = request.form['txtUsuario']
    _nombre = request.form['txtNombre']
    _password = request.form['txtPassword']
    _correo = request.form['txtCorreo']
    _telefono = request.form['txtTelefono']

    tiempo = datetime.now()
    _fecha=tiempo.strftime('%X %x')

    directorio = "templates/user/userPosts/"+_usuario
    if not os.path.exists(directorio):
        os.makedirs(directorio)

    tiempo = datetime.now()
    horaActual=tiempo.strftime('%X %x')

    sql='''INSERT INTO usuariosfinales (user, nombre, email, telefono, password, fecha) VALUES (?, ?, ?, ?, ?, ?)'''
    datos=(_usuario,_nombre,_correo,_telefono,_password,horaActual)

    cursor=con.cursor()
    cursor.execute(sql,datos)
    con.commit()

    return redirect('/admin/usuariosFinales')

@app.route('/admin/usuariosFinales/borrar',methods=['POST'])
def admin_usuariosfinales_borrar():

    if not 'loginA' in session:
        return redirect("/admin/login")

    _user=request.form['txtUser']

    """ para borrar carpeta donde guardan post, marca permiso denegado
    if os.path.exists("templates/user/userPosts/"+_user):
        os.unlink("templates/user/userPosts/"+_user)
    """

    sql="DELETE FROM usuariosfinales WHERE user=?"
    cursor=con.cursor()
    cursor.execute(sql,(_user,))
    con.commit()

    return redirect('/admin/usuariosFinales')


@app.route('/admin/usuariosFinales/buscar',methods=['POST'])
def admin_usuariosfinales_buscar():

    if not 'loginA' in session:
        return redirect("/admin/login")

    _user=request.form['txtBuscar']

    sql="SELECT * FROM usuariosfinales WHERE user=?"
    cursor=con.cursor()
    cursor.execute(sql,(_user,))
    usuarios=cursor.fetchall()

    return render_template('admin/usuariosFinales.html', usuarios=usuarios)

@app.route('/admin/posts')
def admin_posts():
    if not 'loginA' in session:
        return redirect("/admin/login")

    sql="SELECT * FROM posts"
    cursor=con.cursor()
    cursor.execute(sql)
    posts=cursor.fetchall()

    return render_template('admin/posts.html', posts=posts)

@app.route('/admin/posts/buscar',methods=['POST'])
def admin_posts_buscar():

    if not 'loginA' in session:
        return redirect("/admin/login")

    _user=request.form['txtBuscar']

    sql="SELECT * FROM posts WHERE user=?"
    cursor=con.cursor()
    cursor.execute(sql,(_user,))
    posts=cursor.fetchall()

    return render_template('admin/posts.html', posts=posts)


if __name__=='__main__':
    app.run(debug=True)
