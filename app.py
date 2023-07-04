from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from config import config
import time
from flask_login import LoginManager,login_user,logout_user,login_required

#Models
from src.ModelUser import ModelUser

#Entities
from src.entities.User import User

app = Flask(__name__)

csrf = CSRFProtect()

#Mysql connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'process'
mysql = MySQL(app)

login_manager_app=LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(mysql,id)

#Settings
app.secret_key='mysecretkey'

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/perfil")
@login_required
def Perfil():
    return render_template("perfil.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method=="POST":
       user = User(0,request.form['username'], request.form['password'])
       logged_user =ModelUser.login(mysql, user)
       if logged_user != None:
        if logged_user.password:
            login_user(logged_user)
            return redirect(url_for('Perfil'))
        else:
            flash("Invalid Password...")
            return render_template('login.html')
       else:
        flash("User not found...")
        return render_template("login.html")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/protected")
@login_required
def protected():
    return "<h1>Esta es una vista protegida, solo para usuarios autenticados<h1>"

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Página no encontrada<h1>"

@app.route("/page")
@login_required
def Page():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM procesotabla')
    data = cur.fetchall()
    print(data)
    return render_template("index.html", procesos = data)


@app.route('/add_process', methods=['POST'])
def add_process():
    if request.method == 'POST':
        tarjeta = request.form['tarjeta']
        trabajador = request.form['trabajador']
        proceso = request.form['proceso']
        subproceso = request.form['subproceso']
        modelo = request.form['modelo']
        material = request.form['material']
        color = request.form['color']
        cantidad = request.form['cantidad']
        precio = request.form['precio']
        total = request.form['total']
        
        cur= mysql.connection.cursor()

        # Verificar si existe un proceso con los mismos valores de tarjeta, modelo, proceso y subproceso
        cur.execute('SELECT * FROM procesotabla WHERE tarjeta = %s AND modelo = %s AND proceso = %s AND subproceso = %s', (tarjeta, modelo, proceso, subproceso))
        existing_process = cur.fetchone()
        
        if existing_process:
            flash('Ya existe un proceso con la misma tarjeta, modelo, proceso y subproceso.')

            # Guardar los datos repetidos en la tabla procesos_repetidos
            cur.execute('INSERT INTO procesorepetidotabla (tarjetarep, trabajadorrep, procesorep, subprocesorep, modelorep, materialrep, colorrep, cantidadrep, preciorep, totalrep) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (tarjeta, trabajador, proceso, subproceso, modelo, material, color, cantidad, precio, total))
            mysql.connection.commit()

            return redirect(url_for('Page'))

        cur.execute('INSERT INTO procesotabla (tarjeta, trabajador, proceso, subproceso, modelo, material, color, cantidad, precio, total) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    (tarjeta, trabajador, proceso, subproceso, modelo, material, color, cantidad, precio, total)) 
        mysql.connection.commit()
        flash('Proceso Agregado Satisfactoriamente')
        return redirect(url_for('Page'))
    
@app.route('/repeated_process_data')
def repeated_process_data():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM procesorepetidotabla')
    data = cur.fetchall()
    return render_template('repeated_process_data.html', procesos=data)



@app.route('/edit_process/<id>')
def get_process(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM procesotabla WHERE id = %s', (id,))
    data = cur.fetchall()
    return render_template('edit-process.html', procesos = data[0])

@app.route('/update_process/<id>', methods =['POST'])
def update_process(id):
    if request.method == 'POST':
        tarjeta = request.form['tarjeta']
        trabajador = request.form['trabajador']
        proceso = request.form['proceso']
        subproceso = request.form['subproceso']
        modelo = request.form['modelo']
        material = request.form['material']
        color = request.form['color']
        cantidad = request.form['cantidad']
        precio = request.form['precio']
        total = request.form['total']
        cur= mysql.connection.cursor()
        cur.execute("""UPDATE procesotabla 
        SET tarjeta= %s, 
            trabajador = %s, 
            proceso = %s, 
            subproceso = %s,
            modelo = %s,
            material = %s,
            color = %s,
            cantidad = %s,
            precio = %s,
            total = %s
            WHERE id=%s
            """, (tarjeta, trabajador, proceso, subproceso, modelo, material, color, cantidad, precio, total, id))
        mysql.connection.commit()
        flash('Process Updated Successfully')
        return redirect(url_for('Page'))


@app.route('/delete_process/<string:id>')
def delete_process(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM procesotabla WHERE id= {0}'.format(id))
    mysql.connection.commit()
    flash('Proceso removido correctamente')
    return redirect(url_for('Page'))

@app.route('/delete_process_repeated/<string:id>')
def delete_process_repeated(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM procesorepetidotabla WHERE idrep= {0}'.format(id))
    mysql.connection.commit()
    flash('Proceso removido correctamente')
    return redirect(url_for('repeated_process_data'))

@app.route("/buscar", methods=['GET', 'POST'])
@login_required
def buscador():
    if request.method == "POST":
        search_query = request.form['search_query']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM procesotabla WHERE tarjeta = %s OR trabajador LIKE %s", (search_query, '%' + search_query + '%'))
        data = cur.fetchall()
        return render_template("busqueda.html", procesos=data, search_query=search_query)
    else:
        return render_template("busqueda.html")

@app.route("/trabajadores")
def trabajadores():
    cur = mysql.connection.cursor()
    cur.execute('SELECT DISTINCT trabajador FROM procesotabla')
    trabajadores = cur.fetchall()  # Obtener la lista de trabajadores
    trabajador_procesos = []  # Lista para almacenar los trabajadores y sus procesos

    for trabajador in trabajadores:
        cur.execute('SELECT * FROM procesotabla WHERE trabajador = %s', (trabajador[0],))
        procesos = cur.fetchall()  # Obtener los procesos del trabajador
        trabajador_procesos.append((trabajador[0], procesos))

    return render_template("trabajadores.html", trabajador_procesos=trabajador_procesos)


@app.route('/eliminar_datos_tabla', methods=['GET'])
def eliminar_datos_tabla():
    cur = mysql.connection.cursor()
    cur.execute('TRUNCATE TABLE procesotabla')
    mysql.connection.commit()
    flash('Los datos de la tabla se han eliminado.')
    return redirect(url_for('Page'))




if __name__ == '__main__':
    app.config.from_object(config['development'])
   #csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=True, port=4000)
    
    print(Flask.__version__) 