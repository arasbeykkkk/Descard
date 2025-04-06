import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import random

# Ayarlar
HOST = '127.0.0.1'
PORT = 55555

clients = {}  # {client: (username, avatar, color, group)}
groups = {"Genel": []}  # grup adı -> client listesi

avatars = ['👾', '🐉', '🦊', '🦁', '🐼', '🐧', '🐸', '👽', '🐺']
colors = ['blue', 'green', 'purple', 'orange', 'brown', 'red', 'teal', 'black']

# === SUNUCU ===
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    def broadcast(msg, group):
        for c in groups[group]:
            try:
                c.send(msg.encode('utf-8'))
            except:
                pass

    def handle(client):
        while True:
            try:
                data = client.recv(1024).decode('utf-8')
                if data.startswith("MSG:"):
                    msg = data[4:]
                    username, avatar, color, group = clients[client]
                    formatted = f"[{avatar} {username}]: {msg}"
                    broadcast(f"<{color}>{formatted}", group)
            except:
                if client in clients:
                    username, _, _, group = clients[client]
                    groups[group].remove(client)
                    broadcast(f"<red>{username} sohbetten ayrıldı.", group)
                    del clients[client]
                    client.close()
                break

    def accept_connections():
        while True:
            client, _ = server.accept()
            init_data = client.recv(1024).decode('utf-8')
            username, avatar, color, group = init_data.split("||")

            clients[client] = (username, avatar, color, group)
            if group not in groups:
                groups[group] = []
            groups[group].append(client)

            broadcast(f"<green>{username} gruba katıldı: {group}", group)
            threading.Thread(target=handle, args=(client,), daemon=True).start()

    threading.Thread(target=accept_connections, daemon=True).start()

# === İSTEMCİ ===
def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except:
        messagebox.showerror("Bağlantı Hatası", "Sunucuya bağlanılamadı.")
        return

    # === GİRİŞ EKRANI ===
    login = tk.Tk()
    login.title("Descard Giriş")

    tk.Label(login, text="Kullanıcı Adı:").pack()
    username_entry = tk.Entry(login)
    username_entry.pack()

    tk.Label(login, text="Avatar (emoji):").pack()
    avatar_var = tk.StringVar(value=random.choice(avatars))
    avatar_menu = tk.OptionMenu(login, avatar_var, *avatars)
    avatar_menu.pack()

    tk.Label(login, text="Grup Adı (örn: Genel, Arkadaşlar):").pack()
    group_entry = tk.Entry(login)
    group_entry.insert(0, "Genel")
    group_entry.pack()

    def proceed():
        username = username_entry.get()
        avatar = avatar_var.get()
        group = group_entry.get()

        if not username.strip():
            messagebox.showerror("Hata", "Kullanıcı adı gerekli.")
            return
        login.destroy()
        color = random.choice(colors)
        init_data = f"{username}||{avatar}||{color}||{group}"
        client.send(init_data.encode('utf-8'))

        # === CHAT PENCERESİ ===
        root = tk.Tk()
        root.title(f"Descard - {username} @ {group}")

        chat_area = scrolledtext.ScrolledText(root, height=20, width=60)
        chat_area.pack(padx=10, pady=10)
        chat_area.config(state='disabled')

        entry = tk.Entry(root)
        entry.pack(padx=10, pady=5, fill='x')

        def send_msg(event=None):
            msg = entry.get()
            if msg.strip():
                client.send(f"MSG:{msg}".encode('utf-8'))
                entry.delete(0, tk.END)

        def receive_msg():
            while True:
                try:
                    raw = client.recv(1024).decode('utf-8')
                    if raw.startswith("<"):
                        color_end = raw.find(">")
                        color = raw[1:color_end]
                        msg = raw[color_end+1:]

                        chat_area.config(state='normal')
                        chat_area.insert(tk.END, msg + "\n", color)
                        chat_area.tag_config(color, foreground=color)
                        chat_area.yview(tk.END)
                        chat_area.config(state='disabled')
                except:
                    break

        entry.bind("<Return>", send_msg)
        tk.Button(root, text="Gönder", command=send_msg).pack(pady=5)

        threading.Thread(target=receive_msg, daemon=True).start()
        root.mainloop()

    tk.Button(login, text="Sohbete Gir", command=proceed).pack(pady=10)
    login.mainloop()

# === BAŞLAT ===
if __name__ == "__main__":
    start_server()
    start_client()
