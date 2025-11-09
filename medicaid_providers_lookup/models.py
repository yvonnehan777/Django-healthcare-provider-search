from django.db import models

class Provider(models.Model):
    provider_id = models.AutoField(primary_key=True)
    npi = models.CharField(max_length=20, unique=False)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    city_name = models.CharField(max_length=255, null=True, blank=True, default='unknown')
    state_name = models.CharField(max_length=50, null=True, blank=True, default='unknown')
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country_code = models.CharField(max_length=5, null=True, blank=True, default='US')
    telephone_number = models.CharField(max_length=20, null=True, blank=True)
    telephone_extension = models.CharField(max_length=10, null=True, blank=True)
    fax_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"Provider {self.npi}"


class Taxonomy(models.Model):
    taxonomy_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    classification = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.classification}"


class ProviderTaxonomy(models.Model):
    id = models.AutoField(primary_key=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    taxonomy = models.ForeignKey(Taxonomy, on_delete=models.CASCADE)
    primary_switch = models.CharField(max_length=1, null=True, blank=True, default='N')

    class Meta:
        unique_together = ('provider', 'taxonomy', 'primary_switch')

    def __str__(self):
        return f"{self.provider.npi} -> {self.taxonomy.code}"
