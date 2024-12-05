from django.shortcuts import render
from katsu_app.sparql_func import SPARQLQueryManager
from django.http import JsonResponse
from difflib import SequenceMatcher
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def show_main(request):
    return render(request, 'index.html')

def get_recipe(request):
    endpoint = "http://localhost:7200/repositories/food-recipe"
    query_manager = SPARQLQueryManager(endpoint)
    recipe = request.GET.get('recipe', '').strip()
    order = request.GET.get('order', '')
    page = request.GET.get('page', 1)
    recipes_per_page = 20  # Number of recipes per page

    query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX v: <http://katsusort.org/vocab#>

        SELECT ?recipe ?recipeLabel ?authorLabel
        WHERE {
            ?recipe rdfs:label ?recipeLabel ;
                    v:url ?url ;
                    
            OPTIONAL {
                ?recipe v:author ?author .
                ?author rdfs:label ?authorLabel .
            }
            FILTER(CONTAINS(LCASE(?recipeLabel), LCASE("%s"))) .
        }
        %s
    """ % (recipe, f"ORDER BY {order}(?recipeLabel)" if order != "RELEVANCE" else "")

    results = query_manager.execute_query(query)
    for row in results:
        row['recipe'] = row['recipe'].replace('http://katsusort.org/', '')

    if order == 'RELEVANCE':
        results = rank_results(results, recipe)

    # Create Paginator
    paginator = Paginator(results, recipes_per_page)
    try:
        paginated_results = paginator.page(page)
    except PageNotAnInteger:
        paginated_results = paginator.page(1)
    except EmptyPage:
        paginated_results = paginator.page(paginator.num_pages)

    # Prepare context for template
    response_data = {
        'recipes': list(paginated_results),
        'total_pages': paginator.num_pages,
        'current_page': paginated_results.number,
        'total_recipes': len(results),
        'query_input': recipe
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(response_data)
    else:
        return render(request, 'search-result.html', response_data)

def rank_results(results, query):
    def similarity(a, b):
        return SequenceMatcher(None, a, b).ratio()
    
    ranked_results = []
    for row in results:
        recipe_label = row['recipeLabel'].lower()
        query_lower = query.lower()
        score = similarity(recipe_label, query_lower) * 100
        row['relevanceScore'] = round(score, 2)
        ranked_results.append(row)

    ranked_results.sort(key=lambda x: x['relevanceScore'], reverse=True)
    return ranked_results

def get_recipe_details(request, recipe_uri):
    endpoint = "http://localhost:7200/repositories/food-recipe"
    query_manager = SPARQLQueryManager(endpoint)
    context = {}

    # Query for non-indonesian recipes
    query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX v: <http://katsusort.org/vocab#>

        SELECT 
        ?recipe ?recipeLabel ?url ?recordHealthLabel ?voteCount ?rating 
        ?cuisineLabel ?courseLabel ?dietLabel ?dietInfo ?description
        ?prepTimeInMinutes ?cookTimeInMinutes ?authorLabel ?categoryLabel 
        ?ingredients ?instructions 
        (GROUP_CONCAT(DISTINCT ?tagLabel; SEPARATOR="&") AS ?tags)
        WHERE {
            FILTER(STR(?recipe) = "http://katsusort.org/%s") .
            ?recipe rdfs:label ?recipeLabel ;
                   v:url ?url .
            OPTIONAL { 
                ?recipe v:recordHealth ?recordHealth .
                ?recordHealth rdfs:label ?recordHealthLabel 
            }
            OPTIONAL { ?recipe v:voteCount ?voteCount }
            OPTIONAL { ?recipe v:rating ?rating }
            OPTIONAL { 
                ?recipe v:cuisine ?cuisine .
                ?cuisine rdfs:label ?cuisineLabel 
            }
            OPTIONAL { 
                ?recipe v:course ?course .
                ?course rdfs:label ?courseLabel 
            }
            OPTIONAL { 
                ?recipe v:diet ?diet .
                ?diet rdfs:label ?dietLabel .
                ?diet rdfs:seeAlso ?dietInfo 
            }
            OPTIONAL { ?recipe v:description ?description }
            OPTIONAL { ?recipe v:prepTimeInMinutes ?prepTimeInMinutes }
            OPTIONAL { ?recipe v:cookTimeInMinutes ?cookTimeInMinutes }
            OPTIONAL { 
                ?recipe v:author ?author .
                ?author rdfs:label ?authorLabel 
            }
            OPTIONAL { 
                ?recipe v:category ?category .
                ?category rdfs:label ?categoryLabel 
            }
            OPTIONAL { ?recipe v:ingredients ?ingredients }
            OPTIONAL { ?recipe v:instructions ?instructions }
            OPTIONAL { 
                ?recipe v:tags ?tag .
                ?tag rdfs:label ?tagLabel 
            }
        }
        GROUP BY ?recipe ?recipeLabel ?url ?recordHealthLabel ?voteCount 
        ?rating ?cuisineLabel ?courseLabel ?dietLabel ?dietInfo ?description
        ?prepTimeInMinutes ?cookTimeInMinutes ?authorLabel ?categoryLabel 
        ?ingredients ?instructions
    """ % recipe_uri

    results = query_manager.execute_query(query)

    if results:
        recipe = results[0]
        context['instructions'] = recipe.get('instructions', '').split('\r\n')
        context['ingredients'] = recipe.get('ingredients', '').split(', ')
        context['tags'] = recipe.get('tags', '').split('&')
        if recipe.get('rating'):
            recipe['rating'] = round(float(recipe['rating']), 2)
        context['is_indo_recipe'] = False

    else:
        # Query for indonesian recipes
        query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX v: <http://katsusort.org/vocab#>

            SELECT ?recipe ?recipeLabel ?url ?loves ?totalIngredients 
            ?totalSteps ?instructions ?ingredients ?cleanTitle
            WHERE {
                FILTER(STR(?recipe) = "http://katsusort.org/%s") .
                ?recipe rdfs:label ?recipeLabel ;
                       v:url ?url .
                OPTIONAL { ?recipe v:loves ?loves }
                OPTIONAL { ?recipe v:totalIngredients ?totalIngredients }
                OPTIONAL { ?recipe v:totalSteps ?totalSteps }
                OPTIONAL { ?recipe v:instructions ?instructions }
                OPTIONAL { ?recipe v:ingredients ?ingredients }
                OPTIONAL { ?recipe v:cleanTitle ?cleanTitle }
            }
        """ % recipe_uri

        results = query_manager.execute_query(query)
        if not results:
            raise Exception("Recipe not found")

        recipe = results[0]
        context['instructions'] = recipe.get('instructions', '').split('\r\n')
        context['ingredients'] = [i for i in recipe.get('ingredients', '').split(', ') if i]
        context['is_indo_recipe'] = True

    recipe['recipe'] = recipe['recipe'].replace('http://katsusort.org/', '')    
    context['recipe'] = recipe
    
    return render(request, 'search-result-details.html', context)