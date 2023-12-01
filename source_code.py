import customtkinter as ctk
from datetime import date
from tkcalendar import Calendar
import sqlite3
import os
from PIL import Image
import shutil
import webbrowser

#Percorsi alle cartelle
percorso_applicazione = "/Users/simonecotardo/GitHub/Bilancio-giornaliero/"
percorso_database = "/Users/simonecotardo/Documents/Progetti/Contabilita/Database/"+"Database.db"
percorso_documenti = "/Users/simonecotardo/Documents/Documenti di contabilità/"

#Import images
bin_icon = ctk.CTkImage(Image.open(percorso_applicazione+"bin_icon.png"))
upload_icon = ctk.CTkImage(Image.open(percorso_applicazione+"upload_icon.png"))
edit_icon = ctk.CTkImage(Image.open(percorso_applicazione+"edit_icon.png"))
warning_icon = ctk.CTkImage(Image.open(percorso_applicazione+"warning_icon.png"), size=(40, 40))
check_icon = ctk.CTkImage(Image.open(percorso_applicazione+"check_icon.png"), size=(40, 40))
error_icon = ctk.CTkImage(Image.open(percorso_applicazione+"error_icon.png"), size=(40, 40))

#Set application colors
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("dark-blue")

#Set app size
app_width = 1100
app_height = 800

def showConfirmMessage(frame, titolo, messaggio, icon_image, kill_app_after_click):
    def destroy():
        message_window.destroy()
        if kill_app_after_click==True:
            frame.destroy()
    message_window = ctk.CTkToplevel(frame)
    message_window.title(titolo)
    #message_window.geometry("350x150")
    ws = message_window.winfo_screenwidth()
    hs = message_window.winfo_screenheight()
    x = (ws/2) - (350/2)
    y = (hs/2) - (150/2)
    message_window.geometry('%dx%d+%d+%d' % (350, 150, x, y))
    message_window.minsize(350, 150)
    message_window.maxsize(350, 150)
    match icon_image:
        case "check":
            icon = ctk.CTkLabel(message_window, text="", image=check_icon)
        case "cancel":
            icon = ctk.CTkLabel(message_window, text="", image=error_icon)
        case "warning":
            icon = ctk.CTkLabel(message_window, text="", image=warning_icon)
    icon.pack(pady=(15,0), padx=20)
    message = ctk.CTkLabel(message_window, text=messaggio, font=("Helvetica",14))
    message.pack(pady=(0,10), padx=20)
    message_button = ctk.CTkButton(message_window, text="Ok", width=50, command=destroy)
    message_button.pack(pady=(15,5), padx=20)
    #msg = CTkMessagebox(master=frame, title=titolo, message=messaggio, icon=icon_image, fade_in_duration=150, font=("Helvetica", 13), cancel_button="None", option_1 ="Ok")
    #if msg.get() == "Ok":
    #    frame.destroy()
    

#****CREA NUOVA PROVA VIEW****
def createNuovaProvaView():
    home.destroy()
    #root
    creaprova = ctk.CTk()
    creaprova.title("Crea prova giornaliera")

    #Set window size
    app_size = str(app_width)+str(app_height)
    creaprova.geometry(app_size)
    creaprova.minsize(app_width-50, app_height)

    #Place window in center of screen
    ws = creaprova.winfo_screenwidth()
    hs = creaprova.winfo_screenheight()
    x = (ws/2) - (app_width/2)
    y = (hs/2) - (app_height/2)
    creaprova.geometry('%dx%d+%d+%d' % (app_width, app_height, x, y))

    #Create date in top of window and select today date
    #Label
    label = ctk.CTkLabel(master=creaprova, text="Data della prova da creare:")
    label.pack(pady=(10,0))


    def destroyMarchirolo(nome_frame, posizione):
        lista_marchirolo[posizione] = ""
        lista_marchirolo_causali[posizione] = ""
        nome_frame.destroy()
        updateMarchirolo()

    #Input
    def updateData(*args):
        entry_cassaprecedente.configure(state='normal')
        entry_cassaprecedente.delete(0,'end')
        entry_cassaprecedente.insert('end', "{:.2f}".format(0))
        entry_cassaprecedente.configure(state='disabled')
        #Ottieni il fondo cassa dal giorno precedente
        #Converti data
        data_converted = (today_date_formatted.get()).split('-')
        data_converted_text=""
        data_converted_text=data_converted[2]+"-"+data_converted[1]+"-"+data_converted[0]
        connection = sqlite3.connect(percorso_database)
        cursor = connection.cursor()
        cursor.execute("SELECT data, fondo_cassa_da_riportare FROM prova WHERE data<'"+data_converted_text+"' ORDER BY data DESC LIMIT 1")
        connection.commit()
        data=cursor.fetchall()
        if (len(data)==0):
            label_daybefore.configure(text="Non trovato")
        else:
            for data_precedente, fondo_cassa_da_riportare_precedente in data:
                entry_cassaprecedente.configure(state='normal')
                entry_cassaprecedente.delete(0,'end')
                entry_cassaprecedente.insert('end', "{:.2f}".format(fondo_cassa_da_riportare_precedente))
                entry_cassaprecedente.configure(state='disabled')
                #Converti la data precedente ottenuta in formato gg-mm-aaaa
                data_converted2 = (data_precedente).split('-')
                data_converted_text2=""
                data_converted_text2=data_converted2[2]+"-"+data_converted2[1]+"-"+data_converted2[0]
                label_daybefore.configure(text="Del "+data_converted_text2)

        #Reset array Marchirolo
        lista_marchirolo.clear()
        lista_marchirolo_causali.clear()
        #Elimina entry all'interno ella lista marchirolo
        for child in frame_marchirolo.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                for child2 in child.winfo_children():
                    if isinstance(child2, ctk.CTkEntry):
                        child2.delete(0, 'end')
                child.destroy()
        #SELECT dalla lista di Marchirolo del giorno precedente
        cursor.execute("SELECT valore, causale FROM liste WHERE data='"+data_precedente+"' AND categoria='marchirolo'")
        rows = cursor.fetchall()
        nomeentry = 0
        def createFrame(valore, causale):
                frame = ctk.CTkFrame(frame_marchirolo)
                frame.pack()
                ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
                var1 = ctk.DoubleVar(frame, valore)
                var1.trace("w", updateMarchirolo)
                ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
                ent1.grid(row=1, column=0)
                #ent1.configure(state='disabled')
                ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
                ent2 = ctk.CTkEntry(frame, width=250)
                ent2.insert('end', causale)
                ent2.grid(row=1, column=1)
                #ent2.configure(state='disabled')
                delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=lambda f=nomeentry: destroyMarchirolo(frame, f))
                delete_button.grid(row=1, column=2)
                lista_marchirolo.append(var1)
                lista_marchirolo_causali.append(ent2)

        for valore,causale in rows:
            createFrame(valore, causale)
            nomeentry = nomeentry + 1
        updateMarchirolo()
        '''for valore,causale in rows:
            frame = ctk.CTkFrame(frame_marchirolo)
            frame.pack()
            ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
            var1 = ctk.DoubleVar(frame_marchirolo, valore)
            var1.trace("w", updateMarchirolo)
            ent1 = ctk.CTkEntry(frame, textvariable=var1)
            ent1.grid(row=1, column=0)
            ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
            ent2 = ctk.CTkEntry(frame)
            ent2.insert('end', causale)
            ent2.grid(row=1, column=1)
            lista_marchirolo.append(var1)
            lista_marchirolo_causali.append(ent2)
        updateMarchirolo()'''

        connection.close()

    today_date = date.today()
    today_date_formatted = ctk.StringVar(creaprova, today_date.strftime("%d-%m-%Y"))
    today_date_formatted.trace("w", updateData)
    input_date = ctk.CTkEntry(master=creaprova, textvariable=today_date_formatted, placeholder_text="gg-mm-aaaa")
    input_date.pack(pady=(0,10))

    #Create frame inside the window
    tabview = ctk.CTkTabview(master=creaprova)
    tabview.pack(pady=(0,15), padx=20, fill="both", expand=True)

    tabview.add("Incassi")
    tabview.add("Sospesi")
    tabview.add("Recupero sospesi")
    tabview.add("Uscite")
    tabview.add("Marchirolo")
    tabview.add("Resoconto")
    tabview.add("Documenti")

    #UPDATE VALUES DECLARATION
    def updateIncassiVittoria(*args):
        #print("Aggiorna totale parziale 1")
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_per_conto.get()
        except: b=0
        try: c=incasso_das.get()
        except: c=0
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')

        #print("Aggiorna Incasso contanti")
        try: g=totale_incassi_vittoria.get()
        except: g=0
        try: h=incasso_polizze_bonifici.get()
        except: h=0
        try: i=incasso_polizze_carte_pos.get()
        except: i=0
        try: j=totale_sospesi.get()
        except: j=0
        result2=g-h-i-j
        entry_incassicontante.configure(state='normal')
        entry_incassicontante.delete(0,'end')
        entry_incassicontante.insert('end', "{:.2f}".format(result2))
        entry_incassicontante.configure(state='disabled')
    def updateIncassoPerConto(*args):
        #print("Aggiorna totale parziale 1")
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_per_conto.get()
        except: b=0
        try: c=incasso_das.get()
        except: c=0
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')
    def updateIncassoDAS(*args):
        #print("Aggiorna totale parziale 1")
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_per_conto.get()
        except: b=0
        try: c=incasso_das.get()
        except: c=0
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')
    def updateTotaleBonifici(*args):
        #print("Aggiorna totale parziale 1")
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_per_conto.get()
        except: b=0
        try: c=incasso_das.get()
        except: c=0
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')

        #print("Aggiorna Incasso polizze bonifici")
        try: g=totale_bonifici.get()
        except: g=0
        try: h=totale_recupero_sospesi_bonifici.get()
        except: h=0
        result2=g-h
        entry_incasso_polizzebonifici.configure(state='normal')
        entry_incasso_polizzebonifici.delete(0,'end')
        entry_incasso_polizzebonifici.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzebonifici.configure(state='disabled')
    def updateIncassoPolizzeBonifici(*args):
        #print("Aggiorna Incasso polizze bonifici")
        try: a=totale_bonifici.get()
        except: a=0
        try: b=totale_recupero_sospesi_bonifici.get()
        except: b=0
        result=a-b
        entry_incasso_polizzebonifici.configure(state='normal')
        entry_incasso_polizzebonifici.delete(0,'end')
        entry_incasso_polizzebonifici.insert('end', "{:.2f}".format(result))
        entry_incasso_polizzebonifici.configure(state='disabled')

        #Aggiorna Incasso contanti
        #print("Aggiorna Incasso contanti")
        try: c=totale_incassi_vittoria.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result2=c-d-e-f
        entry_incassicontante.configure(state='normal')
        entry_incassicontante.delete(0,'end')
        entry_incassicontante.insert('end', "{:.2f}".format(result2))
        entry_incassicontante.configure(state='disabled')
    def updateTotaleCartePOS(*args):
        #print("Aggiorna totale parziale 1")
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_per_conto.get()
        except: b=0
        try: c=incasso_das.get()
        except: c=0
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')

        #print("Aggiorna incasso polizze pos/carte")
        try: g=totale_carte_pos.get()
        except: g=0
        try: h=totale_recupero_sospesi_carte_pos.get()
        except: h=0
        result2=g-h
        entry_incasso_polizzecartepos.configure(state='normal')
        entry_incasso_polizzecartepos.delete(0,'end')
        entry_incasso_polizzecartepos.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzecartepos.configure(state='disabled')
    def updateIncassoPolizzeCartePOS(*args):
        #print("Aggiorna Incasso contanti")
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_polizze_bonifici.get()
        except: b=0
        try: c=incasso_polizze_carte_pos.get()
        except: c=0
        try: d=totale_sospesi.get()
        except: d=0
        result=a-b-c-d
        entry_incassicontante.configure(state='normal')
        entry_incassicontante.delete(0,'end')
        entry_incassicontante.insert('end', "{:.2f}".format(result))
        entry_incassicontante.configure(state='disabled')
    def updateTotaleParziale1(*args):
        #print("Aggiorna totale parziale 2")
        try: a=totale_parziale_1.get()
        except: a=0
        try: b=fondo_cassa_precedente.get()
        except: b=0
        result=a+b
        entry_tot_parziale_2.configure(state='normal')
        entry_tot_parziale_2.delete(0,'end')
        entry_tot_parziale_2.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_2.configure(state='disabled')
    def updateFondoCassaPrecedente(*args):
        #print("Aggiorna totale parziale 2")
        try: a=totale_parziale_1.get()
        except: a=0
        try: b=fondo_cassa_precedente.get()
        except: b=0
        result=a+b
        entry_tot_parziale_2.configure(state='normal')
        entry_tot_parziale_2.delete(0,'end')
        entry_tot_parziale_2.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_2.configure(state='disabled')
    def updateTotaleParziale2(*args):
        #print("Aggiorna totale cassa contante")
        try: a=totale_parziale_2.get()
        except: a=0
        try: b=totale_recupero_sospesi.get()
        except: b=0
        result=a+b
        entry_tot_cassacontanti.configure(state='normal')
        entry_tot_cassacontanti.delete(0,'end')
        entry_tot_cassacontanti.insert('end', "{:.2f}".format(result))
        entry_tot_cassacontanti.configure(state='disabled')
    def updateTotaleRecuperoSospesiContanti(*args):
        #print("Aggiorna totale recupero sospesi")
        try: a=totale_recupero_sospesi_contanti.get()
        except: a=0
        try: b=totale_recupero_sospesi_carte_pos.get()
        except: b=0
        try: c=totale_recupero_sospesi_bonifici.get()
        except: c=0
        result=a+b+c
        entry_tot_recuperosospesi.configure(state='normal')
        entry_tot_recuperosospesi.delete(0,'end')
        entry_tot_recuperosospesi.insert('end', "{:.2f}".format(result))
        entry_tot_recuperosospesi.configure(state='disabled')
    def updateTotaleRecuperoSospesiCartePOS(*args):
        #print("Aggiorna totale recupero sospesi")
        try: a=totale_recupero_sospesi_contanti.get()
        except: a=0
        try: b=totale_recupero_sospesi_carte_pos.get()
        except: b=0
        try: c=totale_recupero_sospesi_bonifici.get()
        except: c=0
        result=a+b+c
        entry_tot_recuperosospesi.configure(state='normal')
        entry_tot_recuperosospesi.delete(0,'end')
        entry_tot_recuperosospesi.insert('end', "{:.2f}".format(result))
        entry_tot_recuperosospesi.configure(state='disabled')

        #print("Aggiorna incasso polizze pos/carte")
        try: d=totale_carte_pos.get()
        except: d=0
        try: e=totale_recupero_sospesi_carte_pos.get()
        except: e=0
        result2=d-e
        entry_incasso_polizzecartepos.configure(state='normal')
        entry_incasso_polizzecartepos.delete(0,'end')
        entry_incasso_polizzecartepos.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzecartepos.configure(state='disabled')
    def updateTotaleRecuperoSospesiBonifici(*args):
        #print("Aggiorna totale recupero sospesi")
        try: a=totale_recupero_sospesi_contanti.get()
        except: a=0
        try: b=totale_recupero_sospesi_carte_pos.get()
        except: b=0
        try: c=totale_recupero_sospesi_bonifici.get()
        except: c=0
        result=a+b+c
        entry_tot_recuperosospesi.configure(state='normal')
        entry_tot_recuperosospesi.delete(0,'end')
        entry_tot_recuperosospesi.insert('end', "{:.2f}".format(result))
        entry_tot_recuperosospesi.configure(state='disabled')

        #print("Aggiorna Incasso polizze bonifici")
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_recupero_sospesi_bonifici.get()
        except: e=0
        result2=d-e
        entry_incasso_polizzebonifici.configure(state='normal')
        entry_incasso_polizzebonifici.delete(0,'end')
        entry_incasso_polizzebonifici.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzebonifici.configure(state='disabled')
    def updateTotaleRecuperoSospesi(*args):
        #print("Aggiorna totale cassa contante")
        try: a=totale_parziale_2.get()
        except: a=0
        try: b=totale_recupero_sospesi.get()
        except: b=0
        result=a+b
        entry_tot_cassacontanti.configure(state='normal')
        entry_tot_cassacontanti.delete(0,'end')
        entry_tot_cassacontanti.insert('end', "{:.2f}".format(result))
        entry_tot_cassacontanti.configure(state='disabled')

        #Aggiorna saldo sospesi
        try: c=totale_sospesi.get()
        except: c=0
        try: d=totale_recupero_sospesi.get()
        except: d=0
        result3=c-d
        entry_saldo_sospesi.configure(state='normal')
        entry_saldo_sospesi.delete(0,'end')
        entry_saldo_sospesi.insert('end', "{:.2f}".format(result3))
        entry_saldo_sospesi.configure(state='disabled')
    def updateTotaleCassaContante(*args):
        #print("Aggiorna fondo cassa da riportare")
        try: a=totale_cassa_contante.get()
        except: a=0
        try: b=totale_generale_uscite.get()
        except: b=0
        result=a-b
        entry_fondodariportare.configure(state='normal')
        entry_fondodariportare.delete(0,'end')
        entry_fondodariportare.insert('end', "{:.2f}".format(result))
        entry_fondodariportare.configure(state='disabled')
    def updateTotaleAbbuoni(*args):
        #print("Aggiorna Totale generale uscite")
        try: a=totale_abbuoni.get()
        except: a=0
        try: b=totale_uscite_varie.get()
        except: b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_tot_generaleuscite.configure(state='normal')
        entry_tot_generaleuscite.delete(0,'end')
        entry_tot_generaleuscite.insert('end', "{:.2f}".format(result))
        entry_tot_generaleuscite.configure(state='disabled')
    def updateTotaleUsciteVarie(*args):
        #print("Aggiorna Totale generale uscite")
        try:a=totale_abbuoni.get()
        except:a=0
        try:b=totale_uscite_varie.get()
        except:b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_tot_generaleuscite.configure(state='normal')
        entry_tot_generaleuscite.delete(0,'end')
        entry_tot_generaleuscite.insert('end', "{:.2f}".format(result))
        entry_tot_generaleuscite.configure(state='disabled')
    def updateTotaleGeneraleUscite(*args):
        #print("Aggiorna fondo cassa da riportare")
        try: a=totale_cassa_contante.get()
        except: a=0
        try: b=totale_generale_uscite.get()
        except: b=0
        result=a-b
        entry_fondodariportare.configure(state='normal')
        entry_fondodariportare.delete(0,'end')
        entry_fondodariportare.insert('end', "{:.2f}".format(result))
        entry_fondodariportare.configure(state='disabled')
    def updateFondoCassaDaRiportare(*args):
        #print("Aggiorna saldo cassa")
        try: a=fondo_cassa_da_riportare.get()
        except: a=0
        try: b=totale_marchirolo.get()
        except: b=0
        result=a-b
        entry_saldocassa.configure(state='normal')
        entry_saldocassa.delete(0,'end')
        entry_saldocassa.insert('end', "{:.2f}".format(result))
        entry_saldocassa.configure(state='disabled')
    def updateSospesi(*args):
        #print("Aggiorna totale sospesi:")
        somma=0
        for item in lista_sospesi_values:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_sospesi.configure(state='normal')
        entry_sospesi.delete(0,'end')
        entry_sospesi.insert('end', "{:.2f}".format(somma))
        entry_sospesi.configure(state='disabled')
    def updateRecuperoContanti(*args):
        #Aggiorna totale recupero sospesi contanti
        somma=0
        for item in lista_recupero_contanti:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_tot_contante_recuperato.configure(state='normal')
        entry_tot_contante_recuperato.delete(0,'end')
        entry_tot_contante_recuperato.insert('end', "{:.2f}".format(somma))
        entry_tot_contante_recuperato.configure(state='disabled')
    def updateRecuperoCartePOS(*args):
        #Aggiorna totale recupero sospesi carte/pos
        somma=0
        for item in lista_recupero_cartepos:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_tot_cartapos_recuperato.configure(state='normal')
        entry_tot_cartapos_recuperato.delete(0,'end')
        entry_tot_cartapos_recuperato.insert('end', "{:.2f}".format(somma))
        entry_tot_cartapos_recuperato.configure(state='disabled')
    def updateRecuperoBonifici(*args):
        #Aggiorna totale recupero sospesi carte/pos
        somma=0
        for item in lista_recupero_bonifici:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_tot_bonifici_recuperato.configure(state='normal')
        entry_tot_bonifici_recuperato.delete(0,'end')
        entry_tot_bonifici_recuperato.insert('end', "{:.2f}".format(somma))
        entry_tot_bonifici_recuperato.configure(state='disabled')
    def updateUsciteVarie(*args):
        #Aggiorna totale uscite varie
        somma=0
        for item in lista_uscite_varie:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_tot_uscite_varie.configure(state='normal')
        entry_tot_uscite_varie.delete(0,'end')
        entry_tot_uscite_varie.insert('end', "{:.2f}".format(somma))
        entry_tot_uscite_varie.configure(state='disabled')
    def updateVersamenti(*args):
        #Aggiorna totale versamenti
        somma=0
        for item in lista_versamenti:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_tot_versamenti.configure(state='normal')
        entry_tot_versamenti.delete(0,'end')
        entry_tot_versamenti.insert('end', "{:.2f}".format(somma))
        entry_tot_versamenti.configure(state='disabled')
    def updateMarchirolo(*args):
        #Aggiorna totale marchirolo
        somma=0
        for item in lista_marchirolo:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_tot_marchirolo.configure(state='normal')
        entry_tot_marchirolo.delete(0,'end')
        entry_tot_marchirolo.insert('end', "{:.2f}".format(somma))
        entry_tot_marchirolo.configure(state='disabled')
    def updateTotaleMarchirolo(*args):
        #print("Aggiorna saldo cassa")
        try: a=fondo_cassa_da_riportare.get()
        except: a=0
        try: b=totale_marchirolo.get()
        except: b=0
        result=a-b
        entry_saldocassa.configure(state='normal')
        entry_saldocassa.delete(0,'end')
        entry_saldocassa.insert('end', "{:.2f}".format(result))
        entry_saldocassa.configure(state='disabled')
    def updateTotaleSospesi(*args):
        #Aggiorna totale parziale 1
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_per_conto.get()
        except: b=0
        try: c=incasso_das.get()
        except: c=0
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')

        #print("Aggiorna Incasso contanti")
        try: g=totale_incassi_vittoria.get()
        except: g=0
        try: h=incasso_polizze_bonifici.get()
        except: h=0
        try: i=incasso_polizze_carte_pos.get()
        except: i=0
        try: j=totale_sospesi.get()
        except: j=0
        result2=g-h-i-j
        entry_incassicontante.configure(state='normal')
        entry_incassicontante.delete(0,'end')
        entry_incassicontante.insert('end', "{:.2f}".format(result2))
        entry_incassicontante.configure(state='disabled')

        #Aggiorna saldo sospesi
        try: k=totale_sospesi.get()
        except: k=0
        try: l=totale_recupero_sospesi.get()
        except: l=0
        result3=k-l
        entry_saldo_sospesi.configure(state='normal')
        entry_saldo_sospesi.delete(0,'end')
        entry_saldo_sospesi.insert('end', "{:.2f}".format(result3))
        entry_saldo_sospesi.configure(state='disabled')
    def updateUsciteVersamenti(*args):
        #print("Aggiorna Totale generale uscite")
        try: a=totale_abbuoni.get()
        except: a=0
        try: b=totale_uscite_varie.get()
        except: b=0
        try: c=totale_uscite_versamenti.get()
        except: c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_tot_generaleuscite.configure(state='normal')
        entry_tot_generaleuscite.delete(0,'end')
        entry_tot_generaleuscite.insert('end', "{:.2f}".format(result))
        entry_tot_generaleuscite.configure(state='disabled')
    def updateAssegni(*args):
        print("Entry assegni cambiata")
        #Aggiorna
    
    def updateIncassoContante(*args):
        print("Entry incasso contanti cambiata")
        #Aggiorna

    def updateSaldoSospesi(*args):
        print("Entry saldo sospesi cambiata")
        #Aggiorna
    def updatePuntiViva(*args):
        #print("Aggiorna Totale generale uscite")
        try: a=totale_abbuoni.get()
        except: a=0
        try: b=totale_uscite_varie.get()
        except: b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_tot_generaleuscite.configure(state='normal')
        entry_tot_generaleuscite.delete(0,'end')
        entry_tot_generaleuscite.insert('end', "{:.2f}".format(result))
        entry_tot_generaleuscite.configure(state='disabled')
     


    #VARIABLES DECLARATION
    totale_incassi_vittoria = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_incassi_vittoria.trace("w", updateIncassiVittoria)
    incasso_per_conto = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    incasso_per_conto.trace("w", updateIncassoPerConto)
    incasso_das = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    incasso_das.trace("w", updateIncassoDAS)
    totale_bonifici = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_bonifici.trace("w", updateTotaleBonifici)
    incasso_polizze_bonifici = ctk.DoubleVar(creaprova, "{:.2f}".format(0))   
    incasso_polizze_bonifici.trace("w", updateIncassoPolizzeBonifici)
    totale_carte_pos = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_carte_pos.trace("w", updateTotaleCartePOS)
    incasso_polizze_carte_pos = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    incasso_polizze_carte_pos.trace("w", updateIncassoPolizzeCartePOS)
    totale_sospesi = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_sospesi.trace("w", updateTotaleSospesi)
    totale_parziale_1 = ctk.DoubleVar(creaprova, "{:.2f}".format(0))                   #totale_incassi_vittoria+incasso_per_conto+incasso_das-totale_bonifici-totale_carte_pos-totale_sospesi
    totale_parziale_1.trace("w", updateTotaleParziale1)
    fondo_cassa_precedente = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    fondo_cassa_precedente.trace("w", updateFondoCassaPrecedente)
    incassi_contante = ctk.DoubleVar(creaprova, "{:.2f}".format(0))                    #totale_incassi_vittoria - incasso_polizze_bonifici - incasso_polizze_carte_pos - totale_sospesi
    totale_parziale_2 = ctk.DoubleVar(creaprova, "{:.2f}".format(0))                   #totale_parziale_2 + fondo_cassa_precedente
    totale_parziale_2.trace("w", updateTotaleParziale2)
    totale_recupero_sospesi_contanti = ctk.DoubleVar(creaprova, "{:.2f}".format(0))    #somma array recupero_sospesi_contanti
    totale_recupero_sospesi_contanti.trace("w", updateTotaleRecuperoSospesiContanti)
    totale_recupero_sospesi_carte_pos = ctk.DoubleVar(creaprova, "{:.2f}".format(0))   #somma array recupero_sospesi_carte_pos
    totale_recupero_sospesi_carte_pos.trace("w", updateTotaleRecuperoSospesiCartePOS)
    totale_recupero_sospesi_bonifici = ctk.DoubleVar(creaprova, "{:.2f}".format(0))    #somma array recupero_sospesi_bonifici
    totale_recupero_sospesi_bonifici.trace("w", updateTotaleRecuperoSospesiBonifici)
    totale_recupero_sospesi = ctk.DoubleVar(creaprova, "{:.2f}".format(0))             #totale_recupero_sospesi_contanti + totale_recupero_sospesi_carte_pos + totale_recupero_sospesi_bonifici
    totale_recupero_sospesi.trace("w", updateTotaleRecuperoSospesi)
    totale_cassa_contante = ctk.DoubleVar(creaprova, "{:.2f}".format(0))               #totale_parziale_2 + totale_recupero_sospesi
    totale_cassa_contante.trace("w", updateTotaleCassaContante)
    totale_abbuoni = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_abbuoni.trace("w", updateTotaleAbbuoni)
    totale_uscite_varie = ctk.DoubleVar(creaprova, "{:.2f}".format(0))                 #uscite_varie + uscite_versamenti
    totale_uscite_varie.trace("w", updateTotaleUsciteVarie)
    totale_uscite_versamenti = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_uscite_versamenti.trace("w", updateUsciteVersamenti)
    totale_generale_uscite = ctk.DoubleVar(creaprova, "{:.2f}".format(0))              #totale_abbuoni + totale_uscite_varie
    totale_generale_uscite.trace("w", updateTotaleGeneraleUscite)
    fondo_cassa_da_riportare = ctk.DoubleVar(creaprova, "{:.2f}".format(0))            #totale_cassa_contante - totale_generale_uscite
    fondo_cassa_da_riportare.trace("w", updateFondoCassaDaRiportare)
    totale_marchirolo = ctk.DoubleVar(creaprova, "{:.2f}".format(0))                   #somma array somme_marchirolo
    totale_marchirolo.trace("w", updateTotaleMarchirolo)
    saldo_cassa = ctk.DoubleVar(creaprova, "{:.2f}".format(0))                         #fondo_cassa_da_riportare - totale_marchirolo - totale_mimmo - totale_ditta
    incasso_assegni = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    incasso_assegni.trace("w", updateAssegni)
    incasso_contante = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    incasso_contante.trace("w", updateIncassoContante)
    saldo_sospesi = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    saldo_sospesi.trace("w", updateSaldoSospesi)
    punti_viva = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    punti_viva.trace("w", updatePuntiViva)
    commenti = ctk.StringVar(creaprova, "")



    #----TAB INCASSI----
    #Create frame inside the tab
    frame_incassi = ctk.CTkFrame(master=tabview.tab("Incassi"))
    frame_incassi.pack(pady=(20,0))
    #Incassi Vittoria
    label_incassi_vittoria = ctk.CTkLabel(master=frame_incassi, text="Premio lordo:")
    label_incassi_vittoria.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_incassi_vittoria = ctk.CTkEntry(frame_incassi, textvariable=totale_incassi_vittoria, width=100)
    entry_incassi_vittoria.grid(row=0, column=1, pady=10, padx=20, sticky="nw")
    #Incasso per conto
    label_incasso_conto = ctk.CTkLabel(master=frame_incassi, text="Incasso per conto:")
    label_incasso_conto.grid(row=1, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_conto = ctk.CTkEntry(frame_incassi, textvariable=incasso_per_conto, width=100)
    entry_incasso_conto.grid(row=1, column=1, pady=10, padx=20, sticky="nw")
    #Incasso DAS
    label_incasso_das = ctk.CTkLabel(master=frame_incassi, text="Incasso DAS:")
    label_incasso_das.grid(row=2, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_das = ctk.CTkEntry(frame_incassi, textvariable=incasso_das, width=100)
    entry_incasso_das.grid(row=2, column=1, pady=10, padx=20, sticky="nw")
    #Incasso bonifici
    label_incasso_bonifici = ctk.CTkLabel(master=frame_incassi, text="Movimenti bancari:")
    label_incasso_bonifici.grid(row=3, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_bonifici = ctk.CTkEntry(frame_incassi, textvariable=totale_bonifici, width=100)
    entry_incasso_bonifici.grid(row=3, column=1, pady=10, padx=20, sticky="nw")
    #Incasso polizze bonifici
    label_incasso_polizzebonifici = ctk.CTkLabel(master=frame_incassi, text="Incasso polizze bonifici:", font=("Helvetica",14,"bold"))
    label_incasso_polizzebonifici.grid(row=4, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_polizzebonifici = ctk.CTkEntry(frame_incassi, textvariable=incasso_polizze_bonifici, state="disabled", font=("Helvetica",15,"bold"), width=100)
    entry_incasso_polizzebonifici.grid(row=4, column=1, pady=10, padx=20, sticky="nw")
    #Incasso carte/POS
    label_incasso_cartepos = ctk.CTkLabel(master=frame_incassi, text="Totale carte/POS:")
    label_incasso_cartepos.grid(row=5, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_cartepos = ctk.CTkEntry(frame_incassi, textvariable=totale_carte_pos, width=100)
    entry_incasso_cartepos.grid(row=5, column=1, pady=10, padx=20, sticky="nw")
    #Incasso polizze carte/POS
    label_incasso_polizzecartepos = ctk.CTkLabel(master=frame_incassi, text="Incasso polizze carte/POS:", font=("Helvetica",14,"bold"))
    label_incasso_polizzecartepos.grid(row=6, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_polizzecartepos = ctk.CTkEntry(frame_incassi, textvariable=incasso_polizze_carte_pos, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_incasso_polizzecartepos.grid(row=6, column=1, pady=10, padx=20, sticky="nw")
    #Incasso contante
    label_incasso_contante = ctk.CTkLabel(master=frame_incassi, text="Contanti:")
    label_incasso_contante.grid(row=7, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_contante = ctk.CTkEntry(frame_incassi, textvariable=incasso_contante, width=100)
    entry_incasso_contante.grid(row=7, column=1, pady=10, padx=20, sticky="nw")
    #Incasso assegni
    label_incasso_assegni = ctk.CTkLabel(master=frame_incassi, text="Assegni:")
    label_incasso_assegni.grid(row=8, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_assegni = ctk.CTkEntry(frame_incassi, textvariable=incasso_assegni, width=100)
    entry_incasso_assegni.grid(row=8, column=1, pady=10, padx=20, sticky="nw")



    #----TAB SOSPESI----
    #Create frame inside the tab
    frame_sospesi = ctk.CTkScrollableFrame(master=tabview.tab("Sospesi"), width=500, height=300, border_color="black", border_width=1)
    frame_sospesi.pack()
    #LISTA SOSPESI
    #Aggiungi sospeso
    def addSospeso():
        #Elimina sospeso
        def destroy():
            var1.set(0)
            lista_sospesi_values.remove(var1)
            lista_sospesi_causali.remove(ent2)
            frame.pack_forget()
            print("Sospeso eliminato")
        print ("Sospeso aggiunto")
        frame = ctk.CTkFrame(frame_sospesi)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_sospesi, "{:.2f}".format(0))
        var1.trace("w", updateSospesi)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        #lista_sospesi.append( (ent1, ent2) )
        lista_sospesi_values.append(var1)
        lista_sospesi_causali.append(ent2)
    #Print all entries
    #def showSospesi():
    #    for number, (ent1, ent2) in enumerate(lista_sospesi_values):
    #        print (number, ent1.get(), ent2.get())
    #lista_sospesi = []
    lista_sospesi_values = []
    lista_sospesi_causali = []
    #showButton = ctk.CTkButton(frame_sospesi, text='Stampa tutti i sospesi', command=showSospesi)
    #showButton.pack()
    addboxButton = ctk.CTkButton(frame_sospesi, text='Aggiungi sospeso', command=addSospeso)
    addboxButton.pack(padx=20, pady=20)

    #Totale sospesi
    label_sospesi = ctk.CTkLabel(master=tabview.tab("Sospesi"), text="Totale sospesi:", font=("Helvetica",14,"bold"))
    label_sospesi.pack(side="left", anchor="ne", pady=(25,0), padx=10, expand="True")
    entry_sospesi = ctk.CTkEntry(tabview.tab("Sospesi"), textvariable=totale_sospesi, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_sospesi.pack(side="right", anchor="nw", pady=(25,0), expand="True")



    #----TAB RECUPERO SOSPESI----
    frame_recuperosospesi = ctk.CTkScrollableFrame(master=tabview.tab("Recupero sospesi"), width=500, height=480, border_color="black", border_width=1)
    frame_recuperosospesi.pack()
    #--Sospeso recuperato CONTANTI--
    frame_recuperosospesi_contante = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_recuperosospesi_contante.pack()

    def addSospContante():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            lista_recupero_contanti.remove(var1)
            lista_recupero_contanti_causali.remove(ent2)
            frame.pack_forget()
            print("Sospeso contante eliminato")
        print ("Sospeso recuperato contante aggiunto")
        frame = ctk.CTkFrame(frame_recuperosospesi_contante)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_recuperosospesi_contante, "{:.2f}".format(0))
        var1.trace("w", updateRecuperoContanti)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        lista_recupero_contanti.append(var1)
        lista_recupero_contanti_causali.append(ent2)
    lista_recupero_contanti = []
    lista_recupero_contanti_causali = []

    add_contante_recuperato = ctk.CTkButton(frame_recuperosospesi_contante, text='Aggiungi contante recuperato', command=addSospContante)
    add_contante_recuperato.pack(padx=20, pady=(20,0))

    #Totale contante recuperato
    frame_contanterecuperato = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_contanterecuperato.pack()
    label_tot_contante_recuperato = ctk.CTkLabel(master=frame_contanterecuperato, text="Totale sospesi contanti recuperato:", font=("Helvetica",14,"bold"))
    label_tot_contante_recuperato.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_contante_recuperato = ctk.CTkEntry(frame_contanterecuperato, textvariable=totale_recupero_sospesi_contanti, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_contante_recuperato.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #--Sospeso recuperato CARTE/POS--
    frame_recuperosospesi_cartapos = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_recuperosospesi_cartapos.pack()

    def addSospCartePOS():
        #Elimina sospeso carta/POS
        def destroy():
            var1.set(0)
            lista_recupero_cartepos.remove(var1)
            lista_recupero_cartepos_causali.remove(ent2)
            frame.pack_forget()
            print("Sospeso carta/POS eliminato")
        print ("Sospeso recuperato carta/POS aggiunto")
        frame = ctk.CTkFrame(frame_recuperosospesi_cartapos)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_recuperosospesi_cartapos, "{:.2f}".format(0))
        var1.trace("w", updateRecuperoCartePOS)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        lista_recupero_cartepos.append(var1)
        lista_recupero_cartepos_causali.append(ent2)
    lista_recupero_cartepos = []
    lista_recupero_cartepos_causali = []

    add_cartapos_recuperato = ctk.CTkButton(frame_recuperosospesi_cartapos, text='Aggiungi Carta/POS recuperato', command=addSospCartePOS)
    add_cartapos_recuperato.pack(pady=(25,0))
    #Totale carte/POS recuperato
    frame_carteposrecuperato = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_carteposrecuperato.pack()
    label_tot_cartapos_recuperato = ctk.CTkLabel(master=frame_carteposrecuperato, text="Totale sospesi carte/POS recuperato:", font=("Helvetica",14,"bold"))
    label_tot_cartapos_recuperato.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_cartapos_recuperato = ctk.CTkEntry(frame_carteposrecuperato, textvariable=totale_recupero_sospesi_carte_pos, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_cartapos_recuperato.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #--Sospeso recuperato bonifici--
    frame_recuperosospesi_bonifici = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_recuperosospesi_bonifici.pack()

    def addSospBonifici():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            lista_recupero_bonifici.remove(var1)
            lista_recupero_bonifici_causali.remove(ent2)
            frame.pack_forget()
            print("Sospeso bonifico eliminato")
        print ("Sospeso recuperato bonifico aggiunto")
        frame = ctk.CTkFrame(frame_recuperosospesi_bonifici)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_recuperosospesi_bonifici, "{:.2f}".format(0))
        var1.trace("w", updateRecuperoBonifici)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        lista_recupero_bonifici.append(var1)
        lista_recupero_bonifici_causali.append(ent2)
    lista_recupero_bonifici = []
    lista_recupero_bonifici_causali = []

    add_bonifici_recuperato = ctk.CTkButton(frame_recuperosospesi_bonifici, text='Aggiungi bonifico recuperato', command=addSospBonifici)
    add_bonifici_recuperato.pack(pady=(25,0))
    #Totale bonifici recuperato
    frame_bonificirecuperato = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_bonificirecuperato.pack()
    label_tot_bonifici_recuperato = ctk.CTkLabel(master=frame_bonificirecuperato, text="Totale sospesi bonifici recuperato:", font=("Helvetica",14,"bold"))
    label_tot_bonifici_recuperato.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_bonifici_recuperato = ctk.CTkEntry(frame_bonificirecuperato, textvariable=totale_recupero_sospesi_bonifici, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_bonifici_recuperato.grid(row=0, column=1, pady=20, padx=10, sticky="nw")


    #Frame totali
    frame_recuperosospesi_totali = ctk.CTkFrame(master=tabview.tab("Recupero sospesi"))
    frame_recuperosospesi_totali.pack(pady=(20,0))
    #--Totale recupero sospesi--
    label_tot_recuperosospesi = ctk.CTkLabel(master=frame_recuperosospesi_totali, text="Totale recupero sospesi:", font=("Helvetica",14,"bold"))
    label_tot_recuperosospesi.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_recuperosospesi = ctk.CTkEntry(frame_recuperosospesi_totali, textvariable=totale_recupero_sospesi, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_recuperosospesi.grid(row=0, column=1, pady=10, padx=20, sticky="nw")
    #--Totale cassa contanti--
    label_tot_cassacontanti = ctk.CTkLabel(master=frame_recuperosospesi_totali, text="Totale cassa contanti:", font=("Helvetica",14,"bold"))
    label_tot_cassacontanti.grid(row=1, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_cassacontanti = ctk.CTkEntry(frame_recuperosospesi_totali, textvariable=totale_cassa_contante, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_cassacontanti.grid(row=1, column=1, pady=10, padx=20, sticky="nw")

    #----TAB USCITE----
    frame_uscite_abbuoniviva = ctk.CTkFrame(master=tabview.tab("Uscite"))
    frame_uscite_abbuoniviva.pack()
    #--Abbuoni--
    label_abbuoni = ctk.CTkLabel(master=frame_uscite_abbuoniviva, text="Totale abbuoni:")
    label_abbuoni.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_abbuoni = ctk.CTkEntry(frame_uscite_abbuoniviva, textvariable=totale_abbuoni, width=100)
    entry_abbuoni.grid(row=0, column=1, pady=10, padx=20, sticky="nw")

    #--Punti VIVA--
    label_viva = ctk.CTkLabel(master=frame_uscite_abbuoniviva, text="Totale punti Viva:")
    label_viva.grid(row=1, column=0, pady=10, padx=20, sticky="ne")
    entry_viva = ctk.CTkEntry(frame_uscite_abbuoniviva, textvariable=punti_viva, width=100)
    entry_viva.grid(row=1, column=1, pady=10, padx=20, sticky="nw")

    frame_uscitevarieandversamenti = ctk.CTkScrollableFrame(master = tabview.tab("Uscite"), width=500, height=450, border_color="black", border_width=1)
    frame_uscitevarieandversamenti.pack()
    #--Aggiungi VERSAMENTI--
    frame_versamenti = ctk.CTkFrame(master=frame_uscitevarieandversamenti)
    frame_versamenti.pack()
    def addVersamento():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            lista_versamenti.remove(var1)
            lista_versamenti_causali.remove(ent2)
            frame.pack_forget()
            print("Versamento eliminato")
        print ("Versamento aggiunta")
        frame = ctk.CTkFrame(frame_versamenti)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_versamenti, "{:.2f}".format(0))
        var1.trace("w", updateVersamenti)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        lista_versamenti.append(var1)
        lista_versamenti_causali.append(ent2)
    lista_versamenti = []
    lista_versamenti_causali = []

    add_versamento = ctk.CTkButton(frame_versamenti, text='Aggiungi versamento', command=addVersamento)
    add_versamento.pack(padx=20, pady=(20,0))
    #Totale versamenti
    frame_usciteversamenti = ctk.CTkFrame(master=frame_uscitevarieandversamenti)
    frame_usciteversamenti.pack()
    label_tot_versamenti = ctk.CTkLabel(master=frame_usciteversamenti, text="Totale versamenti:", font=("Helvetica",14,"bold"))
    label_tot_versamenti.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_versamenti = ctk.CTkEntry(frame_usciteversamenti, textvariable=totale_uscite_versamenti, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_versamenti.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #--Aggiungi USCITE VARIE--
    frame_uscite_varie = ctk.CTkFrame(master=frame_uscitevarieandversamenti)
    frame_uscite_varie.pack()
    def addUsciteVarie():
        #Elimina uscita varia
        def destroy():
            var1.set(0)
            lista_uscite_varie.remove(var1)
            lista_uscite_varie_causali.remove(ent2)
            frame.pack_forget()
            print("Uscita varia eliminata")
        print ("Uscita varia aggiunta")
        frame = ctk.CTkFrame(frame_uscite_varie)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_uscite_varie, "{:.2f}".format(0))
        var1.trace("w", updateUsciteVarie)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        lista_uscite_varie.append(var1)
        lista_uscite_varie_causali.append(ent2)
    lista_uscite_varie = []
    lista_uscite_varie_causali = []

    add_uscite_varie = ctk.CTkButton(frame_uscite_varie, text='Aggiungi uscite varie', command=addUsciteVarie)
    add_uscite_varie.pack(padx=20, pady=(20,0))
    #Totale uscite varie
    frame_totaleuscitevarie = ctk.CTkFrame(master=frame_uscitevarieandversamenti)
    frame_totaleuscitevarie.pack()
    label_tot_uscite_varie = ctk.CTkLabel(master=frame_totaleuscitevarie, text="Totale uscite varie:", font=("Helvetica",14,"bold"))
    label_tot_uscite_varie.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_uscite_varie = ctk.CTkEntry(frame_totaleuscitevarie, textvariable=totale_uscite_varie, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_uscite_varie.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    frame_uscitetotali = ctk.CTkFrame(master=tabview.tab("Uscite"))
    frame_uscitetotali.pack(pady=(20,0))
    #--Fondo cassa da riportare--
    label_fondodariportare = ctk.CTkLabel(master=frame_uscitetotali, text="Fondo cassa da riportare:", font=("Helvetica",14,"bold"))
    label_fondodariportare.grid(row=1, column=0, pady=10, padx=10, sticky="ne")
    entry_fondodariportare = ctk.CTkEntry(frame_uscitetotali, textvariable=fondo_cassa_da_riportare, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_fondodariportare.grid(row=1, column=1, pady=10, padx=10, sticky="nw")

    #----TAB MARCHIROLO----
    frame_marchirolo = ctk.CTkScrollableFrame(master=tabview.tab("Marchirolo"), width=500, height=300, border_color="black", border_width=1)
    frame_marchirolo.pack()
    def addUscitaMarchirolo():
        #Elimina sospeso carta/POS
        def destroy():
            var1.set(0)
            lista_marchirolo.remove(var1)
            lista_marchirolo_causali.remove(ent2)
            frame.pack_forget()
            print("Marchirolo eliminato")
        print ("Uscita marchirolo aggiunta")
        frame = ctk.CTkFrame(frame_marchirolo)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_marchirolo, "{:.2f}".format(0))
        var1.trace("w", updateMarchirolo)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        lista_marchirolo.append(var1)
        lista_marchirolo_causali.append(ent2)
    lista_marchirolo = []
    lista_marchirolo_causali = []

    add_uscitamarchirolo = ctk.CTkButton(frame_marchirolo, text='Aggiungi uscita Marchirolo', command=addUscitaMarchirolo)
    add_uscitamarchirolo.pack(padx=20, pady=(20,0))

    #Totale Marchirolo
    frame_uscitemarchirolo = ctk.CTkFrame(master=frame_uscitevarieandversamenti)
    frame_uscitemarchirolo.pack()
    label_tot_marchirolo = ctk.CTkLabel(master=tabview.tab("Marchirolo"), text="Totale Marchirolo:", font=("Helvetica",14,"bold"))
    label_tot_marchirolo.pack(side="left", anchor="ne", pady=(25,0), padx=10, expand="True")
    entry_tot_marchirolo = ctk.CTkEntry(tabview.tab("Marchirolo"), textvariable=totale_marchirolo, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_marchirolo.pack(side="right", anchor="nw", pady=(25,0), expand="True")

    #----TAB RESCONTO----
    #Create frame inside the tab
    frame_resoconto = ctk.CTkFrame(master=tabview.tab("Resoconto"))
    frame_resoconto.pack(pady=(20,0))
    #Totale parziale 1
    label_tot_parziale_1 = ctk.CTkLabel(master=frame_resoconto, text="Totale parziale 1:", font=("Helvetica",14,"bold"))
    label_tot_parziale_1.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_parziale_1 = ctk.CTkEntry(frame_resoconto, textvariable=totale_parziale_1, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_parziale_1.grid(row=0, column=1, pady=10, padx=20, sticky="nw")
    explain_tot_parziale_1 = ctk.CTkLabel(master=frame_resoconto, text="Incassi - bonifici - POS - sospesi", text_color="#969595", font=("Helvetica",13))
    explain_tot_parziale_1.grid(row=0, column=2, pady=10, padx=20, sticky="nw")
    #Fondo cassa precedente
    label_cassaprecedente = ctk.CTkLabel(master=frame_resoconto, text="Fondo cassa precedente:", font=("Helvetica",14,"bold"))
    label_cassaprecedente.grid(row=1, column=0, pady=10, padx=20, sticky="ne")
    entry_cassaprecedente = ctk.CTkEntry(frame_resoconto, textvariable=fondo_cassa_precedente, font=("Helvetica",15,"bold"), width=100)
    entry_cassaprecedente.grid(row=1, column=1, pady=10, padx=20, sticky="nw")
    label_daybefore = ctk.CTkLabel(master=frame_resoconto, text="Non trovato", text_color="#969595", font=("Helvetica",13))
    label_daybefore.grid(row=1, column=2, pady=10, padx=20, sticky="nw")
    #Incassi contante
    label_incassicontante = ctk.CTkLabel(master=frame_resoconto, text="Incassi contante:", font=("Helvetica",14,"bold"))
    label_incassicontante.grid(row=3, column=0, pady=10, padx=20, sticky="ne")
    entry_incassicontante = ctk.CTkEntry(frame_resoconto, textvariable=incassi_contante, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_incassicontante.grid(row=3, column=1, pady=10, padx=20, sticky="nw")
    explain_incassi_contante = ctk.CTkLabel(master=frame_resoconto, text="Tot. parz. 2 + tot. rec. sosp. contante", text_color="#969595", font=("Helvetica",13))
    explain_incassi_contante.grid(row=3, column=2, pady=10, padx=20, sticky="nw")
    #Saldo sospesi
    label_saldo_sospesi = ctk.CTkLabel(master=frame_resoconto, text="Saldo sospesi:", font=("Helvetica",14,"bold"))
    label_saldo_sospesi.grid(row=4, column=0, pady=10, padx=20, sticky="ne")
    entry_saldo_sospesi = ctk.CTkEntry(frame_resoconto, textvariable=saldo_sospesi, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_saldo_sospesi.grid(row=4, column=1, pady=10, padx=20, sticky="nw")
    explain_saldo_sospesi = ctk.CTkLabel(master=frame_resoconto, text="Sospesi - rec. sospesi", text_color="#969595", font=("Helvetica",13))
    explain_saldo_sospesi.grid(row=4, column=2, pady=10, padx=20, sticky="nw")
    #Totale parziale 2
    label_tot_parziale_2 = ctk.CTkLabel(master=frame_resoconto, text="Totale parziale 2:", font=("Helvetica",14,"bold"))
    label_tot_parziale_2.grid(row=5, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_parziale_2 = ctk.CTkEntry(frame_resoconto, textvariable=totale_parziale_2, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_parziale_2.grid(row=5, column=1, pady=10, padx=20, sticky="nw")
    explain_tot_parziale_2 = ctk.CTkLabel(master=frame_resoconto, text="Tot. parz. 1 + fondo cassa precedente", text_color="#969595", font=("Helvetica",13))
    explain_tot_parziale_2.grid(row=5, column=2, pady=10, padx=20, sticky="nw")
    #--Totale generale uscite--
    label_tot_generaleuscite = ctk.CTkLabel(master=frame_resoconto, text="Totale generale uscite:", font=("Helvetica",14,"bold"))
    label_tot_generaleuscite.grid(row=6, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_generaleuscite = ctk.CTkEntry(frame_resoconto, textvariable=totale_generale_uscite, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_generaleuscite.grid(row=6, column=1, pady=10, padx=20, sticky="nw")
    explain_tot_generaleuscite = ctk.CTkLabel(master=frame_resoconto, text="Abbuoni + p.ti Viva + uscite varie + versamenti", text_color="#969595", font=("Helvetica",13))
    explain_tot_generaleuscite.grid(row=6, column=2, pady=10, padx=20, sticky="nw")
    #Totale Marchirolo COPIA
    label_tot_marchirolo_copy = ctk.CTkLabel(master=frame_resoconto, text="Totale Marchirolo:", font=("Helvetica",14,"bold"))
    label_tot_marchirolo_copy.grid(row=7, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_marchirolo_copy = ctk.CTkEntry(frame_resoconto, textvariable=totale_marchirolo, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_marchirolo_copy.grid(row=7, column=1, pady=10, padx=20, sticky="nw")
    explain_tot_marchirolo_copy = ctk.CTkLabel(master=frame_resoconto, text="Totale uscite Marchirolo", text_color="#969595", font=("Helvetica",13))
    explain_tot_marchirolo_copy.grid(row=7, column=2, pady=10, padx=20, sticky="nw")
    #Saldo cassa
    label_saldocassa = ctk.CTkLabel(master=frame_resoconto, text="Saldo cassa:", font=("Helvetica",14,"bold"))
    label_saldocassa.grid(row=8, column=0, pady=10, padx=20, sticky="ne")
    entry_saldocassa = ctk.CTkEntry(frame_resoconto, textvariable=saldo_cassa, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_saldocassa.grid(row=8, column=1, pady=10, padx=20, sticky="nw")
    explain_saldocassa = ctk.CTkLabel(master=frame_resoconto, text="F. cass da riportare + tot. Marchirolo", text_color="#969595", font=("Helvetica",13))
    explain_saldocassa.grid(row=8, column=2, pady=10, padx=20, sticky="nw")
    #Commenti
    label_commenti = ctk.CTkLabel(master=tabview.tab("Resoconto"), text="Commenti:")
    label_commenti.pack()
    entry_commenti = ctk.CTkTextbox(tabview.tab("Resoconto"), height=100, width=300, border_width=2)
    entry_commenti.pack()


    #----TAB DOCUMENTI----
    def apriDocumenti():
        #Splitta data
        dataperfile = (today_date_formatted.get()).split('-')
        #Controlla se la cartella del giorno esiste, in caso creala
        if not os.path.exists(percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]):     
            os.makedirs(percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0])
        path = percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]    #DEVE ESSERE IL PERCORSO COMPLETO PER FAR FUNZIONARE WEBBROWSER
        webbrowser.open('file:///' + path)

    apri_cartella_documenti = ctk.CTkButton(tabview.tab("Documenti"), text='Apri documenti', command=apriDocumenti)
    apri_cartella_documenti.pack(padx=20, pady=(20,0))

    def uploadFile():
        #Comando associato al tasto Sfoglia
        def chooseFile():
            inputfile_path = ""
            inputfile_path = ctk.filedialog.askopenfilename()
            entry_inputfile.delete(0, 'end')  # Remove current text in entry
            entry_inputfile.insert(0, inputfile_path)  # Insert the 'path'
        #Comando associato al tasto Carica
        def loadFile():
            new_filename = entry_outputfilename.get()
            original_path = entry_inputfile.get()
            fullpath, file_extension = os.path.splitext(original_path)
            head, tail = os.path.split(original_path)
            print(tail)
            dataperfile = (today_date_formatted.get()).split('-')
            #Se la cartella della categoria non esiste, creala
            if not os.path.exists(percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()):     
                os.makedirs(percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get())
            #Se dai un nuovo nome al file
            if(new_filename != ""):
                #os.rename(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)
                #os.replace(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)
                shutil.move(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)    
                print("File caricato")
            #Altrimenti spostalo con lo stesso nome
            else:
                #os.rename(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+filename+file_extension)
                #os.replace(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+filename+file_extension)
                shutil.move(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+tail)    
                print("File caricato")
            showConfirmMessage(creaprova, "Successo","Documento correttamente caricato", "check", False)
            frame.destroy()
        frame = ctk.CTkFrame(tabview.tab("Documenti"))
        frame.pack(padx=20, pady=10)
        input_button = ctk.CTkButton(frame, text="Sfoglia", command=chooseFile, width=60)
        input_button.grid(row=0, column=0)
        entry_inputfile = ctk.CTkEntry(frame, width=250, placeholder_text="Scegli file da spostare...")
        entry_inputfile.grid(row=0, column=1)
        entry_outputcategory = ctk.CTkComboBox(frame, values=("Bonifici", "Movimenti POS", "Versamenti", "Assegni", "Quadratura punto vendita", "Recupero sospesi", "Chiusure POS", "Quitanze", "Foglio cassa", "Altro"))
        entry_outputcategory.grid(row=0, column=3)
        entry_outputfilename = ctk.CTkEntry(frame, width=250, placeholder_text="Rinomina il file...")
        entry_outputfilename.grid(row=0, column=4)
        loadfile_button = ctk.CTkButton(frame, image=upload_icon, text="", width=30, command=loadFile)
        loadfile_button.grid(row=0, column=5)

    carica_documento = ctk.CTkButton(tabview.tab("Documenti"), text='Carica documento', command=uploadFile)
    carica_documento.pack(padx=20, pady=(20,0))
    


    def sendToDatabase():
        conn = sqlite3.connect(percorso_database)
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
        #Crea tabelle se non esistono
        c.execute("""CREATE TABLE IF NOT EXISTS prova(
            data DATE,
            totale_incassi_vittoria DOUBLE,
            incasso_per_conto DOUBLE,
            incasso_das DOUBLE,
            totale_bonifici DOUBLE,
            incasso_polizze_bonifici DOUBLE,
            totale_carte_pos DOUBLE,
            incasso_polizze_carte_pos DOUBLE,
            totale_sospesi DOUBLE,
            totale_parziale_1 DOUBLE,
            fondo_cassa_precedente DOUBLE,
            incassi_contante DOUBLE,
            totale_parziale_2 DOUBLE,
            totale_recupero_sospesi_contanti DOUBLE,
            totale_recupero_sospesi_carte_pos DOUBLE,
            totale_recupero_sospesi_bonifici DOUBLE,
            totale_recupero_sospesi DOUBLE,
            totale_cassa_contante DOUBLE,
            totale_abbuoni DOUBLE,
            totale_uscite_varie DOUBLE,
            totale_uscite_versamenti DOUBLE,
            totale_generale_uscite DOUBLE,
            fondo_cassa_da_riportare DOUBLE,
            totale_marchirolo DOUBLE,
            saldo_cassa DOUBLE,
            completato TEXT,
            incasso_assegni DOUBLE,
            incasso_contante DOUBLE,
            saldo_sospesi DOUBLE,
            punti_viva DOUBLE,
            commenti TEXT,
            PRIMARY KEY(data)
            )"""
        )
        conn.commit()
        c.execute("""CREATE TABLE IF NOT EXISTS liste(
            data DATE,
            categoria TEXT,
            valore DOUBLE,
            causale TEXT,
            CONSTRAINT fk_sospesi_prova FOREIGN KEY (data) REFERENCES prova(data)
            );
            """
        )
        conn.commit()

        #Converti data
        data_converted = (today_date_formatted.get()).split('-')
        data_converted_text=""
        data_converted_text=data_converted[2]+"-"+data_converted[1]+"-"+data_converted[0]

        #Controlla se la data esiste già
        c.execute("SELECT data FROM prova WHERE data='"+data_converted_text+"'")
        maybe_exists = c.fetchall()
        conn.commit()
        if (len(maybe_exists)!=0):
            showConfirmMessage(creaprova, "Attenzione", "Il giorno che stai tentando di creare esiste già", "cancel", False) 
            conn.close()
        else:

            def safeLoad(input):
                try:
                    output = input.get()
                except:
                    output = 0
                return output
            #Aggiungi tutte le entry
            c.execute("INSERT INTO prova VALUES ('"+data_converted_text+"', "
                    +str(safeLoad(totale_incassi_vittoria))+", "
                    +str(safeLoad(incasso_per_conto))+", "
                    +str(safeLoad(incasso_das))+", "
                    +str(safeLoad(totale_bonifici))+", "
                    +str(safeLoad(incasso_polizze_bonifici))+", "
                    +str(safeLoad(totale_carte_pos))+", "
                    +str(safeLoad(incasso_polizze_carte_pos))+", "
                    +str(safeLoad(totale_sospesi))+", "
                    +str(safeLoad(totale_parziale_1))+", "
                    +str(safeLoad(fondo_cassa_precedente))+", "
                    +str(safeLoad(incassi_contante))+", "
                    +str(safeLoad(totale_parziale_2))+", "
                    +str(safeLoad(totale_recupero_sospesi_contanti))+", "
                    +str(safeLoad(totale_recupero_sospesi_carte_pos))+", "
                    +str(safeLoad(totale_recupero_sospesi_bonifici))+", "
                    +str(safeLoad(totale_recupero_sospesi))+", "
                    +str(safeLoad(totale_cassa_contante))+", "
                    +str(safeLoad(totale_abbuoni))+", "
                    +str(safeLoad(totale_uscite_varie))+", "
                    +str(safeLoad(totale_uscite_versamenti))+", "
                    +str(safeLoad(totale_generale_uscite))+", "
                    +str(safeLoad(fondo_cassa_da_riportare))+", "
                    +str(safeLoad(totale_marchirolo))+", "
                    +str(safeLoad(saldo_cassa))+
                    ", 'false', "
                    +str(safeLoad(incasso_assegni))+", "
                    +str(safeLoad(incasso_contante))+", "
                    +str(safeLoad(saldo_sospesi))+", "
                    +str(safeLoad(punti_viva))+", "
                    +"'"+str(entry_commenti.get('0.0','end'))+"'"+")"
            )
            conn.commit()
            
            #Aggiungi liste
            for valore, causale in zip(lista_sospesi_values, lista_sospesi_causali):
                try:
                    if valore.get() != "" and causale.get() != "":
                        c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                                +"'sospesi', "
                                +str(valore.get())+", '"
                                +causale.get()+
                                "')"
                        )
                except:
                    print("Entries vuote non caricate")
            conn.commit()
            for valore, causale in zip(lista_recupero_contanti, lista_recupero_contanti_causali):
                try:
                    if valore.get() != "" and causale.get() != "":
                        c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                                +"'recupero_contanti', "
                                +str(valore.get())+", '"
                                +causale.get()+
                                "')"
                        )
                except:
                    print("Entries vuote non caricate")
            conn.commit()
            for valore, causale in zip(lista_recupero_cartepos, lista_recupero_cartepos_causali):
                try:
                    if valore.get() != "" and causale.get() != "":
                        c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                                +"'recupero_cartepos', "
                                +str(valore.get())+", '"
                                +causale.get()+
                                "')"
                        )
                except:
                    print("Entries vuote non caricate")
            conn.commit()
            for valore, causale in zip(lista_recupero_bonifici, lista_recupero_bonifici_causali):
                try:
                    if valore.get() != "" and causale.get() != "":
                        c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                                +"'recupero_bonifici', "
                                +str(valore.get())+", '"
                                +causale.get()+
                                "')"
                        )
                except:
                    print("Entries vuote non caricate")
            conn.commit()
            for valore, causale in zip(lista_uscite_varie, lista_uscite_varie_causali):
                try:
                    if valore.get() != "" and causale.get() != "":
                        c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                                +"'uscite_varie', "
                                +str(valore.get())+", '"
                                +causale.get()+
                                "')"
                        )
                except:
                    print("Entries vuote non caricate")
            conn.commit()
            for valore, causale in zip(lista_versamenti, lista_versamenti_causali):
                try:
                    if valore.get() != "" and causale.get() != "":
                        c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                                +"'uscite_versamenti', "
                                +str(valore.get())+", '"
                                +causale.get()+
                                "')"
                        )
                except:
                    print("Entries vuote non caricate")
            conn.commit()
            for valore, causale in zip(lista_marchirolo, lista_marchirolo_causali):
                try:
                    if valore.get() != "" and causale.get() != "":
                        c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                                +"'marchirolo', "
                                +str(valore.get())+", '"
                                +causale.get()+
                                "')"
                        )
                except:
                    print("Entries vuote non caricate")
            conn.commit()  

            conn.close()
            showConfirmMessage(creaprova, "Caricamento completato", "Dati correttamente aggiunti al database", "check", True)

    #----SAVE BUTTON----
    save_btn = ctk.CTkButton(creaprova, text='Salva', fg_color="#809d5f", hover_color="#B7C019", command=sendToDatabase)
    #save_btn.pack()
    save_btn.pack(side="bottom", pady=(0,5))
    #------FINE CREAZIONE GUI------

    #Ottieni fondo cassa dal giorno precedente
    updateData()

    #Show window
    creaprova.mainloop()


#****VISUALIZZA DATABASE****
def visualizzaProva():
    home.destroy()
    #root
    visualizzaprova = ctk.CTk()
    visualizzaprova.title("Visualizza prova giornaliera")

    app_size = str(app_width)+str(app_height)
    visualizzaprova.geometry(app_size)
    visualizzaprova.minsize(app_width-250, app_height)

    #Place window in center of screen
    ws = visualizzaprova.winfo_screenwidth()
    hs = visualizzaprova.winfo_screenheight()
    x = (ws/2) - (app_width/2)
    y = (hs/2) - (app_height/2)
    visualizzaprova.geometry('%dx%d+%d+%d' % (app_width, app_height, x, y))



    #UPDATE VALUES DECLARATION
    def updateIncassiVittoria(*args):
        #print("Aggiorna totale parziale 1")
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_per_conto.get()
        except: b=0
        try: c=incasso_das.get()
        except: c=0
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')

        #print("Aggiorna Incasso contanti")
        try: g=totale_incassi_vittoria.get()
        except: g=0
        try: h=incasso_polizze_bonifici.get()
        except: h=0
        try: i=incasso_polizze_carte_pos.get()
        except: i=0
        try: j=totale_sospesi.get()
        except: j=0
        result2=g-h-i-j
        entry_incassicontante.configure(state='normal')
        entry_incassicontante.delete(0,'end')
        entry_incassicontante.insert('end', "{:.2f}".format(result2))
        entry_incassicontante.configure(state='disabled')
    def updateIncassoPerConto(*args):
        #print("Aggiorna totale parziale 1")
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_per_conto.get()
        except: b=0
        try: c=incasso_das.get()
        except: c=0
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')
    def updateIncassoDAS(*args):
        #print("Aggiorna totale parziale 1")
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_per_conto.get()
        except: b=0
        try: c=incasso_das.get()
        except: c=0
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')
    def updateTotaleBonifici(*args):
        #print("Aggiorna totale parziale 1")
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_per_conto.get()
        except: b=0
        try: c=incasso_das.get()
        except: c=0
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')

        #print("Aggiorna Incasso polizze bonifici")
        try: g=totale_bonifici.get()
        except: g=0
        try: h=totale_recupero_sospesi_bonifici.get()
        except: h=0
        result2=g-h
        entry_incasso_polizzebonifici.configure(state='normal')
        entry_incasso_polizzebonifici.delete(0,'end')
        entry_incasso_polizzebonifici.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzebonifici.configure(state='disabled')
    def updateIncassoPolizzeBonifici(*args):
        #print("Aggiorna Incasso polizze bonifici")
        try: a=totale_bonifici.get()
        except: a=0
        try: b=totale_recupero_sospesi_bonifici.get()
        except: b=0
        result=a-b
        entry_incasso_polizzebonifici.configure(state='normal')
        entry_incasso_polizzebonifici.delete(0,'end')
        entry_incasso_polizzebonifici.insert('end', "{:.2f}".format(result))
        entry_incasso_polizzebonifici.configure(state='disabled')

        #Aggiorna Incasso contanti
        #print("Aggiorna Incasso contanti")
        try: c=totale_incassi_vittoria.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result2=c-d-e-f
        entry_incassicontante.configure(state='normal')
        entry_incassicontante.delete(0,'end')
        entry_incassicontante.insert('end', "{:.2f}".format(result2))
        entry_incassicontante.configure(state='disabled')
    def updateTotaleCartePOS(*args):
        #print("Aggiorna totale parziale 1")
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_per_conto.get()
        except: b=0
        try: c=incasso_das.get()
        except: c=0
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')

        #print("Aggiorna incasso polizze pos/carte")
        try: g=totale_carte_pos.get()
        except: g=0
        try: h=totale_recupero_sospesi_carte_pos.get()
        except: h=0
        result2=g-h
        entry_incasso_polizzecartepos.configure(state='normal')
        entry_incasso_polizzecartepos.delete(0,'end')
        entry_incasso_polizzecartepos.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzecartepos.configure(state='disabled')
    def updateIncassoPolizzeCartePOS(*args):
        #print("Aggiorna Incasso contanti")
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_polizze_bonifici.get()
        except: b=0
        try: c=incasso_polizze_carte_pos.get()
        except: c=0
        try: d=totale_sospesi.get()
        except: d=0
        result=a-b-c-d
        entry_incassicontante.configure(state='normal')
        entry_incassicontante.delete(0,'end')
        entry_incassicontante.insert('end', "{:.2f}".format(result))
        entry_incassicontante.configure(state='disabled')
    def updateTotaleParziale1(*args):
        #print("Aggiorna totale parziale 2")
        try: a=totale_parziale_1.get()
        except: a=0
        try: b=fondo_cassa_precedente.get()
        except: b=0
        result=a+b
        entry_tot_parziale_2.configure(state='normal')
        entry_tot_parziale_2.delete(0,'end')
        entry_tot_parziale_2.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_2.configure(state='disabled')
    def updateFondoCassaPrecedente(*args):
        #print("Aggiorna totaele parziale 2")
        try: a=totale_parziale_1.get()
        except: a=0
        try: b=fondo_cassa_precedente.get()
        except: b=0
        result=a+b
        entry_tot_parziale_2.configure(state='normal')
        entry_tot_parziale_2.delete(0,'end')
        entry_tot_parziale_2.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_2.configure(state='disabled')
    def updateTotaleParziale2(*args):
        #print("Aggiorna totale cassa contante")
        try: a=totale_parziale_2.get()
        except: a=0
        try: b=totale_recupero_sospesi.get()
        except: b=0
        result=a+b
        entry_tot_cassacontanti.configure(state='normal')
        entry_tot_cassacontanti.delete(0,'end')
        entry_tot_cassacontanti.insert('end', "{:.2f}".format(result))
        entry_tot_cassacontanti.configure(state='disabled')
    def updateTotaleRecuperoSospesiContanti(*args):
        #print("Aggiorna totale recupero sospesi")
        try: a=totale_recupero_sospesi_contanti.get()
        except: a=0
        try: b=totale_recupero_sospesi_carte_pos.get()
        except: b=0
        try: c=totale_recupero_sospesi_bonifici.get()
        except: c=0
        result=a+b+c
        entry_tot_recuperosospesi.configure(state='normal')
        entry_tot_recuperosospesi.delete(0,'end')
        entry_tot_recuperosospesi.insert('end', "{:.2f}".format(result))
        entry_tot_recuperosospesi.configure(state='disabled')
    def updateTotaleRecuperoSospesiCartePOS(*args):
        #print("Aggiorna totale recupero sospesi")
        try: a=totale_recupero_sospesi_contanti.get()
        except: a=0
        try: b=totale_recupero_sospesi_carte_pos.get()
        except: b=0
        try: c=totale_recupero_sospesi_bonifici.get()
        except: c=0
        result=a+b+c
        entry_tot_recuperosospesi.configure(state='normal')
        entry_tot_recuperosospesi.delete(0,'end')
        entry_tot_recuperosospesi.insert('end', "{:.2f}".format(result))
        entry_tot_recuperosospesi.configure(state='disabled')

        #print("Aggiorna incasso polizze pos/carte")
        try: d=totale_carte_pos.get()
        except: d=0
        try: e=totale_recupero_sospesi_carte_pos.get()
        except: e=0
        result2=d-e
        entry_incasso_polizzecartepos.configure(state='normal')
        entry_incasso_polizzecartepos.delete(0,'end')
        entry_incasso_polizzecartepos.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzecartepos.configure(state='disabled')
    def updateTotaleRecuperoSospesiBonifici(*args):
        #print("Aggiorna totale recupero sospesi")
        try: a=totale_recupero_sospesi_contanti.get()
        except: a=0
        try: b=totale_recupero_sospesi_carte_pos.get()
        except: b=0
        try: c=totale_recupero_sospesi_bonifici.get()
        except: c=0
        result=a+b+c
        entry_tot_recuperosospesi.configure(state='normal')
        entry_tot_recuperosospesi.delete(0,'end')
        entry_tot_recuperosospesi.insert('end', "{:.2f}".format(result))
        entry_tot_recuperosospesi.configure(state='disabled')

        #print("Aggiorna Incasso polizze bonifici")
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_recupero_sospesi_bonifici.get()
        except: e=0
        result2=d-e
        entry_incasso_polizzebonifici.configure(state='normal')
        entry_incasso_polizzebonifici.delete(0,'end')
        entry_incasso_polizzebonifici.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzebonifici.configure(state='disabled')
    def updateTotaleRecuperoSospesi(*args):
        #print("Aggiorna totale cassa contante")
        try: a=totale_parziale_2.get()
        except: a=0
        try: b=totale_recupero_sospesi.get()
        except: b=0
        result=a+b
        entry_tot_cassacontanti.configure(state='normal')
        entry_tot_cassacontanti.delete(0,'end')
        entry_tot_cassacontanti.insert('end', "{:.2f}".format(result))
        entry_tot_cassacontanti.configure(state='disabled')
        
        #Aggiorna saldo sospesi
        try: c=totale_sospesi.get()
        except: c=0
        try: d=totale_recupero_sospesi.get()
        except: d=0
        result3=c-d
        entry_saldo_sospesi.configure(state='normal')
        entry_saldo_sospesi.delete(0,'end')
        entry_saldo_sospesi.insert('end', "{:.2f}".format(result3))
        entry_saldo_sospesi.configure(state='disabled')
    def updateTotaleCassaContante(*args):
        #print("Aggiorna fondo cassa da riportare")
        try: a=totale_cassa_contante.get()
        except: a=0
        try: b=totale_generale_uscite.get()
        except: b=0
        result=a-b
        entry_fondodariportare.configure(state='normal')
        entry_fondodariportare.delete(0,'end')
        entry_fondodariportare.insert('end', "{:.2f}".format(result))
        entry_fondodariportare.configure(state='disabled')
    def updateTotaleAbbuoni(*args):
        #print("Aggiorna Totale generale uscite")
        try: a=totale_abbuoni.get()
        except: a=0
        try: b=totale_uscite_varie.get()
        except: b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_tot_generaleuscite.configure(state='normal')
        entry_tot_generaleuscite.delete(0,'end')
        entry_tot_generaleuscite.insert('end', "{:.2f}".format(result))
        entry_tot_generaleuscite.configure(state='disabled')
    def updateTotaleUsciteVarie(*args):
        #print("Aggiorna Totale generale uscite")
        try:a=totale_abbuoni.get()
        except:a=0
        try:b=totale_uscite_varie.get()
        except:b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_tot_generaleuscite.configure(state='normal')
        entry_tot_generaleuscite.delete(0,'end')
        entry_tot_generaleuscite.insert('end', "{:.2f}".format(result))
        entry_tot_generaleuscite.configure(state='disabled')
    def updateTotaleGeneraleUscite(*args):
        #print("Aggiorna fondo cassa da riportare")
        try: a=totale_cassa_contante.get()
        except: a=0
        try: b=totale_generale_uscite.get()
        except: b=0
        result=a-b
        entry_fondodariportare.configure(state='normal')
        entry_fondodariportare.delete(0,'end')
        entry_fondodariportare.insert('end', "{:.2f}".format(result))
        entry_fondodariportare.configure(state='disabled')
    def updateFondoCassaDaRiportare(*args):
        #print("Aggiorna saldo cassa")
        try: a=fondo_cassa_da_riportare.get()
        except: a=0
        try: b=totale_marchirolo.get()
        except: b=0
        result=a-b
        entry_saldocassa.configure(state='normal')
        entry_saldocassa.delete(0,'end')
        entry_saldocassa.insert('end', "{:.2f}".format(result))
        entry_saldocassa.configure(state='disabled')
    def updateSospesi(*args):
        #print("Aggiorna totale sospesi:")
        somma=0
        for item in new_lista_sospesi_values:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_sospesi.configure(state='normal')
        entry_sospesi.delete(0,'end')
        entry_sospesi.insert('end', "{:.2f}".format(somma))
        entry_sospesi.configure(state='disabled')
    def updateRecuperoContanti(*args):
        #Aggiorna totale recupero sospesi contanti
        somma=0
        for item in new_lista_recupero_contanti:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_tot_contante_recuperato.configure(state='normal')
        entry_tot_contante_recuperato.delete(0,'end')
        entry_tot_contante_recuperato.insert('end', "{:.2f}".format(somma))
        entry_tot_contante_recuperato.configure(state='disabled')
    def updateRecuperoCartePOS(*args):
        #Aggiorna totale recupero sospesi carte/pos
        somma=0
        for item in new_lista_recupero_cartepos:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_tot_cartapos_recuperato.configure(state='normal')
        entry_tot_cartapos_recuperato.delete(0,'end')
        entry_tot_cartapos_recuperato.insert('end', "{:.2f}".format(somma))
        entry_tot_cartapos_recuperato.configure(state='disabled')
    def updateRecuperoBonifici(*args):
        #Aggiorna totale recupero sospesi carte/pos
        somma=0
        for item in new_lista_recupero_bonifici:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_tot_bonifici_recuperato.configure(state='normal')
        entry_tot_bonifici_recuperato.delete(0,'end')
        entry_tot_bonifici_recuperato.insert('end', "{:.2f}".format(somma))
        entry_tot_bonifici_recuperato.configure(state='disabled')
    def updateUsciteVarie(*args):
        #Aggiorna totale uscite varie
        somma=0
        for item in new_lista_uscite_varie:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_tot_uscite_varie.configure(state='normal')
        entry_tot_uscite_varie.delete(0,'end')
        entry_tot_uscite_varie.insert('end', "{:.2f}".format(somma))
        entry_tot_uscite_varie.configure(state='disabled')
    def updateVersamenti(*args):
        #Aggiorna totale versamenti
        somma=0
        for item in new_lista_versamenti:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_tot_versamenti.configure(state='normal')
        entry_tot_versamenti.delete(0,'end')
        entry_tot_versamenti.insert('end', "{:.2f}".format(somma))
        entry_tot_versamenti.configure(state='disabled')
    def updateMarchirolo(*args):
        #Aggiorna totale marchirolo
        somma=0
        for item in new_lista_marchirolo:
            try: tmp=item.get()
            except: tmp=0
            somma = somma+tmp
        entry_tot_marchirolo.configure(state='normal')
        entry_tot_marchirolo.delete(0,'end')
        entry_tot_marchirolo.insert('end', "{:.2f}".format(somma))
        entry_tot_marchirolo.configure(state='disabled')
    def updateTotaleMarchirolo(*args):
        #print("Aggiorna saldo cassa")
        try: a=fondo_cassa_da_riportare.get()
        except: a=0
        try: b=totale_marchirolo.get()
        except: b=0
        result=a-b
        entry_saldocassa.configure(state='normal')
        entry_saldocassa.delete(0,'end')
        entry_saldocassa.insert('end', "{:.2f}".format(result))
        entry_saldocassa.configure(state='disabled')
    def updateTotaleSospesi(*args):
        #Aggiorna totale parziale 1
        try: a=totale_incassi_vittoria.get()
        except: a=0
        try: b=incasso_per_conto.get()
        except: b=0
        try: c=incasso_das.get()
        except: c=0
        try: d=totale_bonifici.get()
        except: d=0
        try: e=totale_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')

        #print("Aggiorna Incasso contanti")
        try: g=totale_incassi_vittoria.get()
        except: g=0
        try: h=incasso_polizze_bonifici.get()
        except: h=0
        try: i=incasso_polizze_carte_pos.get()
        except: i=0
        try: j=totale_sospesi.get()
        except: j=0
        result2=g-h-i-j
        entry_incassicontante.configure(state='normal')
        entry_incassicontante.delete(0,'end')
        entry_incassicontante.insert('end', "{:.2f}".format(result2))
        entry_incassicontante.configure(state='disabled')

        #Aggiorna saldo sospesi
        try: k=totale_sospesi.get()
        except: k=0
        try: l=totale_recupero_sospesi.get()
        except: l=0
        result3=k-l
        entry_saldo_sospesi.configure(state='normal')
        entry_saldo_sospesi.delete(0,'end')
        entry_saldo_sospesi.insert('end', "{:.2f}".format(result3))
        entry_saldo_sospesi.configure(state='disabled')
    def updateUsciteVersamenti(*args):
        #print("Aggiorna Totale generale uscite")
        try: a=totale_abbuoni.get()
        except: a=0
        try: b=totale_uscite_varie.get()
        except: b=0
        try: c=totale_uscite_versamenti.get()
        except: c=0
        result=a+b+c
        entry_tot_generaleuscite.configure(state='normal')
        entry_tot_generaleuscite.delete(0,'end')
        entry_tot_generaleuscite.insert('end', "{:.2f}".format(result))
        entry_tot_generaleuscite.configure(state='disabled')
    def updateAssegni(*args):
        print("Entry assegni cambiata")
        #Aggiorna

    def updateIncassoContante(*args):
        print("Entry incasso contanti cambiata")
        #Aggiorna

    def updateSaldoSospesi(*args):
        print("Entry saldo sospesi cambiata")
        #Aggiorna
    def updatePuntiViva(*args):
         #print("Aggiorna Totale generale uscite")
        try: a=totale_abbuoni.get()
        except: a=0
        try: b=totale_uscite_varie.get()
        except: b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_tot_generaleuscite.configure(state='normal')
        entry_tot_generaleuscite.delete(0,'end')
        entry_tot_generaleuscite.insert('end', "{:.2f}".format(result))
        entry_tot_generaleuscite.configure(state='disabled')

    #VARIABLES DECLARATION
    totale_incassi_vittoria = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_incassi_vittoria.trace("w", updateIncassiVittoria)
    incasso_per_conto = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    incasso_per_conto.trace("w", updateIncassoPerConto)
    incasso_das = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    incasso_das.trace("w", updateIncassoDAS)
    totale_bonifici = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_bonifici.trace("w", updateTotaleBonifici)
    incasso_polizze_bonifici = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))   #totale_bonifici-totale_recupero_sospesi_bonifici
    incasso_polizze_bonifici.trace("w", updateIncassoPolizzeBonifici)
    totale_carte_pos = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_carte_pos.trace("w", updateTotaleCartePOS)
    incasso_polizze_carte_pos = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    incasso_polizze_carte_pos.trace("w", updateIncassoPolizzeCartePOS)
    totale_sospesi = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))                      #somma array sospesi
    totale_sospesi.trace("w", updateTotaleSospesi)
    totale_parziale_1 = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))                   #totale_incassi_vittoria+incasso_per_conto+incasso_das-totale_bonifici-totale_carte_pos-totale_sospesi
    totale_parziale_1.trace("w", updateTotaleParziale1)
    fondo_cassa_precedente = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    fondo_cassa_precedente.trace("w", updateFondoCassaPrecedente)
    incassi_contante = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))                    #totale_incassi_vittoria - incasso_polizze_bonifici - incasso_polizze_carte_pos - totale_sospesi
    totale_parziale_2 = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))                   #totale_parziale_2 + fondo_cassa_precedente
    totale_parziale_2.trace("w", updateTotaleParziale2)
    totale_recupero_sospesi_contanti = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))    #somma array recupero_sospesi_contanti
    totale_recupero_sospesi_contanti.trace("w", updateTotaleRecuperoSospesiContanti)
    totale_recupero_sospesi_carte_pos = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))   #somma array recupero_sospesi_carte_pos
    totale_recupero_sospesi_carte_pos.trace("w", updateTotaleRecuperoSospesiCartePOS)
    totale_recupero_sospesi_bonifici = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))    #somma array recupero_sospesi_bonifici
    totale_recupero_sospesi_bonifici.trace("w", updateTotaleRecuperoSospesiBonifici)
    totale_recupero_sospesi = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))             #totale_recupero_sospesi_contanti + totale_recupero_sospesi_carte_pos + totale_recupero_sospesi_bonifici
    totale_recupero_sospesi.trace("w", updateTotaleRecuperoSospesi)
    totale_cassa_contante = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))               #totale_parziale_2 + totale_recupero_sospesi
    totale_cassa_contante.trace("w", updateTotaleCassaContante)
    totale_abbuoni = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_abbuoni.trace("w", updateTotaleAbbuoni)
    totale_uscite_varie = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))                 #uscite_varie + uscite_versamenti
    totale_uscite_varie.trace("w", updateTotaleUsciteVarie)
    totale_uscite_versamenti = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_uscite_versamenti.trace("w", updateUsciteVersamenti)
    totale_generale_uscite = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))              #totale_abbuoni + totale_uscite_varie
    totale_generale_uscite.trace("w", updateTotaleGeneraleUscite)
    fondo_cassa_da_riportare = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))            #totale_cassa_contante - totale_generale_uscite
    fondo_cassa_da_riportare.trace("w", updateFondoCassaDaRiportare)
    totale_marchirolo = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))                   #somma array somme_marchirolo
    totale_marchirolo.trace("w", updateTotaleMarchirolo)
    saldo_cassa = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    completato = ctk.StringVar(visualizzaprova, "")
    incasso_assegni = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    incasso_assegni.trace("w", updateAssegni)
    incasso_contante = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    incasso_contante.trace("w", updateIncassoContante)
    saldo_sospesi = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    saldo_sospesi.trace("w", updateSaldoSospesi)
    punti_viva = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    punti_viva.trace("w", updatePuntiViva)


    #SELECT dal database e aggiorna entries 
    def saveData(database_entry, ctk_entry, ctk_variable, c):
        #Converti data
        data_converted = (calendar.get_date()).split('-')
        data_converted_text=""
        data_converted_text=data_converted[2]+"-"+data_converted[1]+"-"+data_converted[0]
        c.execute("SELECT "+database_entry+" FROM prova WHERE data='"+data_converted_text+"'")
        rows = c.fetchall()
        for row in rows:
            ctk_entry.configure(state='normal')
            ctk_entry.delete(0,'end')
            ctk_entry.insert('end', row)
            tmp = ctk_variable.get()
            ctk_entry.delete(0,'end')
            ctk_entry.insert('end', "{:.2f}".format(tmp))
            ctk_entry.configure(state='disabled')
    def saveDataTextBox(database_entry, ctk_entry, c):
        #Converti data
        data_converted = (calendar.get_date()).split('-')
        data_converted_text=""
        data_converted_text=data_converted[2]+"-"+data_converted[1]+"-"+data_converted[0]
        c.execute("SELECT "+database_entry+" FROM prova WHERE data='"+data_converted_text+"'")
        row = c.fetchall()
        ctk_entry.configure(state='normal')
        ctk_entry.delete('0.0','end')
        ctk_entry.insert('0.0', row)
        ctk_entry.configure(state='disabled')
        ctk_entry.get('0.0', 'end')


    '''def ricercaPosizioneEntry(frame_name, nome_entry):
        posizione = 0
        isvalore = 0
        for child in frame_name.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                for child2 in child.winfo_children():
                    if isinstance(child2, ctk.CTkLabel):
                        if isvalore==2:
                            labelavalue = child2.cget("text")
                            print("if", str(labelavalue), " = ", str(nome_entry))
                            if str(labelavalue) == str(nome_entry):
                                print ("La posizione cercata è: ", posizione)
                                return posizione
                            else:
                                print("false")
                                posizione = posizione + 1
                            isvalore = 0
                        else:
                            isvalore = isvalore + 1
    
    def destroy(frame_import, nomeposizione, new_lista_values, new_lista_causali):
        pos = ricercaPosizioneEntry (frame_import, nomeposizione.cget("text"))
        print("Sto eliminando il valore alla posizione: ", pos, " che ha valore:")
        ind = 0
        for item in new_lista_values:
            if ind == pos:
                print(item.get())
            ind = ind + 1
        new_lista_values.pop(pos)
        new_lista_causali.pop(pos)
        frame.pack_forget()
        defUpdate()
        print("Elemento eliminato dalla lista")'''
    
    def aggiornaTutteLeEntries(*args):
        updateSospesi()
        updateRecuperoContanti()
        updateRecuperoCartePOS()
        updateRecuperoBonifici()
        updateUsciteVarie()
        updateVersamenti()
        updateMarchirolo()
    def destroy(nome_frame, posizione, lista_valori, lista_causali):
        print(posizione)
        #lista_valori.pop(posizione)
        #lista_causali.pop(posizione)
        lista_valori[posizione] = ""
        lista_causali[posizione] = ""
        nome_frame.destroy()
        aggiornaTutteLeEntries()
        

    #SELECT dalle liste del database e aggiorna lista
    def saveDataList(frame_import, categoria, new_lista_values, new_lista_causali, defUpdate, c):
        #Converti data
        data_converted = (calendar.get_date()).split('-')
        data_converted_text=""
        data_converted_text=data_converted[2]+"-"+data_converted[1]+"-"+data_converted[0]
        c.execute("SELECT valore, causale FROM liste WHERE data='"+data_converted_text+"' AND categoria='"+categoria+"'")
        rows = c.fetchall()
        nomeentry = 0
        def createFrame(valore, causale):
                frame = ctk.CTkFrame(frame_import)
                frame.pack()
                ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
                var1 = ctk.DoubleVar(frame, valore)
                var1.trace("w", defUpdate)
                ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
                ent1.grid(row=1, column=0)
                ent1.configure(state='disabled')
                ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
                ent2 = ctk.CTkEntry(frame, width=250)
                ent2.insert('end', causale)
                ent2.grid(row=1, column=1)
                ent2.configure(state='disabled')
                delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=lambda f=nomeentry: destroy(frame, f, new_lista_values, new_lista_causali), state="disabled")
                delete_button.grid(row=1, column=2)
                new_lista_values.append(var1)
                new_lista_causali.append(ent2)

        for valore,causale in rows:
            createFrame(valore, causale)
            nomeentry = nomeentry + 1
        
    

    def getDataFromDatabase():
        conn = sqlite3.connect(percorso_database)
        c = conn.cursor()

        saveData("totale_incassi_vittoria", entry_incassi_vittoria, totale_incassi_vittoria, c)
        saveData("incasso_per_conto", entry_incasso_conto, incasso_per_conto, c)
        saveData("incasso_das", entry_incasso_das, incasso_das, c)
        saveData("totale_bonifici", entry_incasso_bonifici, totale_bonifici, c)
        saveData("incasso_polizze_bonifici", entry_incasso_polizzebonifici, incasso_polizze_bonifici, c)
        saveData("totale_carte_pos", entry_incasso_cartepos, totale_carte_pos, c)
        saveData("incasso_polizze_carte_pos", entry_incasso_polizzecartepos, incasso_polizze_carte_pos, c)
        saveData("totale_sospesi", entry_sospesi, totale_sospesi, c)
        saveData("totale_parziale_1", entry_tot_parziale_1, totale_parziale_1, c)
        saveData("fondo_cassa_precedente", entry_cassaprecedente, fondo_cassa_precedente, c)
        saveData("incassi_contante", entry_incassicontante, incassi_contante, c)
        saveData("totale_parziale_2", entry_tot_parziale_2, totale_parziale_2, c)
        saveData("totale_recupero_sospesi_contanti", entry_tot_contante_recuperato, totale_recupero_sospesi_contanti, c)
        saveData("totale_recupero_sospesi_carte_pos", entry_tot_cartapos_recuperato, totale_recupero_sospesi_carte_pos, c)
        saveData("totale_recupero_sospesi_bonifici", entry_tot_bonifici_recuperato, totale_recupero_sospesi_bonifici, c)
        saveData("totale_recupero_sospesi", entry_tot_recuperosospesi, totale_recupero_sospesi, c)
        saveData("totale_cassa_contante", entry_tot_cassacontanti, totale_cassa_contante, c)
        saveData("totale_abbuoni", entry_abbuoni, totale_abbuoni, c)
        saveData("totale_uscite_varie", entry_tot_uscite_varie, totale_uscite_varie, c)
        saveData("totale_uscite_versamenti", entry_tot_versamenti, totale_uscite_versamenti, c)
        saveData("totale_generale_uscite", entry_tot_generaleuscite, totale_generale_uscite, c)
        saveData("fondo_cassa_da_riportare", entry_fondodariportare, fondo_cassa_da_riportare, c)
        saveData("totale_marchirolo", entry_tot_marchirolo, totale_marchirolo, c)
        saveData("saldo_cassa", entry_saldocassa, saldo_cassa, c)
        saveData("incasso_assegni", entry_incasso_assegni, incasso_assegni, c)
        saveData("incasso_contante", entry_incasso_contante, incasso_contante, c)
        saveData("saldo_sospesi", entry_saldo_sospesi, saldo_sospesi, c)
        saveData("punti_viva", entry_viva, punti_viva, c)
        saveDataTextBox("commenti", entry_commenti, c)

        saveDataList(frame_sospesi, "sospesi", new_lista_sospesi_values, new_lista_sospesi_causali, updateSospesi, c)
        saveDataList(frame_recuperosospesi_contante, "recupero_contanti", new_lista_recupero_contanti, new_lista_recupero_contanti_causali, updateRecuperoContanti, c)
        saveDataList(frame_recuperosospesi_cartapos, "recupero_cartepos", new_lista_recupero_cartepos, new_lista_recupero_cartepos_causali, updateRecuperoCartePOS, c)
        saveDataList(frame_recuperosospesi_bonifici, "recupero_bonifici", new_lista_recupero_bonifici, new_lista_recupero_bonifici_causali, updateRecuperoBonifici, c)
        saveDataList(frame_uscite_varie, "uscite_varie", new_lista_uscite_varie, new_lista_uscite_varie_causali, updateUsciteVarie, c)
        saveDataList(frame_versamenti, "uscite_versamenti", new_lista_versamenti, new_lista_versamenti_causali, updateVersamenti, c)
        saveDataList(frame_marchirolo, "marchirolo", new_lista_marchirolo, new_lista_marchirolo_causali, updateMarchirolo, c)
        

        #Converti data
        data_converted = (calendar.get_date()).split('-')
        data_converted_text=""
        data_converted_text=data_converted[2]+"-"+data_converted[1]+"-"+data_converted[0]
        #Aggiorna fondo cassa precedente
        c.execute("SELECT data, fondo_cassa_da_riportare FROM prova WHERE data<'"+data_converted_text+"' ORDER BY data DESC LIMIT 1")
        rows=c.fetchall()
        if len(rows)==0:
            label_daybefore.configure(text="Non trovato")
        else:
            for data_precedente, fondo_cassa_da_riportare_precedente in rows:
                entry_cassaprecedente.configure(state='normal')
                entry_cassaprecedente.delete(0,'end')
                entry_cassaprecedente.insert('end', "{:.2f}".format(fondo_cassa_da_riportare_precedente))
                entry_cassaprecedente.configure(state='disabled')
                #Converti di nuovo la data in formato gg-mm-aaaa
                data_converted2 = (data_precedente).split('-')
                data_converted_text2=""
                data_converted_text2=data_converted2[2]+"-"+data_converted2[1]+"-"+data_converted2[0]
                label_daybefore.configure(text="Del "+data_converted_text2)

        #Prendi prova completata si/no
        c.execute("SELECT completato FROM prova WHERE data='"+data_converted_text+"'")
        check_completato=c.fetchall()
        conn.commit()
        for check in check_completato:
            completato.set(check[0])
            if check[0] == 'true':
                label_conferma.pack(padx=20, pady=(40,0))
            else:
                bottone_conferma.pack(padx=20, pady=(40,0))

        conn.commit()
        conn.close()

    

    #Picked date and label update
    def chooseDate(event):
        #Cancella valori attualmente presenti nelle entry (prevenzione se non esiste il giorno)
        def resetEntry(entry_name):
            entry_name.configure(state='normal')
            entry_name.delete(0,'end')
            entry_name.insert('end', "{:.2f}".format(0))
            entry_name.configure(state='disabled')
        def resetEntryTextBox(entry_name):
            entry_name.configure(state='normal')
            entry_name.delete('0.0','end')
            entry_name.configure(state='disabled')
        resetEntry(entry_incassi_vittoria)
        resetEntry(entry_incasso_conto)
        resetEntry(entry_incasso_das)
        resetEntry(entry_incasso_bonifici)
        resetEntry(entry_incasso_polizzebonifici)
        resetEntry(entry_incasso_cartepos)
        resetEntry(entry_incasso_polizzecartepos)
        resetEntry(entry_sospesi)
        resetEntry(entry_tot_parziale_1)
        resetEntry(entry_cassaprecedente)
        resetEntry(entry_incassicontante)
        resetEntry(entry_tot_parziale_2)
        resetEntry(entry_tot_contante_recuperato)
        resetEntry(entry_tot_cartapos_recuperato)
        resetEntry(entry_tot_bonifici_recuperato)
        resetEntry(entry_tot_recuperosospesi)
        resetEntry(entry_tot_cassacontanti)
        resetEntry(entry_abbuoni)
        resetEntry(entry_tot_uscite_varie)
        resetEntry(entry_tot_versamenti)
        resetEntry(entry_tot_generaleuscite)
        resetEntry(entry_fondodariportare)
        resetEntry(entry_tot_marchirolo)
        resetEntry(entry_saldocassa)
        resetEntry(entry_incasso_assegni)
        resetEntry(entry_incasso_contante)
        resetEntry(entry_viva)
        resetEntryTextBox(entry_commenti)
        #Elimina entry all'interno di un frame lista
        def resetEntryInsideFrame(frame_name):
            for child in frame_name.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    child.pack_forget()               
        resetEntryInsideFrame(frame_sospesi)
        resetEntryInsideFrame(frame_recuperosospesi_contante)
        resetEntryInsideFrame(frame_recuperosospesi_bonifici)
        resetEntryInsideFrame(frame_recuperosospesi_cartapos)
        resetEntryInsideFrame(frame_uscite_varie)
        resetEntryInsideFrame(frame_versamenti)
        resetEntryInsideFrame(frame_marchirolo)
        #Reset all lists
        def resetLists (lista_values, lista_causali):
            lista_values.clear()
            lista_causali.clear()
        resetLists(new_lista_sospesi_values, new_lista_sospesi_causali)
        resetLists(new_lista_recupero_contanti, new_lista_recupero_contanti_causali)
        resetLists(new_lista_recupero_cartepos, new_lista_recupero_cartepos_causali)
        resetLists(new_lista_recupero_bonifici, new_lista_recupero_bonifici_causali)
        resetLists(new_lista_uscite_varie, new_lista_uscite_varie_causali)
        resetLists(new_lista_versamenti, new_lista_versamenti_causali)
        resetLists(new_lista_marchirolo, new_lista_marchirolo_causali)

        label_daybefore.configure(text="Non trovato")
        label_conferma.pack_forget()
        bottone_conferma.pack_forget()

        #Controlla se il giorno selezionato è nel database
        conn = sqlite3.connect(percorso_database)
        c = conn.cursor()
        #Converti data
        data_converted = (calendar.get_date()).split('-')
        data_converted_text=""
        data_converted_text=data_converted[2]+"-"+data_converted[1]+"-"+data_converted[0]
        c.execute("SELECT * FROM prova WHERE data='"+data_converted_text+"'")
        data=c.fetchall()
        conn.commit()
        if (len(data)==0):
            showConfirmMessage(visualizzaprova,"Attenzione", "Il giorno selezionato non è presente", "cancel", False)
            label_date_picked.configure(text="*** Seleziona una data per visualizzare i dati ***")
            edit_button.pack_forget()
            bottone_conferma.pack_forget()
            label_conferma.pack_forget()
        else:
            label_date_picked.configure(text="🗓️ Prova giornaliera del " + calendar.get_date())
            getDataFromDatabase()
            edit_button.pack(side="bottom", pady=(0,5))
            c.execute("SELECT completato FROM prova WHERE data='"+data_converted_text+"'")
            check_completato=c.fetchall()
            conn.commit()
            for check in check_completato:
                if check[0] == 'true':
                    label_conferma.pack(padx=20, pady=(40,0))
                    edit_button.pack_forget()
                else:
                    bottone_conferma.pack(padx=20, pady=(40,0))
        conn.commit()
        conn.close()
    label_date_picked = ctk.CTkLabel(visualizzaprova, text="*** Seleziona una data per visualizzare i dati ***", font=("Helvetica",14,"bold"))
    label_date_picked.pack()

    #Create tabview
    tabview = ctk.CTkTabview(master=visualizzaprova)
    tabview.pack(pady=(0,15), padx=20, fill="both", expand=True)

    tabview.add("Data")
    tabview.add("Incassi")
    tabview.add("Sospesi")
    tabview.add("Recupero sospesi")
    tabview.add("Uscite")
    tabview.add("Marchirolo")
    tabview.add("Resoconto")
    tabview.add("Documenti")

    #----TAB DATA----
    calendar = Calendar(tabview.tab("Data"),
                        locale="it",
                        date_pattern="dd-mm-yyy",
                        font="Helvetica 20",
                        #cursor="hand1",
                        #borderwidth = 8,
                        showweeknumbers=False,
                        showothermonthdays=False,
                        background = "#eeeeee",
                        foreground = "black",
                        selectbackground = "#CFCFCF", 
                        selectforeground = "black",
                        normalforeground = "#CFCFCF",
                        weekendforeground = "#CFCFCF")
    calendar.pack(pady=20)
    calendar.bind('<<CalendarSelected>>', chooseDate)

    def coloraGiorniCompletati():
        #Get completed days from database
        conn = sqlite3.connect(percorso_database)
        c = conn.cursor()
        c.execute("SELECT data FROM prova WHERE completato='true'")
        conn.commit()
        rows = c.fetchall()
        for row in rows:
            #Converti data
            data_converted = row[0].split('-')
            data_converted_text=""
            data_converted_text=data_converted[2]+"-"+data_converted[1]+"-"+data_converted[0]
            dt = Calendar.datetime.strptime(data_converted_text, "%d-%m-%Y").date()
            calendar.calevent_create(date=dt, text='Giorno completato', tags= "Completata")
            calendar.tag_config("Completata", background='red', foreground='#809d5f')

        conn.commit()
        conn.close()
        
    coloraGiorniCompletati()
    #----TAB INCASSI----
    #Create frame inside the tab
    frame_incassi = ctk.CTkFrame(master=tabview.tab("Incassi"))
    frame_incassi.pack(pady=(20,0))
    #Incassi Vittoria
    label_incassi_vittoria = ctk.CTkLabel(master=frame_incassi, text="Premio lordo:")
    label_incassi_vittoria.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_incassi_vittoria = ctk.CTkEntry(frame_incassi, textvariable=totale_incassi_vittoria, state='disabled', width=100)
    entry_incassi_vittoria.grid(row=0, column=1, pady=10, padx=20, sticky="nw")
    #Incasso per conto
    label_incasso_conto = ctk.CTkLabel(master=frame_incassi, text="Incasso per conto:")
    label_incasso_conto.grid(row=1, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_conto = ctk.CTkEntry(frame_incassi, textvariable=incasso_per_conto, state='disabled', width=100)
    entry_incasso_conto.grid(row=1, column=1, pady=10, padx=20, sticky="nw")
    #Incasso DAS
    label_incasso_das = ctk.CTkLabel(master=frame_incassi, text="Incasso DAS:")
    label_incasso_das.grid(row=2, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_das = ctk.CTkEntry(frame_incassi, textvariable=incasso_das, state='disabled', width=100)
    entry_incasso_das.grid(row=2, column=1, pady=10, padx=20, sticky="nw")
    #Incasso bonifici
    label_incasso_bonifici = ctk.CTkLabel(master=frame_incassi, text="Movimenti bancari:")
    label_incasso_bonifici.grid(row=3, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_bonifici = ctk.CTkEntry(frame_incassi, textvariable=totale_bonifici, state='disabled', width=100)
    entry_incasso_bonifici.grid(row=3, column=1, pady=10, padx=20, sticky="nw")
    #Incasso polizze bonifici
    label_incasso_polizzebonifici = ctk.CTkLabel(master=frame_incassi, text="Incasso polizze bonifici:", font=("Helvetica",14,"bold"))
    label_incasso_polizzebonifici.grid(row=4, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_polizzebonifici = ctk.CTkEntry(frame_incassi, textvariable=incasso_polizze_bonifici, state="disabled", font=("Helvetica",15,"bold"), width=100)
    entry_incasso_polizzebonifici.grid(row=4, column=1, pady=10, padx=20, sticky="nw")
    #Incasso carte/POS
    label_incasso_cartepos = ctk.CTkLabel(master=frame_incassi, text="Totale carte/POS:")
    label_incasso_cartepos.grid(row=5, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_cartepos = ctk.CTkEntry(frame_incassi, textvariable=totale_carte_pos, state='disabled', width=100)
    entry_incasso_cartepos.grid(row=5, column=1, pady=10, padx=20, sticky="nw")
    #Incasso polizze carte/POS
    label_incasso_polizzecartepos = ctk.CTkLabel(master=frame_incassi, text="Incasso polizze carte/POS:", font=("Helvetica",14,"bold"))
    label_incasso_polizzecartepos.grid(row=6, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_polizzecartepos = ctk.CTkEntry(frame_incassi, textvariable=incasso_polizze_carte_pos, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_incasso_polizzecartepos.grid(row=6, column=1, pady=10, padx=20, sticky="nw")
    #Incasso contante
    label_incasso_contante = ctk.CTkLabel(master=frame_incassi, text="Contanti:")
    label_incasso_contante.grid(row=7, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_contante = ctk.CTkEntry(frame_incassi, textvariable=incasso_contante, state='disabled', width=100)
    entry_incasso_contante.grid(row=7, column=1, pady=10, padx=20, sticky="nw")
    #Incasso assegni
    label_incasso_assegni = ctk.CTkLabel(master=frame_incassi, text="Assegni:")
    label_incasso_assegni.grid(row=8, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_assegni = ctk.CTkEntry(frame_incassi, textvariable=incasso_assegni, state='disabled', width=100)
    entry_incasso_assegni.grid(row=8, column=1, pady=10, padx=20, sticky="nw")



    #----TAB SOSPESI----
    #Create frame inside the tab
    frame_sospesi = ctk.CTkScrollableFrame(master=tabview.tab("Sospesi"), width=500, height=300, border_color="black", border_width=1)
    frame_sospesi.pack()
    #LISTA SOSPESI
    #Aggiungi sospeso
    def addSospeso():
        #Elimina sospeso
        def destroy():
            var1.set(0)
            new_lista_sospesi_values.remove(var1)
            new_lista_sospesi_causali.remove(ent2)
            frame.pack_forget()
            print("Sospeso eliminato")
        print ("Sospeso aggiunto")
        frame = ctk.CTkFrame(frame_sospesi)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_sospesi, "{:.2f}".format(0))
        var1.trace("w", updateSospesi)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        #lista_sospesi.append( (ent1, ent2) )
        new_lista_sospesi_values.append(var1)
        new_lista_sospesi_causali.append(ent2)
    #Print all entries
    #def showSospesi():
    #    for number, (ent1, ent2) in enumerate(lista_sospesi_values):
    #        print (number, ent1.get(), ent2.get())
    #lista_sospesi = []
    new_lista_sospesi_values = []
    new_lista_sospesi_causali = []
    #showButton = ctk.CTkButton(frame_sospesi, text='Stampa tutti i sospesi', command=showSospesi)
    #showButton.pack()
    addboxButton = ctk.CTkButton(frame_sospesi, text='Aggiungi sospeso', command=addSospeso)


    #Totale sospesi
    label_sospesi = ctk.CTkLabel(master=tabview.tab("Sospesi"), text="Totale sospesi:", font=("Helvetica",14,"bold"))
    label_sospesi.pack(side="left", anchor="ne", pady=(25,0), padx=10, expand="True")
    entry_sospesi = ctk.CTkEntry(tabview.tab("Sospesi"), textvariable=totale_sospesi, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_sospesi.pack(side="right", anchor="nw", pady=(25,0), expand="True")



    #----TAB RECUPERO SOSPESI----
    frame_recuperosospesi = ctk.CTkScrollableFrame(master=tabview.tab("Recupero sospesi"), width=500, height=480, border_color="black", border_width=1)
    frame_recuperosospesi.pack()
    #--Sospeso recuperato CONTANTI--
    frame_recuperosospesi_contante = ctk.CTkFrame(master=frame_recuperosospesi, height=50)
    frame_recuperosospesi_contante.pack()

    def addSospContante():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            new_lista_recupero_contanti.remove(var1)
            new_lista_recupero_contanti_causali.remove(ent2)
            frame.pack_forget()
            print("Sospeso contante eliminato")
        print ("Sospeso recuperato contante aggiunto")
        frame = ctk.CTkFrame(frame_recuperosospesi_contante)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_recuperosospesi_contante, "{:.2f}".format(0))
        var1.trace("w", updateRecuperoContanti)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        new_lista_recupero_contanti.append(var1)
        new_lista_recupero_contanti_causali.append(ent2)
    new_lista_recupero_contanti = []
    new_lista_recupero_contanti_causali = []
    add_contante_recuperato = ctk.CTkButton(frame_recuperosospesi_contante, text='Aggiungi contante recuperato', command=addSospContante)

    #Totale contante recuperato
    frame_contanterecuperato = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_contanterecuperato.pack()
    label_tot_contante_recuperato = ctk.CTkLabel(master=frame_contanterecuperato, text="Totale sospesi contanti recuperato:", font=("Helvetica",14,"bold"))
    label_tot_contante_recuperato.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_contante_recuperato = ctk.CTkEntry(frame_contanterecuperato, textvariable=totale_recupero_sospesi_contanti, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_contante_recuperato.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #--Sospeso recuperato CARTE/POS--
    frame_recuperosospesi_cartapos = ctk.CTkFrame(master=frame_recuperosospesi, height=50)
    frame_recuperosospesi_cartapos.pack()

    def addSospCartePOS():
        #Elimina sospeso carta/POS
        def destroy():
            var1.set(0)
            new_lista_recupero_cartepos.remove(var1)
            new_lista_recupero_cartepos_causali.remove(ent2)
            frame.pack_forget()
            print("Sospeso carta/POS eliminato")
        print ("Sospeso recuperato carta/POS aggiunto")
        frame = ctk.CTkFrame(frame_recuperosospesi_cartapos)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_recuperosospesi_cartapos, "{:.2f}".format(0))
        var1.trace("w", updateRecuperoCartePOS)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        new_lista_recupero_cartepos.append(var1)
        new_lista_recupero_cartepos_causali.append(ent2)
    new_lista_recupero_cartepos = []
    new_lista_recupero_cartepos_causali = []
    add_cartapos_recuperato = ctk.CTkButton(frame_recuperosospesi_cartapos, text='Aggiungi Carta/POS recuperato', command=addSospCartePOS)


    #Totale carte/POS recuperato
    frame_carteposrecuperato = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_carteposrecuperato.pack()
    label_tot_cartapos_recuperato = ctk.CTkLabel(master=frame_carteposrecuperato, text="Totale sospesi carte/POS recuperato:", font=("Helvetica",14,"bold"))
    label_tot_cartapos_recuperato.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_cartapos_recuperato = ctk.CTkEntry(frame_carteposrecuperato, textvariable=totale_recupero_sospesi_carte_pos, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_cartapos_recuperato.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #--Sospeso recuperato bonifici--
    frame_recuperosospesi_bonifici = ctk.CTkFrame(master=frame_recuperosospesi, height=50)
    frame_recuperosospesi_bonifici.pack()

    def addSospBonifici():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            new_lista_recupero_bonifici.remove(var1)
            new_lista_recupero_bonifici_causali.remove(ent2)
            frame.pack_forget()
            print("Sospeso bonifico eliminato")
        print ("Sospeso recuperato bonifico aggiunto")
        frame = ctk.CTkFrame(frame_recuperosospesi_bonifici)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_recuperosospesi_bonifici, "{:.2f}".format(0))
        var1.trace("w", updateRecuperoBonifici)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        new_lista_recupero_bonifici.append(var1)
        new_lista_recupero_bonifici_causali.append(ent2)
    new_lista_recupero_bonifici = []
    new_lista_recupero_bonifici_causali = []
    add_bonifici_recuperato = ctk.CTkButton(frame_recuperosospesi_bonifici, text='Aggiungi bonifico recuperato', command=addSospBonifici)


    #Totale bonifici recuperato
    frame_bonificirecuperato = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_bonificirecuperato.pack()
    label_tot_bonifici_recuperato = ctk.CTkLabel(master=frame_bonificirecuperato, text="Totale sospesi bonifici recuperato:", font=("Helvetica",14,"bold"))
    label_tot_bonifici_recuperato.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_bonifici_recuperato = ctk.CTkEntry(frame_bonificirecuperato, textvariable=totale_recupero_sospesi_bonifici, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_bonifici_recuperato.grid(row=0, column=1, pady=20, padx=10, sticky="nw")


    #Frame totali
    frame_recuperosospesi_totali = ctk.CTkFrame(master=tabview.tab("Recupero sospesi"))
    frame_recuperosospesi_totali.pack(pady=(20,0))
    #--Totale recupero sospesi--
    label_tot_recuperosospesi = ctk.CTkLabel(master=frame_recuperosospesi_totali, text="Totale recupero sospesi:", font=("Helvetica",14,"bold"))
    label_tot_recuperosospesi.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_recuperosospesi = ctk.CTkEntry(frame_recuperosospesi_totali, textvariable=totale_recupero_sospesi, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_recuperosospesi.grid(row=0, column=1, pady=10, padx=20, sticky="nw")
    #--Totale cassa contanti--
    label_tot_cassacontanti = ctk.CTkLabel(master=frame_recuperosospesi_totali, text="Totale cassa contanti:", font=("Helvetica",14,"bold"))
    label_tot_cassacontanti.grid(row=1, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_cassacontanti = ctk.CTkEntry(frame_recuperosospesi_totali, textvariable=totale_cassa_contante, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_cassacontanti.grid(row=1, column=1, pady=10, padx=20, sticky="nw")

    #----TAB USCITE----
    frame_uscite_abbuoniviva = ctk.CTkFrame(master=tabview.tab("Uscite"))
    frame_uscite_abbuoniviva.pack()
    #--Abbuoni--
    label_abbuoni = ctk.CTkLabel(master=frame_uscite_abbuoniviva, text="Totale abbuoni:")
    label_abbuoni.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_abbuoni = ctk.CTkEntry(frame_uscite_abbuoniviva, textvariable=totale_abbuoni, state='disabled', width=100)
    entry_abbuoni.grid(row=0, column=1, pady=10, padx=20, sticky="nw")

    #--Punti VIVA--
    label_viva = ctk.CTkLabel(master=frame_uscite_abbuoniviva, text="Totale punti Viva:")
    label_viva.grid(row=1, column=0, pady=10, padx=20, sticky="ne")
    entry_viva = ctk.CTkEntry(frame_uscite_abbuoniviva, textvariable=punti_viva, state='disabled', width=100)
    entry_viva.grid(row=1, column=1, pady=10, padx=20, sticky="nw")
    
    frame_uscitevarieandversamenti = ctk.CTkScrollableFrame(master = tabview.tab("Uscite"), width=500, height=450, border_color="black", border_width=1)
    frame_uscitevarieandversamenti.pack()
    #--Aggiungi VERSAMENTI--
    frame_versamenti = ctk.CTkFrame(master=frame_uscitevarieandversamenti, height=50)
    frame_versamenti.pack()
    def addVersamento():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            new_lista_versamenti.remove(var1)
            new_lista_versamenti_causali.remove(ent2)
            frame.pack_forget()
            print("Versamento eliminato")
        print ("Versamento aggiunta")
        frame = ctk.CTkFrame(frame_versamenti)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_versamenti, "{:.2f}".format(0))
        var1.trace("w", updateVersamenti)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        new_lista_versamenti.append(var1)
        new_lista_versamenti_causali.append(ent2)
    new_lista_versamenti = []
    new_lista_versamenti_causali = []
    add_versamento = ctk.CTkButton(frame_versamenti, text='Aggiungi versamento', command=addVersamento)
    #Totale versamenti
    frame_usciteversamenti = ctk.CTkFrame(master=frame_uscitevarieandversamenti)
    frame_usciteversamenti.pack()
    label_tot_versamenti = ctk.CTkLabel(master=frame_usciteversamenti, text="Totale versamenti:", font=("Helvetica",14,"bold"))
    label_tot_versamenti.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_versamenti = ctk.CTkEntry(frame_usciteversamenti, textvariable=totale_uscite_versamenti, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_versamenti.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #--Aggiungi USCITE VARIE--
    frame_uscite_varie = ctk.CTkFrame(master=frame_uscitevarieandversamenti, height=50)
    frame_uscite_varie.pack()
    def addUsciteVarie():
        #Elimina uscita varia
        def destroy():
            var1.set(0)
            new_lista_uscite_varie.remove(var1)
            new_lista_uscite_varie_causali.remove(ent2)
            frame.pack_forget()
            print("Uscita varia eliminata")
        print ("Uscita varia aggiunta")
        frame = ctk.CTkFrame(frame_uscite_varie)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_uscite_varie, "{:.2f}".format(0))
        var1.trace("w", updateUsciteVarie)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        new_lista_uscite_varie.append(var1)
        new_lista_uscite_varie_causali.append(ent2)
    new_lista_uscite_varie = []
    new_lista_uscite_varie_causali = []
    add_uscite_varie = ctk.CTkButton(frame_uscite_varie, text='Aggiungi uscite varie', command=addUsciteVarie)
    #Totale uscite varie
    frame_totaleuscitevarie = ctk.CTkFrame(master=frame_uscitevarieandversamenti)
    frame_totaleuscitevarie.pack()
    label_tot_uscite_varie = ctk.CTkLabel(master=frame_totaleuscitevarie, text="Totale uscite varie:", font=("Helvetica",14,"bold"))
    label_tot_uscite_varie.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_uscite_varie = ctk.CTkEntry(frame_totaleuscitevarie, textvariable=totale_uscite_varie, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_uscite_varie.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    frame_uscitetotali = ctk.CTkFrame(master=tabview.tab("Uscite"))
    frame_uscitetotali.pack(pady=(20,0))
    #--Fondo cassa da riportare--
    label_fondodariportare = ctk.CTkLabel(master=frame_uscitetotali, text="Fondo cassa da riportare:", font=("Helvetica",14,"bold"))
    label_fondodariportare.grid(row=1, column=0, pady=10, padx=10, sticky="ne")
    entry_fondodariportare = ctk.CTkEntry(frame_uscitetotali, textvariable=fondo_cassa_da_riportare, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_fondodariportare.grid(row=1, column=1, pady=10, padx=10, sticky="nw")

    #----TAB MARCHIROLO----
    frame_marchirolo = ctk.CTkScrollableFrame(master=tabview.tab("Marchirolo"), width=500, height=300, border_color="black", border_width=1)
    frame_marchirolo.pack()
    def addUscitaMarchirolo():
        #Elimina sospeso carta/POS
        def destroy():
            var1.set(0)
            new_lista_marchirolo.remove(var1)
            new_lista_marchirolo_causali.remove(ent2)
            frame.pack_forget()
            print("Marchirolo eliminato")
        print ("Uscita marchirolo aggiunta")
        frame = ctk.CTkFrame(frame_marchirolo)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_marchirolo, "{:.2f}".format(0))
        var1.trace("w", updateMarchirolo)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)
        new_lista_marchirolo.append(var1)
        new_lista_marchirolo_causali.append(ent2)
    new_lista_marchirolo = []
    new_lista_marchirolo_causali = []
    add_uscitamarchirolo = ctk.CTkButton(frame_marchirolo, text='Aggiungi uscita Marchirolo', command=addUscitaMarchirolo)

    label_tot_marchirolo = ctk.CTkLabel(master=tabview.tab("Marchirolo"), text="Totale Marchirolo:", font=("Helvetica",14,"bold"))
    label_tot_marchirolo.pack(side="left", anchor="ne", pady=(25,0), padx=10, expand="True")
    entry_tot_marchirolo = ctk.CTkEntry(tabview.tab("Marchirolo"), textvariable=totale_marchirolo, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_marchirolo.pack(side="right", anchor="nw", pady=(25,0), expand="True")

    #----TAB RESCONTO----
    #Create frame inside the tab
    frame_resoconto = ctk.CTkFrame(master=tabview.tab("Resoconto"))
    frame_resoconto.pack(pady=(20,0))
    #Totale parziale 1
    label_tot_parziale_1 = ctk.CTkLabel(master=frame_resoconto, text="Totale parziale 1:", font=("Helvetica",14,"bold"))
    label_tot_parziale_1.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_parziale_1 = ctk.CTkEntry(frame_resoconto, textvariable=totale_parziale_1, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_parziale_1.grid(row=0, column=1, pady=10, padx=20, sticky="nw")
    explain_tot_parziale_1 = ctk.CTkLabel(master=frame_resoconto, text="Incassi - bonifici - POS - sospesi", text_color="#969595", font=("Helvetica",13))
    explain_tot_parziale_1.grid(row=0, column=2, pady=10, padx=20, sticky="nw")
    #Fondo cassa precedente
    label_cassaprecedente = ctk.CTkLabel(master=frame_resoconto, text="Fondo cassa precedente:", font=("Helvetica",14,"bold"))
    label_cassaprecedente.grid(row=1, column=0, pady=10, padx=20, sticky="ne")
    entry_cassaprecedente = ctk.CTkEntry(frame_resoconto, textvariable=fondo_cassa_precedente, font=("Helvetica",15,"bold"), width=100)
    entry_cassaprecedente.grid(row=1, column=1, pady=10, padx=20, sticky="nw")
    label_daybefore = ctk.CTkLabel(master=frame_resoconto, text="Non trovato", text_color="#969595", font=("Helvetica",13))
    label_daybefore.grid(row=1, column=2, pady=10, padx=20, sticky="nw")
    #Incassi contante
    label_incassicontante = ctk.CTkLabel(master=frame_resoconto, text="Incassi contante:", font=("Helvetica",14,"bold"))
    label_incassicontante.grid(row=3, column=0, pady=10, padx=20, sticky="ne")
    entry_incassicontante = ctk.CTkEntry(frame_resoconto, textvariable=incassi_contante, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_incassicontante.grid(row=3, column=1, pady=10, padx=20, sticky="nw")
    explain_incassicontante = ctk.CTkLabel(master=frame_resoconto, text="Tot. parz. 2 + tot. rec. sosp. contante", text_color="#969595", font=("Helvetica",13))
    explain_incassicontante.grid(row=3, column=2, pady=10, padx=20, sticky="nw")
    #Saldo sospesi
    label_saldo_sospesi = ctk.CTkLabel(master=frame_resoconto, text="Saldo sospesi:", font=("Helvetica",14,"bold"))
    label_saldo_sospesi.grid(row=4, column=0, pady=10, padx=20, sticky="ne")
    entry_saldo_sospesi = ctk.CTkEntry(frame_resoconto, textvariable=saldo_sospesi, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_saldo_sospesi.grid(row=4, column=1, pady=10, padx=20, sticky="nw")
    explain_saldo_sospesi = ctk.CTkLabel(master=frame_resoconto, text="Sospesi - rec. sospesi", text_color="#969595", font=("Helvetica",13))
    explain_saldo_sospesi.grid(row=4, column=2, pady=10, padx=20, sticky="nw")
    #Totale parziale 2
    label_tot_parziale_2 = ctk.CTkLabel(master=frame_resoconto, text="Totale parziale 2:", font=("Helvetica",14,"bold"))
    label_tot_parziale_2.grid(row=5, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_parziale_2 = ctk.CTkEntry(frame_resoconto, textvariable=totale_parziale_2, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_parziale_2.grid(row=5, column=1, pady=10, padx=20, sticky="nw")
    explain_tot_parziale_2 = ctk.CTkLabel(master=frame_resoconto, text="Tot. parz. 1 + fondo cassa precedente", text_color="#969595", font=("Helvetica",13))
    explain_tot_parziale_2.grid(row=5, column=2, pady=10, padx=20, sticky="nw")
    #--Totale generale uscite--
    label_tot_generaleuscite = ctk.CTkLabel(master=frame_resoconto, text="Totale generale uscite:", font=("Helvetica",14,"bold"))
    label_tot_generaleuscite.grid(row=6, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_generaleuscite = ctk.CTkEntry(frame_resoconto, textvariable=totale_generale_uscite, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_generaleuscite.grid(row=6, column=1, pady=10, padx=20, sticky="nw")
    explain_tot_generaleuscite = ctk.CTkLabel(master=frame_resoconto, text="Abbuoni + p.ti Viva + uscite varie + versamenti", text_color="#969595", font=("Helvetica",13))
    explain_tot_generaleuscite.grid(row=6, column=2, pady=10, padx=20, sticky="nw")
    #Totale Marchirolo COPIA
    label_tot_marchirolo_copy = ctk.CTkLabel(master=frame_resoconto, text="Totale Marchirolo:", font=("Helvetica",14,"bold"))
    label_tot_marchirolo_copy.grid(row=7, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_marchirolo_copy = ctk.CTkEntry(frame_resoconto, textvariable=totale_marchirolo, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_marchirolo_copy.grid(row=7, column=1, pady=10, padx=20, sticky="nw")
    explain_tot_marchirolo_copy = ctk.CTkLabel(master=frame_resoconto, text="Totale uscite Marchirolo", text_color="#969595", font=("Helvetica",13))
    explain_tot_marchirolo_copy.grid(row=7, column=2, pady=10, padx=20, sticky="nw")
    #Saldo cassa
    label_saldocassa = ctk.CTkLabel(master=frame_resoconto, text="Saldo cassa:", font=("Helvetica",14,"bold"))
    label_saldocassa.grid(row=8, column=0, pady=10, padx=20, sticky="ne")
    entry_saldocassa = ctk.CTkEntry(frame_resoconto, textvariable=saldo_cassa, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_saldocassa.grid(row=8, column=1, pady=10, padx=20, sticky="nw")
    explain_saldocassa = ctk.CTkLabel(master=frame_resoconto, text="F. cass da riportare + tot. Marchirolo", text_color="#969595", font=("Helvetica",13))
    explain_saldocassa.grid(row=8, column=2, pady=10, padx=20, sticky="nw")
    #Commenti
    label_commenti = ctk.CTkLabel(master=tabview.tab("Resoconto"), text="Commenti:")
    label_commenti.pack()
    entry_commenti = ctk.CTkTextbox(tabview.tab("Resoconto"), height=100, width=300, border_width=2, state='disabled')
    entry_commenti.pack()
    

    #----TAB DOCUMENTI----
    def apriDocumenti():
        #Controlla che sia selezionato un giorno
        if label_date_picked.cget("text") == "*** Seleziona una data per visualizzare i dati ***":
            showConfirmMessage(visualizzaprova,"Attenzione", "Devi prima selezionare un giorno", "warning", False)
        else:
            #Splitta data
            dataperfile = (calendar.get_date()).split('-')
            #Controlla se la cartella delgiorno esiste, in caso creala
            if not os.path.exists(percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]):     
                os.makedirs(percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0])
            path = percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]    #FULL PATH
            webbrowser.open('file:///' + path)        

    apri_cartella_documenti = ctk.CTkButton(tabview.tab("Documenti"), text='Apri documenti', command=apriDocumenti)
    apri_cartella_documenti.pack(padx=20, pady=(20,0))

    def uploadFile():
        #Comando associato al tasto Sfoglia
        def chooseFile():
            inputfile_path = ""
            inputfile_path = ctk.filedialog.askopenfilename()
            print(inputfile_path)
            entry_inputfile.delete(0, 'end')  # Remove current text in entry
            entry_inputfile.insert(0, inputfile_path)  # Insert the 'path'
        #Comando associato al tasto Carica
        def loadFile():
            new_filename = entry_outputfilename.get()
            original_path = entry_inputfile.get()
            fullpath, file_extension = os.path.splitext(original_path)
            head, tail = os.path.split(original_path)
            dataperfile = (calendar.get_date()).split('-')
            #Se la cartella della categoria non esiste, creala
            if not os.path.exists(percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()):     
                os.makedirs(percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get())
            #Controlla se è un versamento. Se si, il nome del file deve essere uguale ad una causale esistente e poi lo carica. Altrimenti manda un avviso
            if entry_outputcategory.get() == "Versamenti":
                causale_trovata = False
                #Se dai un nuovo nome al file
                if(new_filename != ""):
                    for item in new_lista_versamenti_causali:
                        if new_filename == item.get():
                            causale_trovata = True                                
                    if causale_trovata == True:
                        shutil.move(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)    
                        print("File caricato")
                        showConfirmMessage(visualizzaprova,"Successo","Documento correttamente caricato", "check", False)
                        frame.destroy()
                    else:
                        print("Attenzione: i nomi non combaciano")
                        showConfirmMessage(visualizzaprova,"Attenzione","Il nome non corrisponde a nessuna causale", "warning", False)
                #Altrimenti spostalo con lo stesso nome
                else:
                    for item in new_lista_versamenti_causali:
                        print(str(tail[:-4]))
                        print(item.get())
                        if tail[:-4] == item.get():
                            causale_trovata = True  
                    if causale_trovata == True:
                        shutil.move(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+tail)    
                        print("File caricato")
                        showConfirmMessage(visualizzaprova,"Successo","Documento correttamente caricato", "check", False)
                        frame.destroy()
                    else:
                        print("Attenzione: i nomi non combaciano")
                        showConfirmMessage(visualizzaprova,"Attenzione","Il nome non corrisponde a nessuna causale", "warning", False)
            else:
                #Se dai un nuovo nome al file
                if(new_filename != ""):
                    #os.rename(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)
                    #os.replace(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)
                    shutil.move(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)    
                    print("File caricato")
                    showConfirmMessage(visualizzaprova,"Successo","Documento correttamente caricato", "check", False)
                    frame.destroy()
                #Altrimenti spostalo con lo stesso nome
                else:
                    #os.rename(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+filename+file_extension)
                    #os.replace(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+filename+file_extension)
                    shutil.move(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+tail)    
                    print("File caricato")
                    showConfirmMessage(visualizzaprova,"Successo","Documento correttamente caricato", "check", False)
                    frame.destroy()

        #Controlla che sia selezionato un giorno
        if label_date_picked.cget("text") == "*** Seleziona una data per visualizzare i dati ***":
            showConfirmMessage(visualizzaprova,"Attenzione", "Devi prima selezionare un giorno", "warning", False)
        else:
            frame = ctk.CTkFrame(tabview.tab("Documenti"))
            frame.pack(padx=20, pady=10)
        input_button = ctk.CTkButton(frame, text="Sfoglia", command=chooseFile, width=60)
        input_button.grid(row=0, column=0)
        entry_inputfile = ctk.CTkEntry(frame, width=250, placeholder_text="Scegli file da spostare...")
        entry_inputfile.grid(row=0, column=1)
        #def updateOutputCategory(*args):
        #    if outputcategory.get() == "Quadratura punto vendita":
        #        entry_outputfilename.insert(0, "Quadratura punto vendita")
        #    else:
        #        entry_outputfilename.delete(0, 'end')
        #outputcategory = ctk.StringVar(frame, "")
        #outputcategory.trace("w", updateOutputCategory)
        entry_outputcategory = ctk.CTkComboBox(frame, values=("Bonifici", "Movimenti POS", "Versamenti", "Assegni", "Quadratura punto vendita", "Recupero sospesi", "Chiusure POS", "Quitanze", "Foglio cassa", "Altro"))
        entry_outputcategory.grid(row=0, column=3)
        entry_outputfilename = ctk.CTkEntry(frame, width=250, placeholder_text="Rinomina il file...")
        entry_outputfilename.grid(row=0, column=4)
        loadfile_button = ctk.CTkButton(frame, image=upload_icon, text="", width=30, command=loadFile)
        loadfile_button.grid(row=0, column=5)

    carica_documento = ctk.CTkButton(tabview.tab("Documenti"), text='Carica documento', command=uploadFile)
    carica_documento.pack(padx=20, pady=(20,0))
    
    #Bottone di conferma
    def confermaProva(*args):
        dataperfile = (calendar.get_date()).split('-')
        if not os.path.exists(percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/Versamenti"):     
            os.makedirs(percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/Versamenti")
        causali_trovate = 0
        file_versamenti_list = os.listdir(path=percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/Versamenti")
        #Togli l'estensione dal nome dei file (estensione è lunga 4 caratteri: .pdf)
        for i in range(len(file_versamenti_list)):
            file_versamenti_list[i] = file_versamenti_list[i][:-4]
        #Per ogni elemento in new_lista_versamenti_causali, se è presente (il nome è =) in file_versamenti_list aumenta causali_trovate
        for j in range(len(new_lista_versamenti_causali)):
            if new_lista_versamenti_causali[j].get() in file_versamenti_list:
                causali_trovate = causali_trovate+1

        if causali_trovate == len(new_lista_versamenti_causali):
            #Converti data
            data_converted = (calendar.get_date()).split('-')
            data_converted_text=""
            data_converted_text=data_converted[2]+"-"+data_converted[1]+"-"+data_converted[0]
            conn = sqlite3.connect(percorso_database)
            c = conn.cursor()
            c.execute("SELECT * FROM prova WHERE data='"+data_converted_text+"'")
            conn.commit()
            data=c.fetchall()
            if (len(data)==0):
                showConfirmMessage(visualizzaprova,"Attenzione", "Il giorno selezionato non è presente", "cancel", False)
            else:
                c.execute("PRAGMA foreign_keys = ON;")
                conn.commit()
                c.execute("UPDATE prova SET completato = 'true' WHERE data='"+data_converted_text+"'")
                conn.commit()
                completato.set("true")
                showConfirmMessage(visualizzaprova,"Prova completata", "Hai contrassegnato la prova come completata", "check", False)
                edit_button.pack_forget()

                conn.commit()  
                conn.close()
                coloraGiorniCompletati()
                bottone_conferma.pack_forget()
                label_conferma.pack(padx=20, pady=(40,0))
        else:
            showConfirmMessage(visualizzaprova,"Attenzione", "Non hai caricato tutti i versamenti", "cancel", False)
    bottone_conferma = ctk.CTkButton(tabview.tab("Resoconto"), text='Prova completata', command=confermaProva)
    label_conferma = ctk.CTkLabel(tabview.tab("Resoconto"), text="✅ La prova è completata")
    



    #----MANAGE DATA SECTION----
    def addButtons():
        #Aggiungi bottoni per sospesi, recuperi e uscite
        addboxButton.pack(padx=20, pady=20)
        add_contante_recuperato.pack(padx=20, pady=(20,0))
        add_cartapos_recuperato.pack(pady=(25,0))
        add_bonifici_recuperato.pack(pady=(25,0))
        add_uscite_varie.pack(padx=20, pady=(20,0))
        add_versamento.pack(padx=20, pady=(20,0))
        add_uscitamarchirolo.pack(padx=20, pady=(20,0))
    def setEnableDisable(new_state):
        entry_incassi_vittoria.configure(state=new_state)
        entry_incasso_conto.configure(state=new_state)
        entry_incasso_das.configure(state=new_state)
        entry_incasso_bonifici.configure(state=new_state)
        entry_incasso_cartepos.configure(state=new_state)
        entry_abbuoni.configure(state=new_state)
        entry_incasso_contante.configure(state=new_state)
        entry_incasso_assegni.configure(state=new_state)
        entry_viva.configure(state=new_state)
        entry_commenti.configure(state=new_state)
        #Configura Entry all'interno di un frame
        def configureEntryInsideFrame(frame_name):
            for child in frame_name.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    for child2 in child.winfo_children():
                        if isinstance(child2, (ctk.CTkEntry, ctk.CTkButton)):
                            child2.configure(state=new_state)
        configureEntryInsideFrame(frame_sospesi)
        configureEntryInsideFrame(frame_recuperosospesi_contante)
        configureEntryInsideFrame(frame_recuperosospesi_bonifici)
        configureEntryInsideFrame(frame_recuperosospesi_cartapos)
        configureEntryInsideFrame(frame_uscite_varie)
        configureEntryInsideFrame(frame_versamenti)
        configureEntryInsideFrame(frame_marchirolo)

    def removeButtons():
        addboxButton.pack_forget()
        add_contante_recuperato.pack_forget()
        add_cartapos_recuperato.pack_forget()
        add_bonifici_recuperato.pack_forget()
        add_uscite_varie.pack_forget()
        add_versamento.pack_forget()
        add_uscitamarchirolo.pack_forget()
    def editProva():
        #Remove disable option
        setEnableDisable("normal")
        #Add editable buttons
        addButtons()
        #Hide MODIFICA BUTTON
        edit_button.pack_forget()
        #Show CANCELLA BUTTON
        cancel_btn.pack(side="top", pady=(0,5), padx=20)
        #Show SAVE BUTTON
        save_btn.pack(side="bottom", pady=(0,5), padx=20)
    def saveButton():
        #Converti data
        data_converted = (calendar.get_date()).split('-')
        data_converted_text=""
        data_converted_text=data_converted[2]+"-"+data_converted[1]+"-"+data_converted[0]
        conn = sqlite3.connect(percorso_database)
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
        #Elimina oggi
        c.execute("DELETE FROM liste WHERE data='"+data_converted_text+"'")
        conn.commit()
        c.execute("DELETE FROM prova WHERE data='"+data_converted_text+"'")
        conn.commit()
        #Nota: si può risolvere con UPDATE CASCADE

        def safeLoad(input):
            try:
                output = input.get()
            except:
                output = 0
            return output
        #Aggiungi tutte le entry
        c.execute("INSERT INTO prova VALUES ('"+data_converted_text+"', "
                  +str(safeLoad(totale_incassi_vittoria))+", "
                  +str(safeLoad(incasso_per_conto))+", "
                  +str(safeLoad(incasso_das))+", "
                  +str(safeLoad(totale_bonifici))+", "
                  +str(safeLoad(incasso_polizze_bonifici))+", "
                  +str(safeLoad(totale_carte_pos))+", "
                  +str(safeLoad(incasso_polizze_carte_pos))+", "
                  +str(safeLoad(totale_sospesi))+", "
                  +str(safeLoad(totale_parziale_1))+", "
                  +str(safeLoad(fondo_cassa_precedente))+", "
                  +str(safeLoad(incassi_contante))+", "
                  +str(safeLoad(totale_parziale_2))+", "
                  +str(safeLoad(totale_recupero_sospesi_contanti))+", "
                  +str(safeLoad(totale_recupero_sospesi_carte_pos))+", "
                  +str(safeLoad(totale_recupero_sospesi_bonifici))+", "
                  +str(safeLoad(totale_recupero_sospesi))+", "
                  +str(safeLoad(totale_cassa_contante))+", "
                  +str(safeLoad(totale_abbuoni))+", "
                  +str(safeLoad(totale_uscite_varie))+", "
                  +str(safeLoad(totale_uscite_versamenti))+", "
                  +str(safeLoad(totale_generale_uscite))+", "
                  +str(safeLoad(fondo_cassa_da_riportare))+", "
                  +str(safeLoad(totale_marchirolo))+", "
                  +str(safeLoad(saldo_cassa))+", '"
                  +str(completato.get())+"', "
                  +str(safeLoad(incasso_assegni))+", "
                  +str(safeLoad(incasso_contante))+", "
                  +str(safeLoad(saldo_sospesi))+", "
                  +str(safeLoad(punti_viva))+", "
                  +"'"+str(entry_commenti.get('0.0','end'))+"'"+")"
        )
        conn.commit()
        #Aggiungi liste
        for valore, causale in zip(new_lista_sospesi_values, new_lista_sospesi_causali):
            try:
                if valore.get() != "" and causale.get() != "":
                    c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                            +"'sospesi', "
                            +str(valore.get())+", '"
                            +causale.get()+
                            "')"
                    )
            except:
                    print("Entries vuote non caricate")
        conn.commit()
        for valore, causale in zip(new_lista_recupero_contanti, new_lista_recupero_contanti_causali):
            try:
                if valore.get() != "" and causale.get() != "":
                    c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                            +"'recupero_contanti', "
                            +str(valore.get())+", '"
                            +causale.get()+
                            "')"
                    )
            except:
                print("Entries vuote non caricate")
        conn.commit()
        for valore, causale in zip(new_lista_recupero_cartepos, new_lista_recupero_cartepos_causali):
            try:
                if valore.get() != "" and causale.get() != "":
                    c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                            +"'recupero_cartepos', "
                            +str(valore.get())+", '"
                            +causale.get()+
                            "')"
                    )
            except:
                print("Entries vuote non caricate")
        conn.commit()
        for valore, causale in zip(new_lista_recupero_bonifici, new_lista_recupero_bonifici_causali):
            try:
                if valore.get() != "" and causale.get() != "":
                    c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                            +"'recupero_bonifici', "
                            +str(valore.get())+", '"
                            +causale.get()+
                            "')"
                    )
            except:
                print("Entries vuote non caricate")
        conn.commit()
        for valore, causale in zip(new_lista_uscite_varie, new_lista_uscite_varie_causali):
            try:
                if valore.get() != "" and causale.get() != "":
                    c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                            +"'uscite_varie', "
                            +str(valore.get())+", '"
                            +causale.get()+
                            "')"
                    )
            except:
                print("Entries vuote non caricate")
        conn.commit()
        for valore, causale in zip(new_lista_versamenti, new_lista_versamenti_causali):
            try:
                if valore.get() != "" and causale.get() != "":
                    c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                            +"'uscite_versamenti', "
                            +str(valore.get())+", '"
                            +causale.get()+
                            "')"
                    )
            except:
                print("Entries vuote non caricate")
        conn.commit()
        for valore, causale in zip(new_lista_marchirolo, new_lista_marchirolo_causali):
            try:
                if valore.get() != "" and causale.get() != "":
                    c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                            +"'marchirolo', "
                            +str(valore.get())+", '"
                            +causale.get()+
                            "')"
                    )
            except:
                print("Entries vuote non caricate")
        conn.commit()

        conn.close()
        showConfirmMessage(visualizzaprova,"Caricamento completato", "Dati correttamente aggiunti al database", "check", False)

        removeButtons()
        #Add disable option
        setEnableDisable("disabled")
        #Hide SAVE and CANCELLA BUTTON
        save_btn.pack_forget()
        cancel_btn.pack_forget()
        edit_button.pack(side="bottom", pady=(0,5))
    def cancelButton():
        #Elimina entry all'interno di un frame lista
        def deleteEntryInsideFrame(frame_name):
            for child in frame_name.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    child.pack_forget()
                        
        deleteEntryInsideFrame(frame_sospesi)
        deleteEntryInsideFrame(frame_recuperosospesi_contante)
        deleteEntryInsideFrame(frame_recuperosospesi_bonifici)
        deleteEntryInsideFrame(frame_recuperosospesi_cartapos)
        deleteEntryInsideFrame(frame_uscite_varie)
        deleteEntryInsideFrame(frame_versamenti)
        deleteEntryInsideFrame(frame_marchirolo)



        getDataFromDatabase()
        removeButtons()
        #Add disable option
        setEnableDisable("disabled")
        #Hide SAVE and CANCELLA BUTTON
        save_btn.pack_forget()
        cancel_btn.pack_forget()
        edit_button.pack(side="bottom", pady=(0,5))

    #----SALVA, MODIFICA E CANCELLA BUTTONS----
    #Create SAVE and CANCEL buttons
    cancel_btn = ctk.CTkButton(visualizzaprova, text='Annulla', fg_color="#A52A2A", hover_color="#EC3737", command=cancelButton)
    save_btn = ctk.CTkButton(visualizzaprova, text='Salva', fg_color="#809d5f", hover_color="#B7C019", command=saveButton)
    #Show MODIFICA BUTTON
    edit_button = ctk.CTkButton(master=visualizzaprova, image=edit_icon, text="Modifica", command=editProva)



    visualizzaprova.mainloop()


#****MAIN****
#HOME VIEW
#root
home = ctk.CTk()
home.title("Contabilità giornaliera")

#Set window size
home_width = 500
home_height = 220
home_size = str(home_width)+str(home_height)
home.geometry(home_size)
home.minsize(home_width, home_height)
home.maxsize(home_width, home_height)

#Place window in center of screen
ws = home.winfo_screenwidth()
hs = home.winfo_screenheight()
x = (ws/2) - (home_width/2)
y = (hs/2) - (home_height/2)
home.geometry('%dx%d+%d+%d' % (home_width, home_height, x, y))

#Create frame inside the window
frame = ctk.CTkFrame(master=home)
frame.pack(pady=20, padx=60, fill="both", expand=True)

#Label
label = ctk.CTkLabel(master=frame, text="Benvenuta, cosa vuoi fare?")
label.pack(pady=12, padx=10)
#Button 1
button1 = ctk.CTkButton(master=frame, text="Crea", corner_radius=25, command=createNuovaProvaView)
button1.pack(side="left", anchor="e", pady=12, padx=10, expand="True")
#Button 2
button2 = ctk.CTkButton(master=frame, text="Visualizza e gestisci", corner_radius=25, command=visualizzaProva)
button2.pack(side="right", anchor="w", pady=12, padx=10, expand="True")

#Show window
home.mainloop()

