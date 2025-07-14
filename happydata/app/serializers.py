from rest_framework import serializers
from .models import Country, Indicator, WorldBankData, HappinessData, RegionalData

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['code', 'name', 'region', 'income_group']

class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        fields = ['code', 'name', 'unit', 'description', 'source', 'topic']

class WorldBankDataSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    indicator_name = serializers.CharField(source='indicator.name', read_only=True)
    
    class Meta:
        model = WorldBankData
        fields = ['country', 'country_name', 'indicator', 'indicator_name', 'year', 'value']

class HappinessDataSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    
    class Meta:
        model = HappinessData
        fields = [
            'country', 'country_name', 'year', 'happiness_score',
            'gdp_per_capita', 'social_support', 'healthy_life_expectancy',
            'freedom_to_make_life_choices', 'generosity', 'perceptions_of_corruption',
            'confidence_in_national_government', 'dystopia_residual'
        ]

class RegionalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionalData
        fields = ['region', 'year', 'avg_happiness_score', 'countries_count']

class CountryTrendsSerializer(serializers.Serializer):
    country = serializers.CharField()
    indicator = serializers.CharField()
    start_year = serializers.IntegerField()
    end_year = serializers.IntegerField()
    
    def validate(self, data):
        if data['start_year'] > data['end_year']:
            raise serializers.ValidationError("Start year must be less than or equal to end year")
        return data

class HappinessComparisonSerializer(serializers.Serializer):
    country = serializers.CharField()
    indicator = serializers.CharField()
    start_year = serializers.IntegerField()
    end_year = serializers.IntegerField()
    
    def validate(self, data):
        if data['start_year'] > data['end_year']:
            raise serializers.ValidationError("Start year must be less than or equal to end year")
        return data

class RegionalSnapshotSerializer(serializers.Serializer):
    region = serializers.CharField()
    indicator = serializers.CharField()
    year = serializers.IntegerField()

class VisualizationDataSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField(child=serializers.DictField())
    
    def to_representation(self, instance):
        return {
            'labels': instance.get('labels', []),
            'datasets': instance.get('datasets', [])
        }