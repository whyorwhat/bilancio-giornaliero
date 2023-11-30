# Bilancio-giornaliero
All'apertura vengono mostrate due categorie di finestra: <i>Crea</i> oppure <i>Visualizza e modifica</i>.

## Crea
La data della prova da creare non deve essere già presente nel [database](Database/README.md) (in caso lo fosse viene visualizzato un avviso).

Ogni tab appartiene ad una categoria di movimenti di cassa.

La lista <i>Marchirolo</i>, quando viene inserita una data nella entry in alto, viene aggiornata con i valori del giorno precedente, perché se non sono stati cancellati il giorno precedente, significa che non sono ancora stati contabilizzati nel complesso. Possono comunque essere modificati.

Lo stesso succede per <i>Fondo cassa precedente</i> al quale viene mostrato a fianco il giorno al quale fa riferimento.

<b>🚨DA FARE: </b>La lista delle causali dei versamenti non può essere vuota per non creare problemi con il check dei file relativi

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
* Creare una piccola cache che carica i dati dell'ultima settimana per accederci più facilmente, essendo quelli più utilizzati
* La lista delle <u>causali</u> dei versamenti non può essere vuota per non creare problemi con il check dei file relativi
