import string
import random
import qrcode
import os
import tkinter as tk
from tkinter import ttk
import librouteros
from librouteros.exceptions import TrapError
import webbrowser
import pdfkit

os.environ['PATH'] += ':/usr/local/bin'

def login():
    global connection  # para poder modificar la variable global

    ip = ip_entry.get()
    user = user_entry.get()
    passw = passw_entry.get()
    port = "8728"

    
    try:
        connection = librouteros.connect(

            host=ip,
            username=user,
            password=passw,
            port=port  # puerto API por defecto en Mikrotik
        )
        status_label.config(text="Conexión Exitosa", fg="green")
                # Llenar los valores de los ComboBox una vez conectado
        hotspot_names = get_hotspot_names(connection)
        user_profiles = get_user_profiles(connection)
        dns_names = get_dns_names(connection)
        
        server_ticke_combobox['values'] = hotspot_names
        profile_ticke_combobox['values'] = user_profiles
        url_ticke_combobox['values'] = dns_names
    except TrapError as e:
        status_label.config(text="Error de Conexion", fg="red")


def get_hotspot_names(connection):
    hotspots = connection(cmd='/ip/hotspot/print')
    hotspot_names = [hotspot.get('name') for hotspot in hotspots if hotspot.get('name')]
    return hotspot_names


def get_user_profiles(connection):
    try:
        profiles = connection(cmd='/ip/hotspot/user/profile/print')
        profile_list = [profile.get('name') for profile in profiles]
        return profile_list
    except librouteros.exceptions.TrapError as e:
        print("Error: ", e)


def get_dns_names(connection):
    profiles = connection(cmd='/ip/hotspot/profile/print')
    dns_names = [profile.get('dns-name') for profile in profiles if profile.get('dns-name')]
    return dns_names

def generar_tickets():
    number_ticke = int(number_ticke_entry.get())
    length_ticke = int(length_ticke_entry.get())
    time_ticke = time_ticke_entry.get()
    price_ticke = price_ticke_entry.get()
    coment_ticke = coment_ticke_entry.get()
    # Obtenemos los valores seleccionados de los combobox
    server_ticke = server_ticke_combobox.get()
    profile_ticke = profile_ticke_combobox.get()
    url_ticke = url_ticke_combobox.get()

    # Creamos la carpeta donde se guardarán los códigos QR si no existe
    if not os.path.exists('qrcodes'):
        os.makedirs('qrcodes')

    with open(f"{coment_ticke}.html", "a") as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"UTF-8\">\n<title>FdezNet Tickets</title>\n</head>\n<body>\n")
        for x in range(number_ticke):
            code = (''.join(random.SystemRandom().choice(
                string.ascii_letters + string.digits)for _ in range(length_ticke)))
            qr = qrcode.make(url_ticke+"/login?username="+code)
            qr.save(f"qrcodes/{code}.png")

            try:
                response = connection(
                    '/ip/hotspot/user/add',
                    **{
                        'server': server_ticke,
                        'name': code,
                        'limit-uptime': time_ticke,
                        'profile': profile_ticke,
                        'comment': coment_ticke
                    }
                )
                generate_label.config(text="Creado Exitosamente", fg="green")
            except TrapError as e:
                generate_label.config(text="Error al crear voucher", fg="red")
                continue

            for item in response:
                response_text.insert(tk.END, f"Exito:{profile_ticke} Creado {item}\n")


            html = f'''<div style="position: relative;width: 250px;height: 140px;background: #eee;margin: 2px;float: left;background-image: url(./img/fondo.png);background-repeat: no-repeat;background-position: center;background-size: cover;font-family: 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', 'DejaVu Sans', Verdana, 'sans-serif';font-size: 11px;font-weight: 600;padding: 0px 10px;border-radius: 10px;" class="container">
    <div style="position: relative;display: flex;align-items: center;justify-content: center;height: 30px;width: 100%;text-align: center;margin-bottom: 5px;margin-top: 5px;gap: 10px;" class="logo">
        <img src="" style="height:100%" />
        <span style="font-size: 20px; color: #fff;font-family: Verdana, Geneva, Tahoma, sans-serif;">FdezNet</span>
    </div>
    <div style="width: 74px;height: 74px;float: right;border: 1px solid #2373fd;border-radius: 10px;" class="qrcode"><img style="width: 74px;height: 74px;float: right;border: 1px solid #2373fd;border-radius: 10px;" src="./qrcodes/{code}.png" alt=""></div>
    <div style="float: left;display: flex;flex-direction: column;align-items: center;justify-content: center;gap: 7px;" class="inf">
        <div style="background: #3e99d2af;padding: 2px 5px;width: 150px;margin: 5px 2px 0 3px;border-radius: 5px;text-align: center; color: #ffffff;" class="pin"><b style="color: #fff;">PIN: </b>{code}</div>
        <div style="padding-left: 6px;font-size: 10px;width: 150px;margin-top: 5px;text-align: center;color: #00a6ff;" class="descripcion">Tiempo: <b style="color: #fff;">{coment_ticke}</b></div>
        <div style="font-size: 12px;font-weight: 600;width: 150px;margin-top: 2px;text-align: center;color: #00a6ff;" class="price">Precio: <b style="color: #fff;">${price_ticke}.00</b></div>
    </div>
    <h4 style="padding: 80px 0px;text-align: center;color: #ffffff;" class="nota">Escanea Con tu <span style="color: #00a6ff;">CAMARA</span> o en la<span style="color: #00a6ff;"> WEB</span></h4>
</div>\n'''

            f.write(html)

        f.write("</body>\n</html>")
        f.write(
            '''\n<style>\n*{margin: 0;padding: 0;box-sizing: border-box;}\n</style>''')
    webbrowser.open(f'{coment_ticke}.html')
    pdfkit.from_file(f'{coment_ticke}.html', f'{coment_ticke}.pdf', options={
        'enable-local-file-access': None,
        'no-stop-slow-scripts': None,
        'print-media-type': None,
        'background': None,
        'orientation': 'landscape',
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '1.00in',
        'margin-bottom': '0.55in',
        'margin-left': '1.25in'
    })



root = tk.Tk()
root.title("Generador de Tickets")
root.geometry("700x450")

# Crear los frames para la interfaz
login_frame = ttk.Frame(root, padding=20)
login_frame.pack(side="left", fill="y")

generate_frame = ttk.Frame(root, padding=20)
generate_frame.pack(side="right", fill="y")

# Widgets para la parte de conexión
status_label = tk.Label(login_frame, text="No Conectado", font=("Arial", 16), fg="red")
status_label.pack(pady=10)

ip_label = ttk.Label(login_frame, text="Connect IP")
ip_label.pack()
ip_entry = ttk.Entry(login_frame)
ip_entry.pack()

user_label = ttk.Label(login_frame, text="Login")
user_label.pack()
user_entry = ttk.Entry(login_frame)
user_entry.pack()

passw_label = ttk.Label(login_frame, text="Password")
passw_label.pack()
passw_entry = ttk.Entry(login_frame)
passw_entry.pack()

button = ttk.Button(login_frame, text="Connect", command=login)
button.pack(pady=10)


response_text = tk.Text(login_frame, height=10, width=40)
response_text.pack()




# Widgets para la parte de generación de tickets
number_ticke_label = ttk.Label(generate_frame, text="Cantidad de Tickets")
number_ticke_label.pack()
number_ticke_entry = ttk.Entry(generate_frame)
number_ticke_entry.pack()

server_ticke_label = ttk.Label(generate_frame, text="Servidor Hotspot")
server_ticke_label.pack()
server_ticke_combobox = ttk.Combobox(generate_frame)
server_ticke_combobox.pack()

url_ticke_label = ttk.Label(generate_frame, text="URL del DNS")
url_ticke_label.pack()
url_ticke_combobox = ttk.Combobox(generate_frame)
url_ticke_combobox.pack()

profile_ticke_label = ttk.Label(generate_frame, text="Perfil de usuario")
profile_ticke_label.pack()
profile_ticke_combobox = ttk.Combobox(generate_frame)
profile_ticke_combobox.pack()

length_ticke_label = ttk.Label(generate_frame, text="Longitud del PIN")
length_ticke_label.pack()
length_ticke_entry = ttk.Entry(generate_frame)
length_ticke_entry.pack()



time_ticke_label = ttk.Label(generate_frame, text="Tiempo : hrs:min:seg")
time_ticke_label.pack()
time_ticke_entry = ttk.Entry(generate_frame)
time_ticke_entry.pack()

coment_ticke_label = ttk.Label(generate_frame, text="Comentario : 30-MIN")
coment_ticke_label.pack()
coment_ticke_entry = ttk.Entry(generate_frame)
coment_ticke_entry.pack()

price_ticke_label = ttk.Label(generate_frame, text="Precio del ticket")
price_ticke_label.pack()
price_ticke_entry = ttk.Entry(generate_frame)
price_ticke_entry.pack()

button = ttk.Button(generate_frame, text="Generar", command=generar_tickets)
button.pack(pady=10)

generate_label = tk.Label(
    generate_frame, text="Gracias por Usar FdezTicket", font=("Arial", 16), fg="red")
generate_label.pack(pady=10)

root.mainloop()
 