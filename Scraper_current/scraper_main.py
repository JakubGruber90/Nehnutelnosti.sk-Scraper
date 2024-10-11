import requests
import tkinter as tk
import tkinter.simpledialog
import pickle
import os
import scraper_def as sc #moj vlastny modul
from bs4 import BeautifulSoup
from tkinter import messagebox
from tkinter import OptionMenu
from unidecode import unidecode

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
        
        for F in (start_menu, manual_scraper_GUI, automatic_scraper_GUI, city_list_GUI):
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
            
        title = tk.Label(self, text="Vyberte akciu:", font=FONT)        
        title.grid(row=0, column=1, padx=10, pady=10)
        
        man_button = tk.Button(self, text="Manualny scraping", command= lambda : controller.show_frame(manual_scraper_GUI), font=FONT)
        man_button.grid(row=1, column= 0, padx=10, pady=10)
        
        aut_button = tk.Button(self, text="Automaticky scraping", command= lambda : controller.show_frame(automatic_scraper_GUI), font=FONT)
        aut_button.grid(row=1, column= 2, padx=10, pady=10)
        
        cit_button = tk.Button(self, text="Upravit zoznam miest", command= lambda : controller.show_frame(city_list_GUI), font=FONT)
        cit_button.grid(row=2, column= 2, padx=10, pady=10)
 
class city_list_GUI(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        self.dropdown_label = tk.Label(self, text="Zoznam miest na automaticky scraping:", font=FONT)
        self.dropdown_label.grid(row=0, column=1, padx=10, pady=10)
        self.options = sc.city_list
        self.clicked = tk.StringVar(self)
        self.clicked.set(self.options[0])
        self.dropdown = OptionMenu(self, self.clicked, *self.options)
        self.dropdown.config(font=FONT)
        self.dropdown.grid(row=1, column=1, padx=10, pady=10)
        
        self.addbtn = tk.Button(self, text="Pridat mesto", command=self.add_city, font=FONT)
        self.addbtn.grid(row= 2, column=0, padx=10, pady=10)
        
        self.delbtn = tk.Button(self, text="Odstranit vybrane mesto", command=self.del_city, font=FONT)
        self.delbtn.grid(row= 2, column=2, padx=10, pady=10)
    
        self.homebtn = tk.Button(self, text="Spat na hlavne menu", command=lambda : controller.show_frame(start_menu), font=FONT)
        self.homebtn.grid(row=3, column=0, padx=10, pady=10)
    
    def add_city(self):
        new_city = custom_askstring("Pridat mesto", "Zadajte nazov mesta:", parent=self)
        print(new_city)

        if new_city:
            if new_city not in sc.city_list:
                sc.city_list.append(new_city)
                serialize()

                self.options = sc.city_list
                self.clicked.set(new_city)
                self.dropdown_update()
                print(sc.city_list)
    
    def del_city(self):
        selected_city = self.clicked.get()

        if selected_city in sc.city_list:
            sc.city_list.remove(selected_city)
            serialize()
            
            self.options = sc.city_list
            self.dropdown_update()
            
            if not self.options:
                self.clicked.set('')
            else:
                self.clicked.set(self.options[0])
            print(sc.city_list)
    
    def dropdown_update(self):
        menu = self.dropdown["menu"] #vymazanie mesta z menu
        menu.delete(0, "end")
        for city in self.options:
            menu.add_command(label=city, command=lambda value=city: self.clicked.set(value))
            
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
            
        self.dropdown_label = tk.Label(self, text="Zvolte kategoriu:", font=FONT)
        self.dropdown_label.grid(row=4, column=3, padx=10, pady=10)
        self.options = ['vsetky moznosti', 'predaj', 'prenajom', 'kupa', 'podnajom', 'vymena', 'drazba']
        self.clicked = tk.StringVar(self)
        self.clicked.set('prenajom')
        self.dropdown = OptionMenu(self, self.clicked, *self.options)
        self.dropdown.config(font=FONT)
        self.dropdown.grid(row=5, column=3, padx=10, pady=10)
            
        self.file_name = tk.Label(self, text="Zadajte meno suboru (povinne):", font=FONT)
        self.file_name.grid(row= 7, column= 3, padx=10, pady=10)
            
        self.f_name_entry = tk.Entry(self, font=FONT)
        self.f_name_entry.grid(row= 8, column= 3, padx=10, pady=10)
        
        self.runbtn = tk.Button(self, text="Spustit", font=FONT, command=self.man_scraper_init)
        self.runbtn.grid(row= 9, column= 3, padx=10, pady=10)
        
        self.homebtn = tk.Button(self, text="Spat na hlavne menu", command=lambda : controller.show_frame(start_menu), font=FONT)
        self.homebtn.grid(row= 10, column= 3, padx=10, pady=10)
            
    def man_scraper_init(self):
        if len(self.loc_entry.get())==0 or len(self.f_name_entry.get())==0:
            messagebox.showerror(message="Nezadali ste povinne udaje")
            return
        
        insertion_type = self.clicked.get() 
        
        if insertion_type=="vsetky moznosti" and len(self.re_type_entry.get())==0:
            base_url="https://www.nehnutelnosti.sk/{}/".format(self.loc_entry.get())
        if insertion_type!="vsetky moznosti" and len(self.re_type_entry.get())==0:
            base_url="https://www.nehnutelnosti.sk/{}/{}/".format(self.loc_entry.get(), insertion_type)
        if insertion_type=="vsetky moznosti" and len(self.re_type_entry.get())>0:
            base_url="https://www.nehnutelnosti.sk/{}/{}/".format(self.loc_entry.get(), self.re_type_entry.get())
        if insertion_type!="vsetky moznosti" and len(self.re_type_entry.get())>0:
            base_url="https://www.nehnutelnosti.sk/{}/{}/{}/".format(self.loc_entry.get(), self.re_type_entry.get(), insertion_type)
            
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
            
        sc.scraper(base_url, page_num, self.f_name_entry.get()+'.xlsx', False)
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
        
        room_num = ['1-izbove-byty', '2-izbove-byty', '3-izbove-byty']
        insertion_type = self.clicked.get()
        
        city_detail_list = []
        
        for city in sc.city_list:
            city_format = unidecode(city).lower().replace(' ', '-')
            city_dict = {}
            city_dict["city"] = city
            city_dict["insertion_type"] = insertion_type
            city_dict["avgs"] = []
            
            for num in room_num:
                if insertion_type == "vsetky moznosti":
                    base_url="https://www.nehnutelnosti.sk/{}/{}/".format(city_format, num)
                else:
                    base_url="https://www.nehnutelnosti.sk/{}/{}/{}/".format(city_format, num, insertion_type)
                
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
                
                avg_new_other = sc.scraper(base_url, page_num, self.f_name_entry.get()+'.xlsx', True)
                city_dict["avgs"].append(avg_new_other)
         
            city_detail_list.append(city_dict)        
        
        current_directory = os.getcwd()
        file_path = os.path.join(current_directory, self.f_name_entry.get()+'.xlsx')
        sc.write_summary(file_path, city_detail_list)
           
        #progbar.stop()
        messagebox.showinfo(message="Program skoncil")

class CustomDialog(tk.simpledialog.Dialog): #override simpledialog.askstring, aby som vedel zmenit, ako vyzera DELETE IF BREAKS PROGRAM
    def __init__(self, parent, title=None, prompt=None):
        self.prompt = prompt
        self.value = None
        tk.simpledialog.Dialog.__init__(self, parent, title=title)

    def body(self, master):
        self.geometry("300x150")
        tk.Label(master, text=self.prompt, font=FONT).grid(row=0)
        self.entry = tk.Entry(master, font=FONT)
        self.entry.grid(row=1)
        return self.entry

    def apply(self):
        self.result = self.entry.get()

def custom_askstring(title, prompt, parent=None):
    d = CustomDialog(parent, title, prompt)
    return d.result

def serialize():
    outputfile = open("program_data", "wb")
    pickle.dump(sc.city_list, outputfile)
    outputfile.close()
     
app = scraper_App()
app.mainloop()