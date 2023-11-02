import json

from django.test import TestCase
from django.urls import reverse

from techtest.articles.models import Article
from techtest.authors.models import Author
from techtest.regions.models import Region


class ArticleListViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("articles-list")
        self.author = Author.objects.create(first_name='AuthorName', last_name='AuthorLastName')
        self.article_1 = Article.objects.create(title="Fake Article 1", author=self.author)
        self.region_1 = Region.objects.create(code="AL", name="Albania")
        self.region_2 = Region.objects.create(code="UK", name="United Kingdom")
        self.article_2 = Article.objects.create(
            title="Fake Article 2", content="Lorem Ipsum", author=None
        )
        self.article_2.regions.set([self.region_1, self.region_2])

    def test_serializes_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            [
                {
                    "id": self.article_1.id,
                    "title": "Fake Article 1",
                    "content": "",
                    "regions": [],
                    "author": {
                        "id": self.author.id,
                        "first_name": self.author.first_name,
                        "last_name": self.author.last_name
                    }
                },
                {
                    "id": self.article_2.id,
                    "title": "Fake Article 2",
                    "content": "Lorem Ipsum",
                    "regions": [
                        {
                            "id": self.region_1.id,
                            "code": "AL",
                            "name": "Albania",
                        },
                        {
                            "id": self.region_2.id,
                            "code": "UK",
                            "name": "United Kingdom",
                        },
                    ],
                    "author": {}
                },
            ],
        )

    def test_creates_new_article_with_regions_and_author(self):
        payload = {
            "title": "Fake Article 3",
            "content": "To be or not to be",
            "regions": [
                {"code": "US", "name": "United States of America"},
                {"code": "AU", "name": "Austria"},
            ],
            "author": {
                "first_name": "testname",
                "last_name": "testlastname"
            }

        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        regions = Region.objects.filter(articles__id=article.id)
        author = Author.objects.filter(id=article.author.id)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 2)
        self.assertIsNotNone(author)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 3",
                "content": "To be or not to be",
                "regions": [
                    {
                        "id": regions.all()[0].id,
                        "code": "US",
                        "name": "United States of America",
                    },
                    {"id": regions.all()[1].id, "code": "AU", "name": "Austria"},
                ],
                "author": {
                    "id": article.author.id,
                    "first_name": payload['author']['first_name'],
                    "last_name": payload['author']['last_name']
                }
            },
            response.json(),
        )

    def test_create_new_article_without_author_and_regions(self):
        payload = {
            "title": "Fake Article 3",
            "content": "To be or not to be",
            "regions": [],
            "author": {}

        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(article)
        self.assertIsNone(article.author)
        self.assertEqual(regions.count(), 0)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 3",
                "content": "To be or not to be",
                "regions": [],
                "author": {}
            },
            response.json(),
        )

class ArticleViewTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name='AuthorName1', last_name='AuthorLastName1')
        self.article = Article.objects.create(title="Fake Article 1", author=self.author)
        self.region_1 = Region.objects.create(code="AL", name="Albania")
        self.region_2 = Region.objects.create(code="UK", name="United Kingdom")
        self.article.regions.set([self.region_1, self.region_2])
        self.url = reverse("article", kwargs={"article_id": self.article.id})

    def test_serializes_single_record_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            {
                "id": self.article.id,
                "title": "Fake Article 1",
                "content": "",
                "regions": [
                    {
                        "id": self.region_1.id,
                        "code": "AL",
                        "name": "Albania",
                    },
                    {
                        "id": self.region_2.id,
                        "code": "UK",
                        "name": "United Kingdom",
                    },
                ],
                "author": {
                    "id": self.author.id,
                    "first_name": self.author.first_name,
                    "last_name": self.author.last_name
                }
            },
        )

    def test_updates_article_author_and_regions(self):
        # Change regions
        payload = {
            "title": "Fake Article 1 (Modified)",
            "content": "To be or not to be here",
            "regions": [
                {"code": "US", "name": "United States of America"},
                {"id": self.region_2.id},
            ],
            "author": {
                "first_name": "AuthorName1(Modified)",
                "last_name": "AuthorLastName1(Modified)"
            }
        }
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.first()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 2)
        self.assertEqual(Article.objects.count(), 1)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 1 (Modified)",
                "content": "To be or not to be here",
                "regions": [
                    {
                        "id": self.region_2.id,
                        "code": "UK",
                        "name": "United Kingdom",
                    },
                    {
                        "id": regions.all()[1].id,
                        "code": "US",
                        "name": "United States of America",
                    },
                ],
                "author": {
                    "id": article.author.id,
                    "first_name": payload['author']['first_name'],
                    "last_name": payload['author']['last_name'],
                }
            },
            response.json(),
        )
        # Remove regions
        payload["regions"] = []
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 0)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 1 (Modified)",
                "content": "To be or not to be here",
                "regions": [],
                "author": {
                    "id": article.author.id,
                    "first_name": payload['author']['first_name'],
                    "last_name": payload['author']['last_name'],
                }
            },
            response.json(),
        )

        # Remove author
        payload["author"] = {}
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 0)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 1 (Modified)",
                "content": "To be or not to be here",
                "regions": [],
                "author": {}
            },
            response.json(),
        )

    def test_removes_article(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Article.objects.count(), 0)


