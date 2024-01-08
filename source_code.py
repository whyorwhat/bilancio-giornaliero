import customtkinter as ctk
from datetime import date
from tkcalendar import Calendar
import sqlite3
import os
from PIL import Image
import shutil
import webbrowser

# Apro il file delle posizioni in modalità lettura
with open('posizioni.txt', 'r') as file:
    # Leggo le tre righe dal file e le sarvo nelle loro variabili
    percorso_applicazione = file.readline().replace('Percorso app: ', '').strip()
    percorso_database = file.readline().replace('Percorso database: ', '').strip()
    percorso_documenti = file.readline().replace('Percorso documenti: ', '').strip()

conn = sqlite3.connect(percorso_database)
c = conn.cursor()
c.execute("PRAGMA foreign_keys = ON;")
conn.commit()
#Crea tabelle se non esistono
c.execute("""CREATE TABLE IF NOT EXISTS prova(
    data DATE,
    premio_lordo DOUBLE,
    movimenti_bancari DOUBLE,
    incasso_polizze_bonifici DOUBLE,
    totale_carte_pos DOUBLE,
    incasso_polizze_carte_pos DOUBLE,
    totale_das_contante DOUBLE,
    totale_das_bonifico DOUBLE,
    totale_das_cartepos DOUBLE,
    totale_das DOUBLE,
    totale_incassi_per_conto DOUBLE,
    totale_sospesi DOUBLE,
    totale_parziale_1 DOUBLE,
    fondo_cassa_precedente DOUBLE,
    totale_recupero_sospesi_contanti DOUBLE,
    totale_recupero_sospesi_carte_pos DOUBLE,
    totale_recupero_sospesi_bonifici DOUBLE,
    totale_abbuoni DOUBLE,
    totale_uscite_varie DOUBLE,
    totale_uscite_versamenti DOUBLE,
    totale_generale_uscite DOUBLE,
    fondo_cassa_da_riportare DOUBLE,
    totale_marchirolo DOUBLE,
    saldo_cassa DOUBLE,
    saldo_sospesi DOUBLE,
    punti_viva DOUBLE,
    quadratura_contante_cassa_assegno DOUBLE,
    totale_entrate_cassa_contante DOUBLE,
    commenti TEXT,
    completato TEXT,
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
conn.close()

#Import images
bin_icon = ctk.CTkImage(Image.open(percorso_applicazione+"bin_icon.png"), size=(20,20))
upload_icon = ctk.CTkImage(Image.open(percorso_applicazione+"upload_icon.png"), size=(20,20))
edit_icon = ctk.CTkImage(Image.open(percorso_applicazione+"edit_icon.png"), size=(20,20))
warning_icon = ctk.CTkImage(Image.open(percorso_applicazione+"warning_icon.png"), size=(40, 40))
check_icon = ctk.CTkImage(Image.open(percorso_applicazione+"check_icon.png"), size=(40, 40))
error_icon = ctk.CTkImage(Image.open(percorso_applicazione+"error_icon.png"), size=(40, 40))

#Set application colors
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("dark-blue")

#Set app size
app_width = 850
app_height = 800

def showConfirmMessage(frame, titolo, messaggio, icon_image, kill_app_after_click):
    def destroy():
        message_window.destroy()
        if kill_app_after_click==True:
            frame.destroy()
    message_window = ctk.CTkToplevel(frame)
    message_window.grab_set()   #Setta finestra sopra il frame principale
    message_window.title(titolo)
    message_window.iconbitmap(percorso_applicazione+"app_icon.ico")
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

def exitFromApp(frame):
    def destroy():
        message_window.destroy()
        frame.destroy()
    def stay():
        message_window.destroy()
    message_window = ctk.CTkToplevel(frame)
    message_window.grab_set()   #Setta finestra sopra il frame principale
    message_window.title("Attenzione")
    message_window.iconbitmap(percorso_applicazione+"app_icon.ico")
    ws = message_window.winfo_screenwidth()
    hs = message_window.winfo_screenheight()
    x = (ws/2) - (350/2)
    y = (hs/2) - (150/2)
    message_window.geometry('%dx%d+%d+%d' % (350, 150, x, y))
    message_window.minsize(350, 150)
    message_window.maxsize(350, 150)
    icon = ctk.CTkLabel(message_window, text="", image=warning_icon)
    icon.pack(pady=(15,0), padx=20)
    message = ctk.CTkLabel(message_window, text="Se hai effettuato modifiche, non saranno salvate", font=("Helvetica",14))
    message.pack(pady=(0,10), padx=20)
    no_button = ctk.CTkButton(message_window, text="Resta", width=50, command=stay)
    no_button.pack(side="left", pady=(0,5), padx=(110,0))
    yes_button = ctk.CTkButton(message_window, text="Esci", fg_color="#A52A2A", hover_color="#EC3737", width=50, command=destroy)
    yes_button.pack(side="right", pady=(0,5), padx=(0,110))
    

#****CREA NUOVA PROVA VIEW****
def createNuovaProvaView():
    home.destroy()
    #root
    creaprova = ctk.CTk()
    creaprova.title("Crea prova giornaliera")

    #Set window size
    app_size = str(app_width)+str(app_height)
    creaprova.geometry(app_size)
    creaprova.minsize(app_width-20, app_height)
    creaprova.iconbitmap(percorso_applicazione+"app_icon.ico")

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
            data_precedente=""
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
        for valore,causale in rows:
            createFrame(valore, causale)
            nomeentry = nomeentry + 1
        updateMarchirolo()

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
    tabview.add("Altri incassi")
    tabview.add("Sospesi")
    tabview.add("Recupero sospesi")
    tabview.add("Uscite")
    tabview.add("Marchirolo")
    tabview.add("Resoconto")
    tabview.add("Documenti")

    #CAMBIAMENTO DI VARIABILI: Le seguenti variabili sono associate ad una variabile. Quando questa cambia valore, permette di aggiornare altre entries, come specificato all'interno di ogni def
    def updateLista(nome_frame, entry):
        somma=0
        isvalore = True
        for child in nome_frame.winfo_children():           #Scorri ogni elemento nel frame-padre
            if isinstance(child, ctk.CTkFrame):             #Se è un sotto-frame
                for child2 in child.winfo_children():       #scorri ogni elemento nel sotto-frame
                    if isinstance(child2, ctk.CTkEntry):    #se è una entry
                        if isvalore==True:                  #ed è il valore, aggiorna somma. la prossima entry sarà la causale
                            try: valore=float(child2.get())
                            except: valore=0
                            somma=somma+valore   
                            isvalore=False
                        else:                               #altrimenti è la causale: la prossima entry sarà il valore
                            isvalore = True
        entry.configure(state='normal')                     #Aggiorna la entry
        entry.delete(0,'end')
        entry.insert('end', "{:.2f}".format(somma))
        entry.configure(state='disabled')
    
    def updatePremioLordo(*args):
        #Aggiorna totale parziale 1
        try: a=premio_lordo.get()
        except: a=0
        try: b=totale_incassi_per_conto.get()
        except: b=0
        try: c=totale_das_contante.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')
    def updateTotaleIncassoPerConto(*args):
        #Aggiorna totale parziale 1
        try: a=premio_lordo.get()
        except: a=0
        try: b=totale_incassi_per_conto.get()
        except: b=0
        try: c=totale_das_contante.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')
    def updateMovimentiBancari(*args):
        #Aggiorna Incasso polizze bonifici
        try: a=movimenti_bancari.get()
        except: a=0
        try: b=totale_das_bonifico.get()
        except: b=0
        result2=a+b
        entry_incasso_polizzebonifici.configure(state='normal')
        entry_incasso_polizzebonifici.delete(0,'end')
        entry_incasso_polizzebonifici.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzebonifici.configure(state='disabled')
    def updateIncassoPolizzeBonifici(*args):
        #Aggiorna totale parziale 1
        try: a=premio_lordo.get()
        except: a=0
        try: b=totale_incassi_per_conto.get()
        except: b=0
        try: c=totale_das_contante.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')
    def updateTotaleCartePOS(*args):
        #Aggiorna incasso polizze pos/carte
        try: a=totale_carte_pos.get()
        except: a=0
        try: b=totale_recupero_sospesi_carte_pos.get()
        except: b=0
        result2=a+b
        entry_incasso_polizzecartepos.configure(state='normal')
        entry_incasso_polizzecartepos.delete(0,'end')
        entry_incasso_polizzecartepos.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzecartepos.configure(state='disabled')
    def updateIncassoPolizzeCartePOS(*args):
        #Aggiorna totale parziale 1
        try: a=premio_lordo.get()
        except: a=0
        try: b=totale_incassi_per_conto.get()
        except: b=0
        try: c=totale_das_contante.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')
    def updateTotaleParziale1(*args):
        #Aggiorna totale entrate cassa contante
        try: a=totale_parziale_1.get()
        except: a=0
        try: b=fondo_cassa_precedente.get()
        except: b=0
        try: c=totale_recupero_sospesi_contanti.get()
        except: c=0
        result=a+b+c
        entry_totale_entrate_cassa_contante.configure(state='normal')
        entry_totale_entrate_cassa_contante.delete(0,'end')
        entry_totale_entrate_cassa_contante.insert('end', "{:.2f}".format(result))
        entry_totale_entrate_cassa_contante.configure(state='disabled')
        #Aggiorna Quadratura contante cassa + assegno
        try: g=totale_abbuoni.get()
        except: g=0
        try: h=punti_viva.get()
        except: h=0
        result3=a+c-g-h
        entry_quadratura_contante_cassa_assegno.configure(state='normal')
        entry_quadratura_contante_cassa_assegno.delete(0,'end')
        entry_quadratura_contante_cassa_assegno.insert('end', "{:.2f}".format(result3))
        entry_quadratura_contante_cassa_assegno.configure(state='disabled')
    def updateFondoCassaPrecedente(*args):
        #Aggiorna totale entrate cassa contante
        try: a=totale_parziale_1.get()
        except: a=0
        try: b=fondo_cassa_precedente.get()
        except: b=0
        try: c=totale_recupero_sospesi_contanti.get()
        except: c=0
        result=a+b+c
        entry_totale_entrate_cassa_contante.configure(state='normal')
        entry_totale_entrate_cassa_contante.delete(0,'end')
        entry_totale_entrate_cassa_contante.insert('end', "{:.2f}".format(result))
        entry_totale_entrate_cassa_contante.configure(state='disabled')
    def updateTotaleRecuperoSospesiContanti(*args):
        #Aggiorna saldo sospesi
        try: a=totale_sospesi.get()
        except: a=0
        try: b=totale_recupero_sospesi_contanti.get()
        except: b=0
        try: c=totale_recupero_sospesi_carte_pos.get()
        except: c=0
        try: d=totale_recupero_sospesi_bonifici.get()
        except: d=0
        result=a-b-c-d
        entry_saldo_sospesi.configure(state='normal')
        entry_saldo_sospesi.delete(0,'end')
        entry_saldo_sospesi.insert('end', "{:.2f}".format(result))
        entry_saldo_sospesi.configure(state='disabled')

        #Aggiorna Totale entrate cassa contante
        try: e=totale_parziale_1.get()
        except: e=0
        try: f=fondo_cassa_precedente.get()
        except: f=0
        result2=e+f+b
        entry_totale_entrate_cassa_contante.configure(state='normal')
        entry_totale_entrate_cassa_contante.delete(0,'end')
        entry_totale_entrate_cassa_contante.insert('end', "{:.2f}".format(result2))
        entry_totale_entrate_cassa_contante.configure(state='disabled')

        #Aggiorna Quadratura contante cassa + assegno
        try: g=totale_abbuoni.get()
        except: g=0
        try: h=punti_viva.get()
        except: h=0
        result3=e+b-g-h
        entry_quadratura_contante_cassa_assegno.configure(state='normal')
        entry_quadratura_contante_cassa_assegno.delete(0,'end')
        entry_quadratura_contante_cassa_assegno.insert('end', "{:.2f}".format(result3))
        entry_quadratura_contante_cassa_assegno.configure(state='disabled')
    def updateTotaleRecuperoSospesiCartePOS(*args):
        #Aggiorna saldo sospesi
        try: a=totale_sospesi.get()
        except: a=0
        try: b=totale_recupero_sospesi_contanti.get()
        except: b=0
        try: c=totale_recupero_sospesi_carte_pos.get()
        except: c=0
        try: d=totale_recupero_sospesi_bonifici.get()
        except: d=0
        result=a-b-c-d
        entry_saldo_sospesi.configure(state='normal')
        entry_saldo_sospesi.delete(0,'end')
        entry_saldo_sospesi.insert('end', "{:.2f}".format(result))
        entry_saldo_sospesi.configure(state='disabled')
    def updateTotaleRecuperoSospesiBonifici(*args):
        #Aggiorna saldo sospesi
        try: a=totale_sospesi.get()
        except: a=0
        try: b=totale_recupero_sospesi_contanti.get()
        except: b=0
        try: c=totale_recupero_sospesi_carte_pos.get()
        except: c=0
        try: d=totale_recupero_sospesi_bonifici.get()
        except: d=0
        result=a-b-c-d
        entry_saldo_sospesi.configure(state='normal')
        entry_saldo_sospesi.delete(0,'end')
        entry_saldo_sospesi.insert('end', "{:.2f}".format(result))
        entry_saldo_sospesi.configure(state='disabled')
    def updateTotaleAbbuoni(*args):
        #Aggiorna Totale generale uscite
        try: a=totale_abbuoni.get()
        except: a=0
        try: b=totale_uscite_varie.get()
        except: b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_totale_generale_uscite.configure(state='normal')
        entry_totale_generale_uscite.delete(0,'end')
        entry_totale_generale_uscite.insert('end', "{:.2f}".format(result))
        entry_totale_generale_uscite.configure(state='disabled')

        #Aggiorna Quadratura contante cassa + assegno
        try: e=totale_parziale_1.get()
        except: g=0
        try: f=totale_recupero_sospesi_contanti.get()
        except: h=0
        result2=e+f-a-d
        entry_quadratura_contante_cassa_assegno.configure(state='normal')
        entry_quadratura_contante_cassa_assegno.delete(0,'end')
        entry_quadratura_contante_cassa_assegno.insert('end', "{:.2f}".format(result2))
        entry_quadratura_contante_cassa_assegno.configure(state='disabled')
    def updateTotaleUsciteVarie(*args):
        #Aggiorna Totale generale uscite
        try:a=totale_abbuoni.get()
        except:a=0
        try:b=totale_uscite_varie.get()
        except:b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_totale_generale_uscite.configure(state='normal')
        entry_totale_generale_uscite.delete(0,'end')
        entry_totale_generale_uscite.insert('end', "{:.2f}".format(result))
        entry_totale_generale_uscite.configure(state='disabled')
    def updateTotaleGeneraleUscite(*args):
        #Aggiorna fondo cassa da riportare
        try: a=totale_entrate_cassa_contante.get()
        except: a=0
        try: b=totale_generale_uscite.get()
        except: b=0
        result=a-b
        entry_fondodariportare.configure(state='normal')
        entry_fondodariportare.delete(0,'end')
        entry_fondodariportare.insert('end', "{:.2f}".format(result))
        entry_fondodariportare.configure(state='disabled')
    def updateFondoCassaDaRiportare(*args):
        #Aggiorna saldo cassa
        try: a=fondo_cassa_da_riportare.get()
        except: a=0
        try: b=totale_marchirolo.get()
        except: b=0
        result=a-b
        entry_saldocassa.configure(state='normal')
        entry_saldocassa.delete(0,'end')
        entry_saldocassa.insert('end', "{:.2f}".format(result))
        entry_saldocassa.configure(state='disabled')
    def updateIncassoPerConto(*args):
        updateLista(frame_incasso_per_conto, entry_totale_incassi_per_conto)
    def updateSospesi(*args):
        updateLista(frame_sospesi, entry_sospesi)
    def updateRecuperoContanti(*args):
        #Aggiorna totale recupero sospesi contanti
        updateLista(frame_recuperosospesi_contante, entry_tot_contante_recuperato)
    def updateRecuperoCartePOS(*args):
        #Aggiorna totale recupero sospesi carte/pos
        updateLista(frame_recuperosospesi_cartapos, entry_tot_cartapos_recuperato)
    def updateRecuperoBonifici(*args):
        #Aggiorna totale recupero sospesi carte/pos
        updateLista(frame_recuperosospesi_bonifici, entry_tot_bonifici_recuperato)
    def updateUsciteVarie(*args):
        #Aggiorna totale uscite varie
        updateLista(frame_uscite_varie, entry_tot_uscite_varie)
    def updateVersamenti(*args):
        #Aggiorna totale versamenti
        updateLista(frame_versamenti, entry_tot_versamenti)
    def updateMarchirolo(*args):
        #Aggiorna totale marchirolo
        updateLista(frame_marchirolo, entry_tot_marchirolo)
    def updateDasContanti(*args):
        updateLista(frame_das_contante, entry_totale_das_contante)
    def updateDasCartePOS(*args):
        updateLista(frame_das_cartepos, entry_totale_das_cartepos)
    def updateDasBonifici(*args):
        updateLista(frame_das_bonifico, entry_totale_das_bonifico)
    def updateTotaleMarchirolo(*args):
        #Aggiorna saldo cassa
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
        try: a=premio_lordo.get()
        except: a=0
        try: b=totale_incassi_per_conto.get()
        except: b=0
        try: c=totale_das_contante.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')

        #Aggiorna saldo sospesi
        try: g=totale_recupero_sospesi_contanti.get()
        except: g=0
        try: h=totale_recupero_sospesi_carte_pos.get()
        except: h=0
        try: i=totale_recupero_sospesi_bonifici.get()
        except: i=0
        result2=f-g-h-i
        entry_saldo_sospesi.configure(state='normal')
        entry_saldo_sospesi.delete(0,'end')
        entry_saldo_sospesi.insert('end', "{:.2f}".format(result2))
        entry_saldo_sospesi.configure(state='disabled')

    def updateUsciteVersamenti(*args):
        #Aggiorna Totale generale uscite
        try: a=totale_abbuoni.get()
        except: a=0
        try: b=totale_uscite_varie.get()
        except: b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_totale_generale_uscite.configure(state='normal')
        entry_totale_generale_uscite.delete(0,'end')
        entry_totale_generale_uscite.insert('end', "{:.2f}".format(result))
        entry_totale_generale_uscite.configure(state='disabled')
    def updatePuntiViva(*args):
        #Aggiorna Totale generale uscite
        try: a=totale_abbuoni.get()
        except: a=0
        try: b=totale_uscite_varie.get()
        except: b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_totale_generale_uscite.configure(state='normal')
        entry_totale_generale_uscite.delete(0,'end')
        entry_totale_generale_uscite.insert('end', "{:.2f}".format(result))
        entry_totale_generale_uscite.configure(state='disabled')

        #Aggiorna Quadratura contante cassa + assegno
        try: e=totale_parziale_1.get()
        except: g=0
        try: f=totale_recupero_sospesi_contanti.get()
        except: h=0
        result2=e+f-a-d
        entry_quadratura_contante_cassa_assegno.configure(state='normal')
        entry_quadratura_contante_cassa_assegno.delete(0,'end')
        entry_quadratura_contante_cassa_assegno.insert('end', "{:.2f}".format(result2))
        entry_quadratura_contante_cassa_assegno.configure(state='disabled')
    def updateTotaleDasContanti(*args):
        #Aggiorna totale parziale 1
        try: a=premio_lordo.get()
        except: a=0
        try: b=totale_incassi_per_conto.get()
        except: b=0
        try: c=totale_das_contante.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')

        #Aggiorna totale DAS
        try: g=totale_das_cartepos.get()
        except:g=0
        try: h=totale_das_bonifico.get()
        except:h=0
        result=c+g+h
        entry_totale_das.configure(state='normal')
        entry_totale_das.delete(0,'end')
        entry_totale_das.insert('end', "{:.2f}".format(result))
        entry_totale_das.configure(state='disabled')
    def updateTotaleDasBonifico(*args):
        #Aggiorna totale DAS
        try: a=totale_das_contante.get()
        except: a=0
        try: b=totale_das_cartepos.get()
        except:b=0
        try: c=totale_das_bonifico.get()
        except:c=0
        result=a+b+c
        entry_totale_das.configure(state='normal')
        entry_totale_das.delete(0,'end')
        entry_totale_das.insert('end', "{:.2f}".format(result))
        entry_totale_das.configure(state='disabled')

        #Aggiorna incasso polizze bonifici
        try: d=movimenti_bancari.get()
        except: d=0
        result2=d+c
        entry_incasso_polizzebonifici.configure(state='normal')
        entry_incasso_polizzebonifici.delete(0,'end')
        entry_incasso_polizzebonifici.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzebonifici.configure(state='disabled')
    def updateTotaleDasCartePOS(*args):
        #Aggiorna totale DAS
        try: a=totale_das_contante.get()
        except: a=0
        try: b=totale_das_cartepos.get()
        except:b=0
        try: c=totale_das_bonifico.get()
        except:c=0
        result=a+b+c
        entry_totale_das.configure(state='normal')
        entry_totale_das.delete(0,'end')
        entry_totale_das.insert('end', "{:.2f}".format(result))
        entry_totale_das.configure(state='disabled')

        #Aggiorna incasso polizze carte/pos
        try: d=totale_carte_pos.get()
        except: d=0
        result2=b+d
        entry_incasso_polizzecartepos.configure(state='normal')
        entry_incasso_polizzecartepos.delete(0,'end')
        entry_incasso_polizzecartepos.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzecartepos.configure(state='disabled')
    def updateTotaleEntrateCassaContante(*args):
        #Aggiorna fondo cassa da riportare
        try: a=totale_entrate_cassa_contante.get()
        except: a=0
        try: b=totale_generale_uscite.get()
        except: b=0
        result=a-b
        entry_fondodariportare.configure(state='normal')
        entry_fondodariportare.delete(0,'end')
        entry_fondodariportare.insert('end', "{:.2f}".format(result))
        entry_fondodariportare.configure(state='disabled')
     


    #DICHIARAZIONE VARIABILI
    premio_lordo = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    premio_lordo.trace("w", updatePremioLordo)
    movimenti_bancari = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    movimenti_bancari.trace("w", updateMovimentiBancari)
    incasso_polizze_bonifici = ctk.DoubleVar(creaprova, "{:.2f}".format(0))   
    incasso_polizze_bonifici.trace("w", updateIncassoPolizzeBonifici)
    totale_carte_pos = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_carte_pos.trace("w", updateTotaleCartePOS)
    incasso_polizze_carte_pos = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    incasso_polizze_carte_pos.trace("w", updateIncassoPolizzeCartePOS)
    totale_das_contante = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_das_contante.trace("w", updateTotaleDasContanti)
    totale_das_bonifico = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_das_bonifico.trace("w", updateTotaleDasBonifico)
    totale_das_cartepos = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_das_cartepos.trace("w", updateTotaleDasCartePOS)
    totale_das = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_incassi_per_conto = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_incassi_per_conto.trace("w", updateTotaleIncassoPerConto)
    totale_sospesi = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_sospesi.trace("w", updateTotaleSospesi)
    totale_parziale_1 = ctk.DoubleVar(creaprova, "{:.2f}".format(0))                   
    totale_parziale_1.trace("w", updateTotaleParziale1)
    fondo_cassa_precedente = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    fondo_cassa_precedente.trace("w", updateFondoCassaPrecedente)
    totale_recupero_sospesi_contanti = ctk.DoubleVar(creaprova, "{:.2f}".format(0))    #somma array recupero_sospesi_contanti
    totale_recupero_sospesi_contanti.trace("w", updateTotaleRecuperoSospesiContanti)
    totale_recupero_sospesi_carte_pos = ctk.DoubleVar(creaprova, "{:.2f}".format(0))   #somma array recupero_sospesi_carte_pos
    totale_recupero_sospesi_carte_pos.trace("w", updateTotaleRecuperoSospesiCartePOS)
    totale_recupero_sospesi_bonifici = ctk.DoubleVar(creaprova, "{:.2f}".format(0))    #somma array recupero_sospesi_bonifici
    totale_recupero_sospesi_bonifici.trace("w", updateTotaleRecuperoSospesiBonifici)
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
    saldo_sospesi = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    punti_viva = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    punti_viva.trace("w", updatePuntiViva)
    quadratura_contante_cassa_assegno = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_entrate_cassa_contante = ctk.DoubleVar(creaprova, "{:.2f}".format(0))
    totale_entrate_cassa_contante.trace("w", updateTotaleEntrateCassaContante)
    commenti = ctk.StringVar(creaprova, "")



    #----TAB INCASSI----
    #Create frame inside the tab
    frame_incassi = ctk.CTkFrame(master=tabview.tab("Incassi"))
    frame_incassi.pack(pady=(20,0))
    #Premio lordo
    label_premio_lordo = ctk.CTkLabel(master=frame_incassi, text="Premio lordo:")
    label_premio_lordo.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_premio_lordo = ctk.CTkEntry(frame_incassi, textvariable=premio_lordo, width=100)
    entry_premio_lordo.grid(row=0, column=1, pady=10, padx=20, sticky="nw")
    #Movimenti bancari
    label_movimenti_bancari = ctk.CTkLabel(master=frame_incassi, text="Movimenti bancari:")
    label_movimenti_bancari.grid(row=3, column=0, pady=10, padx=20, sticky="ne")
    entry_movimenti_bancari = ctk.CTkEntry(frame_incassi, textvariable=movimenti_bancari, width=100)
    entry_movimenti_bancari.grid(row=3, column=1, pady=10, padx=20, sticky="nw")
    #Incasso polizze bonifici
    label_incasso_polizzebonifici = ctk.CTkLabel(master=frame_incassi, text="Incasso polizze bonifici:", font=("Helvetica",14,"bold"))
    label_incasso_polizzebonifici.grid(row=4, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_polizzebonifici = ctk.CTkEntry(frame_incassi, textvariable=incasso_polizze_bonifici, state="disabled", font=("Helvetica",15,"bold"), width=100)
    entry_incasso_polizzebonifici.grid(row=4, column=1, pady=10, padx=20, sticky="nw")
    #Totale carte/POS
    label_totale_carte_pos = ctk.CTkLabel(master=frame_incassi, text="Totale carte/POS:")
    label_totale_carte_pos.grid(row=5, column=0, pady=10, padx=20, sticky="ne")
    entry_totale_carte_pos = ctk.CTkEntry(frame_incassi, textvariable=totale_carte_pos, width=100)
    entry_totale_carte_pos.grid(row=5, column=1, pady=10, padx=20, sticky="nw")
    #Incasso polizze carte/POS
    label_incasso_polizzecartepos = ctk.CTkLabel(master=frame_incassi, text="Incasso polizze carte/POS:", font=("Helvetica",14,"bold"))
    label_incasso_polizzecartepos.grid(row=6, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_polizzecartepos = ctk.CTkEntry(frame_incassi, textvariable=incasso_polizze_carte_pos, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_incasso_polizzecartepos.grid(row=6, column=1, pady=10, padx=20, sticky="nw")

    #------TAB ALTRI INCASSI------
    #--Lista DAS--
    frame_das = ctk.CTkScrollableFrame(master=tabview.tab("Altri incassi"), width=500, height=250, border_color="black", border_width=1)
    frame_das.pack()

    #--DAS contanti--
    frame_das_contante = ctk.CTkFrame(master=frame_das)
    frame_das_contante.pack()
    def addDasContante():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            frame.destroy()
            print("DAS contante eliminato")
        print ("DAS contante aggiunto")
        frame = ctk.CTkFrame(frame_das_contante)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_das_contante, "{:.2f}".format(0))
        var1.trace("w", updateDasContanti)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)

    add_das_contante = ctk.CTkButton(frame_das_contante, text='+ DAS contante', command=addDasContante)
    add_das_contante.pack(padx=20, pady=(20,0))
    #Totale contante das
    frame_totale_das_contante = ctk.CTkFrame(master=frame_das)
    frame_totale_das_contante.pack()
    label_totale_das_contante = ctk.CTkLabel(master=frame_totale_das_contante, text="Totale DAS contanti:", font=("Helvetica",14,"bold"))
    label_totale_das_contante.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_totale_das_contante = ctk.CTkEntry(frame_totale_das_contante, textvariable=totale_das_contante, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_das_contante.grid(row=0, column=1, pady=20, padx=10, sticky="nw")
    
    #--DAS carte/pos--
    frame_das_cartepos = ctk.CTkFrame(master=frame_das)
    frame_das_cartepos.pack()
    def addDasCartePOS():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            frame.destroy()
            print("DAS carte/pos eliminato")
        print ("DAS carte/pos aggiunto")
        frame = ctk.CTkFrame(frame_das_cartepos)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_das_cartepos, "{:.2f}".format(0))
        var1.trace("w", updateDasCartePOS)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)

    add_das_cartepos = ctk.CTkButton(frame_das_cartepos, text='+ DAS carta/POS', command=addDasCartePOS)
    add_das_cartepos.pack(padx=20, pady=(20,0))
    #Totale carte/pos das
    frame_totale_das_cartepos = ctk.CTkFrame(master=frame_das)
    frame_totale_das_cartepos.pack()
    label_totale_das_cartepos = ctk.CTkLabel(master=frame_totale_das_cartepos, text="Totale DAS carte/POS:", font=("Helvetica",14,"bold"))
    label_totale_das_cartepos.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_totale_das_cartepos = ctk.CTkEntry(frame_totale_das_cartepos, textvariable=totale_das_cartepos, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_das_cartepos.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #--DAS bonifico--
    frame_das_bonifico = ctk.CTkFrame(master=frame_das)
    frame_das_bonifico.pack()
    def addDasBonifico():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            frame.destroy()
            print("DAS bonifico eliminato")
        print ("DAS bonifico aggiunto")
        frame = ctk.CTkFrame(frame_das_bonifico)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_das_bonifico, "{:.2f}".format(0))
        var1.trace("w", updateDasBonifici)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)

    add_das_bonifico = ctk.CTkButton(frame_das_bonifico, text='+ DAS bonifico', command=addDasBonifico)
    add_das_bonifico.pack(padx=20, pady=(20,0))
    #Totale carte/pos das
    frame_totale_das_bonifico = ctk.CTkFrame(master=frame_das)
    frame_totale_das_bonifico.pack()
    label_totale_das_bonifico = ctk.CTkLabel(master=frame_totale_das_bonifico, text="Totale DAS bonifici:", font=("Helvetica",14,"bold"))
    label_totale_das_bonifico.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_totale_das_bonifico = ctk.CTkEntry(frame_totale_das_bonifico, textvariable=totale_das_bonifico, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_das_bonifico.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #Totale DAS
    frame_totale_das=ctk.CTkFrame(master=tabview.tab("Altri incassi"))
    frame_totale_das.pack(pady=(0,15))
    label_totale_das = ctk.CTkLabel(master=frame_totale_das, text="Totale DAS:", font=("Helvetica",14,"bold"))
    label_totale_das.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_totale_das = ctk.CTkEntry(frame_totale_das, textvariable=totale_das, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_das.grid(row=0, column=1, pady=10, padx=20, sticky="nw")


    #--Lista incasso per conto--
    frame_incasso_per_conto = ctk.CTkScrollableFrame(master=tabview.tab("Altri incassi"), width=500, height=150, border_color="black", border_width=1)
    frame_incasso_per_conto.pack()

    def addIncassoPerConto():
        #Elimina sospeso carta/POS
        def destroy():
            var1.set(0)
            frame.destroy()
            print("Incasso per conto eliminato")
        print ("Incasso per conto aggiunto")
        frame = ctk.CTkFrame(frame_incasso_per_conto)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_incasso_per_conto, "{:.2f}".format(0))
        var1.trace("w", updateIncassoPerConto)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)

    add_incasso_per_conto = ctk.CTkButton(frame_incasso_per_conto, text='+ Incasso per conto', command=addIncassoPerConto)
    add_incasso_per_conto.pack(padx=20, pady=(20,0))

    #Totale incassi per conto
    frame_totale_incassi_per_conto=ctk.CTkFrame(master=tabview.tab("Altri incassi"))
    frame_totale_incassi_per_conto.pack(pady=(0,15))
    label_totale_incassi_per_conto = ctk.CTkLabel(master=frame_totale_incassi_per_conto, text="Totale incassi per conto:", font=("Helvetica",14,"bold"))
    label_totale_incassi_per_conto.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_totale_incassi_per_conto = ctk.CTkEntry(frame_totale_incassi_per_conto, textvariable=totale_incassi_per_conto, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_incassi_per_conto.grid(row=0, column=1, pady=10, padx=20, sticky="nw")




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
            frame.destroy()
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
    addboxButton = ctk.CTkButton(frame_sospesi, text='+ Sospeso', command=addSospeso)
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
            frame.destroy()
            print("Recupero sospeso contante eliminato")
        print ("Recupero sospeso contante aggiunto")
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

    add_contante_recuperato = ctk.CTkButton(frame_recuperosospesi_contante, text='+ Recupero contante', command=addSospContante)
    add_contante_recuperato.pack(padx=20, pady=(20,0))

    #Totale contante recuperato
    frame_contanterecuperato = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_contanterecuperato.pack()
    label_tot_contante_recuperato = ctk.CTkLabel(master=frame_contanterecuperato, text="Totale recupero sospesi contante:", font=("Helvetica",14,"bold"))
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
            frame.destroy()
            print("Recupero sospeso carta/POS eliminato")
        print ("Recupero sospeso carta/POS aggiunto")
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

    add_cartapos_recuperato = ctk.CTkButton(frame_recuperosospesi_cartapos, text='+ Recupero carta/POS', command=addSospCartePOS)
    add_cartapos_recuperato.pack(pady=(25,0))
    #Totale carte/POS recuperato
    frame_carteposrecuperato = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_carteposrecuperato.pack()
    label_tot_cartapos_recuperato = ctk.CTkLabel(master=frame_carteposrecuperato, text="Totale recupero sospesi carte/POS:", font=("Helvetica",14,"bold"))
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
            frame.destroy()
            print("Recupero sospeso bonifico eliminato")
        print ("Recupero sospeso bonifico aggiunto")
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

    add_bonifici_recuperato = ctk.CTkButton(frame_recuperosospesi_bonifici, text='+ Recupero bonifico', command=addSospBonifici)
    add_bonifici_recuperato.pack(pady=(25,0))
    #Totale bonifici recuperato
    frame_bonificirecuperato = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_bonificirecuperato.pack()
    label_tot_bonifici_recuperato = ctk.CTkLabel(master=frame_bonificirecuperato, text="Totale recupero sospesi bonifici:", font=("Helvetica",14,"bold"))
    label_tot_bonifici_recuperato.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_bonifici_recuperato = ctk.CTkEntry(frame_bonificirecuperato, textvariable=totale_recupero_sospesi_bonifici, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_bonifici_recuperato.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #Frame saldo sospesi
    frame_saldo_sospesi = ctk.CTkFrame(master=tabview.tab("Recupero sospesi"))
    frame_saldo_sospesi.pack(pady=(20,0))
    label_saldo_sospesi = ctk.CTkLabel(master=frame_saldo_sospesi, text="Saldo sospesi:", font=("Helvetica",14,"bold"))
    label_saldo_sospesi.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_saldo_sospesi = ctk.CTkEntry(frame_saldo_sospesi, textvariable=saldo_sospesi, font=("Helvetica",15,"bold"), width=100)
    entry_saldo_sospesi.grid(row=0, column=1, pady=10, padx=20, sticky="nw")


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

    frame_uscitevarieandversamenti = ctk.CTkScrollableFrame(master = tabview.tab("Uscite"), width=500, height=400, border_color="black", border_width=1)
    frame_uscitevarieandversamenti.pack()
    #--Aggiungi VERSAMENTI--
    frame_versamenti = ctk.CTkFrame(master=frame_uscitevarieandversamenti)
    frame_versamenti.pack()
    def addVersamento():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            frame.destroy()
            print("Versamento eliminato")
        print ("Versamento aggiunto")
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

    add_versamento = ctk.CTkButton(frame_versamenti, text='+ Versamento', command=addVersamento)
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
            frame.destroy()
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

    add_uscite_varie = ctk.CTkButton(frame_uscite_varie, text='+ Uscita extra', command=addUsciteVarie)
    add_uscite_varie.pack(padx=20, pady=(20,0))
    #Totale uscite varie
    frame_totaleuscitevarie = ctk.CTkFrame(master=frame_uscitevarieandversamenti)
    frame_totaleuscitevarie.pack()
    label_tot_uscite_varie = ctk.CTkLabel(master=frame_totaleuscitevarie, text="Totale uscite extra:", font=("Helvetica",14,"bold"))
    label_tot_uscite_varie.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_uscite_varie = ctk.CTkEntry(frame_totaleuscitevarie, textvariable=totale_uscite_varie, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_uscite_varie.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #--Frame in fondo a uscite--
    frame_totale_generale_uscite_e_quadratura = ctk.CTkFrame(master=tabview.tab("Uscite"))
    frame_totale_generale_uscite_e_quadratura.pack(pady=(20,0))
    #--Totale generale uscite--
    label_totale_generale_uscite = ctk.CTkLabel(master=frame_totale_generale_uscite_e_quadratura, text="Totale generale uscite:", font=("Helvetica",14,"bold"))
    label_totale_generale_uscite.grid(row=1, column=0, pady=10, padx=10, sticky="ne")
    entry_totale_generale_uscite = ctk.CTkEntry(frame_totale_generale_uscite_e_quadratura, textvariable=totale_generale_uscite, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_generale_uscite.grid(row=1, column=1, pady=10, padx=10, sticky="nw")
    #--Quadratura contante cassa + assegno--
    label_quadratura_contante_cassa_assegno = ctk.CTkLabel(master=frame_totale_generale_uscite_e_quadratura, text="Quadratura contante cassa + assegno:", font=("Helvetica",14,"bold"))
    label_quadratura_contante_cassa_assegno.grid(row=2, column=0, pady=10, padx=10, sticky="ne")
    entry_quadratura_contante_cassa_assegno = ctk.CTkEntry(frame_totale_generale_uscite_e_quadratura, textvariable=quadratura_contante_cassa_assegno, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_quadratura_contante_cassa_assegno.grid(row=2, column=1, pady=10, padx=10, sticky="nw")

    #----TAB MARCHIROLO----
    frame_marchirolo = ctk.CTkScrollableFrame(master=tabview.tab("Marchirolo"), width=500, height=300, border_color="black", border_width=1)
    frame_marchirolo.pack()
    def addUscitaMarchirolo():
        #Elimina sospeso carta/POS
        def destroy():
            var1.set(0)
            frame.destroy()
            print("Marchirolo eliminato")
        print ("Marchirolo aggiunto")
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

    add_uscitamarchirolo = ctk.CTkButton(frame_marchirolo, text='+ Cassa Marchirolo', command=addUscitaMarchirolo)
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
    label_tot_parziale_1 = ctk.CTkLabel(master=frame_resoconto, text="Tot. parz. 1 | Cassa contanti:", font=("Helvetica",14,"bold"))
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
    #Totale sospesi contante recuperato
    label_tot_contante_recuperato_copia = ctk.CTkLabel(master=frame_resoconto, text="Totale recupero sospesi contante:", font=("Helvetica",14,"bold"))
    label_tot_contante_recuperato_copia.grid(row=2, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_contante_recuperato_copia = ctk.CTkEntry(frame_resoconto, textvariable=totale_recupero_sospesi_contanti, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_contante_recuperato_copia.grid(row=2, column=1, pady=10, padx=20, sticky="nw")
    explain_tot_contante_recuperato_copia = ctk.CTkLabel(master=frame_resoconto, text="Tot. parz. 2 + tot. rec. sosp. contante", text_color="#969595", font=("Helvetica",13))
    explain_tot_contante_recuperato_copia.grid(row=2, column=2, pady=10, padx=20, sticky="nw")
    #Totale entrate cassa contante
    label_totale_entrate_cassa_contante = ctk.CTkLabel(master=frame_resoconto, text="Totale entrate cassa contante:", font=("Helvetica",14,"bold"))
    label_totale_entrate_cassa_contante.grid(row=3, column=0, pady=10, padx=20, sticky="ne")
    entry_totale_entrate_cassa_contante = ctk.CTkEntry(frame_resoconto, textvariable=totale_entrate_cassa_contante, font=("Helvetica",15,"bold"), width=100)
    entry_totale_entrate_cassa_contante.grid(row=3, column=1, pady=10, padx=20, sticky="nw")
    #Totale generale uscite
    label_totale_generale_uscite_copia = ctk.CTkLabel(master=frame_resoconto, text="Totale generale uscite:", font=("Helvetica",14,"bold"))
    label_totale_generale_uscite_copia.grid(row=4, column=0, pady=10, padx=20, sticky="ne")
    entry_totale_generale_uscite_copia = ctk.CTkEntry(frame_resoconto, textvariable=totale_generale_uscite, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_generale_uscite_copia.grid(row=4, column=1, pady=10, padx=20, sticky="nw")
    explain_totale_generale_uscite_copia = ctk.CTkLabel(master=frame_resoconto, text="Abbuoni + p.ti Viva + uscite varie + versamenti", text_color="#969595", font=("Helvetica",13))
    explain_totale_generale_uscite_copia.grid(row=4, column=2, pady=10, padx=20, sticky="nw")
    #Fondo cassa da riportare
    label_fondodariportare = ctk.CTkLabel(master=frame_resoconto, text="Fondo cassa da riportate:", font=("Helvetica",14,"bold"))
    label_fondodariportare.grid(row=5, column=0, pady=10, padx=20, sticky="ne")
    entry_fondodariportare = ctk.CTkEntry(frame_resoconto, textvariable=fondo_cassa_da_riportare, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_fondodariportare.grid(row=5, column=1, pady=10, padx=20, sticky="nw")
    #Totale Marchirolo COPIA
    label_tot_marchirolo_copy = ctk.CTkLabel(master=frame_resoconto, text="Totale Marchirolo:", font=("Helvetica",14,"bold"))
    label_tot_marchirolo_copy.grid(row=6, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_marchirolo_copy = ctk.CTkEntry(frame_resoconto, textvariable=totale_marchirolo, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_marchirolo_copy.grid(row=6, column=1, pady=10, padx=20, sticky="nw")
    explain_tot_marchirolo_copy = ctk.CTkLabel(master=frame_resoconto, text="Totale uscite Marchirolo", text_color="#969595", font=("Helvetica",13))
    explain_tot_marchirolo_copy.grid(row=6, column=2, pady=10, padx=20, sticky="nw")
    #Saldo cassa
    label_saldocassa = ctk.CTkLabel(master=frame_resoconto, text="Saldo cassa:", font=("Helvetica",14,"bold"))
    label_saldocassa.grid(row=7, column=0, pady=10, padx=20, sticky="ne")
    entry_saldocassa = ctk.CTkEntry(frame_resoconto, textvariable=saldo_cassa, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_saldocassa.grid(row=7, column=1, pady=10, padx=20, sticky="nw")
    explain_saldocassa = ctk.CTkLabel(master=frame_resoconto, text="F. cass da riportare + tot. Marchirolo", text_color="#969595", font=("Helvetica",13))
    explain_saldocassa.grid(row=7, column=2, pady=10, padx=20, sticky="nw")
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
            print("Aggiungo il file chiamato"+tail)
            dataperfile = (today_date_formatted.get()).split('-')
            #Se la cartella della categoria non esiste, creala
            if not os.path.exists(percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()):     
                os.makedirs(percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get())
            #Se dai un nuovo nome al file
            if(new_filename != ""):
                #os.rename(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)
                #os.replace(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)
                shutil.move(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)    
            #Altrimenti spostalo con lo stesso nome
            else:
                #os.rename(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+filename+file_extension)
                #os.replace(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+filename+file_extension)
                shutil.move(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+tail)    
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

    carica_documento = ctk.CTkButton(tabview.tab("Documenti"), text='+ Documento', command=uploadFile)
    carica_documento.pack(padx=20, pady=(20,0))
    


    def sendToDatabase():
        def causaleVuota(nome_frame):
            isvalore = True
            for child in nome_frame.winfo_children():                #Scorri ogni elemento nel frame-padre
                if isinstance(child, ctk.CTkFrame):             #Se è un sotto-frame
                    for child2 in child.winfo_children():       #scorri ogni elemento nel sotto-frame
                        if isinstance(child2, ctk.CTkEntry):    #se è una entry
                            if isvalore==True:                  #ed è il valore, la prossima entry sarà la causale
                                isvalore=False
                            else:                               #altrimenti è la causale: se è vuota ritorna "True", altrimenti la prossima entry sarà il valore
                                if child2.get()=="":
                                    return(True)
                                isvalore = True
            return(False)

        if causaleVuota(frame_versamenti):
            showConfirmMessage(creaprova, "Attenzione", "La causale dei versamenti non può essere vuota", "warning", False) 
        else:
            conn = sqlite3.connect(percorso_database)
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON;")
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
                        +str(safeLoad(premio_lordo))+", "
                        +str(safeLoad(movimenti_bancari))+", "
                        +str(safeLoad(incasso_polizze_bonifici))+", "
                        +str(safeLoad(totale_carte_pos))+", "
                        +str(safeLoad(incasso_polizze_carte_pos))+", "
                        +str(safeLoad(totale_das_contante))+", "
                        +str(safeLoad(totale_das_bonifico))+", "
                        +str(safeLoad(totale_das_cartepos))+", "
                        +str(safeLoad(totale_das))+", "
                        +str(safeLoad(totale_incassi_per_conto))+", "
                        +str(safeLoad(totale_sospesi))+", "
                        +str(safeLoad(totale_parziale_1))+", "
                        +str(safeLoad(fondo_cassa_precedente))+", "
                        +str(safeLoad(totale_recupero_sospesi_contanti))+", "
                        +str(safeLoad(totale_recupero_sospesi_carte_pos))+", "
                        +str(safeLoad(totale_recupero_sospesi_bonifici))+", "
                        +str(safeLoad(totale_abbuoni))+", "
                        +str(safeLoad(totale_uscite_varie))+", "
                        +str(safeLoad(totale_uscite_versamenti))+", "
                        +str(safeLoad(totale_generale_uscite))+", "
                        +str(safeLoad(fondo_cassa_da_riportare))+", "
                        +str(safeLoad(totale_marchirolo))+", "
                        +str(safeLoad(saldo_cassa))+", "
                        +str(safeLoad(saldo_sospesi))+", "
                        +str(safeLoad(punti_viva))+", "
                        +str(safeLoad(quadratura_contante_cassa_assegno))+", "
                        +str(safeLoad(totale_entrate_cassa_contante))+", "
                        +"'"+str(entry_commenti.get('0.0','end'))+"',"+
                        " 'false')"
                )
                conn.commit()
                
                #Scorri lista e aggiungi: is valore si alterna tra True e False
                def listToDatabase(frame, categoria):
                    isvalore = True
                    for child in frame.winfo_children():                #Scorri ogni elemento nel frame-padre
                        if isinstance(child, ctk.CTkFrame):             #Se è un sotto-frame
                            for child2 in child.winfo_children():       #scorri ogni elemento nel sotto-frame
                                if isinstance(child2, ctk.CTkEntry):    #se è una entry
                                    if isvalore==True:                  #ed è il valore, salva il valore e la prossima entry sarà la causale
                                        valore=child2.get()
                                        isvalore=False
                                    else:                               #altrimenti è la causale, quindi salva la causale e la prossima entry sarà il valore
                                        causale=child2.get()
                                        isvalore = True
                            c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                                    +"'"+categoria+"', "
                                    +valore+", '"
                                    +causale+
                                    "')"
                            )
                    conn.commit()
                
                listToDatabase(frame_sospesi, "sospesi")
                listToDatabase(frame_recuperosospesi_contante, "recupero_contanti")
                listToDatabase(frame_recuperosospesi_cartapos, "recupero_cartepos")
                listToDatabase(frame_recuperosospesi_bonifici, "recupero_bonifici")
                listToDatabase(frame_versamenti, "uscite_versamenti")
                listToDatabase(frame_uscite_varie, "uscite_varie")
                listToDatabase(frame_marchirolo, "marchirolo")
                listToDatabase(frame_das_contante, "das_contanti")
                listToDatabase(frame_das_cartepos, "das_cartepos")
                listToDatabase(frame_das_bonifico, "das_bonifico")
                listToDatabase(frame_incasso_per_conto, "incasso_per_conto")



                conn.close()
                showConfirmMessage(creaprova, "Caricamento completato", "Dati correttamente aggiunti al database", "check", True)

    #----SAVE BUTTON----
    save_btn = ctk.CTkButton(creaprova, text='Salva', fg_color="#809d5f", hover_color="#B7C019", command=sendToDatabase)
    #save_btn.pack()
    save_btn.pack(side="right", pady=(0,5), padx=(0,20))
    #------FINE CREAZIONE GUI------

    #Ottieni fondo cassa dal giorno precedente
    updateData()

    def close_window():
        exitFromApp(creaprova)
    creaprova.protocol('WM_DELETE_WINDOW', close_window)
    creaprova.mainloop()


#****VISUALIZZA DATABASE****
def visualizzaProva():
    home.destroy()
    #root
    visualizzaprova = ctk.CTk()
    visualizzaprova.title("Visualizza prova giornaliera")

    app_size = str(app_width)+str(app_height)
    visualizzaprova.geometry(app_size)
    visualizzaprova.minsize(app_width-20, app_height)
    visualizzaprova.iconbitmap(percorso_applicazione+"app_icon.ico")

    #Place window in center of screen
    ws = visualizzaprova.winfo_screenwidth()
    hs = visualizzaprova.winfo_screenheight()
    x = (ws/2) - (app_width/2)
    y = (hs/2) - (app_height/2)
    visualizzaprova.geometry('%dx%d+%d+%d' % (app_width, app_height, x, y))



    #CAMBIAMENTO DI VARIABILI: Le seguenti variabili sono associate ad una variabile. Quando questa cambia valore, permette di aggiornare altre entries, come specificato all'interno di ogni def
    def updateLista(nome_frame, entry):
        somma=0
        isvalore = True
        for child in nome_frame.winfo_children():           #Scorri ogni elemento nel frame-padre
            if isinstance(child, ctk.CTkFrame):             #Se è un sotto-frame
                for child2 in child.winfo_children():       #scorri ogni elemento nel sotto-frame
                    if isinstance(child2, ctk.CTkEntry):    #se è una entry
                        if isvalore==True:                  #ed è il valore, aggiorna somma. la prossima entry sarà la causale
                            try: valore=float(child2.get())
                            except: valore=0
                            somma=somma+valore   
                            isvalore=False
                        else:                               #altrimenti è la causale: la prossima entry sarà il valore
                            isvalore = True
        entry.configure(state='normal')                     #Aggiorna la entry
        entry.delete(0,'end')
        entry.insert('end', "{:.2f}".format(somma))
        entry.configure(state='disabled')

    def updatePremioLordo(*args):
        #Aggiorna totale parziale 1
        try: a=premio_lordo.get()
        except: a=0
        try: b=totale_incassi_per_conto.get()
        except: b=0
        try: c=totale_das_contante.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')
    def updateTotaleIncassoPerConto(*args):
        #Aggiorna totale parziale 1
        try: a=premio_lordo.get()
        except: a=0
        try: b=totale_incassi_per_conto.get()
        except: b=0
        try: c=totale_das_contante.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')
    def updateMovimentiBancari(*args):
        #Aggiorna Incasso polizze bonifici
        try: a=movimenti_bancari.get()
        except: a=0
        try: b=totale_das_bonifico.get()
        except: b=0
        result2=a+b
        entry_incasso_polizzebonifici.configure(state='normal')
        entry_incasso_polizzebonifici.delete(0,'end')
        entry_incasso_polizzebonifici.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzebonifici.configure(state='disabled')
    def updateIncassoPolizzeBonifici(*args):
        #Aggiorna totale parziale 1
        try: a=premio_lordo.get()
        except: a=0
        try: b=totale_incassi_per_conto.get()
        except: b=0
        try: c=totale_das_contante.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')
    def updateTotaleCartePOS(*args):
        #Aggiorna incasso polizze pos/carte
        try: a=totale_carte_pos.get()
        except: a=0
        try: b=totale_recupero_sospesi_carte_pos.get()
        except: b=0
        result2=a+b
        entry_incasso_polizzecartepos.configure(state='normal')
        entry_incasso_polizzecartepos.delete(0,'end')
        entry_incasso_polizzecartepos.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzecartepos.configure(state='disabled')
    def updateIncassoPolizzeCartePOS(*args):
        #Aggiorna totale parziale 1
        try: a=premio_lordo.get()
        except: a=0
        try: b=totale_incassi_per_conto.get()
        except: b=0
        try: c=totale_das_contante.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')
    def updateTotaleParziale1(*args):
        #Aggiorna totale entrate cassa contante
        try: a=totale_parziale_1.get()
        except: a=0
        try: b=fondo_cassa_precedente.get()
        except: b=0
        try: c=totale_recupero_sospesi_contanti.get()
        except: c=0
        result=a+b+c
        entry_totale_entrate_cassa_contante.configure(state='normal')
        entry_totale_entrate_cassa_contante.delete(0,'end')
        entry_totale_entrate_cassa_contante.insert('end', "{:.2f}".format(result))
        entry_totale_entrate_cassa_contante.configure(state='disabled')
        #Aggiorna Quadratura contante cassa + assegno
        try: g=totale_abbuoni.get()
        except: g=0
        try: h=punti_viva.get()
        except: h=0
        result3=a+c-g-h
        entry_quadratura_contante_cassa_assegno.configure(state='normal')
        entry_quadratura_contante_cassa_assegno.delete(0,'end')
        entry_quadratura_contante_cassa_assegno.insert('end', "{:.2f}".format(result3))
        entry_quadratura_contante_cassa_assegno.configure(state='disabled')
    def updateFondoCassaPrecedente(*args):
        #Aggiorna totale entrate cassa contante
        try: a=totale_parziale_1.get()
        except: a=0
        try: b=fondo_cassa_precedente.get()
        except: b=0
        try: c=totale_recupero_sospesi_contanti.get()
        except: c=0
        result=a+b+c
        entry_totale_entrate_cassa_contante.configure(state='normal')
        entry_totale_entrate_cassa_contante.delete(0,'end')
        entry_totale_entrate_cassa_contante.insert('end', "{:.2f}".format(result))
        entry_totale_entrate_cassa_contante.configure(state='disabled')
    def updateTotaleRecuperoSospesiContanti(*args):
        #Aggiorna saldo sospesi
        try: a=totale_sospesi.get()
        except: a=0
        try: b=totale_recupero_sospesi_contanti.get()
        except: b=0
        try: c=totale_recupero_sospesi_carte_pos.get()
        except: c=0
        try: d=totale_recupero_sospesi_bonifici.get()
        except: d=0
        result=a-b-c-d
        entry_saldo_sospesi.configure(state='normal')
        entry_saldo_sospesi.delete(0,'end')
        entry_saldo_sospesi.insert('end', "{:.2f}".format(result))
        entry_saldo_sospesi.configure(state='disabled')

        #Aggiorna Totale entrate cassa contante
        try: e=totale_parziale_1.get()
        except: e=0
        try: f=fondo_cassa_precedente.get()
        except: f=0
        result2=e+f+b
        entry_totale_entrate_cassa_contante.configure(state='normal')
        entry_totale_entrate_cassa_contante.delete(0,'end')
        entry_totale_entrate_cassa_contante.insert('end', "{:.2f}".format(result2))
        entry_totale_entrate_cassa_contante.configure(state='disabled')

        #Aggiorna Quadratura contante cassa + assegno
        try: g=totale_abbuoni.get()
        except: g=0
        try: h=punti_viva.get()
        except: h=0
        result3=e+b-g-h
        entry_quadratura_contante_cassa_assegno.configure(state='normal')
        entry_quadratura_contante_cassa_assegno.delete(0,'end')
        entry_quadratura_contante_cassa_assegno.insert('end', "{:.2f}".format(result3))
        entry_quadratura_contante_cassa_assegno.configure(state='disabled')
    def updateTotaleRecuperoSospesiCartePOS(*args):
        #Aggiorna saldo sospesi
        try: a=totale_sospesi.get()
        except: a=0
        try: b=totale_recupero_sospesi_contanti.get()
        except: b=0
        try: c=totale_recupero_sospesi_carte_pos.get()
        except: c=0
        try: d=totale_recupero_sospesi_bonifici.get()
        except: d=0
        result=a-b-c-d
        entry_saldo_sospesi.configure(state='normal')
        entry_saldo_sospesi.delete(0,'end')
        entry_saldo_sospesi.insert('end', "{:.2f}".format(result))
        entry_saldo_sospesi.configure(state='disabled')
    def updateTotaleRecuperoSospesiBonifici(*args):
        #Aggiorna saldo sospesi
        try: a=totale_sospesi.get()
        except: a=0
        try: b=totale_recupero_sospesi_contanti.get()
        except: b=0
        try: c=totale_recupero_sospesi_carte_pos.get()
        except: c=0
        try: d=totale_recupero_sospesi_bonifici.get()
        except: d=0
        result=a-b-c-d
        entry_saldo_sospesi.configure(state='normal')
        entry_saldo_sospesi.delete(0,'end')
        entry_saldo_sospesi.insert('end', "{:.2f}".format(result))
        entry_saldo_sospesi.configure(state='disabled')
    def updateTotaleAbbuoni(*args):
        #Aggiorna Totale generale uscite
        try: a=totale_abbuoni.get()
        except: a=0
        try: b=totale_uscite_varie.get()
        except: b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_totale_generale_uscite.configure(state='normal')
        entry_totale_generale_uscite.delete(0,'end')
        entry_totale_generale_uscite.insert('end', "{:.2f}".format(result))
        entry_totale_generale_uscite.configure(state='disabled')

        #Aggiorna Quadratura contante cassa + assegno
        try: e=totale_parziale_1.get()
        except: g=0
        try: f=totale_recupero_sospesi_contanti.get()
        except: h=0
        result2=e+f-a-d
        entry_quadratura_contante_cassa_assegno.configure(state='normal')
        entry_quadratura_contante_cassa_assegno.delete(0,'end')
        entry_quadratura_contante_cassa_assegno.insert('end', "{:.2f}".format(result2))
        entry_quadratura_contante_cassa_assegno.configure(state='disabled')
    def updateTotaleUsciteVarie(*args):
        #Aggiorna Totale generale uscite
        try:a=totale_abbuoni.get()
        except:a=0
        try:b=totale_uscite_varie.get()
        except:b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_totale_generale_uscite.configure(state='normal')
        entry_totale_generale_uscite.delete(0,'end')
        entry_totale_generale_uscite.insert('end', "{:.2f}".format(result))
        entry_totale_generale_uscite.configure(state='disabled')
    def updateTotaleGeneraleUscite(*args):
        #Aggiorna fondo cassa da riportare
        try: a=totale_entrate_cassa_contante.get()
        except: a=0
        try: b=totale_generale_uscite.get()
        except: b=0
        result=a-b
        entry_fondodariportare.configure(state='normal')
        entry_fondodariportare.delete(0,'end')
        entry_fondodariportare.insert('end', "{:.2f}".format(result))
        entry_fondodariportare.configure(state='disabled')
    def updateFondoCassaDaRiportare(*args):
        #Aggiorna saldo cassa
        try: a=fondo_cassa_da_riportare.get()
        except: a=0
        try: b=totale_marchirolo.get()
        except: b=0
        result=a-b
        entry_saldocassa.configure(state='normal')
        entry_saldocassa.delete(0,'end')
        entry_saldocassa.insert('end', "{:.2f}".format(result))
        entry_saldocassa.configure(state='disabled')
    def updateIncassoPerConto(*args):
        updateLista(frame_incasso_per_conto, entry_totale_incassi_per_conto)
    def updateSospesi(*args):
        updateLista(frame_sospesi, entry_sospesi)
    def updateRecuperoContanti(*args):
        #Aggiorna totale recupero sospesi contanti
        updateLista(frame_recuperosospesi_contante, entry_tot_contante_recuperato)
    def updateRecuperoCartePOS(*args):
        #Aggiorna totale recupero sospesi carte/pos
        updateLista(frame_recuperosospesi_cartapos, entry_tot_cartapos_recuperato)
    def updateRecuperoBonifici(*args):
        #Aggiorna totale recupero sospesi carte/pos
        updateLista(frame_recuperosospesi_bonifici, entry_tot_bonifici_recuperato)
    def updateUsciteVarie(*args):
        #Aggiorna totale uscite varie
        updateLista(frame_uscite_varie, entry_tot_uscite_varie)
    def updateVersamenti(*args):
        #Aggiorna totale versamenti
        updateLista(frame_versamenti, entry_tot_versamenti)
    def updateMarchirolo(*args):
        #Aggiorna totale marchirolo
        updateLista(frame_marchirolo, entry_tot_marchirolo)
    def updateDasContanti(*args):
        updateLista(frame_das_contante, entry_totale_das_contante)
    def updateDasCartePOS(*args):
        updateLista(frame_das_cartepos, entry_totale_das_cartepos)
    def updateDasBonifici(*args):
        updateLista(frame_das_bonifico, entry_totale_das_bonifico)
    def updateTotaleMarchirolo(*args):
        #Aggiorna saldo cassa
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
        try: a=premio_lordo.get()
        except: a=0
        try: b=totale_incassi_per_conto.get()
        except: b=0
        try: c=totale_das_contante.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')

        #Aggiorna saldo sospesi
        try: g=totale_recupero_sospesi_contanti.get()
        except: g=0
        try: h=totale_recupero_sospesi_carte_pos.get()
        except: h=0
        try: i=totale_recupero_sospesi_bonifici.get()
        except: i=0
        result2=f-g-h-i
        entry_saldo_sospesi.configure(state='normal')
        entry_saldo_sospesi.delete(0,'end')
        entry_saldo_sospesi.insert('end', "{:.2f}".format(result2))
        entry_saldo_sospesi.configure(state='disabled')

    def updateUsciteVersamenti(*args):
        #Aggiorna Totale generale uscite
        try: a=totale_abbuoni.get()
        except: a=0
        try: b=totale_uscite_varie.get()
        except: b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_totale_generale_uscite.configure(state='normal')
        entry_totale_generale_uscite.delete(0,'end')
        entry_totale_generale_uscite.insert('end', "{:.2f}".format(result))
        entry_totale_generale_uscite.configure(state='disabled')
    def updatePuntiViva(*args):
        #Aggiorna Totale generale uscite
        try: a=totale_abbuoni.get()
        except: a=0
        try: b=totale_uscite_varie.get()
        except: b=0
        try:c=totale_uscite_versamenti.get()
        except:c=0
        try:d=punti_viva.get()
        except:d=0
        result=a+b+c+d
        entry_totale_generale_uscite.configure(state='normal')
        entry_totale_generale_uscite.delete(0,'end')
        entry_totale_generale_uscite.insert('end', "{:.2f}".format(result))
        entry_totale_generale_uscite.configure(state='disabled')

        #Aggiorna Quadratura contante cassa + assegno
        try: e=totale_parziale_1.get()
        except: g=0
        try: f=totale_recupero_sospesi_contanti.get()
        except: h=0
        result2=e+f-a-d
        entry_quadratura_contante_cassa_assegno.configure(state='normal')
        entry_quadratura_contante_cassa_assegno.delete(0,'end')
        entry_quadratura_contante_cassa_assegno.insert('end', "{:.2f}".format(result2))
        entry_quadratura_contante_cassa_assegno.configure(state='disabled')
    def updateTotaleDasContanti(*args):
        #Aggiorna totale parziale 1
        try: a=premio_lordo.get()
        except: a=0
        try: b=totale_incassi_per_conto.get()
        except: b=0
        try: c=totale_das_contante.get()
        except: c=0
        try: d=incasso_polizze_bonifici.get()
        except: d=0
        try: e=incasso_polizze_carte_pos.get()
        except: e=0
        try: f=totale_sospesi.get()
        except: f=0
        result=a+b+c-d-e-f
        entry_tot_parziale_1.configure(state='normal')
        entry_tot_parziale_1.delete(0,'end')
        entry_tot_parziale_1.insert('end', "{:.2f}".format(result))
        entry_tot_parziale_1.configure(state='disabled')

        #Aggiorna totale DAS
        try: g=totale_das_cartepos.get()
        except:g=0
        try: h=totale_das_bonifico.get()
        except:h=0
        result=c+g+h
        entry_totale_das.configure(state='normal')
        entry_totale_das.delete(0,'end')
        entry_totale_das.insert('end', "{:.2f}".format(result))
        entry_totale_das.configure(state='disabled')
    def updateTotaleDasBonifico(*args):
        #Aggiorna totale DAS
        try: a=totale_das_contante.get()
        except: a=0
        try: b=totale_das_cartepos.get()
        except:b=0
        try: c=totale_das_bonifico.get()
        except:c=0
        result=a+b+c
        entry_totale_das.configure(state='normal')
        entry_totale_das.delete(0,'end')
        entry_totale_das.insert('end', "{:.2f}".format(result))
        entry_totale_das.configure(state='disabled')

        #Aggiorna incasso polizze bonifici
        try: d=movimenti_bancari.get()
        except: d=0
        result2=d+c
        entry_incasso_polizzebonifici.configure(state='normal')
        entry_incasso_polizzebonifici.delete(0,'end')
        entry_incasso_polizzebonifici.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzebonifici.configure(state='disabled')
    def updateTotaleDasCartePOS(*args):
        #Aggiorna totale DAS
        try: a=totale_das_contante.get()
        except: a=0
        try: b=totale_das_cartepos.get()
        except:b=0
        try: c=totale_das_bonifico.get()
        except:c=0
        result=a+b+c
        entry_totale_das.configure(state='normal')
        entry_totale_das.delete(0,'end')
        entry_totale_das.insert('end', "{:.2f}".format(result))
        entry_totale_das.configure(state='disabled')

        #Aggiorna incasso polizze carte/pos
        try: d=totale_carte_pos.get()
        except: d=0
        result2=b+d
        entry_incasso_polizzecartepos.configure(state='normal')
        entry_incasso_polizzecartepos.delete(0,'end')
        entry_incasso_polizzecartepos.insert('end', "{:.2f}".format(result2))
        entry_incasso_polizzecartepos.configure(state='disabled')
    def updateTotaleEntrateCassaContante(*args):
        #Aggiorna fondo cassa da riportare
        try: a=totale_entrate_cassa_contante.get()
        except: a=0
        try: b=totale_generale_uscite.get()
        except: b=0
        result=a-b
        entry_fondodariportare.configure(state='normal')
        entry_fondodariportare.delete(0,'end')
        entry_fondodariportare.insert('end', "{:.2f}".format(result))
        entry_fondodariportare.configure(state='disabled')
     


    #DICHIARAZIONE VARIABILI
    premio_lordo = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    premio_lordo.trace("w", updatePremioLordo)
    movimenti_bancari = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    movimenti_bancari.trace("w", updateMovimentiBancari)
    incasso_polizze_bonifici = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))   
    incasso_polizze_bonifici.trace("w", updateIncassoPolizzeBonifici)
    totale_carte_pos = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_carte_pos.trace("w", updateTotaleCartePOS)
    incasso_polizze_carte_pos = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    incasso_polizze_carte_pos.trace("w", updateIncassoPolizzeCartePOS)
    totale_das_contante = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_das_contante.trace("w", updateTotaleDasContanti)
    totale_das_bonifico = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_das_bonifico.trace("w", updateTotaleDasBonifico)
    totale_das_cartepos = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_das_cartepos.trace("w", updateTotaleDasCartePOS)
    totale_das = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_incassi_per_conto = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_incassi_per_conto.trace("w", updateTotaleIncassoPerConto)
    totale_sospesi = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_sospesi.trace("w", updateTotaleSospesi)
    totale_parziale_1 = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))                   
    totale_parziale_1.trace("w", updateTotaleParziale1)
    fondo_cassa_precedente = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    fondo_cassa_precedente.trace("w", updateFondoCassaPrecedente)
    totale_recupero_sospesi_contanti = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))    #somma array recupero_sospesi_contanti
    totale_recupero_sospesi_contanti.trace("w", updateTotaleRecuperoSospesiContanti)
    totale_recupero_sospesi_carte_pos = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))   #somma array recupero_sospesi_carte_pos
    totale_recupero_sospesi_carte_pos.trace("w", updateTotaleRecuperoSospesiCartePOS)
    totale_recupero_sospesi_bonifici = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))    #somma array recupero_sospesi_bonifici
    totale_recupero_sospesi_bonifici.trace("w", updateTotaleRecuperoSospesiBonifici)
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
    saldo_cassa = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))                         #fondo_cassa_da_riportare - totale_marchirolo - totale_mimmo - totale_ditta
    saldo_sospesi = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    punti_viva = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    punti_viva.trace("w", updatePuntiViva)
    quadratura_contante_cassa_assegno = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_entrate_cassa_contante = ctk.DoubleVar(visualizzaprova, "{:.2f}".format(0))
    totale_entrate_cassa_contante.trace("w", updateTotaleEntrateCassaContante)
    commenti = ctk.StringVar(visualizzaprova, "")
    completato = ctk.StringVar(visualizzaprova, "")


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
        for item in row:
            ctk_entry.configure(state='normal')
            ctk_entry.insert('0.0', "\n".join(item))
            ctk_entry.configure(state='disabled')
    
    def aggiornaTutteLeEntries(*args):
        updateSospesi()
        updateRecuperoContanti()
        updateRecuperoCartePOS()
        updateRecuperoBonifici()
        updateUsciteVarie()
        updateVersamenti()
        updateMarchirolo()
        updateDasContanti()
        updateDasCartePOS()
        updateDasBonifici()
        updateIncassoPerConto()
    def destroy(nome_frame, posizione):
        nome_frame.destroy()
        aggiornaTutteLeEntries()
        

    #SELECT dalle liste del database e aggiorna lista
    def saveDataList(frame_import, categoria, defUpdate, c):
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
                delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=lambda f=nomeentry: destroy(frame, f), state="disabled")
                delete_button.grid(row=1, column=2)
        for valore,causale in rows:
            createFrame(valore, causale)
            nomeentry = nomeentry + 1
        
    

    def getDataFromDatabase():
        conn = sqlite3.connect(percorso_database)
        c = conn.cursor()

        saveData("premio_lordo", entry_premio_lordo, premio_lordo, c)
        saveData("movimenti_bancari", entry_movimenti_bancari, movimenti_bancari, c)
        saveData("incasso_polizze_bonifici", entry_incasso_polizzebonifici, incasso_polizze_bonifici, c)
        saveData("totale_carte_pos", entry_totale_carte_pos, totale_carte_pos, c)
        saveData("incasso_polizze_carte_pos", entry_incasso_polizzecartepos, incasso_polizze_carte_pos, c)
        saveData("totale_das_contante", entry_totale_das_contante, totale_das_contante, c)
        saveData("totale_das_bonifico", entry_totale_das_bonifico, totale_das_bonifico, c)
        saveData("totale_das_cartepos", entry_totale_das_cartepos, totale_das_cartepos, c)
        saveData("totale_das", entry_totale_das, totale_das, c)
        saveData("totale_incassi_per_conto", entry_totale_incassi_per_conto, totale_incassi_per_conto, c)
        saveData("totale_sospesi", entry_sospesi, totale_sospesi, c)
        saveData("totale_parziale_1", entry_tot_parziale_1, totale_parziale_1, c)
        saveData("fondo_cassa_precedente", entry_cassaprecedente, fondo_cassa_precedente, c)
        saveData("totale_recupero_sospesi_contanti", entry_tot_contante_recuperato, totale_recupero_sospesi_contanti, c)
        saveData("totale_recupero_sospesi_carte_pos", entry_tot_cartapos_recuperato, totale_recupero_sospesi_carte_pos, c)
        saveData("totale_recupero_sospesi_bonifici", entry_tot_bonifici_recuperato, totale_recupero_sospesi_bonifici, c)
        saveData("totale_entrate_cassa_contante", entry_totale_entrate_cassa_contante, totale_entrate_cassa_contante, c)
        saveData("totale_abbuoni", entry_abbuoni, totale_abbuoni, c)
        saveData("totale_uscite_varie", entry_tot_uscite_varie, totale_uscite_varie, c)
        saveData("totale_uscite_versamenti", entry_tot_versamenti, totale_uscite_versamenti, c)
        saveData("totale_generale_uscite", entry_totale_generale_uscite, totale_generale_uscite, c)
        saveData("fondo_cassa_da_riportare", entry_fondodariportare, fondo_cassa_da_riportare, c)
        saveData("totale_marchirolo", entry_tot_marchirolo, totale_marchirolo, c)
        saveData("saldo_cassa", entry_saldocassa, saldo_cassa, c)
        saveData("saldo_sospesi", entry_saldo_sospesi, saldo_sospesi, c)
        saveData("punti_viva", entry_viva, punti_viva, c)
        saveData("quadratura_contante_cassa_assegno", entry_quadratura_contante_cassa_assegno, quadratura_contante_cassa_assegno, c)
        saveData("totale_entrate_cassa_contante", entry_totale_entrate_cassa_contante, totale_entrate_cassa_contante, c)
        saveDataTextBox("commenti", entry_commenti, c)

        saveDataList(frame_das_contante, "das_contanti", updateDasContanti, c)
        saveDataList(frame_das_cartepos, "das_cartepos", updateDasCartePOS, c)
        saveDataList(frame_das_bonifico, "das_bonifico", updateDasBonifici, c)
        saveDataList(frame_incasso_per_conto, "incasso_per_conto", updateIncassoPerConto, c)
        saveDataList(frame_sospesi, "sospesi", updateSospesi, c)
        saveDataList(frame_recuperosospesi_contante, "recupero_contanti", updateRecuperoContanti, c)
        saveDataList(frame_recuperosospesi_cartapos, "recupero_cartepos", updateRecuperoCartePOS, c)
        saveDataList(frame_recuperosospesi_bonifici, "recupero_bonifici", updateRecuperoBonifici, c)
        saveDataList(frame_uscite_varie, "uscite_varie", updateUsciteVarie, c)
        saveDataList(frame_versamenti, "uscite_versamenti", updateVersamenti, c)
        saveDataList(frame_marchirolo, "marchirolo", updateMarchirolo, c)
        

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
        '''#Cancella valori attualmente presenti nelle entry (prevenzione se non esiste il giorno)
        def resetEntry(entry_name):
            entry_name.configure(state='normal')
            entry_name.delete(0,'end')
            entry_name.insert('end', "{:.2f}".format(0))
            entry_name.configure(state='disabled')
        def resetEntryTextBox(entry_name):
            entry_name.configure(state='normal')
            entry_name.delete('0.0','end')
            entry_name.configure(state='disabled')
        resetEntry(entry_premio_lordo)
        resetEntry(entry_movimenti_bancari)
        resetEntry(entry_incasso_polizzebonifici)
        resetEntry(entry_totale_carte_pos)
        resetEntry(entry_totale_das_contante)
        resetEntry(entry_totale_das_bonifico)
        resetEntry(entry_totale_das_cartepos)
        resetEntry(entry_totale_das)
        resetEntry(entry_totale_incassi_per_conto)
        resetEntry(entry_sospesi)
        resetEntry(entry_tot_parziale_1)
        resetEntry(entry_cassaprecedente)
        resetEntry(entry_tot_contante_recuperato)
        resetEntry(entry_tot_cartapos_recuperato)
        resetEntry(entry_tot_bonifici_recuperato)
        resetEntry(entry_totale_entrate_cassa_contante)
        resetEntry(entry_abbuoni)
        resetEntry(entry_tot_uscite_varie)
        resetEntry(entry_tot_versamenti)
        resetEntry(entry_totale_generale_uscite)
        resetEntry(entry_fondodariportare)
        resetEntry(entry_tot_marchirolo)
        resetEntry(entry_saldocassa)
        resetEntry(entry_saldo_sospesi)
        resetEntry(entry_viva)
        resetEntry(entry_quadratura_contante_cassa_assegno)
        resetEntry(entry_totale_entrate_cassa_contante)
        resetEntryTextBox(entry_commenti)'''
        #Elimina frame delle liste (nota: i valori singoli, se sono =0, sono comunque ripristinati quando li sovrascrivo, mentre le liste -per la struttura della table- chiaramente no)
        def resetEntryInsideFrame(frame_name):
            for child in frame_name.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    child.destroy()   
        resetEntryInsideFrame(frame_das_contante)
        resetEntryInsideFrame(frame_das_cartepos)
        resetEntryInsideFrame(frame_das_bonifico)
        resetEntryInsideFrame(frame_incasso_per_conto)            
        resetEntryInsideFrame(frame_sospesi)
        resetEntryInsideFrame(frame_recuperosospesi_contante)
        resetEntryInsideFrame(frame_recuperosospesi_bonifici)
        resetEntryInsideFrame(frame_recuperosospesi_cartapos)
        resetEntryInsideFrame(frame_uscite_varie)
        resetEntryInsideFrame(frame_versamenti)
        resetEntryInsideFrame(frame_marchirolo)

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
        #Se la data non è presente
        if (len(data)==0):
            showConfirmMessage(visualizzaprova,"Attenzione", "Il giorno selezionato non è presente", "cancel", False)
            label_date_picked.configure(text="*** Seleziona una data per visualizzare i dati ***")
            edit_button.pack_forget()
            bottone_conferma.pack_forget()
            label_conferma.pack_forget()
        else:
            label_date_picked.configure(text="🗓️ Prova giornaliera del " + calendar.get_date())
            getDataFromDatabase()
            edit_button.pack(side="right", pady=(0,5), padx=(0,20))
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
    tabview.add("Altri incassi")
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
                        foreground = "#333333",
                        selectbackground = "#147da3", 
                        selectforeground = "black",
                        normalforeground = "#333333",
                        weekendforeground = "#333333",
                        weekendbackground = "white")
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
            calendar.tag_config("Completata", background='#809d5f', foreground='black')

        conn.commit()
        conn.close()
        
    coloraGiorniCompletati()
    #----TAB INCASSI----
    #Create frame inside the tab
    frame_incassi = ctk.CTkFrame(master=tabview.tab("Incassi"))
    frame_incassi.pack(pady=(20,0))
    #Premio lordo
    label_premio_lordo = ctk.CTkLabel(master=frame_incassi, text="Premio lordo:")
    label_premio_lordo.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_premio_lordo = ctk.CTkEntry(frame_incassi, textvariable=premio_lordo, width=100)
    entry_premio_lordo.grid(row=0, column=1, pady=10, padx=20, sticky="nw")
    #Movimenti bancari
    label_movimenti_bancari = ctk.CTkLabel(master=frame_incassi, text="Movimenti bancari:")
    label_movimenti_bancari.grid(row=3, column=0, pady=10, padx=20, sticky="ne")
    entry_movimenti_bancari = ctk.CTkEntry(frame_incassi, textvariable=movimenti_bancari, width=100)
    entry_movimenti_bancari.grid(row=3, column=1, pady=10, padx=20, sticky="nw")
    #Incasso polizze bonifici
    label_incasso_polizzebonifici = ctk.CTkLabel(master=frame_incassi, text="Incasso polizze bonifici:", font=("Helvetica",14,"bold"))
    label_incasso_polizzebonifici.grid(row=4, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_polizzebonifici = ctk.CTkEntry(frame_incassi, textvariable=incasso_polizze_bonifici, state="disabled", font=("Helvetica",15,"bold"), width=100)
    entry_incasso_polizzebonifici.grid(row=4, column=1, pady=10, padx=20, sticky="nw")
    #Totale carte/POS
    label_totale_carte_pos = ctk.CTkLabel(master=frame_incassi, text="Totale carte/POS:")
    label_totale_carte_pos.grid(row=5, column=0, pady=10, padx=20, sticky="ne")
    entry_totale_carte_pos = ctk.CTkEntry(frame_incassi, textvariable=totale_carte_pos, width=100)
    entry_totale_carte_pos.grid(row=5, column=1, pady=10, padx=20, sticky="nw")
    #Incasso polizze carte/POS
    label_incasso_polizzecartepos = ctk.CTkLabel(master=frame_incassi, text="Incasso polizze carte/POS:", font=("Helvetica",14,"bold"))
    label_incasso_polizzecartepos.grid(row=6, column=0, pady=10, padx=20, sticky="ne")
    entry_incasso_polizzecartepos = ctk.CTkEntry(frame_incassi, textvariable=incasso_polizze_carte_pos, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_incasso_polizzecartepos.grid(row=6, column=1, pady=10, padx=20, sticky="nw")

    #------TAB ALTRI INCASSI------
    #--Lista DAS--
    frame_das = ctk.CTkScrollableFrame(master=tabview.tab("Altri incassi"), width=500, height=250, border_color="black", border_width=1)
    frame_das.pack()

    #--DAS contanti--
    frame_das_contante = ctk.CTkFrame(master=frame_das, height=50)
    frame_das_contante.pack()
    def addDasContante():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            frame.destroy()
            print("DAS contante eliminato")
        print ("DAS contante aggiunto")
        frame = ctk.CTkFrame(frame_das_contante)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_das_contante, "{:.2f}".format(0))
        var1.trace("w", updateDasContanti)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)

    add_das_contante = ctk.CTkButton(frame_das_contante, text='+ DAS contante', command=addDasContante)
    #Totale contante das
    frame_totale_das_contante = ctk.CTkFrame(master=frame_das)
    frame_totale_das_contante.pack()
    label_totale_das_contante = ctk.CTkLabel(master=frame_totale_das_contante, text="Totale DAS contanti:", font=("Helvetica",14,"bold"))
    label_totale_das_contante.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_totale_das_contante = ctk.CTkEntry(frame_totale_das_contante, textvariable=totale_das_contante, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_das_contante.grid(row=0, column=1, pady=20, padx=10, sticky="nw")
    
    #--DAS carte/pos--
    frame_das_cartepos = ctk.CTkFrame(master=frame_das, height=50)
    frame_das_cartepos.pack()
    def addDasCartePOS():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            frame.destroy()
            print("DAS carte/pos eliminato")
        print ("DAS carte/pos aggiunto")
        frame = ctk.CTkFrame(frame_das_cartepos)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_das_cartepos, "{:.2f}".format(0))
        var1.trace("w", updateDasCartePOS)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)

    add_das_cartepos = ctk.CTkButton(frame_das_cartepos, text='+ DAS carta/POS', command=addDasCartePOS)
    #Totale carte/pos das
    frame_totale_das_cartepos = ctk.CTkFrame(master=frame_das)
    frame_totale_das_cartepos.pack()
    label_totale_das_cartepos = ctk.CTkLabel(master=frame_totale_das_cartepos, text="Totale DAS carte/POS:", font=("Helvetica",14,"bold"))
    label_totale_das_cartepos.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_totale_das_cartepos = ctk.CTkEntry(frame_totale_das_cartepos, textvariable=totale_das_cartepos, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_das_cartepos.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #--DAS bonifico--
    frame_das_bonifico = ctk.CTkFrame(master=frame_das, height=50)
    frame_das_bonifico.pack()
    def addDasBonifico():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            frame.destroy()
            print("DAS carte/pos eliminato")
        print ("DAS carte/pos aggiunto")
        frame = ctk.CTkFrame(frame_das_bonifico)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_das_bonifico, "{:.2f}".format(0))
        var1.trace("w", updateDasBonifici)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)

    add_das_bonifico = ctk.CTkButton(frame_das_bonifico, text='+ DAS bonifico', command=addDasBonifico)
    #Totale carte/pos das
    frame_totale_das_bonifico = ctk.CTkFrame(master=frame_das)
    frame_totale_das_bonifico.pack()
    label_totale_das_bonifico = ctk.CTkLabel(master=frame_totale_das_bonifico, text="Totale DAS bonifici:", font=("Helvetica",14,"bold"))
    label_totale_das_bonifico.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_totale_das_bonifico = ctk.CTkEntry(frame_totale_das_bonifico, textvariable=totale_das_bonifico, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_das_bonifico.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #Totale DAS
    frame_totale_das=ctk.CTkFrame(master=tabview.tab("Altri incassi"))
    frame_totale_das.pack(pady=(0,15))
    label_totale_das = ctk.CTkLabel(master=frame_totale_das, text="Totale DAS:", font=("Helvetica",14,"bold"))
    label_totale_das.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_totale_das = ctk.CTkEntry(frame_totale_das, textvariable=totale_das, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_das.grid(row=0, column=1, pady=10, padx=20, sticky="nw")


    #--Lista incasso per conto--
    frame_incasso_per_conto = ctk.CTkScrollableFrame(master=tabview.tab("Altri incassi"), width=500, height=150, border_color="black", border_width=1)
    frame_incasso_per_conto.pack()

    def addIncassoPerConto():
        #Elimina sospeso carta/POS
        def destroy():
            var1.set(0)
            frame.destroy()
            print("Incasso per conto eliminato")
        print ("Incasso per conto aggiunto")
        frame = ctk.CTkFrame(frame_incasso_per_conto)
        frame.pack()
        ctk.CTkLabel(frame, text='Valore in €:').grid(row=0, column=0)
        var1 = ctk.DoubleVar(frame_incasso_per_conto, "{:.2f}".format(0))
        var1.trace("w", updateIncassoPerConto)
        ent1 = ctk.CTkEntry(frame, textvariable=var1, width=100)
        ent1.grid(row=1, column=0)
        ctk.CTkLabel(frame, text='Causale:').grid(row=0, column=1)
        ent2 = ctk.CTkEntry(frame, width=250)
        ent2.grid(row=1, column=1)
        delete_button = ctk.CTkButton(frame, image=bin_icon, text="", width=30, command=destroy)
        delete_button.grid(row=1, column=2)

    add_incasso_per_conto = ctk.CTkButton(frame_incasso_per_conto, text='+ Incasso per conto', command=addIncassoPerConto)

    #Totale incassi per conto
    frame_totale_incassi_per_conto=ctk.CTkFrame(master=tabview.tab("Altri incassi"))
    frame_totale_incassi_per_conto.pack(pady=(0,15))
    label_totale_incassi_per_conto = ctk.CTkLabel(master=frame_totale_incassi_per_conto, text="Totale incassi per conto:", font=("Helvetica",14,"bold"))
    label_totale_incassi_per_conto.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_totale_incassi_per_conto = ctk.CTkEntry(frame_totale_incassi_per_conto, textvariable=totale_incassi_per_conto, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_incassi_per_conto.grid(row=0, column=1, pady=10, padx=20, sticky="nw")

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
            frame.destroy()
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

    addboxButton = ctk.CTkButton(frame_sospesi, text='+ Sospeso', command=addSospeso)

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
            frame.destroy()
            print("Recupero sospeso contante eliminato")
        print ("Recupero sospeso contante aggiunto")
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

    add_contante_recuperato = ctk.CTkButton(frame_recuperosospesi_contante, text='+ Recupero contante', command=addSospContante)

    #Totale contante recuperato
    frame_contanterecuperato = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_contanterecuperato.pack()
    label_tot_contante_recuperato = ctk.CTkLabel(master=frame_contanterecuperato, text="Totale recupero sospesi contante:", font=("Helvetica",14,"bold"))
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
            frame.destroy()
            print("Recupero sospeso carta/POS eliminato")
        print ("Recupero sospeso carta/POS aggiunto")
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

    add_cartapos_recuperato = ctk.CTkButton(frame_recuperosospesi_cartapos, text='+ Recupero carta/POS', command=addSospCartePOS)
    #Totale carte/POS recuperato
    frame_carteposrecuperato = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_carteposrecuperato.pack()
    label_tot_cartapos_recuperato = ctk.CTkLabel(master=frame_carteposrecuperato, text="Totale recupero sospesi carte/POS:", font=("Helvetica",14,"bold"))
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
            frame.destroy()
            print("Recupero sospeso bonifico eliminato")
        print ("Recupero sospeso bonifico aggiunto")
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

    add_bonifici_recuperato = ctk.CTkButton(frame_recuperosospesi_bonifici, text='+ Recupero bonifico', command=addSospBonifici)
    #Totale bonifici recuperato
    frame_bonificirecuperato = ctk.CTkFrame(master=frame_recuperosospesi)
    frame_bonificirecuperato.pack()
    label_tot_bonifici_recuperato = ctk.CTkLabel(master=frame_bonificirecuperato, text="Totale recupero sospesi bonifici:", font=("Helvetica",14,"bold"))
    label_tot_bonifici_recuperato.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_bonifici_recuperato = ctk.CTkEntry(frame_bonificirecuperato, textvariable=totale_recupero_sospesi_bonifici, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_bonifici_recuperato.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #Frame saldo sospesi
    frame_saldo_sospesi = ctk.CTkFrame(master=tabview.tab("Recupero sospesi"))
    frame_saldo_sospesi.pack(pady=(20,0))
    label_saldo_sospesi = ctk.CTkLabel(master=frame_saldo_sospesi, text="Saldo sospesi:", font=("Helvetica",14,"bold"))
    label_saldo_sospesi.grid(row=0, column=0, pady=10, padx=20, sticky="ne")
    entry_saldo_sospesi = ctk.CTkEntry(frame_saldo_sospesi, textvariable=saldo_sospesi, font=("Helvetica",15,"bold"), width=100)
    entry_saldo_sospesi.grid(row=0, column=1, pady=10, padx=20, sticky="nw")


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

    frame_uscitevarieandversamenti = ctk.CTkScrollableFrame(master = tabview.tab("Uscite"), width=500, height=400, border_color="black", border_width=1)
    frame_uscitevarieandversamenti.pack()
    #--Aggiungi VERSAMENTI--
    frame_versamenti = ctk.CTkFrame(master=frame_uscitevarieandversamenti, height=50)
    frame_versamenti.pack()
    def addVersamento():
        #Elimina sospeso contante
        def destroy():
            var1.set(0)
            frame.destroy()
            print("Versamento eliminato")
        print ("Versamento aggiunto")
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

    add_versamento = ctk.CTkButton(frame_versamenti, text='+ Versamento', command=addVersamento)
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
            frame.destroy()
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

    add_uscite_varie = ctk.CTkButton(frame_uscite_varie, text='+ Uscita extra', command=addUsciteVarie)
    #Totale uscite varie
    frame_totaleuscitevarie = ctk.CTkFrame(master=frame_uscitevarieandversamenti)
    frame_totaleuscitevarie.pack()
    label_tot_uscite_varie = ctk.CTkLabel(master=frame_totaleuscitevarie, text="Totale uscite extra:", font=("Helvetica",14,"bold"))
    label_tot_uscite_varie.grid(row=0, column=0, pady=20, padx=10, sticky="ne")
    entry_tot_uscite_varie = ctk.CTkEntry(frame_totaleuscitevarie, textvariable=totale_uscite_varie, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_uscite_varie.grid(row=0, column=1, pady=20, padx=10, sticky="nw")

    #--Frame in fondo a uscite--
    frame_totale_generale_uscite_e_quadratura = ctk.CTkFrame(master=tabview.tab("Uscite"))
    frame_totale_generale_uscite_e_quadratura.pack(pady=(20,0))
    #--Totale generale uscite--
    label_totale_generale_uscite = ctk.CTkLabel(master=frame_totale_generale_uscite_e_quadratura, text="Totale generale uscite:", font=("Helvetica",14,"bold"))
    label_totale_generale_uscite.grid(row=1, column=0, pady=10, padx=10, sticky="ne")
    entry_totale_generale_uscite = ctk.CTkEntry(frame_totale_generale_uscite_e_quadratura, textvariable=totale_generale_uscite, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_generale_uscite.grid(row=1, column=1, pady=10, padx=10, sticky="nw")
    #--Quadratura contante cassa + assegno--
    label_quadratura_contante_cassa_assegno = ctk.CTkLabel(master=frame_totale_generale_uscite_e_quadratura, text="Quadratura contante cassa + assegno:", font=("Helvetica",14,"bold"))
    label_quadratura_contante_cassa_assegno.grid(row=2, column=0, pady=10, padx=10, sticky="ne")
    entry_quadratura_contante_cassa_assegno = ctk.CTkEntry(frame_totale_generale_uscite_e_quadratura, textvariable=quadratura_contante_cassa_assegno, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_quadratura_contante_cassa_assegno.grid(row=2, column=1, pady=10, padx=10, sticky="nw")

    #----TAB MARCHIROLO----
    frame_marchirolo = ctk.CTkScrollableFrame(master=tabview.tab("Marchirolo"), width=500, height=300, border_color="black", border_width=1)
    frame_marchirolo.pack()
    def addUscitaMarchirolo():
        #Elimina sospeso carta/POS
        def destroy():
            var1.set(0)
            frame.destroy()
            print("Marchirolo eliminato")
        print ("Marchirolo aggiunto")
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

    add_uscitamarchirolo = ctk.CTkButton(frame_marchirolo, text='+ Cassa Marchirolo', command=addUscitaMarchirolo)

    label_tot_marchirolo = ctk.CTkLabel(master=tabview.tab("Marchirolo"), text="Totale Marchirolo:", font=("Helvetica",14,"bold"))
    label_tot_marchirolo.pack(side="left", anchor="ne", pady=(25,0), padx=10, expand="True")
    entry_tot_marchirolo = ctk.CTkEntry(tabview.tab("Marchirolo"), textvariable=totale_marchirolo, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_marchirolo.pack(side="right", anchor="nw", pady=(25,0), expand="True")

    #----TAB RESCONTO----
    #Create frame inside the tab
    frame_resoconto = ctk.CTkFrame(master=tabview.tab("Resoconto"))
    frame_resoconto.pack(pady=(20,0))
    #Totale parziale 1
    label_tot_parziale_1 = ctk.CTkLabel(master=frame_resoconto, text="Tot. parz. 1 | Cassa contanti:", font=("Helvetica",14,"bold"))
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
    #Totale sospesi contante recuperato
    label_tot_contante_recuperato_copia = ctk.CTkLabel(master=frame_resoconto, text="Totale recupero sospesi contante:", font=("Helvetica",14,"bold"))
    label_tot_contante_recuperato_copia.grid(row=2, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_contante_recuperato_copia = ctk.CTkEntry(frame_resoconto, textvariable=totale_recupero_sospesi_contanti, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_contante_recuperato_copia.grid(row=2, column=1, pady=10, padx=20, sticky="nw")
    explain_tot_contante_recuperato_copia = ctk.CTkLabel(master=frame_resoconto, text="Tot. parz. 2 + tot. rec. sosp. contante", text_color="#969595", font=("Helvetica",13))
    explain_tot_contante_recuperato_copia.grid(row=2, column=2, pady=10, padx=20, sticky="nw")
    #Totale entrate cassa contante
    label_totale_entrate_cassa_contante = ctk.CTkLabel(master=frame_resoconto, text="Totale entrate cassa contante:", font=("Helvetica",14,"bold"))
    label_totale_entrate_cassa_contante.grid(row=3, column=0, pady=10, padx=20, sticky="ne")
    entry_totale_entrate_cassa_contante = ctk.CTkEntry(frame_resoconto, textvariable=totale_entrate_cassa_contante, font=("Helvetica",15,"bold"), width=100)
    entry_totale_entrate_cassa_contante.grid(row=3, column=1, pady=10, padx=20, sticky="nw")
    #Totale generale uscite
    label_totale_generale_uscite_copia = ctk.CTkLabel(master=frame_resoconto, text="Totale generale uscite:", font=("Helvetica",14,"bold"))
    label_totale_generale_uscite_copia.grid(row=4, column=0, pady=10, padx=20, sticky="ne")
    entry_totale_generale_uscite_copia = ctk.CTkEntry(frame_resoconto, textvariable=totale_generale_uscite, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_totale_generale_uscite_copia.grid(row=4, column=1, pady=10, padx=20, sticky="nw")
    explain_totale_generale_uscite_copia = ctk.CTkLabel(master=frame_resoconto, text="Abbuoni + p.ti Viva + uscite varie + versamenti", text_color="#969595", font=("Helvetica",13))
    explain_totale_generale_uscite_copia.grid(row=4, column=2, pady=10, padx=20, sticky="nw")
    #Fondo cassa da riportare
    label_fondodariportare = ctk.CTkLabel(master=frame_resoconto, text="Fondo cassa da riportate:", font=("Helvetica",14,"bold"))
    label_fondodariportare.grid(row=5, column=0, pady=10, padx=20, sticky="ne")
    entry_fondodariportare = ctk.CTkEntry(frame_resoconto, textvariable=fondo_cassa_da_riportare, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_fondodariportare.grid(row=5, column=1, pady=10, padx=20, sticky="nw")
    #Totale Marchirolo COPIA
    label_tot_marchirolo_copy = ctk.CTkLabel(master=frame_resoconto, text="Totale Marchirolo:", font=("Helvetica",14,"bold"))
    label_tot_marchirolo_copy.grid(row=6, column=0, pady=10, padx=20, sticky="ne")
    entry_tot_marchirolo_copy = ctk.CTkEntry(frame_resoconto, textvariable=totale_marchirolo, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_tot_marchirolo_copy.grid(row=6, column=1, pady=10, padx=20, sticky="nw")
    explain_tot_marchirolo_copy = ctk.CTkLabel(master=frame_resoconto, text="Totale uscite Marchirolo", text_color="#969595", font=("Helvetica",13))
    explain_tot_marchirolo_copy.grid(row=6, column=2, pady=10, padx=20, sticky="nw")
    #Saldo cassa
    label_saldocassa = ctk.CTkLabel(master=frame_resoconto, text="Saldo cassa:", font=("Helvetica",14,"bold"))
    label_saldocassa.grid(row=7, column=0, pady=10, padx=20, sticky="ne")
    entry_saldocassa = ctk.CTkEntry(frame_resoconto, textvariable=saldo_cassa, state='disabled', font=("Helvetica",15,"bold"), width=100)
    entry_saldocassa.grid(row=7, column=1, pady=10, padx=20, sticky="nw")
    explain_saldocassa = ctk.CTkLabel(master=frame_resoconto, text="F. cass da riportare + tot. Marchirolo", text_color="#969595", font=("Helvetica",13))
    explain_saldocassa.grid(row=7, column=2, pady=10, padx=20, sticky="nw")
    #Commenti
    label_commenti = ctk.CTkLabel(master=tabview.tab("Resoconto"), text="Commenti:")
    label_commenti.pack()
    entry_commenti = ctk.CTkTextbox(tabview.tab("Resoconto"), height=100, width=300, border_width=2)
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
                #Salva i nomi delle causali nella lista causali_versamenti
                causali_versamenti=[]
                isvalore = True
                for child in frame_versamenti.winfo_children():                #Scorri ogni elemento nel frame-padre
                    if isinstance(child, ctk.CTkFrame):             #Se è un sotto-frame
                        for child2 in child.winfo_children():       #scorri ogni elemento nel sotto-frame
                            if isinstance(child2, ctk.CTkEntry):    #se è una entry
                                if isvalore==True:                  #ed è il valore, la prossima entry sarà la causale
                                    isvalore=False
                                else:                               #altrimenti è la causale: se è vuota ritorna "True", altrimenti la prossima entry sarà il valore
                                    causali_versamenti.append(child2.get())
                                    isvalore = True
                #SE DAI UN NUOVO NOME AL FILE
                if(new_filename != ""):
                    #Cerca un nome del file
                    for item in causali_versamenti:
                        if new_filename == item:
                            causale_trovata = True                                
                    if causale_trovata == True:
                        shutil.move(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)    
                        showConfirmMessage(visualizzaprova,"Successo","Documento correttamente caricato", "check", False)
                        frame.destroy()
                    else:
                        showConfirmMessage(visualizzaprova,"Attenzione","Il nome non corrisponde a nessuna causale", "warning", False)
                #ALTRIMENTI SPOSTALO CON LO STESSO NOME
                else:
                    for item in causali_versamenti:
                        if tail[:-4] == item:
                            causale_trovata = True  
                    if causale_trovata == True:
                        shutil.move(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+tail)    
                        showConfirmMessage(visualizzaprova,"Successo","Documento correttamente caricato", "check", False)
                        frame.destroy()
                    else:
                        showConfirmMessage(visualizzaprova,"Attenzione","Il nome non corrisponde a nessuna causale", "warning", False)
            else:
                #Se dai un nuovo nome al file
                if(new_filename != ""):
                    #os.rename(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)
                    #os.replace(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)
                    shutil.move(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+new_filename+file_extension)    
                    showConfirmMessage(visualizzaprova,"Successo","Documento correttamente caricato", "check", False)
                    frame.destroy()
                #Altrimenti spostalo con lo stesso nome
                else:
                    #os.rename(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+filename+file_extension)
                    #os.replace(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+filename+file_extension)
                    shutil.move(original_path, percorso_documenti+dataperfile[2]+"/"+dataperfile[1]+"/"+dataperfile[0]+"/"+entry_outputcategory.get()+"/"+tail)    
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
        entry_outputcategory = ctk.CTkComboBox(frame, values=("Bonifici", "Movimenti POS", "Versamenti", "Assegni", "Quadratura punto vendita", "Recupero sospesi", "Chiusure POS", "Quitanze", "Foglio cassa", "Altro"))
        entry_outputcategory.grid(row=0, column=3)
        entry_outputfilename = ctk.CTkEntry(frame, width=250, placeholder_text="Rinomina il file...")
        entry_outputfilename.grid(row=0, column=4)
        loadfile_button = ctk.CTkButton(frame, image=upload_icon, text="", width=30, command=loadFile)
        loadfile_button.grid(row=0, column=5)

    carica_documento = ctk.CTkButton(tabview.tab("Documenti"), text='+ Documento', command=uploadFile)
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
        #Salva i nomi delle causali nella lista causali_versamenti
        causali_versamenti=[]
        isvalore = True
        for child in frame_versamenti.winfo_children():                #Scorri ogni elemento nel frame-padre
            if isinstance(child, ctk.CTkFrame):             #Se è un sotto-frame
                for child2 in child.winfo_children():       #scorri ogni elemento nel sotto-frame
                    if isinstance(child2, ctk.CTkEntry):    #se è una entry
                        if isvalore==True:                  #ed è il valore, la prossima entry sarà la causale
                            isvalore=False
                        else:                               #altrimenti è la causale: se è vuota ritorna "True", altrimenti la prossima entry sarà il valore
                            causali_versamenti.append(child2.get())
                            isvalore = True
        #Per ogni elemento in new_lista_versamenti_causali, se è presente (il nome è =) in file_versamenti_list aumenta causali_trovate
        for j in range(len(causali_versamenti)):
            if causali_versamenti[j] in file_versamenti_list:
                causali_trovate = causali_trovate+1

        if causali_trovate == len(causali_versamenti):
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
        #Aggiungi bottoni per aggiungere riga alle liste
        add_das_contante.pack(padx=20, pady=(20,0))
        add_das_bonifico.pack(padx=20, pady=(20,0))
        add_das_cartepos.pack(padx=20, pady=(20,0))
        add_incasso_per_conto.pack(padx=20, pady=(20,0))
        addboxButton.pack(padx=20, pady=(20,0))
        add_contante_recuperato.pack(padx=20, pady=(20,0))
        add_cartapos_recuperato.pack(pady=(25,0))
        add_bonifici_recuperato.pack(pady=(25,0))
        add_uscite_varie.pack(padx=20, pady=(20,0))
        add_versamento.pack(padx=20, pady=(20,0))
        add_uscitamarchirolo.pack(padx=20, pady=(20,0))
    def setEnableDisable(new_state):
        entry_premio_lordo.configure(state=new_state)
        entry_movimenti_bancari.configure(state=new_state)
        entry_totale_carte_pos.configure(state=new_state)
        entry_movimenti_bancari.configure(state=new_state)
        entry_abbuoni.configure(state=new_state)
        entry_viva.configure(state=new_state)
        entry_commenti.configure(state=new_state)
        #Configura Entry all'interno di un frame
        def configureEntryInsideFrame(frame_name):
            for child in frame_name.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    for child2 in child.winfo_children():
                        if isinstance(child2, (ctk.CTkEntry, ctk.CTkButton)):
                            child2.configure(state=new_state)
        configureEntryInsideFrame(frame_das_contante)
        configureEntryInsideFrame(frame_das_cartepos)
        configureEntryInsideFrame(frame_das_bonifico)
        configureEntryInsideFrame(frame_incasso_per_conto)
        configureEntryInsideFrame(frame_sospesi)
        configureEntryInsideFrame(frame_recuperosospesi_contante)
        configureEntryInsideFrame(frame_recuperosospesi_bonifici)
        configureEntryInsideFrame(frame_recuperosospesi_cartapos)
        configureEntryInsideFrame(frame_uscite_varie)
        configureEntryInsideFrame(frame_versamenti)
        configureEntryInsideFrame(frame_marchirolo)

    def removeButtons():
        add_das_contante.pack_forget()
        add_das_bonifico.pack_forget()
        add_das_cartepos.pack_forget()
        add_incasso_per_conto.pack_forget()
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
        #Show SAVE BUTTON
        save_btn.pack(side="right", pady=(0,5), padx=(0,20))
        #Show CANCELLA BUTTON
        cancel_btn.pack(side="right", pady=(0,5), padx=(0,20))
        visualizzaprova.protocol('WM_DELETE_WINDOW', close_window)
    def saveButton():
        def causaleVuota(nome_frame):
            isvalore = False
            #Controlla che le causali dei versamenti non siano vuote
            for child in nome_frame.winfo_children():     #Per ogni child nel frame_versamenti
                if isinstance(child, ctk.CTkFrame):             #Se è un frame
                    for child2 in child.winfo_children():       #per figlio nel frame (child)
                        if isinstance(child2, ctk.CTkEntry):    #se è una entry
                            if isvalore==True:                     #se è la causale
                                if child2.get() == "":          #se la causale non è vuota
                                    return(True)
                            else:
                                isvalore = True
            return(False)
        
        if causaleVuota(frame_versamenti):
            showConfirmMessage(visualizzaprova, "Attenzione", "La causale dei versamenti non può essere vuota", "warning", False) 
        else:
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
                    +str(safeLoad(premio_lordo))+", "
                    +str(safeLoad(movimenti_bancari))+", "
                    +str(safeLoad(incasso_polizze_bonifici))+", "
                    +str(safeLoad(totale_carte_pos))+", "
                    +str(safeLoad(incasso_polizze_carte_pos))+", "
                    +str(safeLoad(totale_das_contante))+", "
                    +str(safeLoad(totale_das_bonifico))+", "
                    +str(safeLoad(totale_das_cartepos))+", "
                    +str(safeLoad(totale_das))+", "
                    +str(safeLoad(totale_incassi_per_conto))+", "
                    +str(safeLoad(totale_sospesi))+", "
                    +str(safeLoad(totale_parziale_1))+", "
                    +str(safeLoad(fondo_cassa_precedente))+", "
                    +str(safeLoad(totale_recupero_sospesi_contanti))+", "
                    +str(safeLoad(totale_recupero_sospesi_carte_pos))+", "
                    +str(safeLoad(totale_recupero_sospesi_bonifici))+", "
                    +str(safeLoad(totale_abbuoni))+", "
                    +str(safeLoad(totale_uscite_varie))+", "
                    +str(safeLoad(totale_uscite_versamenti))+", "
                    +str(safeLoad(totale_generale_uscite))+", "
                    +str(safeLoad(fondo_cassa_da_riportare))+", "
                    +str(safeLoad(totale_marchirolo))+", "
                    +str(safeLoad(saldo_cassa))+", "
                    +str(safeLoad(saldo_sospesi))+", "
                    +str(safeLoad(punti_viva))+", "
                    +str(safeLoad(quadratura_contante_cassa_assegno))+", "
                    +str(safeLoad(totale_entrate_cassa_contante))+", "
                    +"'"+str(entry_commenti.get('0.0','end'))+"',"+
                    " 'false')"
            )
            conn.commit()
            #Scorri lista e aggiungi: is valore si alterna tra True e False
            def listToDatabase(frame, categoria):
                isvalore = True
                for child in frame.winfo_children():                #Scorri ogni elemento nel frame-padre
                    if isinstance(child, ctk.CTkFrame):             #Se è un sotto-frame
                        for child2 in child.winfo_children():       #scorri ogni elemento nel sotto-frame
                            if isinstance(child2, ctk.CTkEntry):    #se è una entry
                                if isvalore==True:                  #ed è il valore, salva il valore e la prossima entry sarà la causale
                                    valore=child2.get()
                                    isvalore=False
                                else:                               #altrimenti è la causale, quindi salva la causale e la prossima entry sarà il valore
                                    causale=child2.get()
                                    isvalore = True
                        c.execute("INSERT INTO liste VALUES ('"+data_converted_text+"', "
                                +"'"+categoria+"', "
                                +valore+", '"
                                +causale+
                                "')"
                        )
                conn.commit()
            
            listToDatabase(frame_sospesi, "sospesi")
            listToDatabase(frame_recuperosospesi_contante, "recupero_contanti")
            listToDatabase(frame_recuperosospesi_cartapos, "recupero_cartepos")
            listToDatabase(frame_recuperosospesi_bonifici, "recupero_bonifici")
            listToDatabase(frame_versamenti, "uscite_versamenti")
            listToDatabase(frame_uscite_varie, "uscite_varie")
            listToDatabase(frame_marchirolo, "marchirolo")
            listToDatabase(frame_das_contante, "das_contanti")
            listToDatabase(frame_das_cartepos, "das_cartepos")
            listToDatabase(frame_das_bonifico, "das_bonifico")
            listToDatabase(frame_incasso_per_conto, "incasso_per_conto")

            conn.close()
            showConfirmMessage(visualizzaprova,"Caricamento completato", "Dati correttamente aggiunti al database", "check", False)

            removeButtons()
            #Add disable option
            setEnableDisable("disabled")
            #Hide SAVE and CANCELLA BUTTON
            save_btn.pack_forget()
            cancel_btn.pack_forget()
            edit_button.pack(side="right", pady=(0,5), padx=(0,20))
            visualizzaprova.protocol('WM_DELETE_WINDOW', destroy_window)

    def cancelButton():
        #Elimina entry all'interno di un frame lista
        def deleteEntryInsideFrame(frame_name):
            for child in frame_name.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    child.pack_forget()
                        
        deleteEntryInsideFrame(frame_das_bonifico)
        deleteEntryInsideFrame(frame_das_cartepos)
        deleteEntryInsideFrame(frame_das_contante)
        deleteEntryInsideFrame(frame_incasso_per_conto)
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
        edit_button.pack(side="right", pady=(0,5), padx=(0,20))
        visualizzaprova.protocol('WM_DELETE_WINDOW', destroy_window)

    #----SALVA, MODIFICA E CANCELLA BUTTONS----
    #Create SAVE and CANCEL buttons
    cancel_btn = ctk.CTkButton(visualizzaprova, text='Annulla', fg_color="#A52A2A", hover_color="#EC3737", command=cancelButton)
    save_btn = ctk.CTkButton(visualizzaprova, text='Salva', fg_color="#809d5f", hover_color="#B7C019", command=saveButton)
    #Show MODIFICA BUTTON
    edit_button = ctk.CTkButton(master=visualizzaprova, image=edit_icon, text="Modifica", command=editProva)

    #Definizione funzioni per notificare conferma chiusura app
    def close_window():
        exitFromApp(visualizzaprova)
    def destroy_window():
        visualizzaprova.destroy()
    
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
home.iconbitmap(percorso_applicazione+"app_icon.ico")

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

