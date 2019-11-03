from bs4 import BeautifulSoup
import tools
import re
import os

base_url = 'https://www.gutenberg.org'


def main():
    cats = process_categories()

    for category in cats:
        title, catalog_link = category['title'], category['link']
        catalog_links = process_catalog(title, catalog_link)

        for book_link in catalog_links:
            process_book(book_link, title)


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


def parse_book(html_file):
    soup = BeautifulSoup(html_file, 'html.parser')

    book = {}

    # First confirm that it is actually text
    t = soup.find('td', property='dcterms:type').text
    if t != 'Text':
        return

    # Find url for plaintext book
    for link in soup.find_all('a', type='text/plain'):
        book['url'] = link.get('href')

    bibrec = soup.find('table', 'bibrec')
    # Get author
    author_surname, author_name, life = bibrec.find_next(
        'a', rel='marcrel:aut').text.split(', ')
    book['author'] = author_name + ' ' + author_surname

    # Get the books title
    book['title'] = soup.find('td', itemprop='headline').text.strip()

    # Save all the subjects
    subjects = []
    for subject in soup.find_all('td', property='dcterms:subject'):
        name = subject.find('a').text.strip()
        subjects.append(name)
    book['subjects'] = subjects
    return book


if __name__ == '__main__':
    #main()
    book = tools.read_file('book', 'pages/books')
    parse_book(book)
