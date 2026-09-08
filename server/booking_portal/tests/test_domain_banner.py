from django.test import Client, TestCase

NEW = "onlinecif.bits-hyderabad.ac.in"
OLD = "onlinecal.bits-hyderabad.ac.in"


class TransitionBannerTestCase(TestCase):
    """Both names serve the site while the old one is being retired."""

    def setUp(self):
        self.client = Client()

    def test_the_old_domain_says_where_the_portal_moved_to(self):
        response = self.client.get("/", HTTP_HOST=OLD)

        self.assertContains(response, f"https://{NEW}")
        self.assertContains(response, "Please update your bookmarks")

    def test_the_new_domain_says_nothing(self):
        response = self.client.get("/", HTTP_HOST=NEW)

        self.assertNotContains(response, "Please update your bookmarks")

    def test_the_banner_keeps_the_page_you_were_on(self):
        response = self.client.get("/guidelines/", HTTP_HOST=OLD)

        self.assertContains(response, f"https://{NEW}/guidelines/")
