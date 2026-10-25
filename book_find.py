"""
Find a book based on ISBN by scraping nicebooks.com.
"""

import os

import bs4 as bs
import requests

BASE_URL = "https://nicebooks.com"
SEARCH_RESULT_URL = BASE_URL + "/us/search/result"
COVER_DIR = os.path.join(os.path.dirname(__file__), "static", "book_covers")
TIMEOUT = 20

HEADERS = {
    "Accept-Language": "en-US, en; q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


def get_soup(search_isbn: str):
    """
    Gets a beautifulsoup object for the book page matching the ISBN, or None if no book was found.\n
    The first request is to the search result endpoint and the second is to the actual book page.
    Network errors are raised as requests.RequestException.
    """
    with requests.Session() as session:
        session.headers.update(HEADERS)
        response = session.get(SEARCH_RESULT_URL, params={"q": search_isbn, "p": 1}, timeout=TIMEOUT)
        response.raise_for_status()
        link = bs.BeautifulSoup(response.text, "html5lib").find("a", attrs={"class": "title"})
        if link is None or not link.get("href"):
            return None
        response = session.get(BASE_URL + link["href"], timeout=TIMEOUT)
        response.raise_for_status()
        return bs.BeautifulSoup(response.text, "html5lib")


def get_element_text(soup: bs.BeautifulSoup, tag, itemprop):
    """Gets the text from a beautifulsoup element based on the tag and itemprop"""
    element = soup.find(tag, attrs={"itemprop": itemprop})
    if element:
        return element.text
    return None


def get_element_content(soup: bs.BeautifulSoup, tag, itemprop):
    """Gets the content from a beautifulsoup element based on the tag and itemprop"""
    try:
        element = soup.find(tag, attrs={"itemprop": itemprop}).get("content")
    except AttributeError:
        element = None
    return element


def get_author(soup: bs.BeautifulSoup):
    """Gets the author text from a beautifulsoup object"""
    author = soup.find(itemprop="author")
    if author:
        return author.span.text
    return None


def get_book_format(soup: bs.BeautifulSoup):
    """Gets the book format from a beautifulsoup object"""
    print_format = soup.find("link", attrs={"itemprop": "bookFormat"})
    if print_format:
        print_format = str(print_format.find_parent("div").text.strip())
        return print_format.replace("Format:", "")
    return None


def get_isbn_dict(soup: bs.BeautifulSoup):
    """Gets ISBN-10 and ISBN-13 from a beautifulsoup object"""
    result = {"isbn-10": "", "isbn-13": ""}
    isbn_list = soup.find_all("div", attrs={"itemprop": "isbn"})
    if isbn_list:
        for isbn in isbn_list:
            if isbn.find_previous_sibling("div").text == "ISBN-10":
                isbn_10 = isbn.text
                # print(f'ISBN 10: {isbn_10}')
                result.update({"isbn-10": isbn_10})
            else:
                isbn_13 = isbn.text
                # print(f'ISBN 13: {isbn_13}')
                result.update({"isbn-13": isbn_13})
    return result


def get_image_url(soup: bs.BeautifulSoup):
    """Gets the thumbnail image url from a beautifulsoup object"""
    image = soup.find("img", attrs={"itemprop": "image"})
    return image.get("src") if image else None


def get_image(soup: bs.BeautifulSoup, isbn_13: str):
    """
    Get cover image files and stores them in the book_covers folder\n
    Stores two sizes, one thumbnail and one large with isbn_13 as a name standard\n
    Returns the filename for the thumbnail version
    """
    image_url = get_image_url(soup)
    if not image_url:
        return None
    os.makedirs(COVER_DIR, exist_ok=True)
    image_name = f"{isbn_13}.jpg"
    large_url = image_url.split("?")[0]
    for url, name in ((image_url, image_name), (large_url, f"{isbn_13}_large.jpg")):
        remote_image = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        remote_image.raise_for_status()
        with open(os.path.join(COVER_DIR, name), "wb") as local_image:
            local_image.write(remote_image.content)
    return image_name


def get_book_info(isbn: str, save_image: bool = False):
    """
    Gets all the information on a book from nicebooks.com\n
    All values are None if no book was found. Cover images are only stored if save_image is True.
    """
    book_soup = get_soup(isbn)

    if book_soup:
        # book_title = get_title(book_soup)
        book_title = get_element_text(book_soup, "span", "name")
        book_sub_title = get_element_text(book_soup, "small", "alternativeHeadline")
        book_author = get_author(book_soup)
        book_publisher = get_element_text(book_soup, "a", "publisher")
        book_publication_date = get_element_content(book_soup, "div", "datePublished")
        book_language_iso = get_element_content(book_soup, "div", "inLanguage")
        book_language = get_element_text(book_soup, "div", "inLanguage")
        book_format = get_book_format(book_soup)
        book_nof_pages = get_element_text(book_soup, "div", "numberOfPages")
        isbn_dict = get_isbn_dict(book_soup)
        book_description = get_element_text(book_soup, "p", "description")
        book_image_name = None
        if save_image:
            book_image_name = get_image(book_soup, isbn_dict["isbn-13"].replace("-", "") or isbn)

        return {
            "author": book_author,
            "title": book_title,
            "sub_title": book_sub_title,
            "publisher": book_publisher,
            "publication_date": book_publication_date,
            "language": book_language,
            "language_iso": book_language_iso,
            "nof_pages": book_nof_pages,
            "format": book_format,
            "image_name": book_image_name,
            "image_url": get_image_url(book_soup),
            "isbn-13": isbn_dict["isbn-13"],
            "isbn-10": isbn_dict["isbn-10"],
            "description": book_description,
        }

    return {
        "author": None,
        "title": None,
        "sub_title": None,
        "publisher": None,
        "publication_date": None,
        "language": None,
        "language_iso": None,
        "nof_pages": None,
        "format": None,
        "image_name": None,
        "image_url": None,
        "isbn-13": None,
        "isbn-10": None,
        "description": None,
    }


if __name__ == "__main__":
    input_var = input("ISBN-13: ")
    book = get_book_info(input_var)
