import socket
import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser, Menu, Toplevel, simpledialog
from tkinter.scrolledtext import ScrolledText

class KomutEkrani(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.buttons = {}
        self.button_commands = {}
        self.init_ui()

    def init_ui(self):
        self.add_button = tk.Button(self, text="Buton Ekle", command=self.add_new_button).grid(row=1, column=1)
        self.add_button.pack()

        self.right_click_menu = Menu(self, tearoff=0)
        self.right_click_menu.add_command(label="Komutları Düzenle", command=self.edit_commands)
        self.right_click_menu.add_command(label="Sil", command=self.delete_button)
        self.right_click_menu.add_command(label="Renk Değiştir", command=self.change_color)

        self.current_button = None


    def add_new_button(self):
        button_text = simpledialog.askstring("Buton Ekleme", "Buton Adı:", parent=self.master)
        if button_text and button_text not in self.buttons:
            self.create_button(button_text)
            self.button_commands[button_text] = ""  # Initialize with empty commands

    def send_commands(self, button_text, ip='127.0.0.1', port=9998):
        commands = self.button_commands.get(button_text, "")
        if commands:  # Check if there are commands to send
            for command in commands.split('\n'):
                print(f"Sending command: {command}")
                # Integrate your logic here to send each command over Ethernet
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    try:
                        sock.sendto(command.encode(), (ip, port))
                        print(f"Message '{command}' sent to {ip}:{port}" + '\n')
                    except Exception as e:
                        print(f"Error sending command: {e}")



    def show_right_click_menu(self, event):
        try:
            self.current_button = event.widget.cget("text")
            self.right_click_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.right_click_menu.grab_release()

    def edit_commands(self):
        if self.current_button:
            self.show_command_editor()

    def show_command_editor(self):
        editor = Toplevel(self.master)
        editor.title("Komut Düzenleyici")
        text_area = ScrolledText(editor, wrap=tk.WORD, width=40, height=10)
        text_area.pack(padx=10, pady=10)
        text_area.insert(tk.END, self.button_commands.get(self.current_button, ""))
        
        def save_commands():
            self.button_commands[self.current_button] = text_area.get("1.0", tk.END).strip()
            editor.destroy()

        save_button = tk.Button(editor, text="Kaydet", command=save_commands)
        save_button.pack(pady=5)

    def create_button(self, button_text):
        new_button = tk.Button(self.master, text=button_text)
        new_button.bind("<Button-3>", self.show_right_click_menu)
        new_button.bind("<Button-1>", self.start_drag)
        new_button.bind("<B1-Motion>", self.drag)
        new_button.bind("<ButtonRelease-1>", lambda event, bt=button_text: self.stop_drag(event, bt))
        new_button.pack()
        self.buttons[button_text] = new_button

    def delete_button(self):
        if self.current_button:
            self.buttons[self.current_button].destroy()
            del self.buttons[self.current_button]
            del self.button_commands[self.current_button]

    def change_color(self):
        if self.current_button:
            new_color = colorchooser.askcolor(title ="Renk Seçin")[1]
            if new_color:
                self.buttons[self.current_button].config(bg=new_color)

    # Drag and drop functionality
    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.dragged = False

    def drag(self, event):
        self.dragged = True
        widget = event.widget
        x = widget.winfo_x() - self.drag_start_x + event.x
        y = widget.winfo_y() - self.drag_start_y + event.y
        widget.place(x=x, y=y)

        # Assuming frame_width and frame_height are the dimensions of the frame
        # and widget_width, widget_height are the dimensions of the widget
        frame_width = widget.master.winfo_width()
        frame_height = widget.master.winfo_height()
        widget_width = widget.winfo_width()
        widget_height = widget.winfo_height()

        # Adjust x and y to prevent the widget from moving outside the frame
        x = max(0, min(x, frame_width - widget_width))
        y = max(0, min(y, frame_height - widget_height))

        widget.place(x=x, y=y)

    def stop_drag(self, event, button_text):
        if not self.dragged:
            self.send_commands(button_text)
        self.dragged = False

if __name__ == "__main__":
    root = tk.Tk()
    root.title("CLI Komutlari")
    
    komut_ekrani_frame = KomutEkrani(master=root)
    komut_ekrani_frame.pack(expand=True, fill="both")

    root.mainloop()
