#!/usr/bin/env python
# coding: utf-8
import json
import sys
import requests  # Web client
from bs4 import BeautifulSoup as Bsoup  # HTML data structure

author_links = []
base_url = "https://www.goodreads.com"
start_author = "https://www.goodreads.com/author/show/1077326.J_K_Rowling"
author_links.append(start_author)
author_info = {'authors': []}


def scrape_author(links):
    """Scrapes a Goodreads page to get information"""
    authors_read = 0

    while authors_read < 50 and len(links) > 0:
        try:
            page = requests.get(links.pop(0))
        except requests.exceptions.RequestException as error:
            print(error)
            return False

        soup = Bsoup(page.content, "html.parser")

        author_name = soup.find("h1").get_text().strip()
        author_url = soup.head.link["href"]
        author_id = (author_url.split('/')[-1]).split('.')[0]
        rating = soup.find("span", {"class": "average"}).get_text().strip()
        rating_count = soup.find("span", {"itemprop": "ratingCount"}).get_text().strip()
        review_count = soup.find("span", {"itemprop": "reviewCount"}).get_text().strip()
        image_url = soup.find("img", {"alt": author_name})["src"]
        similar_container = soup.find(class_="hreview-aggregate")
        similar_lists = similar_container.findAll("a")
        # author_books = similar_lists[0]["href"]
        similar_authors = similar_lists[1]["href"]

        try:
            authors_page = requests.get(base_url + similar_authors)
        except requests.exceptions.RequestException as error:
            print(error)
            sys.exit(1)
        authors_soup = Bsoup(authors_page.content, "html.parser")

        list_container = authors_soup.findAll("div", {"class": "listWithDividers__item"})
        authors_list = []
        authors_links = []
        count = 0
        for aut in list_container:
            authors = aut.find("span", {"itemprop": "name"}).get_text().strip()
            author_link = aut.find("a", {"itemprop": "url"})["href"]
            if count != 0:
                authors_list.append(authors)
            if author_link not in links and author_link is not None:
                links.append(author_link)
            count += 1

        books_container = soup.findAll("a", {"class": "bookTitle"})
        books_list = []
        # print(authors_list, "\n", links)
        count = 0
        for bk in books_container:
            sim_book_name = bk.find("span", {"itemprop": "name"})
            if sim_book_name is None:
                continue
            if count != 0:
                books_list.append(sim_book_name.get_text().strip())
            count += 1
        author_object = {
            "name": author_name,
            "author_url": author_url,
            "author_id": author_id,
            "rating": rating,
            "rating_count": rating_count,
            "review_count": review_count,
            "image_url": image_url,
            "related_authors": authors_list,
            "author_books": books_list
        }

        author_info['authors'].append(author_object)
        authors_read += 1
    add_to_json()
    return True


def add_to_json():
    """adds scraped author data to JSON"""
    with open('authors.json', 'w') as author_fd:
        json.dump(author_info, author_fd, indent=4)


def read_from_json():
    """reads data in from JSON file"""
    with open('authors.json', 'r') as author_fd:
        return json.load(author_fd)
