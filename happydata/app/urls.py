from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Frontend
    path('', views.index, name='index'),
    
    # API endpoints
    path('api/countries/', views.CountryListView.as_view(), name='api-countries'),
    path('api/indicators/', views.IndicatorListView.as_view(), name='api-indicators'),
    path('api/worldbank-data/', views.WorldBankDataListView.as_view(), name='api-worldbank-data'),
    path('api/happiness-data/', views.HappinessDataListView.as_view(), name='api-happiness-data'),
    path('api/regional-data/', views.RegionalDataListView.as_view(), name='api-regional-data'),
    
    # Visualization endpoints
    path('api/visualizations/country-trends/', views.CountryTrendsVisualizationView.as_view(), name='api-country-trends'),
    path('api/visualizations/happiness-comparison/', views.HappinessComparisonVisualizationView.as_view(), name='api-happiness-comparison'),
    path('api/visualizations/regional-happiness/', views.RegionalHappinessVisualizationView.as_view(), name='api-regional-happiness'),
    path('api/visualizations/regional-snapshot/', views.RegionalSnapshotVisualizationView.as_view(), name='api-regional-snapshot'),
    path('api/visualizations/india-dashboard/', views.IndiaDashboardVisualizationView.as_view(), name='api-india-dashboard'),
    
    # Utility endpoints
    path('api/regions/', views.get_regions, name='api-regions'),
    path('api/regions/<str:region>/countries/', views.get_countries_by_region, name='api-countries-by-region'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)