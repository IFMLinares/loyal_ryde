from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator

from apps.loyalRyde.forms import ZoneForm
from apps.loyalRyde.models_zones import Zone

import json
import requests
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon


class ZoneCreateView(LoginRequiredMixin, CreateView):
    model = Zone
    form_class = ZoneForm
    template_name = 'loyal_ryde_system/add_zone.html'
    success_url = reverse_lazy('core:zones_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_return'] = self.success_url
        context['title'] = 'Registrar Zona'
        return context

    def form_valid(self, form):
        try:
            geom_json = form.cleaned_data['geometry']
            geom = GEOSGeometry(geom_json)
            if geom.geom_type == 'Polygon':
                geom = MultiPolygon(geom)
            form.instance.polygon = geom
        except Exception as e:
            return HttpResponseBadRequest('Geometría inválida: %s' % e)
        messages.success(self.request, 'Zona registrada exitosamente!')
        return super().form_valid(form)


class ZoneUpdateView(LoginRequiredMixin, UpdateView):
    model = Zone
    form_class = ZoneForm
    template_name = 'loyal_ryde_system/add_zone.html'
    success_url = reverse_lazy('core:zones_list')

    def get_initial(self):
        initial = super().get_initial()
        # Proveer geometría inicial como GeoJSON
        if self.object and self.object.polygon:
            initial['geometry'] = self.object.polygon.geojson
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_return'] = self.success_url
        context['title'] = 'Editar Zona'
        return context

    def form_valid(self, form):
        try:
            geom_json = form.cleaned_data['geometry']
            geom = GEOSGeometry(geom_json)
            if geom.geom_type == 'Polygon':
                geom = MultiPolygon(geom)
            form.instance.polygon = geom
        except Exception as e:
            return HttpResponseBadRequest('Geometría inválida: %s' % e)
        messages.success(self.request, 'Zona actualizada exitosamente!')
        return super().form_valid(form)


class ZonesListView(LoginRequiredMixin, ListView):
    model = Zone
    context_object_name = 'zones'
    template_name = 'loyal_ryde_system/zones.html'


@require_GET
def search_place(request):
    q = request.GET.get('q', '').strip()
    country = request.GET.get('country', '')
    if not q:
        return JsonResponse({'results': []})

    params = {
        'q': q,
        'format': 'jsonv2',
        'polygon_geojson': 1,
        'namedetails': 1,
        'limit': 5,
    }
    if country:
        params['countrycodes'] = country

    try:
        r = requests.get('https://nominatim.openstreetmap.org/search', params=params, timeout=15,
                         headers={'User-Agent': 'LoyalRyde-ZoneImporter/1.0'})
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    results = []
    for item in data:
        name = None
        nd = item.get('namedetails') or {}
        if 'name' in nd and isinstance(nd['name'], dict):
            # pick Spanish or default
            name = nd['name'].get('es') or nd['name'].get('name')
        if not name:
            name = item.get('display_name')
        geom = item.get('geojson') or item.get('polygon_geojson')
        if not geom:
            continue
        results.append({
            'name': name[:100] if name else 'Sin nombre',
            'geojson': geom,
            'type': item.get('type'),
            'class': item.get('class'),
            'lat': item.get('lat'),
            'lon': item.get('lon'),
        })
    return JsonResponse({'results': results})
