from django.db import models

class Movie(models.Model):
    m_id = models.IntegerField(primary_key=True)  # 기존 m_id 값을 유지
    m_korname = models.CharField(max_length=255)
    m_engname = models.CharField(max_length=255, blank=True, null=True)
    m_year = models.IntegerField(blank=True, null=True)
    m_type = models.CharField(max_length=50, blank=True, null=True)
    m_status = models.CharField(max_length=50, blank=True, null=True)
    m_company = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'movie'

    def __str__(self):
        return self.m_korname

class MovieGenre(models.Model):
    mg_id = models.IntegerField(primary_key=True)
    m_id = models.IntegerField()
    genre_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'movie_genre'
        unique_together = ('m_id', 'genre_name')

class MovieCountry(models.Model):
    mc_id = models.IntegerField(primary_key=True)
    m_id = models.IntegerField()
    country_name = models.CharField(max_length=50,blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'movie_country'
        unique_together = ('m_id', 'country_name')

class Director(models.Model):
    d_id = models.IntegerField(primary_key=True)  # 기존 d_id 값을 유지
    d_name = models.CharField(max_length=100, blank=True, null=True, unique=True)

    class Meta:
        managed = False
        db_table = 'director'


class Filming(models.Model):
    f_id = models.IntegerField(primary_key=True)
    m_id = models.IntegerField()
    d_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'filming'
        unique_together = ('m_id', 'd_id')

