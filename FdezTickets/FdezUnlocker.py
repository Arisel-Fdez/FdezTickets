from tkinter import ttk
import netmiko
import tkinter as tk
from tkinter import messagebox
import librouteros
from librouteros.exceptions import TrapError

def login_netmiko():
    global connection

    ip = ip_entry.get()
    user = user_entry.get()
    passw = passw_entry.get()
    port = 22

    mikrotik = {
        'device_type': 'mikrotik_routeros',
        'ip': ip,
        'username': user,
        'password': passw,
        'port': port
    }

    try:
        connection = netmiko.ConnectHandler(**mikrotik)
        status_label.config(text="Conexión Exitosa", fg="green")
        print("conexion Netmiko")
    except Exception as e:
        status_label.config(text="Error de Conexion Netmiko", fg="red")


def login_librouteros():
    global conexion

    ip = ip_entry.get()
    user = user_entry.get()
    passw = passw_entry.get()
    port = "8728"

    try:
        conexion = librouteros.connect(
            host=ip,
            username=user,
            password=passw,
            port=port
        )
        status_label.config(text="Conexión Exitosa", fg="green")
        print("conexion Routeros")
    except TrapError as e:
        status_label.config(text="Error de Conexion Librouteros", fg="red")


def login_all():
    login_netmiko()
    login_librouteros()


def view_user():
    # Limpiar Treeview
    for i in tree.get_children():
        tree.delete(i)

    response = conexion(cmd='/ip/dhcp-server/lease/print')
    bound_items = []
    waiting_items = []

    for item in response:
        hostname = item.get('host-name', '').ljust(15)  # Ajusta la longitud de la cadena a 20
        ip_address = item.get('address', '').ljust(15)  # Ajusta la longitud de la cadena a 15
        status = item.get('status', '').ljust(15)  # Ajusta la longitud de la cadena a 10
        block_access = str(item.get('block-access', 'false')).ljust(10)  # Convertir a cadena y ajustar la longitud a 10
        comment = item.get('comment', '').ljust(15)  # Ajusta la longitud de la cadena a 20

        display_tuple = (hostname, ip_address, status, block_access, comment)

        if status.strip() == 'waiting':
            waiting_items.append(display_tuple)
        else:
            bound_items.append(display_tuple)

    for bound_item in bound_items:
        tree.insert('', tk.END, values=bound_item)

    tree.insert('', tk.END, values=("----User Bloqueado-----", "", "", "", ""))

    for waiting_item in waiting_items:
        tree.insert('', tk.END, values=waiting_item)



def block_user():
    selected_item = tree.item(tree.focus())["values"]
    ip_address = selected_item[1].strip()  # Get IP address

    try:
        command = f"/ip dhcp-server lease set [find address={ip_address}] block-access=yes"
        connection.send_command(command)
        messagebox.showinfo("Bloquear Usuario", f"Usuario con IP {ip_address} bloqueado exitosamente.")
        view_user()
    except Exception as e:
        messagebox.showerror("Error", f"Error al bloquear la IP {ip_address}: {str(e)}")


def unblock_user():
    selected_item = tree.item(tree.focus())["values"]
    ip_address = selected_item[1].strip()  # Get IP address
    try:
        command = f"/ip dhcp-server lease set [find address={ip_address}] block-access=no"
        connection.send_command(command)
        messagebox.showinfo("Desbloquear Usuario", f"Usuario con IP {ip_address} desbloqueado exitosamente.")
        view_user()
    except Exception as e:
        messagebox.showerror("Error", f"Error al desbloquear la IP {ip_address}: {str(e)}")




root = tk.Tk()
root.title("FdezNetUnlocker")
root.geometry("1200x600")  # Cambiar a la altura deseada

login_frame = ttk.Frame(root, padding=20)
login_frame.pack(side="left", fill="y")

lock_frame = ttk.Frame(root, padding=20)
lock_frame.pack(side="right", fill="y")

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

button = ttk.Button(login_frame, text="Connect", command=login_all)
button.pack(pady=10)

# Crear el treeview
tree = ttk.Treeview(root, columns=('User', 'IP', 'Conexion', 'Bloqueado', 'Comment'), show='headings')

# Definir los encabezados
tree.heading('User', text='User')
tree.heading('IP', text='IP')
tree.heading('Conexion', text='Conexion')
tree.heading('Bloqueado', text='Bloqueado')
tree.heading('Comment', text='Comment')

# Ajustar el ancho de las columnas
tree.column('User', width=150)
tree.column('IP', width=150)
tree.column('Conexion', width=150)
tree.column('Bloqueado', width=150)
tree.column('Comment', width=150)


tree.pack(fill=tk.BOTH, expand=True)

tree.bind('<<TreeviewSelect>>')

button = ttk.Button(lock_frame, text="Salir", command=root.quit)
button.pack(pady=10)

button = ttk.Button(lock_frame, text="Bloquear", command=block_user)
button.pack(pady=10)

button = ttk.Button(lock_frame, text="Desbloquear", command=unblock_user)
button.pack(pady=10)

button = ttk.Button(lock_frame, text="Actualizar", command=view_user)
button.pack(pady=10)

root.mainloop()
