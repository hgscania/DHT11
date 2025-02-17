import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def connect_serial():
    global ser, is_running, data_buffer
    port = port_var.get()
    baudrate = baudrate_var.get()
    try:
        ser = serial.Serial(port, baudrate=int(baudrate), timeout=1)
        connect_button.config(text="Disconnect", fg="red", command=disconnect_serial)
        is_running = True
        data_buffer.clear()
        ax.clear()
        canvas.draw()
        threading.Thread(target=read_serial_data, daemon=True).start()
    except Exception as e:
        status_label.config(text=f"Error: {e}")

def disconnect_serial():
    global is_running
    is_running = False
    if ser and ser.is_open:
        ser.close()
    connect_button.config(text="Connect", fg="green", command=connect_serial)

def read_serial_data():
    global ser, is_running, data_buffer
    while is_running:
        try:
            if ser.in_waiting > 0:
                data = ser.readline().decode().strip()
                if data.startswith("&") and data.endswith("&"):
                    values = data[1:-1].split(',')
                    
                    if len(values) == 2:
                        temp = float(values[0])/100
                        humidity =float(values[1])/100
                        data_buffer.append((temp, humidity))
                        if len(data_buffer) > 500:
                            data_buffer.pop(0)
                        update_plot()
                        update_labels(temp, humidity)
        except Exception as e:
            status_label.config(text=f"Error: {e}")
            disconnect_serial()

def update_plot():
    ax.clear()
    temps, hums = zip(*data_buffer) if data_buffer else ([], [])
    ax.plot(temps, label='Temperature', color='red')
    ax.plot(hums, label='Humidity', color='blue')
    ax.legend()
    ax.grid(True, linestyle="--", linewidth=0.5)
    canvas.draw()

def update_labels(temp, humidity):
    temp_label.config(text=f"Temperature: {temp:.2f} °C")
    humidity_label.config(text=f"Humidity: {humidity:.2f} %")

def exit_program():
    disconnect_serial()
    root.quit()

root = tk.Tk()
root.title("Serial Data Logger")
root.geometry("800x600")

port_var = tk.StringVar()
baudrate_var = tk.StringVar(value="115200")

tk.Label(root, text="Port:").pack()
port_menu = ttk.Combobox(root, textvariable=port_var, values=list_serial_ports())
port_menu.pack()

tk.Label(root, text="Baudrate:").pack()
baudrate_menu = ttk.Combobox(root, textvariable=baudrate_var, values=["230400", "115200", "38400", "9600"])
baudrate_menu.pack()

connect_button = tk.Button(root, text="Connect", fg="green", command=connect_serial)
connect_button.pack(pady=5)

exit_button = tk.Button(root, text="Exit", fg="red", command=exit_program)
exit_button.pack(pady=5)

temp_label = tk.Label(root, text="Temperature: -- °C")
temp_label.pack()
humidity_label = tk.Label(root, text="Humidity: -- %")
humidity_label.pack()

fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

data_buffer = []
is_running = False
ser = None

status_label = tk.Label(root, text="Status: Idle")
status_label.pack()

root.mainloop()