from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from dbe.forum.models import *

class SimpleTest(TestCase):
    def setUp(self):
        f = Forum.objects.create(title="cal")
        u = User.objects.create_user("ak", "ak@abc.org", "pwd")
        Site.objects.create(domain="test.org", name="test.org")
        t = Thread.objects.create(title="thread", creator=u, forum=f)
        p = Post.objects.create(title="post", body="body", creator=u, thread=t)

    def test(self):
        c = Client()
        c.login(username="ak", password="pwd")

        r = c.get("/cal/")
        self.assertEquals(r.status_code, 200)
        self.assertTrue('<a href="/cal/cal/1/">cal</a>' in r.content)

        r = c.get("/cal/cal/1/")
        self.assertEquals(r.status_code, 200)
        self.assertTrue('<a href="/cal/thread/1/">thread</a>' in r.content)
        self.assertTrue('ak - post' in r.content)

        r = c.get("/cal/thread/1/")
        self.assertEquals(r.status_code, 200)
        self.assertTrue('<div class="ttitle">thread</div>' in r.content)
        self.assertTrue('<span class="title">post</span>' in r.content)
        self.assertTrue('body <br />' in r.content)
        self.assertTrue('by ak |' in r.content)

        r = c.post("/cal/new_thread/1/", {"subject": "thread2", "body": "body2"})
        r = c.post("/cal/reply/2/", {"subject": "post2", "body": "body3"})

        r = c.get("/cal/thread/2/")
        self.assertEquals(r.status_code, 200)
        self.assertTrue('<div class="ttitle">thread2</div>' in r.content)
        self.assertTrue('<span class="title">post2</span>' in r.content)
        self.assertTrue('body2 <br />' in r.content)
        self.assertTrue('body3 <br />' in r.content)
