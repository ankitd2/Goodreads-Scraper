import unittest
import book_scraper
import author_scraper
import json


class MyTestCase(unittest.TestCase):

    def test_bad_book(self):
        """test bad book connection"""
        book_links = []
        page_url = "hola"
        book_links.append(page_url)
        self.assertEqual(book_scraper.scrape_books(book_links), False)

    def test_good_book(self):
        """tests good book connection"""
        book_links = []
        page_url = "https://www.goodreads.com/book/show/36809135-where-the-crawdads-sing"
        book_links.append(page_url)
        self.assertEqual(book_scraper.scrape_books(book_links), True)

    def test_read_from_file(self):
        """tests data read from file"""
        self.assertTrue(book_scraper.read_from_json())

    def test_write_to_file(self):
        """tests writing data to file"""
        self.assertTrue(book_scraper.add_to_json())

    def test_bad_author(self):
        """tests bad author page"""
        author_links = []
        page_url = "hola"
        author_links.append(page_url)
        self.assertEqual(author_scraper.scrape_author(author_links), False)

    def test_good_author(self):
        """tests good author page"""
        author_links = []
        start_author = "https://www.goodreads.com/author/show/1077326.J_K_Rowling"
        author_links.append(start_author)
        self.assertTrue(author_scraper.scrape_author(author_links))

    def test_store_indb(self):
        """tests storing in db"""
        self.assertTrue(book_scraper.store_to_db())

    def test_book_fromdb(self):
        """tests json file existing"""
        (book_info, author_info) = book_scraper.get_from_db()
        self.assertIsNotNone(book_info)

    def test_author_fromdb(self):
        """tests author file exisiting"""
        (book_info, author_info) = book_scraper.get_from_db()
        self.assertIsNotNone(author_info)

    def test_json_files(self):
        self.assertTrue(book_scraper.read_from_json())


if __name__ == '__main__':
    unittest.main()
