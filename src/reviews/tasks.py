# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from django.db import transaction
from django.utils.translation import ugettext
from django.contrib.contenttypes.models import ContentType
from celery import current_task

from core.celery import app
from reviews.signals import pre_batch_review, post_batch_review, batch_item_indexed
from reviews.models import Review
from notifications.models import notify


logger = logging.getLogger(__name__)


@app.task
def do_batch_import(user_id, contenttype_id, document_ids):
    contenttype = ContentType.objects.get_for_id(contenttype_id)
    document_class = contenttype.model_class()

    docs = document_class.objects \
        .select_related() \
        .filter(document_id__in=document_ids)

    ok = []
    nok = []
    count = 0
    total_docs = docs.count()

    # We compute the progress as the proportion of documents for which the
    # review has started.
    # However, after all documents are treated, there is still the
    # index + refresh step which takes quite some time. So we artificially
    # increase the document count as a hackish way to never display a 100%
    # progress bar as long as the task is not truly finished.
    total_docs += 30

    pre_batch_review.send(sender=do_batch_import)

    for doc in docs:
        try:
            if not doc.latest_revision.can_be_reviewed:
                raise RuntimeError()

            doc.latest_revision.start_review()
            batch_item_indexed.send(
                sender=do_batch_import,
                document_type=doc.document.document_type(),
                document_id=doc.id,
                json=doc.latest_revision.to_json())
            ok.append(doc)
        except:
            nok.append(doc)

        count += 1
        progress = float(count) / total_docs * 100
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': progress})

    post_batch_review.send(sender=do_batch_import, user_id=user_id)

    if len(ok) > 0:
        ok_message = ugettext('The review started for the following documents:')
        ok_list = '</li><li>'.join('<a href="%s">%s</a>' % (doc.get_absolute_url(), doc) for doc in ok)
        notify(user_id, '{} <ul><li>{}</li></ul>'.format(
            ok_message,
            ok_list
        ))

    if len(nok) > 0:
        nok_message = ugettext("We failed to start the review for the following documents:")
        nok_list = '</li><li>'.join('<a href="%s">%s</a>' % (doc.get_absolute_url(), doc) for doc in nok)
        notify(user_id, '{} <ul><li>{}</li></ul>'.format(
            nok_message,
            nok_list
        ))

    return 'done'


@app.task
def batch_close_reviews(user_id, review_ids):
    """Close several reviews at once.

    Only reviewers can do this.

    """
    logger.info('Closing several reviews at once: {}'.format(
        ', '.join(review_ids)))

    ok = []
    nok = []
    nb_reviews = len(review_ids)
    reviews = Review.objects \
        .filter(reviewer_id=user_id) \
        .filter(role=Review.ROLES.reviewer) \
        .filter(status=Review.STATUSES.progress) \
        .filter(id__in=review_ids) \
        .select_related()

    counter = float(1)
    comments = None
    for review in reviews:

        # Update progress counter
        progress = counter / nb_reviews * 100
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': progress})

        try:
            with transaction.atomic():
                # Post an empty review
                logger.info('Closing review {}'.format(review.id))
                review.post_review(comments, save=True)

                # Check if the review step has ended
                # TODO This is highly inefficient. Maybe one day
                # find another way to do it?
                document = review.document
                latest_revision = document.get_latest_revision()
                waiting_reviews = Review.objects \
                    .filter(document=document) \
                    .filter(revision=review.revision) \
                    .filter(role='reviewer') \
                    .exclude(closed_on=None)
                if waiting_reviews.count() == latest_revision.reviewers.count():
                    logger.info('Closing reviewers step')
                    latest_revision.end_reviewers_step(save=False)

            ok.append(review.document)
        except:
            nok.append(review.document)
            pass

        counter += 1

    if len(ok) > 0:
        ok_message = ugettext('You closed the review for the following documents:')
        ok_list = '</li><li>'.join('<a href="%s">%s</a>' % (doc.get_absolute_url(), doc) for doc in ok)
        notify(user_id, '{} <ul><li>{}</li></ul>'.format(
            ok_message,
            ok_list
        ))

    if len(nok) > 0:
        nok_message = ugettext("We failed to close the review for the following documents:")
        nok_list = '</li><li>'.join('<a href="%s">%s</a>' % (doc.get_absolute_url(), doc) for doc in nok)
        notify(user_id, '{} <ul><li>{}</li></ul>'.format(
            nok_message,
            nok_list
        ))

    return 'done'
