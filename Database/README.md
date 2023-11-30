# Database
## File
Il database è un file unico chiamato database.db (usare più anni creerebbe il problema di accedere alle date precedenti alla fine dell'anno, ma è fattibile).
test.py è un file temporaneo per collegarsi al database ed eseguire semplici query

## Tabelle
Per il nuovo database va eseguito
```sh
PRAGMA foreign_keys = ON;
```
al fine di abilitare il vincolo sulle chiavi esterne.

### prova
Contiene la tabella tutti i dati della prova giornaliera, con la data che è la primary key.
| COLUMN | TYPE |
| ------ | ---- |
| data | DATE |
| totale_incassi_vittoria | DOUBLE |
| incasso_per_conto | DOUBLE |
| incasso_das | DOUBLE |
| totale_bonifici | DOUBLE |
| incasso_polizze_bonifici | DOUBLE |
| totale_carte_pos | DOUBLE |
| incasso_polizze_carte_pos | DOUBLE |
| totale_sospesi | DOUBLE |
| totale_parziale_1 | DOUBLE |
| fondo_cassa_precedente | DOUBLE |
| incassi_contante | DOUBLE |
| totale_parziale_2 | DOUBLE |
| totale_recupero_sospesi_contanti | DOUBLE |
| totale_recupero_sospesi_carte_pos | DOUBLE |
| totale_recupero_sospesi_bonifici | DOUBLE |
| totale_recupero_sospesi | DOUBLE |
| totale_cassa_contante | DOUBLE |
| totale_abbuoni | DOUBLE |
| totale_uscite_varie | DOUBLE |
| totale_uscite_versamenti | DOUBLE |
| totale_generale_uscite | DOUBLE |
| fondo_cassa_da_riportare | DOUBLE |
| totale_marchirolo | DOUBLE |
| saldo_cassa | DOUBLE |
| completato | TEXT |
| incasso_assegni | DOUBLE |
| incasso_contante | DOUBLE |
| saldo_sospesi | DOUBLE |
| punti_viva | DOUBLE |
| commenti | TEXT |
| PRIMARY KEY(data) |

Il formato DATE non è direttamente riconosciuto da [SQLite](https://www.sqlite.org/datatype3.html), ma è formattato come YYY-MM-DD, in modo che le date si possano ordinare.

### liste
Contiene le varie liste per ogni giorno.
Non ha primary key siccome per ogni giorno possono esserci molteplici liste. Ha chiaramente il vincolo della chiave esterna per la data.
| COLUMN | TYPE |
| ------ | ---- |
| data | DATE |
| categoria | TEXT |
| valore | DOUBLE |
| causale | TEXT |
| CONSTRAINT fk_sospesi_prova FOREIGN KEY (data) REFERENCES prova(data) |
