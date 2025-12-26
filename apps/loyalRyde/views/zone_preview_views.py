import json
import urllib.parse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required


def _search_nominatim(q: str, country: str, limit: int = 10):
    params = {
        "q": q,
        "format": "json",
        "polygon_geojson": 1,
        "addressdetails": 1,
        "namedetails": 1,
        "countrycodes": country,
        "limit": limit,
    }
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
    req = Request(url, headers={"User-Agent": "LoyalRyde/NominatimPreview"})
    with urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw)


@require_GET
@login_required
def zone_preview(request):
    q = request.GET.get("q")
    country = request.GET.get("country", "ve")
    index = int(request.GET.get("index", 0))
    if not q:
        return render(request, "loyal_ryde_system/zones/preview.html", {"error": "Falta parámetro q"})

    try:
        results = _search_nominatim(q, country)
    except Exception as e:
        return render(request, "loyal_ryde_system/zones/preview.html", {"error": str(e)})

    if not results:
        return render(request, "loyal_ryde_system/zones/preview.html", {"error": "Sin resultados"})

    if index < 0 or index >= len(results):
        return render(request, "loyal_ryde_system/zones/preview.html", {"error": f"Índice {index} fuera de rango"})

    item = results[index]
    namedetails = item.get("namedetails") or {}
    name = namedetails.get("name") or item.get("display_name") or q
    geojson = item.get("geojson")

    return render(
        request,
        "loyal_ryde_system/zones/preview.html",
        {
            "q": q,
            "country": country,
            "index": index,
            "name": name,
            "feature": json.dumps({"type": "Feature", "properties": {"name": name}, "geometry": geojson}),
        },
    )


@require_GET
@login_required
def zone_preview_geojson(request):
    q = request.GET.get("q")
    country = request.GET.get("country", "ve")
    index = int(request.GET.get("index", 0))
    try:
        results = _search_nominatim(q, country)
        item = results[index]
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    namedetails = item.get("namedetails") or {}
    name = namedetails.get("name") or item.get("display_name") or q
    geojson = item.get("geojson")
    return JsonResponse({"type": "Feature", "properties": {"name": name}, "geometry": geojson})
