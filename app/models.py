from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Country(models.Model):
    code = models.CharField(max_length=3, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True, null=True)
    income_group = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Countries'

    def __str__(self):
        return f"{self.name} ({self.code})"

class Indicator(models.Model):
    code = models.CharField(max_length=50, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    topic = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class WorldBankData(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='worldbank_data')
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='worldbank_data')
    year = models.IntegerField(
        validators=[MinValueValidator(1960), MaxValueValidator(2030)]
    )
    value = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['country', 'indicator', 'year']
        ordering = ['country', 'indicator', 'year']
        indexes = [
            models.Index(fields=['country', 'indicator', 'year']),
            models.Index(fields=['year']),
        ]

    def __str__(self):
        return f"{self.country.name} - {self.indicator.name} ({self.year}): {self.value}"

class HappinessData(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='happiness_data')
    year = models.IntegerField(
        validators=[MinValueValidator(2005), MaxValueValidator(2030)]
    )
    happiness_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True, blank=True
    )
    gdp_per_capita = models.FloatField(null=True, blank=True)
    social_support = models.FloatField(null=True, blank=True)
    healthy_life_expectancy = models.FloatField(null=True, blank=True)
    freedom_to_make_life_choices = models.FloatField(null=True, blank=True)
    generosity = models.FloatField(null=True, blank=True)
    perceptions_of_corruption = models.FloatField(null=True, blank=True)
    confidence_in_national_government = models.FloatField(null=True, blank=True)
    dystopia_residual = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['country', 'year']
        ordering = ['country', 'year']
        indexes = [
            models.Index(fields=['country', 'year']),
            models.Index(fields=['year']),
            models.Index(fields=['happiness_score']),
        ]
        verbose_name_plural = 'Happiness Data'

    def __str__(self):
        return f"{self.country.name} ({self.year}): {self.happiness_score}"

class RegionalData(models.Model):
    region = models.CharField(max_length=100)
    year = models.IntegerField(
        validators=[MinValueValidator(2005), MaxValueValidator(2030)]
    )
    avg_happiness_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True, blank=True
    )
    countries_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['region', 'year']
        ordering = ['region', 'year']
        indexes = [
            models.Index(fields=['region', 'year']),
            models.Index(fields=['year']),
        ]
        verbose_name_plural = 'Regional Data'

    def __str__(self):
        return f"{self.region} ({self.year}): {self.avg_happiness_score}"

class DataSource(models.Model):
    SOURCE_CHOICES = [
        ('worldbank', 'World Bank'),
        ('happiness_report', 'World Happiness Report'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    url = models.URLField(blank=True, null=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    update_frequency = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.source_type})"

class DataUpdateLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='update_logs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    records_processed = models.IntegerField(default=0)
    records_created = models.IntegerField(default=0)
    records_updated = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.data_source.name} - {self.status} ({self.created_at})"