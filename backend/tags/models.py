from django.db import models


class Tag(models.Model):
    """Модель Тэг."""

    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        verbose_name='Уникальный слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
