from django.db import models
from django.utils.translation import gettext_lazy as _


class Entrance(models.Model):
    id = models.SmallIntegerField(_("ID"), primary_key=True)
    name = models.CharField(_("Nombre"), max_length=50)


class File(models.Model):
    file = models.FileField(_("Archivo"), upload_to="files/", max_length=100)


class Report(models.Model):
    DIRECTION_TYPE = [
        ("entran", "Entrada"),
        ("salen", "Salida"),
    ]

    entrance = models.ForeignKey(
        Entrance,
        verbose_name=_("Entrada"),
        on_delete=models.CASCADE,
        related_name="reports",
    )
    total = models.IntegerField(_("Total"), blank=True, null=True)
    date = models.DateField(_("Fecha"))
    file = models.ForeignKey(
        File,
        verbose_name=_("Archivo"),
        on_delete=models.CASCADE,
        related_name="reports",
        blank=True,
        null=True,
    )
    direction = models.CharField(_("Dirección"), max_length=6, choices=DIRECTION_TYPE)

    def __str__(self):
        return f"{self.entrance.name} ({self.date})"


class ReportDetail(models.Model):
    report = models.ForeignKey(
        Report,
        verbose_name=_("Reporte"),
        on_delete=models.CASCADE,
        related_name="reportdetails",
    )
    time = models.TimeField(_("Hora"))
    quantity = models.PositiveIntegerField(_("Cantidad"))
