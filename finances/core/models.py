from django.db import models

class AbstractRawDataSource(models.Model):
    movement_name=models.CharField(max_length=255)
    date=models.DateField()
    date_value=models.DateField(null=True)
    details=models.TextField(null=True, blank=True)
    value=models.FloatField()

    def __str__(self):
        return "m:{} d:{} v:{} dd:{}$".format(self.movement_name, self.date, self.value, self.details)

    class Meta:
        abstract = True

class RawDataSource(AbstractRawDataSource):
    kind=models.CharField(max_length=255)
    description = models.TextField(default=None, null=True, blank=True)
    labels = models.ManyToManyField('Label', through='ValuesToLabels', related_name='tags')

    def __str__(self):
        parent = AbstractRawDataSource.__str__(self)
        return "k:{} {}".format(self.kind,parent)

    class Meta:
        indexes = [
            models.Index(fields=['kind', 'movement_name', 'date', 'value'])
        ]
        ordering = ('-date', '-date_value', 'movement_name')

class Label(models.Model):
    name = models.CharField(max_length=200)

class ValuesToLabels(models.Model):
    raw_data_source = models.ForeignKey(RawDataSource, on_delete=models.PROTECT)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    enable = models.IntegerField(default=1) # By default we enable it, only to disable manually. 
    automatic = models.IntegerField()

    class Meta:
        unique_together = (("raw_data_source", "label"),)
        indexes = [
            models.Index(fields=['raw_data_source'], name='rds_vtl_idx'),
            models.Index(fields=['label'], name='label_vtl_idx'),
        ]
