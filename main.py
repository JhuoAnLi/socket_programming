import socket
import tkinter as tk
from tkinter import messagebox
import threading
import select
import datetime
import time

client_credentials = {"username": "", "password": ""}
admin_message_history = []
amy_message_history = []
bob_message_history = []


# Server code
def server():
    host = ""
    port = 12343
    print("Server started!")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    while True:
        readable, _, _ = select.select([server_socket], [], [], 0.1)
        for s in readable:
            if s is server_socket:
                c, addr = server_socket.accept()
                new_thread = threading.Thread(
                    target=handle_client, args=(c,)
                )  # create new thread for client
                new_thread.start()


def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break

        if data == b"hello":
            response = "Hi! What's your name?"
        else:
            response = "Hello, " + str(data.decode("ascii")) + "!"
        current_time = datetime.datetime.now().strftime("%m-%d %H:%M:%S")
        if client_credentials["username"] == "admin":
            admin_message_history.append(
                current_time + "\t\t" + "server" + " : " + response
            )
        elif client_credentials["username"] == "amy":
            amy_message_history.append(
                current_time + "\t\t" + "server" + " : " + response
            )
        elif client_credentials["username"] == "bob":
            bob_message_history.append(
                current_time + "\t\t" + "server" + " : " + response
            )
        update_message_history()
        client_socket.send(response.encode("ascii"))
    client_socket.close()


# Client code
def client(message):
    host = "127.0.0.1"
    port = 12343
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(False)
    try:
        s.connect((host, port))
    except BlockingIOError:
        pass
    counter = 0
    max_iterations = 5
    while True:
        readable, _, _ = select.select([s], [], [], 0.1)
        if not readable:
            print("No new connections during this interval.")
            time.sleep(1) 
            counter += 1
        if counter >= max_iterations:
            break
        else:
            for sock in readable:
                if sock is s:
                    try:
                        data = s.recv(1024)
                        if not data:
                            s.close()
                            print("Connection closed")
                            return
                        return
                    except ConnectionResetError:
                        s.close()
                        print("Connection reset")
                        return
            try:
                s.send(message.encode("ascii"))
            except BrokenPipeError:
                s.close()
                print("Broken pipe")
                return


# Function to send message from GUI input
def send_message():
    message = message_entry.get()
    current_time = datetime.datetime.now().strftime("%m-%d %H:%M:%S")
    if message:
        if client_credentials["username"] == "admin":
            admin_message_history.append(
                current_time + "\t\t" + "admin" + " : " + message
            )
        elif client_credentials["username"] == "amy":
            amy_message_history.append(current_time + "\t\t" + "amy" + " : " + message)
        elif client_credentials["username"] == "bob":
            bob_message_history.append(current_time + "\t\t" + "bob" + " : " + message)
        update_message_history()
        # update_message_history(client_credentials["username"] + ": " + message)
        threading.Thread(target=client, args=(message,)).start()
        message_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Please enter a message!")


# Function to handle login window
def login():
    login_window = tk.Toplevel(root)
    login_window.title("Login")

    username_label = tk.Label(login_window, text="Username:")
    username_label.pack(pady=10)
    username_entry = tk.Entry(login_window, width=30)
    username_entry.pack(pady=5)

    password_label = tk.Label(login_window, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(login_window, width=30, show="*")
    password_entry.pack(pady=10)

    def authenticate():
        username = username_entry.get()
        password = password_entry.get()

        if (
            (username == "admin" and password == "admin")
            or (username == "amy" and password == "amy")
            or (username == "bob" and password == "bob")
        ):
            print("Login successful!")
            message_history_text.delete(1.0, tk.END)
            client_credentials["username"] = username
            client_credentials["password"] = password
            login_window.destroy()
            send_message_button.config(state="normal")
            message_history_text.config(state="normal")
            message_history_text.delete(1.0, tk.END)
            message_history_text.config(state="disabled")
        else:
            messagebox.showerror(
                "Authentication Error", "Invalid username or password."
            )

    login_button = tk.Button(login_window, text="Login", command=authenticate)
    login_button.pack()


# Function to update message history
# def update_message_history(message):
#     message_history_text.config(state="normal")
#     message_history_text.insert(tk.END, f"{message}\n")
#     message_history_text.config(state="disabled")
def update_message_history():
    message_history_text.config(state="normal")
    current_user_message_history = []
    if client_credentials["username"] == "admin":
        current_user_message_history = admin_message_history
    elif client_credentials["username"] == "amy":
        current_user_message_history = amy_message_history
    elif client_credentials["username"] == "bob":
        current_user_message_history = bob_message_history

    message_history_text.delete(1.0, tk.END)
    for message in current_user_message_history:
        message_history_text.insert(tk.END, f"{message}\n")

    message_history_text.config(state="disabled")


# Create Tkinter GUI
root = tk.Tk()
root.title("110403516 Socket Programming")

frame = tk.Frame(root)
frame.pack(pady=50)

message_label = tk.Label(frame, text="Enter a message:")
message_label.grid(row=0, column=0, padx=10)

message_entry = tk.Entry(frame, width=30)
message_entry.grid(row=0, column=1, padx=10)

send_message_button = tk.Button(
    frame, text="Send Message", command=send_message, state="disabled"
)
send_message_button.grid(row=0, column=2, padx=10)

start_server_button = tk.Button(
    frame, text="Start Server", command=lambda: threading.Thread(target=server).start()
)
start_server_button.grid(row=1, column=0, padx=10)

login_button = tk.Button(frame, text="Login", command=login)
login_button.grid(row=1, column=1, padx=10)

# Create a multi-line text widget for message history
message_history_text = tk.Text(frame, state="disabled", wrap=tk.WORD)
message_history_text.grid(row=2, columnspan=3, padx=10, pady=10, sticky="nsew")
scrollbar = tk.Scrollbar(frame, command=message_history_text.yview)
scrollbar.grid(row=2, column=3, sticky="ns")
message_history_text.config(yscrollcommand=scrollbar.set)

root.mainloop()
