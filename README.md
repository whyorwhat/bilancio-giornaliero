# Bilancio-giornaliero
Il file .zip può essere scaricato da [qui](https://www.mediafire.com/file/u9iygsn034gcjel/Bilancio_giornaliero.zip/file).

I percorsi alle cartelle di risorsa dell'app vanno definiti nel file esterno [posizioni.txt](posizioni.txt), <u>prima</u> di eseguire l'applicazione. Nota che va inserito "/" (macOS) oppure "\" (Windows) alla fine del percorso.

All'apertura vengono mostrate due categorie di finestra: <i>Crea</i> oppure <i>Visualizza e modifica</i>.

## Crea
La data della prova da creare non deve essere già presente nel [database](Database/README.md) (in caso lo fosse viene visualizzato un avviso).

Ogni tab appartiene ad una categoria di movimenti di cassa.

La lista <i>Marchirolo</i>, quando viene inserita una data nella entry in alto, viene aggiornata con i valori del giorno precedente, perché se non sono stati cancellati il giorno precedente, significa che non sono ancora stati contabilizzati nel complesso. Possono comunque essere modificati.

Lo stesso succede per <i>Fondo cassa precedente</i> al quale viene mostrato a fianco il giorno al quale fa riferimento.

La lista delle causali dei versamenti non può essere vuota per non creare problemi con il check dei file relativi (viene visualizzato avviso dopo aver cliccato il tasto <i>Invia</i>)

Il pulsante <i>Apri documenti</i> apre, se esiste, la cartella del giorno situata nella cartella principale [Documenti](Documenti/README.md), altrimenti la crea e la apre.

Il pulsante <i>Carica documento</i> crea un frame dove poter scegliere il file da spostare nella cartella documenti, cambiare manualmente il percorso del file, scegliere (o creare) una categoria di documento e rinominare il file.
Se non si rinomina il file, gli viene assegnato il nome originale.
Cliccando sul tasto di upload, il file viene spostato nella cartella del giorno.


## Visualizza e modifica
La finestra viene creata con tutte le entry disabilitate, ad eccezione del calendario da cui si può scegliere la data.

Il calendario mostra i giorni in verde come quelli completati, mentre quello in nero rappresenta il giorno selezionato (viene comunque mostrato anche in alto).

<i>Conferma prova</i> rende la prova non più modificabile.
La prova viene effettivamente confermata se le causali dei versamenti combaciano con i nomi dei file corrispondenti, in caso contrario restituisce errore (la lista dei versamenti vuota permette di confermare la prova).
Il vincolo del nome del file riduce di molto il rischio di errore.

Nel caricamento dei file di versamento, i nomi devono combaciare con i nomi delle causali inserite nella sezione <i>Versamenti</i>, in modo da facilitare il riconoscimento dei versamenti nel momento della conferma della prova. Viene mostrata una finestra di errore quando i nomi non vengono riconosciuti.

## Possibili miglioramenti 
* 🔜 Creare una piccola cache che carica i dati dell'ultima settimana per accederci più facilmente, essendo quelli più utilizzati
* 🔜 La lista delle <u>causali</u> dei versamenti non può essere vuota per non creare problemi con il check dei file relativi
* 🔜 Esportazione PDF
* 🔜 Icone caricamento
* ⚠️ BUG DA RISOLVERE: dopo aver aggiunto un versamento, salvato, modifica, cancellato il nuovo versamento, il saldo cassa visualizza ancora il valore con i 2 versamenti, anziché con 1 versamento come dovrebbe essere
* ⚠️ Manca l'icona dell'applicazione nella finestra di avviso

## Librerie esterne da installare
```sh
pip install customtkinter
```

```sh
pip install tkcalendar
```

```sh
pip install Pillow
```

## Creare app con pyinstaller
```sh
pyinstaller source_code.py --icon="app_icon.ico" --onedir --name "Bilancio giornaliero" --noconsole --hidden-import babel.numbers
```
<i>Nota:</i>
Creato il file, va spostato il contenuto della cartella <i>dist</i> nella cartella principale.

<i>Nota 2:</i>
Invece che inserire <i>--hidden-import babel.numbers</i> nel codice pyinstaller, è possibile modificare il file <i>.spec</i> aggiungendo
```sh
hiddenimports=["babel.numbers"]
```
nella sezione <i>a = Analysis</i>. Una volta fatto reinstallare il file <i>.spec</i> con pyinstaller.
