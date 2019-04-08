from django.test import TestCase
from datetime import date

from ..models import Tag, Filter, FilterConditionals, RawDataSource, ValuesToTag
from ..models import Label, Rule, RuleAndCondition, RuleOrCondition
# Create your tests here.


class RulesModelTest(TestCase):
    def setUp(self):
        self.label = Label(name="Ping")
        self.label.save()

        self.rule = Rule()
        self.rule.save()
        self.rule_child = Rule(parent=self.rule)
        self.rule_child.save()

        self.conditionals_list = []

        c = RuleAndCondition(
            rule = self.rule,
            type_conditional = FilterConditionals.GREATER,
            conditional = 0,
            negate = False
        )
        c.save()

        self.conditionals_list.append(c)

        c = RuleAndCondition(
            rule=self.rule_child,
            type_conditional=FilterConditionals.GREATER,
            conditional=-3,
            negate=False
        )
        c.save()
        self.conditionals_list.append(c)

        c = RuleAndCondition(
            rule=self.rule_child,
            type_conditional = FilterConditionals.LOWER,
            conditional=3,
            negate=False
        )
        c.save()
        self.conditionals_list.append(c)

        self.rds_list = []
        for i in range(0,10):
            rds = RawDataSource(kind="test")
            rds.value = i*2-5
            rds.movement_name = "movement {}".format(i)
            rds.date = date.today()
            rds.save()
            self.rds_list.append(rds)

    def tearDown(self):
        [ c.delete() for c in self.conditionals_list]
        [ rds.delete() for rds in self.rds_list]
        self.label.delete()
        self.rule_child.delete()
        self.rule.delete()

    def test_most_basic(self):
        self.assertTrue(self.rule.check_conditions(self.rds_list[-1]))
        self.assertFalse(self.rule.check_conditions(self.rds_list[0]))

    def test_two_ands(self):
        result = [
            rds.movement_name for rds in self.rds_list
            if self.rule_child.check_conditions(rds)
        ]
        self.assertEqual(len(result), 2)

    def test_with_parent(self):
        result = [
            rds.movement_name for rds in self.rds_list
            if self.rule_child.check_with_parent(rds)
        ]
        self.assertEqual(len(result), 1)

    def test_or_rule(self):
        or_rule = RuleOrCondition(
            or_group = self.conditionals_list[0],
            type_conditional = FilterConditionals.SUFFIX,
            conditional = 0,
            negate = True
        )
        or_rule.save()
        self.conditionals_list.insert(0,or_rule)
        self.assertFalse(self.rule.check_conditions(self.rds_list[0]))
        self.assertTrue(self.rule.check_conditions(self.rds_list[1]))


class TagModelTest(TestCase):
    def setUp(self):
        self.rds_list = []
        for i in range(0,10):
            rds = RawDataSource(kind="test")
            rds.value = i*2-5
            rds.movement_name = "movement {}".format(i)
            rds.date = date.today()
            rds.save()
            self.rds_list.append(rds)
        self.subject = Tag(name="Test tag")
        self.subject.save()

    def tearDown(self):
        self.subject.delete()
        for rds in self.rds_list:
            rds.delete()
    
    def test_apply_filters(self):
        f = Filter(
            tag=self.subject, 
            type_conditional=FilterConditionals.CONTAINS, 
            conditional="movement")
        f.save()
        report = self.subject.apply_filters()
        l=self.subject.values.count()
        self.assertEqual(l, 10)
        self.assertEqual(report['inserted'], 10)

    def test_apply_some_filters(self):
        f1 = Filter(
            tag = self.subject,
            type_conditional = FilterConditionals.SUFFIX,
            conditional = "2"
        )
        f1.save()
        f1 = Filter(
            tag = self.subject,
            type_conditional = FilterConditionals.SUFFIX,
            conditional = "4"
        )
        f1.save()

        report = self.subject.apply_filters()
        l=self.subject.values.count()
        self.assertEqual(l, 2)
        self.assertEqual(report['inserted'], 2)

    def test_apply_negate_filters(self):
        f1 = Filter(
            tag = self.subject,
            type_conditional = FilterConditionals.SUFFIX,
            conditional = "2"
        )
        f1.save()
        f2 = Filter(
            tag = self.subject,
            type_conditional = FilterConditionals.SUFFIX,
            conditional = "4"
        )
        f2.save()
        self.subject.negate_conditional = 1
        self.subject.save()
        report = self.subject.apply_filters()
        l=self.subject.values.count()
        self.assertTrue(self.rds_list[1] in self.subject.values.all())
        self.assertFalse(self.rds_list[2] in self.subject.values.all())
        self.assertEqual(l, 8)
        self.assertEqual(report['inserted'], 8)

    def test_apply_filters_cleaning(self):
        ValuesToTag.objects.create(tag=self.subject, raw_data_source = self.rds_list[0], automatic=1).save()
        ValuesToTag.objects.create(tag=self.subject, raw_data_source = self.rds_list[1], automatic=0).save()
        report = self.subject.apply_filters()
        self.assertEqual(self.subject.values.count(), 1)
        self.assertEqual(self.subject.values.first(), self.rds_list[1])
        self.assertEqual(report['deleted'], 1)
        self.assertEqual(report['inserted'], 0)

    def test_apply_filters_with_previous_manual(self):
        f1 = Filter(
            tag = self.subject,
            type_conditional = FilterConditionals.LOWER,
            conditional = "0"
        )
        f1.save()
        ValuesToTag.objects.create(tag=self.subject, raw_data_source = self.rds_list[0], automatic=0).save()
        report = self.subject.apply_filters()
        self.assertEqual(report['deleted'], 0)
        self.assertEqual(report['inserted'], 2)
    
    def test_apply_filters_parent(self):
        subject = self.subject
        parent = Tag(name="parent")
        parent.save()
        subject.parent = parent
        subject.save()

        f = Filter(
            tag = subject,
            type_conditional = FilterConditionals.PREFIX,
            conditional = "movement"
        )
        f.save()
        ValuesToTag.objects.create(tag=parent, raw_data_source = self.rds_list[5], automatic=1).save()
        subject.apply_filters()
        self.assertEqual(self.subject.values.count(), 1)
        self.assertEqual(self.subject.values.first(), self.rds_list[5])
        subject.parent = None
        subject.save()
        parent.delete()



class FilterModelTests(TestCase):

    def test_filter_contains(self):
        f = Filter(type_conditional=FilterConditionals.CONTAINS, conditional="daleks")
        data1 = RawDataSource(movement_name="Dr Who is the greatest hero ever")
        data2 = RawDataSource(movement_name="Dr Who is the daleks enemy")
        self.assertFalse(f.isValid(data1))
        self.assertTrue(f.isValid(data2))

    def test_filter_prefix(self):
        f = Filter(type_conditional=FilterConditionals.PREFIX, conditional="Dr Who")
        data1 = RawDataSource(movement_name="Dr Strange is the best magician")
        data2 = RawDataSource(movement_name="Dr Who is the dalek enemy")
        self.assertFalse(f.isValid(data1))
        self.assertTrue(f.isValid(data2))

    def test_filter_suffix(self):
        f = Filter(type_conditional=FilterConditionals.SUFFIX, conditional="enemy")
        data1 = RawDataSource(movement_name="Dr Who is the greatest hero ever")
        data2 = RawDataSource(movement_name="Dr Who is the dalek enemy")
        self.assertFalse(f.isValid(data1))
        self.assertTrue(f.isValid(data2))

    def test_filter_greater(self):
        f = Filter(type_conditional=FilterConditionals.GREATER, conditional="0")
        data1 = RawDataSource(value=1)
        data2 = RawDataSource(value=-1)
        data3 = RawDataSource(value=0)
        self.assertTrue(f.isValid(data1))
        self.assertFalse(f.isValid(data2))
        self.assertFalse(f.isValid(data3))

    def test_filter_greater_equal(self):
        f = Filter(type_conditional=FilterConditionals.GREATER_EQUAL, conditional="0")
        data1 = RawDataSource(value=1)
        data2 = RawDataSource(value=-1)
        data3 = RawDataSource(value=0)
        self.assertTrue(f.isValid(data1))
        self.assertFalse(f.isValid(data2))
        self.assertTrue(f.isValid(data3))

    def test_filter_lower_equal(self):
        f = Filter(type_conditional=FilterConditionals.LOWER_EQUAL, conditional="0")
        data1 = RawDataSource(value=-1)
        data2 = RawDataSource(value=1)
        data3 = RawDataSource(value=0)
        self.assertTrue(f.isValid(data1))
        self.assertFalse(f.isValid(data2))
        self.assertTrue(f.isValid(data3))

    def test_filter_lower(self):
        f = Filter(type_conditional=FilterConditionals.LOWER, conditional="0")
        data1 = RawDataSource(value=-1)
        data2 = RawDataSource(value=1)
        data3 = RawDataSource(value=0)
        self.assertTrue(f.isValid(data1))
        self.assertFalse(f.isValid(data2))
        self.assertFalse(f.isValid(data3))