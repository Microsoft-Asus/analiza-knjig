from bs4 import BeautifulSoup
import tools
import re
import os

base_url = 'https://www.gutenberg.org'


def main():
    cats = process_categories()
    books_csv = []
    subjects_csv = []
    categories_csv = []
    for category in cats:
        title, catalog_link = category['title'], category['link']
        catalog_links = process_catalog(title, catalog_link)
        for book_link in catalog_links:
            book, subjects = process_book(book_link, title)
            if not book or not subjects:
                continue
            books_csv.append(book)
            categories_csv.append({
                'book_id': book['id'],
                'category': category['title']
            })
            for subject_id, subject in subjects.items():
                subjects_csv.append({
                    'id': subject_id,
                    'subject': subject,
                    'book_id': book['id']
                })

    books_csv_no_duplicates = [
        dict(t) for t in set(tuple(d.items()) for d in books_csv)
    ]
    tools.write_csv(books_csv_no_duplicates,
                    ['id', 'title', 'author', 'release_date'], 'book_data',
                    'processed_data')
    tools.write_csv(subjects_csv, ['id', 'subject', 'book_id'], 'subject_data',
                    'processed_data')
    tools.write_csv(categories_csv, ['book_id', 'category'], 'category_data',
                    'processed_data')


# Regex patterns for books
eom_pattern = re.compile(
    r'\*\*\*[^*]+\*\*\*')  # Matches the end of metadata in the txt file.
title_pattern = re.compile(r'Title: (.+?)\n')
author_pattern = re.compile(r'Author: (.+?)\n')
rd_pattern = re.compile(r'Release Date: .*?(\d{4}).*?\n')


def format_title(title):
    title = title.replace('(Bookshelf)', '')
    return title.strip()


def format_title_for_file(title):
    return title.lower().replace(' ', '_')


def join_url(base, rest):
    return base + '/' + rest


# Get categories from the fiction categories page and save them to csv


def parse_categories(html_file):
    '''Get all the categories from the category page.'''
    soup = BeautifulSoup(html_file, 'html.parser')
    cats = []
    # For every bookshelf (even though there should only be one) get all of its elements.
    for bookshelf in soup.find_all('div', 'mw-category'):
        for category in bookshelf.find_all('a'):
            title, link = category.get('title'), category.get('href')
            cats.append({'title': format_title(title), 'link': link})
    return cats


def process_categories():
    '''Get all the categories belonging to fiction along with their respective links.'''
    print('Going through categories')
    category_url = 'Category:Fiction_Bookshelf'
    file_name = 'category_fiction'
    directory = 'pages'
    tools.download_page(join_url(base_url, category_url), file_name, directory)
    cats = tools.read_file(file_name, directory)
    cat_dicts = parse_categories(cats)

    categories = []

    # For every category find its catalog
    for c_dict in cat_dicts:
        category, link = c_dict['title'], c_dict['link']
        catalog_link = process_bookshelf(category, link)
        # Skip categories that don't have that many books
        if not catalog_link:
            continue
        categories.append({'title': category, 'link': catalog_link})
    for category in categories:
        c = category['title']
        print(f'Added category {c}')
    #tools.write_csv(categories, ['title', 'link'], 'categories',
    #                'processed_data')
    return categories


# Get the catalog link from the bookshelf


def process_bookshelf(title, link):
    directory = 'pages'
    title_f = format_title_for_file(title)
    tools.download_page(join_url(base_url, link), title_f, directory)
    bookshelf = tools.read_file(title_f, directory)
    return parse_bookshelf(bookshelf)


def parse_bookshelf(html_file):
    soup = BeautifulSoup(html_file, 'html.parser')
    catalog_link = ''
    for ext_text in soup.find_all('a', 'external text'):
        if ext_text.text == 'catalog search':
            return ext_text.get('href')
    for ext_text in soup.find_all('a', 'extiw'):
        if ext_text.text == 'catalog search':
            return 'https:' + ext_text.get(
                'href')  # More or less a special case


# Load all the books from a specific catalog
def process_catalog(category, catalog_link):
    print(f'Downloading books from {category}')
    links = []
    for start_index in range(0, 1000, 25):
        link = catalog_link + f'&start_index={start_index}'
        title = category + f'_{start_index}'
        directory = os.path.join('pages', format_title_for_file(category))
        tools.download_page(link, title, directory)
        catalog_page = tools.read_file(title, directory)
        book_links = parse_catalog(catalog_page)
        # When we reach empty pages stop
        if len(book_links) == 0:
            break
        links += book_links
    return links


def parse_catalog(html_file):
    soup = BeautifulSoup(html_file, 'html.parser')
    book_links = []
    for book_link in soup.find_all('li', 'booklink'):
        for link in book_link.find_all('a'):
            book_links.append(link.get('href'))
    return book_links


# Download a specific book and its metadata
def process_book(book_link, category):
    directory = os.path.join('pages', 'books')
    link = join_url(base_url, book_link)
    book_id = int(book_link.replace('/ebooks/', ''))
    tools.download_page(link, str(book_id), directory)
    book_page = tools.read_file(str(book_id), directory)
    book_link, subjects = parse_book_page(book_page)
    if not book_link:
        return None, None
    directory = 'processed_data/books'
    book_url = join_url(base_url, book_link)
    tools.download_txt(book_url, str(book_id), directory)
    book = parse_metadata(book_id)
    if not book:
        return None, None
    book_row = {
        'id': book_id,
        'title': book['title'],
        'author': book['author'],
        'release_date': book['release_date']
    }
    return book_row, subjects


def parse_book_page(html_file):
    soup = BeautifulSoup(html_file, 'html.parser')
    book = {}
    # First confirm that it is actually text
    t = soup.find('td', property='dcterms:type').text
    if t != 'Text':
        return None, None

    # Save all the subjects
    subjects = {}
    for subject in soup.find_all('td', property='dcterms:subject'):
        l = subject.find('a')
        name = l.text.strip()
        subject_id = int(l.get('href').replace('/ebooks/subject/', ''))
        subjects[subject_id] = name

    # Find url for plaintext book
    for link in soup.find_all('a', title='Download'):
        if link.text == 'Plain Text UTF-8':
            return link.get('href'), subjects
    return None, None


def parse_metadata(book_id):
    txt = tools.read_book(str(book_id), 'processed_data/books')
    e_re = eom_pattern.search(txt)
    if e_re:
        e = e_re.start()
    else:
        return
    metadata_txt = txt[:e]

    title_re = title_pattern.search(metadata_txt)
    author_re = author_pattern.search(metadata_txt)
    release_date_re = rd_pattern.search(metadata_txt)

    if title_re:
        title = title_re[1]
    else:
        title = 'Unknown'
    if author_re:
        author = author_re[1]
    else:
        author = 'Unknown'
    if release_date_re:
        release_date = release_date_re[1]
    else:
        release_date = 0
    return {'title': title, 'author': author, 'release_date': release_date}


if __name__ == '__main__':
    main()
