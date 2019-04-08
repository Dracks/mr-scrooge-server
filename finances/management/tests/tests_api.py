from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

import json

from finances.session.tests import get_user
from ..models import Tag, Rule, RuleAndCondition, RuleOrCondition, FilterConditionals, Label

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

        self.label = Label(name="Daleks")
        self.label.save()

        self.user = get_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def tearDown(self):
        Label.objects.all().delete()
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

    def test_creation(self):
        response = self.client.post('/api/rule/', data={
            'assign_labels': [],
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content)
        parent_id = data['id']

        response = self.client.post('/api/rule/', data={
            'parent': parent_id,
            'assign_labels': [self.label.id]
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content)
        self.assertEqual(data, {
            'id': 3,
            'parent': parent_id,
            'assign_labels': [self.label.id],
            'conditions': []
        })

        Rule.objects.get(id=data['id']).delete()


class RulesAndApiTest(TestCase):
    def setUp(self):
        self.rule1 = Rule()
        self.rule1.save()

        self.user = get_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def tearDown(self):
        RuleAndCondition.objects.all().delete()
        Rule.objects.all().delete()

    def test_post(self):
        send_data = {
            "type_conditional": "g",
            "conditional": "kjaksdfjlaskdjflaskdjflaskdjf"
        }
        response = self.client.post('/api/rule_conditions/', data=send_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.content, b'{"rule":["This field is required."]}')

        send_data['rule'] = self.rule1.pk
        response = self.client.post('/api/rule_conditions/', data=send_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content)
        obj = RuleAndCondition.objects.get(id=data['id'])
        self.assertEqual(obj.negate, False)
        self.assertEqual(obj.type_conditional, "g")



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

