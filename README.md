# Assistent AI de Biblioteques de Barcelona 2024

Aplicació local en Python amb una interfície web feta amb HTML, CSS i JavaScript. L'assistent utilitza el fitxer `2024_dades_biblioteques.csv` com a base de dades per respondre preguntes sobre les biblioteques de Barcelona durant l'any 2024.

El projecte no necessita connexió a cap API externa ni instal·lar llibreries addicionals. Tot funciona en local amb Python 3.

## Funcionalitats

- Consulta dades del CSV amb preguntes en llenguatge natural.
- Respon totals, mitjanes, màxims i mínims.
- Permet fer recomptes per districte, barri o altres columnes del fitxer.
- Genera rànquings, com el top de biblioteques per visites o préstecs.
- Mostra fitxes de biblioteques concretes.
- Inclou una interfície web local fàcil d'utilitzar.

## Exemples de preguntes

- Quin és el total de visites acumulades a totes les biblioteques de Barcelona durant el 2024?
- Quina és la mitjana de `Metres_Quadrats` de les biblioteques analitzades?
- Quantes biblioteques úniques hi ha registrades al fitxer?
- Digue'm la quantitat de biblioteques per districte.
- Total de visites per districte.
- Mitjana de metres quadrats per barri.
- Top 5 biblioteques per `Prestecs_presencials`.
- Quina biblioteca ha fet més préstecs presencials respecte dels virtuals?
- Dona'm les dades de Biblioteca Jaume Fuster.
- Codis de barris.

## Estructura del projecte

```text
bcn-biblioteques-ai/
├── 2024_dades_biblioteques.csv
├── app.py
├── index.html
├── styles.css
├── script.js
├── ejecutar_local.sh
├── ejecutar_local.bat
├── README.md
└── .gitignore
```

## Requisits

- Python 3 instal·lat.
- Un navegador web modern.

No cal instal·lar paquets amb `pip`.

## Fitxers necessaris

Per executar el projecte, el ZIP o el repositori ha d'incloure aquests fitxers:

```text
app.py
index.html
styles.css
script.js
2024_dades_biblioteques.csv
ejecutar_local.sh
ejecutar_local.bat
README.md
```

La carpeta `__pycache__` no és necessària. Python la crea automàticament quan s'executa l'aplicació, per això està ignorada a `.gitignore` i no cal pujar-la a GitHub.

## Descarregar el projecte des de GitHub

### Opció 1: descarregar ZIP

1. Entra a la pàgina del repositori a GitHub.
2. Prem el botó verd `Code`.
3. Selecciona `Download ZIP`.
4. Descomprimeix el fitxer ZIP.
5. Entra dins la carpeta del projecte.

### Opció 2: clonar amb Git

```bash
git clone URL_DEL_REPOSITORI
cd bcn-biblioteques-ai
```

Substitueix `URL_DEL_REPOSITORI` per l'URL real del teu repositori.

## Executar segons el sistema operatiu

### Linux

Obre una terminal dins la carpeta del projecte i executa:

```bash
chmod +x ejecutar_local.sh
./ejecutar_local.sh
```

### macOS

Obre una terminal dins la carpeta del projecte i executa:

```bash
chmod +x ejecutar_local.sh
./ejecutar_local.sh
```

Si macOS bloqueja l'execució del fitxer, també pots iniciar l'aplicació amb:

```bash
python3 app.py
```

### Windows

Opció recomanada:

1. Entra dins la carpeta del projecte.
2. Fes doble clic a `ejecutar_local.bat`.

Opció manual des de PowerShell o CMD:

```bat
python app.py
```

Si Windows no reconeix `python`, prova:

```bat
py app.py
```

Si l'usuari descarrega el projecte com a ZIP, només ha de descomprimir-lo abans d'executar aquests passos.

## Obrir l'aplicació al navegador

Quan s'executa el projecte, s'inicia un servidor local i normalment el navegador s'obre automàticament.

L'adreça habitual és:

```text
http://127.0.0.1:8000
```

Si el port `8000` està ocupat, l'aplicació farà servir automàticament un port entre `8001` i `8019`. La terminal mostrarà l'adreça exacta, per exemple:

```text
Assistent iniciat a http://127.0.0.1:8001
```

Per aturar el servidor, torna a la terminal i prem:

```text
Ctrl + C
```

## Pujar el projecte a GitHub

1. Crea un repositori nou a GitHub.
2. Obre una terminal dins la carpeta del projecte.
3. Executa aquests comandaments:

```bash
git init
git add .
git commit -m "Primera versio de l'assistent de biblioteques"
git branch -M main
git remote add origin URL_DEL_REPOSITORI
git push -u origin main
```

Substitueix `URL_DEL_REPOSITORI` per l'URL del repositori que has creat a GitHub.

Exemple:

```bash
git remote add origin https://github.com/el-teu-usuari/bcn-biblioteques-ai.git
```

## Notes

- El fitxer CSV ha d'estar a la mateixa carpeta que `app.py`.
- L'aplicació funciona en local; no publica les dades a internet.
- El sistema interpreta preguntes sobre el CSV, però no utilitza una API externa d'intel·ligència artificial.
