import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import numpy as np

from .utils import (
get_or_create_vector,
similarity_score,
generate_plot
)


def home(request):
    return render(request, 'home.html')

@csrf_exempt
def analyze_names(request):
    data = json.loads(request.body)
    names = data.get("names", [])
    
    coordinates = {}
    for n in names:
        x, y = get_or_create_vector(n)
        r = float(np.sqrt(x**2 + y**2))
        theta = float(np.degrees(np.arctan2(y, x))) # UI likes degrees
        coordinates[n] = {"r": r, "theta": theta}

    similarities = []
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            n1, n2 = names[i], names[j]
            score = similarity_score(n1, n2, get_or_create_vector(n1), get_or_create_vector(n2))
            similarities.append({"pair": [n1, n2], "score": score})

    # Pass the helper functions into the plotter
    plot_path = generate_plot(names, get_or_create_vector, similarity_score)

    return JsonResponse({
        "coordinates": coordinates,
        "similarities": similarities,
        "plot": plot_path
    })