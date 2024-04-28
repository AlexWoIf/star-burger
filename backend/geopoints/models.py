from django.db import models
from django.utils import timezone
from .yandex_geo_utils import fetch_coordinates


class Geopoint(models.Model):
    address = models.CharField('Адрес', max_length=200, unique=True)
    lon = models.FloatField('Долгота', null=True, blank=True, )
    lat = models.FloatField('Широта', null=True, blank=True, )
    updated_at = models.DateTimeField('Время обновления', default=timezone.now,
                                      db_index=True, )

    class Meta:
        verbose_name = 'Геоточка'
        verbose_name_plural = 'Геоточки'

    def __str__(self):
        return f"{self.address} {self.lon}-{self.lat}"

    def save(self, *args, **kwargs):
        self.lon, self.lat = fetch_coordinates(self.address)
        super(Geopoint, self).save(*args, **kwargs)
