# Analiza knjig

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
  * Določanje tem na podlagi besedila ("subject" na Gutenberg)
  * Število knjig v posameznem letu
  * Pogostost zvrsti
# Podatki
Podatki, zajeti s pomočjo skript `tools.py` in `process_site.py`, se nahajajo v direktoriju `processed_data`.

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
