from functools import reduce

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from finances.core.models import RawDataSource, Label, ValueToLabel

# Create your models here.
class FilterConditionals:
    CONTAINS = "c"
    PREFIX = "p"
    SUFFIX = "s"
    GREATER = "g"
    GREATER_EQUAL = "G"
    LOWER_EQUAL = "L"
    LOWER = "l"
    REGULAR_EXPRESION = "r"

    @staticmethod
    def contains(search, data):
        return search in data.movement_name

    @staticmethod
    def prefix(search, data):
        check = data.movement_name[:len(search)]
        return check == search

    @staticmethod
    def suffix(search, data):
        check = data.movement_name[-len(search):]
        return check == search

    @staticmethod
    def greater(value, data):
        check = float(value)
        return data.value > check

    @staticmethod
    def greater_equal(value, data):
        check = float(value)
        return data.value >= check

    @staticmethod
    def lower_equal(value, data):
        check = float(value)
        return data.value <= check

    @staticmethod
    def lower(value, data):
        check = float(value)
        return data.value < check


FILTER_FUNCTIONS={
    FilterConditionals.CONTAINS: FilterConditionals.contains,
    FilterConditionals.PREFIX: FilterConditionals.prefix,
    FilterConditionals.SUFFIX: FilterConditionals.suffix,
    FilterConditionals.GREATER: FilterConditionals.greater,
    FilterConditionals.GREATER_EQUAL: FilterConditionals.greater_equal,
    FilterConditionals.LOWER_EQUAL: FilterConditionals.lower_equal,
    FilterConditionals.LOWER: FilterConditionals.lower,
}

FILTER_CONDITIONALS = (
    (FilterConditionals.CONTAINS, "Contains"),
    (FilterConditionals.PREFIX, "Prefix"),
    (FilterConditionals.SUFFIX, "Sufix"),
    (FilterConditionals.REGULAR_EXPRESION, "Regular expresion"),
    (FilterConditionals.GREATER, "Greater than"),
    (FilterConditionals.GREATER_EQUAL, "Greater or equal than"),
    (FilterConditionals.LOWER_EQUAL, "Lower or equal than"),
    (FilterConditionals.LOWER, "Lower than")
)


class Rule(models.Model):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.PROTECT)
    assign_labels = models.ManyToManyField(Label)
    labels_setted = models.ManyToManyField(ValueToLabel)


    def check_conditions(self, value):
        is_false = False
        list_conds = self.conditions.all()
        index = 0
        while index < len(list_conds) and not is_false:
            is_false = not list_conds[index].check_conditions(value)
            index += 1
        return not is_false


    def check_with_parent(self, value):
        if self.check_conditions(value):
            if self.parent:
                return self.parent.check_with_parent(value)
            else:
                return True
        else:
            return False


class AbstractCondition(models.Model):
    type_conditional = models.CharField(max_length=1, choices=FILTER_CONDITIONALS)
    conditional = models.CharField(max_length=200)
    negate = models.BooleanField()


    __cached_func = None


    def isValid(self, data):
        if not self.__cached_func:
            self.__cached_func = FILTER_FUNCTIONS.get(self.type_conditional, lambda e, y: False)
        result = self.__cached_func(self.conditional, data)
        return result != self.negate


    def __str__(self):
        return "{}:{}".format(self.type_conditional, self.conditional)

    class Meta:
        abstract = True


class RuleAndCondition(AbstractCondition):
    rule = models.ForeignKey(Rule, on_delete=models.PROTECT, related_name="conditions")

    def check_conditions(self, value):
        is_true = self.isValid(value)
        list_ors = self.or_conditions.all()
        index = 0
        while index < len(list_ors) and not is_true:
            is_true = list_ors[index].isValid(value)
            index += 1
        return is_true


class RuleOrCondition(AbstractCondition):
    or_group = models.ForeignKey(RuleAndCondition, on_delete=models.PROTECT, related_name='or_conditions')


class Tag(models.Model):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    values = models.ManyToManyField(RawDataSource, through='ValuesToTag', related_name='tags')
    negate_conditional = models.BooleanField(default=False)

    def apply_filters_source(self, rds):
        filter_list = self.filters.all()
        if len(filter_list):
            if not self.negate_conditional:
                reducer = lambda ac, v: ac or v
                initial = False
            else:
                reducer = lambda ac, v: ac and not v
                initial = True
            
            l=map(lambda e: e.isValid(rds), filter_list)
            isFilter = reduce(reducer, l, initial)
            if isFilter:
                if ValuesToTag.objects.filter(raw_data_source=rds, tag=self).count()==0:
                    ValuesToTag.objects.create(tag=self, raw_data_source=rds, automatic=1)
                else:
                    isFilter = False

            return isFilter

    def apply_filters(self):
        deleted_relations = ValuesToTag.objects.filter(tag=self, automatic=1).delete()
        count = 0

        if not self.parent:
            source_list = RawDataSource.objects.all()
        else:
            source_list = self.parent.values.all()
        
        for rds in source_list:
            if self.apply_filters_source(rds):
                count += 1

        return {
            'deleted': deleted_relations[0],
            'inserted': count
        }

    def __str__(self):
        return self.name

class ValuesToTag(models.Model):
    raw_data_source = models.ForeignKey(RawDataSource, on_delete=models.PROTECT)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    enable = models.IntegerField(default=1) # By default we enable it, only to disable manually. 
    automatic = models.IntegerField()

    class Meta:
        unique_together = (("raw_data_source", "tag"),)
        indexes = [
            models.Index(fields=['raw_data_source'], name='rds_idx'),
            models.Index(fields=['tag'], name='tag_idx'),
        ]


class Filter(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="filters")
    type_conditional = models.CharField(max_length=1, choices=FILTER_CONDITIONALS)
    conditional = models.CharField(max_length=200)

    __cached_func = None

    def isValid(self, data):
        if not self.__cached_func:
            self.__cached_func = FILTER_FUNCTIONS.get(self.type_conditional, lambda e, y: False)
        result = self.__cached_func(self.conditional, data)
        return result


    def __str__(self):
        return "{} > {}:{}".format(self.tag, self.type_conditional, self.conditional)