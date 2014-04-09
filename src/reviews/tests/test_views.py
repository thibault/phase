from django.test import TestCase
from django.core.urlresolvers import reverse

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from accounts.factories import UserFactory


class ReviewersDocumentListTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.other_user = UserFactory(
            email='test@phase.fr',
            category=self.category
        )
        self.client.login(email=self.user.email, password='pass')
        self.url = reverse('reviewers_review_document_list')

    def test_empty_review_list(self):
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_review_not_started_yet(self):
        """If the review is not started yet, the doc does not appear in list."""
        doc = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'approver': self.other_user,
            }
        )
        self.assertFalse(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_review_started(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.user,
                'approver': self.user,
            }
        )
        doc.latest_revision.start_review()
        self.assertTrue(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

    def test_step_finished(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.user,
                'approver': self.user,
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_reviewers_step()
        self.assertTrue(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_review_finished(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.user,
                'approver': self.user,
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_review()
        self.assertFalse(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')


class LeaderDocumentListTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.other_user = UserFactory(
            email='test@phase.fr',
            category=self.category
        )
        self.client.login(email=self.user.email, password='pass')
        self.url = reverse('leader_review_document_list')

    def test_empty_review_list(self):
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_review_not_started_yet(self):
        """If the review is not started yet, the doc does not appear in list."""
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'approver': self.other_user,
            }
        )
        self.assertFalse(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_previous_step(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'approver': self.other_user,
            }
        )
        doc.latest_revision.start_review()
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

    def test_current_step(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'approver': self.other_user,
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_reviewers_step()
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

    def test_step_finished(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'approver': self.other_user,
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_leader_step()
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')


class ApproverDocumentListTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.other_user = UserFactory(
            email='test@phase.fr',
            category=self.category
        )
        self.client.login(email=self.user.email, password='pass')
        self.url = reverse('approver_review_document_list')

    def test_previous_step(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.other_user,
                'approver': self.user,
            }
        )
        doc.latest_revision.start_review()
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

        doc.latest_revision.end_reviewers_step()
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

    def test_current_step(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.other_user,
                'approver': self.user,
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_leader_step()
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

    def test_step_finished(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.other_user,
                'approver': self.user,
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_review()
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')


class ReviewFormTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.other_user = UserFactory(
            email='test@phase.fr',
            category=self.category
        )
        self.client.login(email=self.user.email, password='pass')
        self.url = reverse('review_document', args=['test_key'])

        self.filename = 'documents/tests/sample_doc_native.docx'

    def test_reviewers_submit_review_without_file(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'approver': self.other_user,
            }
        )
        revision = doc.latest_revision
        revision.start_review()

        review = revision.get_review(self.user)
        self.assertIsNone(review.reviewed_on)

        self.client.post(self.url)
        review = revision.get_review(self.user)
        self.assertIsNotNone(review.reviewed_on)
        self.assertFalse(review.comments)

    def test_reviewers_submit_review_with_file(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'approver': self.other_user,
            }
        )
        revision = doc.latest_revision
        revision.start_review()

        with open(self.filename, 'rb') as fp:
            self.client.post(self.url, {'comments': fp})
            review = revision.get_review(self.user)
            self.assertTrue(review.comments)

    def test_non_reviewer_submit_review(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.other_user],
                'leader': self.other_user,
                'approver': self.other_user,
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 404)

    def test_reviewer_cannot_access_review_when_step_is_closed(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'approver': self.other_user,
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_reviewers_step()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

    def test_reviewer_cannot_do_the_same_review_twice(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'approver': self.other_user,
            }
        )
        revision = doc.latest_revision
        revision.start_review()

        res = self.client.post(self.url, follow=True)
        self.assertEqual(res.status_code, 200)

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

        res = self.client.post(self.url, follow=True)
        self.assertEqual(res.status_code, 404)

    def test_leader_submit_review_without_file(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'approver': self.other_user,
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_reviewers_step()

        self.assertIsNone(revision.leader_step_closed)

        self.client.post(self.url)
        revision = revision.__class__.objects.get(pk=revision.pk)
        self.assertIsNotNone(revision.leader_step_closed)
        self.assertFalse(revision.leader_comments)

    def test_leader_submit_review_with_file(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'approver': self.other_user,
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_reviewers_step()

        with open(self.filename, 'rb') as fp:
            self.client.post(self.url, {'comments': fp})
            revision = revision.__class__.objects.get(pk=revision.pk)
            self.assertIsNotNone(revision.leader_step_closed)
            self.assertTrue(revision.leader_comments)

    def test_leader_cannot_access_review_when_step_is_closed(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'approver': self.other_user,
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_leader_step()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

    def test_approver_submit_review_without_file(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.other_user],
                'leader': self.other_user,
                'approver': self.user,
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_leader_step()

        self.assertIsNone(revision.review_end_date)

        self.client.post(self.url)
        revision = revision.__class__.objects.get(pk=revision.pk)
        self.assertIsNotNone(revision.review_end_date)
        self.assertFalse(revision.approver_comments)

    def test_approver_submit_review_with_file(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.other_user],
                'leader': self.other_user,
                'approver': self.user,
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_leader_step()

        with open(self.filename, 'rb') as fp:
            self.client.post(self.url, {'comments': fp})
            revision = revision.__class__.objects.get(pk=revision.pk)
            self.assertIsNotNone(revision.review_end_date)
            self.assertTrue(revision.approver_comments)

    def test_approver_cannot_access_a_closed_review(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.other_user],
                'leader': self.other_user,
                'approver': self.user,
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_review()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)
