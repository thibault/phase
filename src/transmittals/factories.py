# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import factory

from transmittals.models import Transmittal, TrsRevision


class TransmittalFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Transmittal

    contract_number = factory.Sequence(lambda n: 'FAC10005-CTR-CLT-TRS-{0:05}'.format(n))
    originator = 'CTR'
    recipient = 'CLT'
    sequential_number = 1


class TrsRevisionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TrsRevision

    transmittal = factory.SubFactory(TransmittalFactory)
    document_key = 'FAC10005-CTR-000-EXP-LAY-4891'
    title = factory.Sequence(lambda n: 'Trs Revision {0:05}'.format(n))
    revision = factory.Sequence(lambda n: n)
    is_new_revision = True