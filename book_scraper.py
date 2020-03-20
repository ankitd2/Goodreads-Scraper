#!/usr/bin/env python
# coding: utf-8

import json
from bs4 import BeautifulSoup as Bsoup  # HTML data structure
import requests  # Web client
import pymongo
from author_scraper import scrape_author

book_links = []
page_url = "https://www.goodreads.com/book/show/36809135-where-the-crawdads-sing"
book_links.append(page_url)
book_info = {'books': []}
author_links = []


def scrape_books(links):
    """Parses book information from Goodreads page"""
    books_read = 0
    while books_read < 200 and len(links) > 0:
        try:
            page = requests.get(links.pop(0))
        except requests.exceptions.RequestException as error:
            print(error)
            return False

        soup = Bsoup(page.content, "html.parser")

        book_title = soup.findAll("h1")[0].get_text().strip()
        book_url = soup.head.link["href"]
        book_id = (book_url.split('/')[-1]).split('.')[0]
        isbn13 = soup.find("span", {"itemprop": "isbn"})
        if isbn13 is not None:
            isbn13 = isbn13.get_text().strip()
        author_info = soup.find(class_="authorName")
        author_url = author_info["href"]
        if author_url is not None and author_url not in author_links:
            author_links.append(author_url)
        author_name = author_info.find("span").get_text()
        details_container = soup.find("div", {"id": "details"})
        # isbn = details_container.findAll(class_="infoBoxRowItem")

        page_meta = soup.find(id="bookMeta")
        rating = page_meta.find("span", {"itemprop": "ratingValue"}).get_text().strip()
        rating_count = page_meta.find("meta", {"itemprop": "ratingCount"})["content"]
        review_count = page_meta.find("meta", {"itemprop": "reviewCount"})["content"]
        image_url = soup.find(id="coverImage")["src"]
        similar_list = soup.find("div", {"class": "carouselRow"})
        similar_books = similar_list.findAll("a")
        books = []

        for b in similar_books:
            books.append(b.find("img")["alt"].strip().replace(",", " |"))
            similar_link = book_links.append(b["href"])
            if similar_link not in book_links and similar_link is not None:
                links.append(similar_link)

        book_object = {
            "title": book_title,
            "book_url": book_url,
            "book_id": book_id,
            "ISBN": isbn13,
            "author_url": author_url,
            "author": author_name,
            "rating": rating,
            "rating_count": rating_count,
            "review_count": review_count,
            "image_url": image_url,
            "similar_books": books
        }

        books_read += 1
        book_info['books'].append(book_object)
        print(books_read)
    add_to_json()
    scrape_author(author_links)
    return True


def add_to_json():
    """Adds data to JSON file"""
    # print(book_info)
    with open('books.json', 'w') as book_fd:
        json.dump(book_info, book_fd, indent=4)
    store_to_db()
    return True


def read_from_json():
    """Reads data from JSON file"""
    with open('books.json', 'r') as book_fd:
        return json.load(book_fd)


def store_to_db():
    """Stores JSON array to MongoDB"""
    client = pymongo.MongoClient(
        "mongodb+srv://dbAdmin:dbpassword@goodreads-okywo.mongodb.net/"
        "test?retryWrites=true&w=majority")
    db = client['goodreads_db']
    books_db = db['books']
    with open('books.json') as books_file:
        books_data = json.load(books_file)
    with open('authors.json') as author_file:
        author_data = json.load(author_file)
    books_db.insert_one(books_data)
    db['authors'].insert_one(author_data)
    return True


def get_from_db():
    """Gets information from MongoDB"""
    client = pymongo.MongoClient(
        "mongodb+srv://dbAdmin:dbpassword@goodreads-okywo.mongodb.net/"
        "test?retryWrites=true&w=majority")
    db = client.goodreads_db.books.find()
    dict = {'books': []}
    dict['books'] = (db[0]['books'])

    db_authors = client.goodreads_db['authors'].find()
    dict_authors = {'authors': []}
    # print(db_authors)
    dict_authors['authors'] = (db_authors[0])['authors']
    return dict, dict_authors


# (book_info, author_info) = get_from_db()
scrape_books(book_links)
# print(author_info)
