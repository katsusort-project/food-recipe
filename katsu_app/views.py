from django.shortcuts import render
from katsu_app.sparql_func import SPARQLQueryManager

# Create your views here.
def show_main(request):
    return render(request, 'index.html')

def get_recipe(request):
    endpoint = "http://localhost:7200/repositories/food-recipe"
    query_manager = SPARQLQueryManager(endpoint)
    recipe = request.GET.get('recipe').strip()
    
    query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX v: <http://katsusort.org/vocab#>

        SELECT ?recipe ?recipeLabel
        WHERE {
            ?recipe rdfs:label ?recipeLabel ;
                    v:url ?url .
            FILTER(CONTAINS(LCASE(?recipeLabel), LCASE("%s"))) .
        }
    """ % recipe

    results = query_manager.execute_query(query)
    for row in results:
        row['recipe'] = row['recipe'].replace('http://katsusort.org/', '')

    return render(request, 'search-result.html', {'recipes': results, 'query_input': recipe})

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