from rest_framework import serializers
from .models import Tag, Filter, ValuesToTag, Rule, RuleAndCondition, RuleOrCondition, Label

class AbstractConditionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'type_conditional', 'conditional', 'negate')

class RuleOrSerializer(AbstractConditionSerializer):
    or_group = serializers.PrimaryKeyRelatedField(queryset=RuleAndCondition.objects.all())

    class Meta:
        model = RuleOrCondition
        fields = ('or_group', ) + AbstractConditionSerializer.Meta.fields

class RuleAndSerializer(AbstractConditionSerializer):
    rule = serializers.PrimaryKeyRelatedField(queryset=Rule.objects.all())
    or_conditions = RuleOrSerializer(many=True)

    class Meta:
        model = RuleAndCondition
        fields = ('rule', 'or_conditions') + AbstractConditionSerializer.Meta.fields


class RuleSerializer(serializers.ModelSerializer):
    assign_labels = serializers.PrimaryKeyRelatedField(queryset=Label.objects.all(), many=True)
    conditions = RuleAndSerializer(many=True, read_only=True)

    class Meta:
        model = Rule
        fields = ('id', 'parent', 'assign_labels', 'conditions')


class TagSerializer(serializers.ModelSerializer):
    children = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    filters = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    class Meta:
        model = Tag
        fields = ('id', 'parent', 'children', 'name', 'filters', 'negate_conditional')


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = ('id', 'tag', 'type_conditional', 'conditional')

class ValuesToTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValuesToTag
        fields = ('raw_data_source', 'tag', 'enable', 'automatic')