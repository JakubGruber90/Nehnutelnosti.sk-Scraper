import requests
import tkinter as tk
import threading as tr
import scraper_def as sc #moj vlastny modul
from bs4 import BeautifulSoup
from tkinter import messagebox
from tkinter import OptionMenu

FONT=('Arial', 16)

class scraper_App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Nehnutelnosti.sk scraper")
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight = 1)
        
        self.frames= {}
        
        for F in (start_menu, manual_scraper_GUI, automatic_scraper_GUI):
            frame = F(container, self)
            self.frames[F] = frame
            
            frame.grid(row = 0, column = 0, sticky ="nsew")
            
        self.show_frame(start_menu)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
  
class start_menu(tk.Frame):  
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
            
        title = tk.Label(self, text="Vyberte si, ako chcete, aby boli zadane udaje:", font=FONT)        
        title.grid(row=0, column=4, padx=10, pady=10)
        
        man_button = tk.Button(self, text="Manualne", command= lambda : controller.show_frame(manual_scraper_GUI), font=FONT)
        man_button.grid(row=2, column= 3, padx=10, pady=10)
        
        aut_button = tk.Button(self, text="Automaticky", command= lambda : controller.show_frame(automatic_scraper_GUI), font=FONT)
        aut_button.grid(row=2, column= 5, padx=10, pady=10)
            
class manual_scraper_GUI(tk.Frame):
    def __init__(self, parent, controller):  
        tk.Frame.__init__(self, parent)
          
        self.locality = tk.Label(self, text="Zadajte lokalitu (povinne):", font=FONT)
        self.locality.grid(row= 0, column= 3, padx=10, pady=10)
            
        self.loc_entry = tk.Entry(self, font=FONT)
        self.loc_entry.grid(row= 1, column= 3, padx=10, pady=10)
            
        self.reality_type = tk.Label(self, text="Zadajte typ nehnutelnosti (nepovinne):", font=FONT)
        self.reality_type.grid(row= 2, column= 3, padx=10, pady=10)
            
        self.re_type_entry = tk.Entry(self, font=FONT)
        self.re_type_entry.grid(row= 3, column= 3, padx=10, pady=10)
            
        self.insertion_type = tk.Label(self, text="Zadajte typ inzeratu (nepovinne):", font=FONT)
        self.insertion_type.grid(row= 4, column= 3, padx=10, pady=10)
            
        self.ins_type_entry = tk.Entry(self, font=FONT)
        self.ins_type_entry.grid(row= 5, column= 3, padx=10, pady=10)
            
        self.file_name = tk.Label(self, text="Zadajte meno suboru (povinne):", font=FONT)
        self.file_name.grid(row= 6, column= 3, padx=10, pady=10)
            
        self.f_name_entry = tk.Entry(self, font=FONT)
        self.f_name_entry.grid(row= 7, column= 3, padx=10, pady=10)
        
        self.runbtn = tk.Button(self, text="Spustit", font=FONT, command=self.man_scraper_init)
        self.runbtn.grid(row= 8, column= 3, padx=10, pady=10)
        
        self.homebtn = tk.Button(self, text="Spat na hlavne menu", command=lambda : controller.show_frame(start_menu), font=FONT)
        self.homebtn.grid(row= 9, column= 3, padx=10, pady=10)
            
    def man_scraper_init(self):
        if len(self.loc_entry.get())==0 or len(self.f_name_entry.get())==0:
            messagebox.showerror(message="Nezadali ste povinne udaje")
            return
        
        if len(self.ins_type_entry.get())==0 and len(self.re_type_entry.get())==0:
            base_url="https://www.nehnutelnosti.sk/{}/".format(self.loc_entry.get())
        if len(self.ins_type_entry.get())>0 and len(self.re_type_entry.get())==0:
            base_url="https://www.nehnutelnosti.sk/{}/{}/".format(self.loc_entry.get(), self.ins_type_entry.get())
        if len(self.ins_type_entry.get())==0 and len(self.re_type_entry.get())>0:
            base_url="https://www.nehnutelnosti.sk/{}/{}/".format(self.loc_entry.get(), self.re_type_entry.get())
        if len(self.ins_type_entry.get())>0 and len(self.re_type_entry.get())>0:
            base_url="https://www.nehnutelnosti.sk/{}/{}/{}/".format(self.loc_entry.get(), self.re_type_entry.get(), self.ins_type_entry.get())
            
        try:
            self.response = requests.get(base_url, headers=sc.header)
            soup=BeautifulSoup(self.response.content, "html.parser")
            pagination=soup.find("ul", class_="component-pagination__items d-flex align-items-center") 
            if pagination:
                last_page_link = pagination.find_all("li")[-2].a["href"]
                page_num = int(last_page_link.split("=")[-1]) 
                self.response.raise_for_status()
            else:
                page_num = 0
        except requests.exceptions.RequestException:
            print('Neplatna URL, skuste zadat udaje znovu\n')
            
        sc.scraper(base_url, page_num, self.f_name_entry.get()+'.csv')
        messagebox.showinfo(message="Program skoncil")

class automatic_scraper_GUI(tk.Frame):
    def __init__(self, parent, controller):  
        tk.Frame.__init__(self, parent)
        
        self.file_name = tk.Label(self, text="Zadajte nazov suboru (povinne):", font=FONT)
        self.file_name.grid(row=0, column=1, padx=10, pady=10)
        
        self.f_name_entry = tk.Entry(self, font=FONT)
        self.f_name_entry.grid(row=1, column=1, padx=10, pady=10)
        
        self.dropdown_label = tk.Label(self, text="Zvolte kategoriu:", font=FONT)
        self.dropdown_label.grid(row=2, column=1, padx=10, pady=10)
        self.options = ['vsetky moznosti', 'predaj', 'prenajom', 'kupa', 'podnajom', 'vymena', 'drazba']
        self.clicked = tk.StringVar(self)
        self.clicked.set('prenajom')
        self.dropdown = OptionMenu(self, self.clicked, *self.options)
        self.dropdown.config(font=FONT)
        self.dropdown.grid(row=3, column=1, padx=10, pady=10)
        
        self.runbtn = tk.Button(self, text="Spustit", command=self.auto_scraper_init, font=FONT)
        self.runbtn.grid(row=4, column=1, padx=10, pady=10)
        
        self.homebtn = tk.Button(self, text="Spat na hlavne menu", command=lambda : controller.show_frame(start_menu), font=FONT)
        self.homebtn.grid(row=6, column=1, padx=10, pady=10)
        
    def auto_scraper_init(self):
        #progbar = ttk.Progressbar(self, orient="horizontal", mode="determinate", length=280)
        #progbar.grid(row= 5, column= 1, padx=10, pady=10) 
        
        
        if len(self.f_name_entry.get())==0:
            messagebox.showerror(message="Nezadali ste nazov suboru")
            return
        
        city_list = ['trencin'] #'bratislava', 'trnava', 'nitra', 'trencin' 'zilina', 'presov', 'banska-bystrica', 'kosice'
        room_num = ['1-izbove-byty', '2-izbove-byty', '3-izbove-byty']
        insertion_type = self.clicked.get()
        
        for city in city_list:
            for num in room_num:
                if insertion_type == 'vsetky moznosti':
                    base_url="https://www.nehnutelnosti.sk/{}/{}/".format(city, num)
                else:
                    base_url="https://www.nehnutelnosti.sk/{}/{}/{}/".format(city, num, insertion_type)
                
                
                try:
                    response = requests.get(base_url, headers=sc.header)
                    soup=BeautifulSoup(response.content, "html.parser")
                    pagination=soup.find("ul", class_="component-pagination__items d-flex align-items-center") 
                    if pagination:
                        last_page_link = pagination.find_all("li")[-2].a["href"]
                        page_num = int(last_page_link.split("=")[-1]) 
                        response.raise_for_status()
                    else:
                        page_num = 0
                except requests.exceptions.RequestException:
                    print('Neplatna URL, skuste zadat udaje znovu\n')
                    return

                sc.scraper(base_url, page_num, self.f_name_entry.get()+'.csv')
                
        #progbar.stop()
        messagebox.showinfo(message="Program skoncil")
        
app = scraper_App()
app.mainloop()