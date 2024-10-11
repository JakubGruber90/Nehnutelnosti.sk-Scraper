import requests
import os
from csv import writer
from lxml import etree as et
from bs4 import BeautifulSoup

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.66 Safari/537.36"} #hlavičky pre prehliadač
pages_url=[] #zoznam URL pre jednotlivé stránky webu
listing_url=[] #zoznam URL jednotlivých inzerátov
 
#funkcia na prehladavanie stranok a vytvorenie vysledneho suboru s datami   
def scraper(base_url, page_num, file_name):
    for i in range (1,page_num+1): 
        page_url=base_url + "?p[page]=" + str(i)
        pages_url.append(page_url) 
    
    for page in pages_url:
        get_listing_url(page)
    
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, file_name)
    with open(file_path, 'w', newline='') as file:
        thewriter=writer(file)
        heading=['Link', 'Mesto', 'Ulica', 'Cena', 'Izbovitosť', 'Prenájom/predaj', 'Stav', 'Úžitková plocha v m2', 'Zastavaná plocha v m2', 'EUR/m2']
        thewriter.writerow(heading)
        
        usable_area_list=[]
        eurm2_list=[]

        for list_url in listing_url: 
            listing_dom=get_dom(list_url)
            
            print(list_url)
            
            city=get_city(listing_dom)
            street=get_street(listing_dom)
            price=get_price(listing_dom)
            try:
                price=int(''.join(filter(str.isdigit, price)))
                if price==1: #Osetrenie pre placeholder 1€, aby nekazilo data
                    price='CENA NIE JE DOSTUPNA'
            except:
                pass
            rooms=get_rooms(listing_dom)
            sale_rent=get_sale_rent(listing_dom)
            state=get_state(listing_dom)
            usable_area=get_usable_area(listing_dom)
            try:
                usable_area=int(''.join(filter(str.isdigit, usable_area)))
            except:
                pass
            
            land_area=get_land_area(listing_dom)
            try:
                land_area=int(''.join(filter(str.isdigit, land_area)))
            except:
                pass
            try:
                eurm2=price/usable_area
            except:
                eurm2='CENA/PLOCHA V M2 NIE JE DOSTUPNA'
                
            if isinstance(usable_area, int) and isinstance(eurm2, float): #Osetrenie, aby sa vypocet vazeneho priemeru robil len vtedy, ak su oba udaje pritomne (uzitkova plocha a EUR/m2)
                usable_area_list.append(usable_area)
                eurm2_list.append(eurm2)
                
            information =[list_url, city, street, price, rooms, sale_rent, state, usable_area, land_area, eurm2]
                
            thewriter.writerow(information)
        
        weigh_avg = sum(x * y for x, y in zip(usable_area_list, eurm2_list))/sum(usable_area_list)
        info=['Vazeny priemer', weigh_avg, 'Pocet prezrenych inzeratov', len(listing_url)]
        thewriter.writerow(info)
            
#funkcia na vrátenie DOM ked zadám URL  
def get_dom(the_url):
    try:
        response = requests.get(the_url, headers=header, timeout=20)
    except Exception as e:
        print('Pri dostavani dat zo stranky nastala chyba:', e)
        
    soup = BeautifulSoup(response.text,'lxml')
    dom = et.HTML(str(soup)) 
    return dom

#funkcia, ktorá mi vráti linky na inzeráty v rámci stránky
def get_listing_url(page_url):
    dom = get_dom(page_url)
    page_link_list=dom.xpath('//a[contains(@class, "advertisement-item--content__title d-block text-truncate")]/@href')
    for page_link in page_link_list:
        listing_url.append(page_link)
        
########################################

#Atribúty, ktoré chcem dostať z inzerátu

def get_street(dom):
    try:               
        street=dom.xpath('//*[@id="map-filter-container"]/div[2]/div/div[1]/div[2]/div[2]/span/text()')
        street=street[0].strip().rstrip(',')
        
        if len(street) > 0:
            print(street)
            return street
        else:
            return "ULICA NIE JE ZADANA"
        
    except Exception as e:
        street = "ULICA NIE JE DOSTUPNA"
        print(e)

def get_rooms(dom):
    try:               
        rooms=dom.xpath('//*[@id="map-filter-container"]/div[2]/div/div[1]/div[2]/div[5]/ul/li[1]/div[2]/strong/text()')
        rooms=rooms[0].strip()
        print(rooms)
    except Exception as e:
        rooms = "IZBOVITOST NIE JE DOSTUPNA"
        print(e)
    return rooms

def get_sale_rent(dom):
    try:               
        sale_rent=dom.xpath('//*[@id="map-filter-container"]/div[2]/div/div[1]/div[2]/div[5]/ul/li[1]/div[1]/strong/text()') 
        sale_rent=sale_rent[0].strip()
        print(sale_rent)
    except Exception as e:
        sale_rent = "TYP VLASTNICTVA NIE JE DOSTUPNY"
        print(e)
    return sale_rent

def get_state(dom):
    try:               
        state=dom.xpath('//*[@id="map-filter-container"]/div[2]/div/div[1]/div[2]/div[5]/ul/li[1]/div[3]/strong/text()')
        state=state[0].strip()
        print(state)
    except Exception as e:
        state = "STAV NIE JE DOSTUPNY"
        print(e)
    return state

def get_usable_area(dom):
    try:               
        usable_area=dom.xpath('//*[@id="map-filter-container"]/div[2]/div/div[1]/div[2]/div[5]/ul/li[2]/div[1]/strong/text()')
        usable_area=usable_area[0].strip()
        print(usable_area)
    except Exception as e:
        usable_area = "VYUZITELNY PRIESTOR NIE JE DOSTUPNY"
        print(e)
    return usable_area

def get_land_area(dom):
    try:               
        get_land_area=dom.xpath('//*[@id="map-filter-container"]/div[2]/div/div[1]/div[2]/div[5]/ul/li[2]/div[2]/strong/text()')
        get_land_area=get_land_area[0].strip()
        print(get_land_area)
    except Exception as e:
        get_land_area = "PRIESTOR POZEMKU NIE JE DOSTUPNY"
        print(e)
    return get_land_area

def get_price(dom):
    try:               
        price=dom.xpath('//*[@id="map-filter-container"]/div[2]/div/div[1]/div[2]/div[3]/div/div/div/div/div/span/text()')
        price=price[0].strip()
        print(price)
    except Exception as e:
        price = "CENA NIE JE DOSTUPNA"
        print(e)
    return price

def get_city(dom):
    try:
        city=dom.xpath('//*[@id="map-filter-container"]/div[2]/div/div[1]/div[2]/div[2]/span/a/text()')
        city=city[0].strip()
        print(city)
    except Exception as e:
        city = "MESTO NIE JE DOSTUPNE"
        print(e)
    return city