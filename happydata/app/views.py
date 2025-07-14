from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
import requests
import json
from datetime import datetime
from .models import Country, Indicator, WorldBankData, HappinessData, RegionalData
from .serializers import (
    CountrySerializer, IndicatorSerializer, WorldBankDataSerializer,
    HappinessDataSerializer, RegionalDataSerializer, VisualizationDataSerializer
)

def index(request):
    return render(request, 'index.html')

class CountryListView(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class IndicatorListView(generics.ListAPIView):
    queryset = Indicator.objects.all()
    serializer_class = IndicatorSerializer

class WorldBankDataListView(generics.ListAPIView):
    queryset = WorldBankData.objects.all()
    serializer_class = WorldBankDataSerializer
    
    def get_queryset(self):
        queryset = WorldBankData.objects.all()
        country = self.request.query_params.get('country')
        indicator = self.request.query_params.get('indicator')
        year = self.request.query_params.get('year')
        start_year = self.request.query_params.get('start_year')
        end_year = self.request.query_params.get('end_year')
        
        if country:
            queryset = queryset.filter(country__code=country)
        if indicator:
            queryset = queryset.filter(indicator__code=indicator)
        if year:
            queryset = queryset.filter(year=year)
        if start_year and end_year:
            queryset = queryset.filter(year__range=[start_year, end_year])
        
        return queryset.order_by('year')

class HappinessDataListView(generics.ListAPIView):
    queryset = HappinessData.objects.all()
    serializer_class = HappinessDataSerializer
    
    def get_queryset(self):
        queryset = HappinessData.objects.all()
        country = self.request.query_params.get('country')
        year = self.request.query_params.get('year')
        start_year = self.request.query_params.get('start_year')
        end_year = self.request.query_params.get('end_year')
        
        if country:
            queryset = queryset.filter(country__code=country)
        if year:
            queryset = queryset.filter(year=year)
        if start_year and end_year:
            queryset = queryset.filter(year__range=[start_year, end_year])
        
        return queryset.order_by('year')

class RegionalDataListView(generics.ListAPIView):
    queryset = RegionalData.objects.all()
    serializer_class = RegionalDataSerializer
    
    def get_queryset(self):
        queryset = RegionalData.objects.all()
        region = self.request.query_params.get('region')
        year = self.request.query_params.get('year')
        
        if region:
            queryset = queryset.filter(region=region)
        if year:
            queryset = queryset.filter(year=year)
        
        return queryset.order_by('year')

class CountryTrendsVisualizationView(APIView):
    def get(self, request):
        country = request.query_params.get('country')
        indicator = request.query_params.get('indicator')
        start_year = int(request.query_params.get('start_year', 2000))
        end_year = int(request.query_params.get('end_year', 2023))
        
        if not country or not indicator:
            return Response(
                {'error': 'Country and indicator parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get data from database
            data = WorldBankData.objects.filter(
                country__code=country,
                indicator__code=indicator,
                year__range=[start_year, end_year]
            ).order_by('year')
            
            # If no data in database, try to fetch from API
            if not data.exists():
                self.fetch_worldbank_data(country, indicator, start_year, end_year)
                data = WorldBankData.objects.filter(
                    country__code=country,
                    indicator__code=indicator,
                    year__range=[start_year, end_year]
                ).order_by('year')
            
            # Format data for Chart.js
            years = []
            values = []
            
            for item in data:
                if item.value is not None:
                    years.append(str(item.year))
                    values.append(item.value)
            
            # Get country and indicator names
            country_obj = Country.objects.filter(code=country).first()
            indicator_obj = Indicator.objects.filter(code=indicator).first()
            
            country_name = country_obj.name if country_obj else country
            indicator_name = indicator_obj.name if indicator_obj else indicator
            
            chart_data = {
                'labels': years,
                'datasets': [{
                    'label': f'{indicator_name} - {country_name}',
                    'data': values,
                    'borderColor': 'rgb(37, 99, 235)',
                    'backgroundColor': 'rgba(37, 99, 235, 0.1)',
                    'tension': 0.4,
                    'fill': True
                }]
            }
            
            return Response(chart_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class HappinessComparisonVisualizationView(APIView):
    def get(self, request):
        country = request.query_params.get('country')
        indicator = request.query_params.get('indicator')
        start_year = int(request.query_params.get('start_year', 2000))
        end_year = int(request.query_params.get('end_year', 2023))
        
        if not country or not indicator:
            return Response(
                {'error': 'Country and indicator parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get World Bank data
            wb_data = WorldBankData.objects.filter(
                country__code=country,
                indicator__code=indicator,
                year__range=[start_year, end_year]
            ).order_by('year')
            
            # Get Happiness data
            happiness_data = HappinessData.objects.filter(
                country__code=country,
                year__range=[start_year, end_year]
            ).order_by('year')
            
            # Create aligned data
            years = []
            wb_values = []
            happiness_values = []
            
            # Create dictionaries for easier lookup
            wb_dict = {item.year: item.value for item in wb_data if item.value is not None}
            happiness_dict = {item.year: item.happiness_score for item in happiness_data if item.happiness_score is not None}
            
            # Find common years
            common_years = set(wb_dict.keys()) & set(happiness_dict.keys())
            
            for year in sorted(common_years):
                years.append(str(year))
                wb_values.append(wb_dict[year])
                happiness_values.append(happiness_dict[year])
            
            # Get names
            country_obj = Country.objects.filter(code=country).first()
            indicator_obj = Indicator.objects.filter(code=indicator).first()
            
            country_name = country_obj.name if country_obj else country
            indicator_name = indicator_obj.name if indicator_obj else indicator
            
            chart_data = {
                'labels': years,
                'datasets': [
                    {
                        'label': f'Happiness Score - {country_name}',
                        'data': happiness_values,
                        'borderColor': 'rgb(16, 185, 129)',
                        'backgroundColor': 'rgba(16, 185, 129, 0.1)',
                        'tension': 0.4,
                        'yAxisID': 'y1'
                    },
                    {
                        'label': f'{indicator_name} - {country_name}',
                        'data': wb_values,
                        'borderColor': 'rgb(37, 99, 235)',
                        'backgroundColor': 'rgba(37, 99, 235, 0.1)',
                        'tension': 0.4,
                        'yAxisID': 'y'
                    }
                ]
            }
            
            return Response(chart_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RegionalHappinessVisualizationView(APIView):
    def get(self, request):
        year = int(request.query_params.get('year', 2023))
        
        try:
            # Get regional happiness data
            regional_data = RegionalData.objects.filter(year=year).order_by('region')
            
            # If no regional data, calculate from individual country data
            if not regional_data.exists():
                happiness_data = HappinessData.objects.filter(year=year).exclude(happiness_score__isnull=True)
                
                # Group by region and calculate averages
                regions = {}
                for item in happiness_data:
                    region = item.country.region
                    if region:
                        if region not in regions:
                            regions[region] = []
                        regions[region].append(item.happiness_score)
                
                # Calculate averages
                labels = []
                values = []
                colors = [
                    'rgba(37, 99, 235, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(236, 72, 153, 0.8)',
                    'rgba(34, 197, 94, 0.8)'
                ]
                
                for i, (region, scores) in enumerate(regions.items()):
                    labels.append(region)
                    values.append(round(sum(scores) / len(scores), 2))
                
                chart_data = {
                    'labels': labels,
                    'datasets': [{
                        'label': f'Average Happiness Score ({year})',
                        'data': values,
                        'backgroundColor': colors[:len(labels)],
                        'borderWidth': 1
                    }]
                }
            else:
                # Use pre-calculated regional data
                labels = [item.region for item in regional_data]
                values = [item.avg_happiness_score for item in regional_data]
                
                chart_data = {
                    'labels': labels,
                    'datasets': [{
                        'label': f'Average Happiness Score ({year})',
                        'data': values,
                        'backgroundColor': [
                            'rgba(37, 99, 235, 0.8)',
                            'rgba(16, 185, 129, 0.8)',
                            'rgba(245, 158, 11, 0.8)',
                            'rgba(239, 68, 68, 0.8)',
                            'rgba(139, 92, 246, 0.8)',
                            'rgba(236, 72, 153, 0.8)',
                            'rgba(34, 197, 94, 0.8)'
                        ][:len(labels)],
                        'borderWidth': 1
                    }]
                }
            
            return Response(chart_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RegionalSnapshotVisualizationView(APIView):
    def get(self, request):
        region = request.query_params.get('region')
        indicator = request.query_params.get('indicator')
        year = int(request.query_params.get('year', 2023))
        
        if not region or not indicator:
            return Response(
                {'error': 'Region and indicator parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get countries in the region
            countries = Country.objects.filter(region=region)
            
            # Get data for these countries
            data = WorldBankData.objects.filter(
                country__in=countries,
                indicator__code=indicator,
                year=year
            ).exclude(value__isnull=True).order_by('-value')
            
            # Format data
            labels = [item.country.name for item in data]
            values = [item.value for item in data]
            
            # Get indicator name
            indicator_obj = Indicator.objects.filter(code=indicator).first()
            indicator_name = indicator_obj.name if indicator_obj else indicator
            
            chart_data = {
                'labels': labels,
                'datasets': [{
                    'label': f'{indicator_name} ({year})',
                    'data': values,
                    'backgroundColor': 'rgba(37, 99, 235, 0.8)',
                    'borderColor': 'rgb(37, 99, 235)',
                    'borderWidth': 1
                }]
            }
            
            return Response(chart_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class IndiaDashboardVisualizationView(APIView):
    def get(self, request):
        start_year = int(request.query_params.get('start_year', 2010))
        end_year = int(request.query_params.get('end_year', 2023))
        
        try:
            # Get happiness data for India
            happiness_data = HappinessData.objects.filter(
                country__code='IN',
                year__range=[start_year, end_year]
            ).order_by('year')
            
            # Get key indicators for India
            key_indicators = [
                'NY.GDP.PCAP.CD',  # GDP per capita
                'SI.POV.DDAY',     # Poverty rate
                'SL.UEM.TOTL.ZS',  # Unemployment rate
                'SE.PRM.NENR'      # Primary education enrollment
            ]
            
            years = [str(item.year) for item in happiness_data]
            happiness_values = [item.happiness_score for item in happiness_data if item.happiness_score is not None]
            
            datasets = [{
                'label': 'Happiness Score',
                'data': happiness_values,
                'borderColor': 'rgb(16, 185, 129)',
                'backgroundColor': 'rgba(16, 185, 129, 0.1)',
                'tension': 0.4,
                'yAxisID': 'y1'
            }]
            
            # Add key indicators
            colors = ['rgb(37, 99, 235)', 'rgb(245, 158, 11)', 'rgb(239, 68, 68)', 'rgb(139, 92, 246)']
            
            for i, indicator_code in enumerate(key_indicators):
                indicator_data = WorldBankData.objects.filter(
                    country__code='IN',
                    indicator__code=indicator_code,
                    year__range=[start_year, end_year]
                ).order_by('year')
                
                if indicator_data.exists():
                    indicator_obj = Indicator.objects.filter(code=indicator_code).first()
                    indicator_name = indicator_obj.name if indicator_obj else indicator_code
                    
                    # Align data with happiness data years
                    indicator_dict = {item.year: item.value for item in indicator_data if item.value is not None}
                    aligned_values = []
                    
                    for happiness_item in happiness_data:
                        if happiness_item.year in indicator_dict:
                            aligned_values.append(indicator_dict[happiness_item.year])
                        else:
                            aligned_values.append(None)
                    
                    datasets.append({
                        'label': indicator_name,
                        'data': aligned_values,
                        'borderColor': colors[i % len(colors)],
                        'backgroundColor': colors[i % len(colors)].replace('rgb', 'rgba').replace(')', ', 0.1)'),
                        'tension': 0.4,
                        'yAxisID': 'y'
                    })
            
            chart_data = {
                'labels': years,
                'datasets': datasets
            }
            
            return Response(chart_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def fetch_worldbank_data(self, country, indicator, start_year, end_year):
        """Fetch data from World Bank API"""
        try:
            url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
            params = {
                'format': 'json',
                'date': f'{start_year}:{end_year}',
                'per_page': 100
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    # Create or update country
                    country_obj, created = Country.objects.get_or_create(
                        code=country,
                        defaults={'name': country}
                    )
                    
                    # Create or update indicator
                    indicator_obj, created = Indicator.objects.get_or_create(
                        code=indicator,
                        defaults={'name': indicator}
                    )
                    
                    # Save data
                    for item in data[1]:
                        if item['value'] is not None:
                            WorldBankData.objects.update_or_create(
                                country=country_obj,
                                indicator=indicator_obj,
                                year=item['date'],
                                defaults={'value': item['value']}
                            )
                            
        except Exception as e:
            print(f"Error fetching World Bank data: {e}")

@api_view(['GET'])
def get_regions(request):
    """Get list of available regions"""
    regions = Country.objects.values_list('region', flat=True).distinct().exclude(region__isnull=True)
    return Response(list(regions))

@api_view(['GET'])
def get_countries_by_region(request, region):
    """Get countries in a specific region"""
    countries = Country.objects.filter(region=region)
    serializer = CountrySerializer(countries, many=True)
    return Response(serializer.data)