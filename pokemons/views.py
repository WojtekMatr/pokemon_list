import requests
from django.shortcuts import render
from operator import itemgetter



def pokemon_list(request):
    response = requests.get('https://pokeapi.co/api/v2/pokemon?limit=500')
    data = response.json()
    pokemons = data['results']

    detailed_pokemons = []
    for pokemon in pokemons:
        pokemon_data = requests.get(pokemon['url']).json()
        detailed_pokemons.append({
            'id': pokemon_data['id'],
            'name': pokemon['name'],
            'types': [t['type']['name'] for t in pokemon_data['types']],
            'weight': pokemon_data['weight'],
            'height': pokemon_data['height'],
        })
    sort_by = request.GET.get('sort_by', 'id')
    sort_order = request.GET.get('sort_order', 'asc')

    key_functions = {
        'id': itemgetter('id'),
        'name': itemgetter('name'),
        'types': lambda x: x['types'][0] if x['types'] else '',
        'weight': itemgetter('weight'),
        'height': itemgetter('height'),
    }

    # Sort the list of Pokémon
    if sort_by in key_functions:
        detailed_pokemons = sorted(detailed_pokemons, key=key_functions[sort_by], reverse=(sort_order == 'desc'))

    # Pass the sorting parameters to the template
    context = {
        'pokemons': detailed_pokemons,
        'sort_by': sort_by,
        'sort_order': sort_order,
    }

    return render(request, 'pokemons/pokemon_list.html', {'pokemons': detailed_pokemons})

def pokemon_detail(request, name):
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{name}')
    data = response.json()
    species_response = requests.get(data['species']['url'])
    species_data = species_response.json()
    location_response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{data["id"]}/encounters')
    locations = location_response.json()

    sprite_front = data['sprites']['front_default']
    sprite_back = data['sprites']['back_default']
    map_image = "https://upload.wikimedia.org/wikipedia/commons/7/77/Pixel_art_grass_image.png" 

    pokemon_info = {
        'id': data['id'],
        'name': name,
        'sprite_front': sprite_front,
        'sprite_back': sprite_back,
        'map_image': map_image,
        'types': [t['type']['name'] for t in data['types']],
        'weight': data['weight'],
        'height': data['height'],
        'stats': {stat['stat']['name']: stat['base_stat'] for stat in data['stats']},
        'location_areas': [location['location_area']['name'] for location in locations],
        'color': species_data['color']['name'],
        'forms': [form['name'] for form in data['forms']],
        'habitat': species_data['habitat']['name'] if species_data['habitat'] else 'Unknown',
        'shape': species_data['shape']['name'],
        'species': species_data['name']
    }
    return render(request, 'pokemons/pokemon_detail.html', pokemon_info)