# Analiza knjig
Projektna naloga vsebuje analizo podatkov knjige, ter njene vsebine. Knjige so zbrane iz strani [Project Gutenberg](https://www.gutenberg.org/), ki vsebuje več kot 60 000 strani, v našem primeru, pa se bom osredotočil le na zvrst
`Fiction`, ki pa ima okoli 6000 knjig. Zaradi težavnosti analize knjig iz drugih jezikov, se bom pri pri tem omejil na knjige, ki so napisane v angleščini.
# Vir podatkov
Podatki bodo zajeti iz strani [Gutenberg](https://www.gutenberg.org/), specifično iz kategorije "Fiction".

# Zajeti podatki o posamezni knjigi
  * Naslov
  * Zvrst
  * Teme
  * Besedilo
  * Datum izdaje
  * Avtor

# Procesiranje podatkov
  * Najpogostejše besede posamezne zvrsti
  * Določanje zvrsti na podlagi besedila
  * Število knjig v posameznem letu
  * Pogostost zvrsti
  * Povprečno število strani knjigah
  * Povprečno število strani knjig po zvrsteh
# Podatki
Podatki, zajeti s pomočjo skript `tools.py` in `process_site.py`, se nahajajo v direktoriju `processed_data`.
Poleg tega pa imam še `tokenized_books`, json datoteke besed v knjigi, brez tistih, ki so preveč pogoste v vseh besedilih
neodvisno od zvrsti.
## Struktura CSV datotek:
 * Vsi podatki o knjigah so vsebovani v datoteki `book_data.csv` ki vsebuje vnose oblike:
  `id, title, author, release_date`, pri čemer je `id` vsaklajen z številko knjige na strani [Gutenberg](https://www.gutenberg.org/).
  * Datoteka `category_data.csv` ima za vsako knjigo podane vse njene kategorije in je oblike `book_id, title`, kjer je `title` 
   ime kategorije `book_id` pa številka, ki se sklicuje na `id` iz `book_data.csv`.
   * V `subject_data.csv` se podobno kot v `category_data.csv` nahajajo `book_id, title`, kjer se `title` nanaša na temo, ki jo
    vsebuje knjiga z `id` `book_id`.
    
 ## Ostali podatki
  Med izvajanjem skripte, se spletne strani (html) shranjujejo v direktorij `pages`, ki se nahaja v baznem direktoriju projekta.
  Program naložene knjige shranjuje v mapi `books`, ki se nahaja znotraj `processed_data`, knjige pa so v `txt` formatu in 
  vsebujejo celotno vsebino knjige ter nekaj podatkov, ki jih doda [Gutenberg](https://www.gutenberg.org/) (ime avtorja, leto izdaje, naslov knjige...)
