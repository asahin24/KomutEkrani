import socket
import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser, Menu, Toplevel, simpledialog
from tkinter.scrolledtext import ScrolledText
import json


class KomutEkrani(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.buttons = {}
        self.button_commands = {}
        self.stil = ttk.Style()
        self.init_ui()


    def init_ui(self):
        # Buton Ekleme butonunu ekle
        self.add_button = tk.Button(self, text="Buton Ekle", command=self.yeni_buton_ekle)
        self.add_button.place(x=1, y=1)

        self.sag_tik_komutlarini_olustur()

        self.butonlari_yukle()



        # bu degisken secili butonu takip etmek icin. Islem hangi buton uzerinde uygulanacak.
        self.current_button = None


    def yeni_buton_ekle(self):
        button_text = simpledialog.askstring("Buton Ekleme", "Buton Adı:", parent=self.master)
        if button_text and button_text not in self.buttons:
            self.buton_olustur(button_text)
            self.button_commands[button_text] = ""  # Bos olarak iklenir.
            self.butonlari_kaydet()


    def komutlari_gonder(self, button_text, ip='127.0.0.1', port=9998):
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



    def komut_butonu_sag_tik_menusu_goster(self, event):
        try:
            self.current_button = event.widget.cget("text")
            self.buton_sag_tik.tk_popup(event.x_root, event.y_root)
        finally:
            self.buton_sag_tik.grab_release()

    def buton_komutlarini_duzenle(self):
        if self.current_button:
            self.komut_duzenleyiciyi_goster()

    def komut_duzenleyiciyi_goster(self):
        editor = Toplevel(self.master)
        editor.title("Komut Düzenleyici")
        text_area = ScrolledText(editor, wrap=tk.WORD, width=40, height=10)
        text_area.place(x=0, y=10)
        text_area.insert(tk.END, self.button_commands.get(self.current_button, ""))
        
        def komutlari_kaydet():
            self.button_commands[self.current_button] = text_area.get("1.0", tk.END).strip()
            editor.destroy()
            self.butonlari_kaydet()

        save_button = tk.Button(editor, text="Kaydet", command=komutlari_kaydet)
        save_button.place(x=20, y=5)

    def buton_olustur(self, button_text):
        yeni_buton = tk.Button(self.master, text=button_text)
        yeni_buton.bind("<Button-3>", self.komut_butonu_sag_tik_menusu_goster)
        yeni_buton.bind("<Button-1>", self.suruklemeye_basla)
        yeni_buton.bind("<B1-Motion>", self.surukle)
        yeni_buton.bind("<ButtonRelease-1>", self.suruklemeyi_bitir)
        yeni_buton.place(x=0, y=30)
        self.buttons[button_text] = yeni_buton

    def butonu_sil(self):
        if self.current_button:
            self.buttons[self.current_button].destroy()
            del self.buttons[self.current_button]
            del self.button_commands[self.current_button]
            self.butonlari_kaydet()

    def buton_yazi_rengi_degistir(self):
        if self.current_button:
            new_color = colorchooser.askcolor(title ="Renk Seçin")[1]
            if new_color:
                self.buttons[self.current_button].config(fg=new_color)
                self.butonlari_kaydet()
    
    def buton_arka_plan_degistir(self):
        if self.current_button:
            new_color = colorchooser.askcolor(title ="Renk Seçin")[1]
            if new_color:
                self.buttons[self.current_button].config(bg=new_color)
                self.butonlari_kaydet()

    # Drag and drop functionality
    def suruklemeye_basla(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.dragged = False

    def surukle(self, event):
        self.dragged = True
        widget = event.widget
        x = widget.winfo_x() - self.drag_start_x + event.x
        y = widget.winfo_y() - self.drag_start_y + event.y
        widget.place(x=x, y=y)

        # Kullanici butonu cerceve disina cikaramasin
        frame_width = self.winfo_width()
        frame_height = self.winfo_height()
        widget_width = widget.winfo_width()
        widget_height = widget.winfo_height()

        x = max(0, min(x, frame_width - widget_width))
        y = max(0, min(y, frame_height - widget_height))

        widget.place(x=x, y=y)

    def suruklemeyi_bitir(self, button_text):
        if not self.dragged:
            self.komutlari_gonder(button_text)
        self.butonlari_kaydet()
        self.dragged = False

    def butonlari_yukle(self):
        try:
            # Load the buttons from the file
            with open('butonlar.json', 'r') as infile:
                buttons_data = json.load(infile)
            # Create buttons based on loaded data
            for key, btn_data in buttons_data.items():
                self.buton_yukle(btn_data)
        except FileNotFoundError:
            pass  # If the file does not exist, simply continue without loading buttons

    def buton_yukle(self, btn_data):
        yeni_buton = tk.Button(self.master, text=btn_data["text"], fg=btn_data["fg"], bg=btn_data["bg"])
        yeni_buton.bind("<Button-3>", self.komut_butonu_sag_tik_menusu_goster)
        yeni_buton.bind("<Button-1>", self.suruklemeye_basla)
        yeni_buton.bind("<B1-Motion>", self.surukle)
        yeni_buton.bind("<ButtonRelease-1>", lambda bt=btn_data["text"]: self.suruklemeyi_bitir(bt))
        self.button_commands[btn_data["text"]] = btn_data["commands"]
        yeni_buton.place(x=btn_data["x_coord"], y= btn_data["y_coord"])
        self.buttons[btn_data["text"]] = yeni_buton

    def butonlari_kaydet(self):
        # Prepare the data to be saved
        buttons_data = {key: {"text": btn.cget("text"),\
                              "commands": self.button_commands[key],\
                              "fg": btn.cget("fg"),\
                              "bg": btn.cget("bg"),\
                              "x_coord": btn.winfo_x(),\
                              "y_coord": btn.winfo_y()} for key, btn in self.buttons.items()}
        # Save to a file
        with open('butonlar.json', 'w') as outfile:
            json.dump(buttons_data, outfile)


    def sag_tik_komutlarini_olustur(self):
        # Buton sag tik komutlari
        self.buton_sag_tik = Menu(self, tearoff=0)
        self.buton_sag_tik.add_command(label="Komutları Düzenle", command=self.buton_komutlarini_duzenle)
        self.buton_sag_tik.add_command(label="Sil", command=self.butonu_sil)
        self.buton_sag_tik.add_command(label="Arka Plan Rengini Değiştir", command=self.buton_arka_plan_degistir)
        self.buton_sag_tik.add_command(label="Yazı Rengini Değiştir", command=self.buton_yazi_rengi_degistir)


if __name__ == "__main__":

    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    root = tk.Tk()
    root.title("CLI Komutlari")
    root.geometry("600x400")
   
    komut_ekrani_frame = KomutEkrani(master=root)
    komut_ekrani_frame.place(x=0, y=0, width=600, height=400)

    root.mainloop()
