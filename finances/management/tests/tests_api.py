from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

import json

from finances.session.tests import get_user
from ..models import Tag, Rule, RuleAndCondition, RuleOrCondition, FilterConditionals

class RulesApiTest(TestCase):
    def setUp(self):
        rule1 = Rule()
        rule1.save()

        and_condition = RuleAndCondition(
            rule=rule1,
            type_conditional=FilterConditionals.CONTAINS,
            conditional="1",
            negate=False
        )
        and_condition.save()

        or_condition = RuleOrCondition(
            or_group=and_condition,
            type_conditional=FilterConditionals.GREATER,
            conditional="3",
            negate=True
        )
        or_condition.save()

        self.user = get_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def tearDown(self):
        RuleOrCondition.objects.all().delete()
        RuleAndCondition.objects.all().delete()
        Rule.objects.all().delete()

    def test_get(self):
        response = self.client.get('/api/rule/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data, [{
            'id': 1,
            'parent': None,
            'assign_labels': [],
            'conditions': [{
                'rule': 1,
                'id': 1,
                'type_conditional': 'c',
                'conditional': '1',
                'negate': False,
                'or_conditions': [{
                    'or_group': 1,
                    'id': 1,
                    'type_conditional': 'g',
                    'conditional': '3',
                    'negate': True
                }]
            }]
        }])


class TagApiTest(TestCase):
    def setUp(self):
        self.tag = Tag(name="peperoni")
        self.tag.save()
        self.user = get_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def tearDown(self):
        Tag.objects.all().delete()

    def test_get_list(self):
        response = self.client.get('/api/tag/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)

    def test_delete(self):
        response = self.client.delete('/api/tag/{}/'.format(self.tag.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

