import os
import requests
from time import sleep
from bs4 import BeautifulSoup
from . import scraper_def as sc

def main():
    while True: #zjednodusene menu
        print('Zadajte lokalitu: ')
        city=input()
        os.system('cls')
        
        while True:
            print('Chcete zadat typ nehnutelnosti? (y/n): ')
            reality_type=input()
            if reality_type=="y":    
                print('Zadajte typ nehnutelnosti: ')
                reality_type=input()
                break
            if reality_type=="n":
                break
            elif reality_type!="n" or reality_type!="y":
                print('Nespravna moznost\n')
                continue
            
        os.system('cls')
        
        while True:   
            print('Chcete zadat typ inzeratu, napr. kupa/predaj...? (y/n): ')
            insertion_type=input()
            if insertion_type=="y":
                print('Zadajte typ inzeratu: ')
                insertion_type=input()
                os.system('cls')
                break
            if insertion_type=="n":
                break
            elif insertion_type!="n" or insertion_type!="y":
                print('Nespravna moznost\n')
                continue
        
        os.system('cls')
          
        print('Zadajte nazov vytvoreneho suboru: ')
        file_name=input()+".csv"
        os.system('cls')
        
        if reality_type=="n" and insertion_type=="n":
            base_url="https://www.nehnutelnosti.sk/{}/".format(city)
        if reality_type=="n" and insertion_type!="n":
            base_url="https://www.nehnutelnosti.sk/{}/{}/".format(city, insertion_type)
        if reality_type!="n" and insertion_type=="n":
            base_url="https://www.nehnutelnosti.sk/{}/{}/".format(city, reality_type)
        if reality_type!="n" and insertion_type!="n":
            base_url="https://www.nehnutelnosti.sk/{}/{}/{}/".format(city, reality_type, insertion_type)
        
        try:
            response = requests.get(base_url, headers=sc.header)
            soup=BeautifulSoup(response.content, "html.parser")
            pagination=soup.find("ul", class_="component-pagination__items d-flex align-items-center") 
            if pagination:
                last_page_link = pagination.find_all("li")[-2].a["href"]
                page_num = int(last_page_link.split("=")[-1]) 
            response.raise_for_status()
            break
        except requests.exceptions.RequestException:
            print('Neplatna URL, skuste zadat udaje znovu\n')
        
    sc.scraper(base_url, page_num, file_name)
    print('Program skoncil')
    sleep(10)