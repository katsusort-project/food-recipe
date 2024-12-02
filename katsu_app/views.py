from django.shortcuts import render
from katsu_app.sparql_func import SPARQLQueryManager

# Create your views here.
def show_main(request):
    return render(request, 'index.html')

def get_recipe(request):
 
    endpoint = "http://localhost:7200/repositories/food-recipe"
    query_manager = SPARQLQueryManager(endpoint)
    
    # Get genre from query parameters
    recipe = request.GET.get('recipe')
    
    query = """
        PREFIX : <http://katsusort.org/data#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX v: <http://katsusort.org/vocab#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT 
        ?recipe 
        ?recipeLabel
        ?url 
        ?recordHealthLabel 
        ?voteCount 
        ?rating 
        ?cuisineLabel 
        ?courseLabel 
        ?dietLabel 
        ?dietInfo
        ?prepTimeInMinutes 
        ?cookTimeInMinutes 
        ?authorLabel 
        ?categoryLabel 
        ?ingredients 
        ?instructions 
        (GROUP_CONCAT(DISTINCT ?tagLabel; SEPARATOR="&") AS ?tags)
        WHERE {
            ?recipe rdfs:label ?recipeLabel .
            FILTER(CONTAINS(LCASE(?recipeLabel), LCASE("%s"))) .
                
            ?recipe v:url ?url .
            ?recipe v:recordHealth ?recordHealth .
            ?recordHealth rdfs:label ?recordHealthLabel .
            ?recipe v:voteCount ?voteCount .
            ?recipe v:rating ?rating .
            ?recipe v:cuisine ?cuisine .
            ?cuisine rdfs:label ?cuisineLabel .
            ?recipe v:course ?course .
            ?course rdfs:label ?courseLabel .
            ?recipe v:diet ?diet .
            ?diet rdfs:label ?dietLabel .
            ?diet rdfs:seeAlso ?dietInfo .
            ?recipe v:prepTimeInMinutes ?prepTimeInMinutes .
            ?recipe v:cookTimeInMinutes ?cookTimeInMinutes .
            ?recipe v:author ?author .
            ?author rdfs:label ?authorLabel .
            ?recipe v:category ?category .
            ?category rdfs:label ?categoryLabel .
            ?recipe v:ingredients ?ingredients .
            ?recipe v:instructions ?instructions .
            
            OPTIONAL {
                ?recipe v:tags ?tag .
                ?tag rdfs:label ?tagLabel .
            }
        }
        GROUP BY 
        ?recipe 
        ?recipeLabel
        ?url 
        ?recordHealthLabel 
        ?voteCount 
        ?rating 
        ?cuisineLabel 
        ?courseLabel 
        ?dietLabel 
        ?dietInfo
        ?prepTimeInMinutes 
        ?cookTimeInMinutes 
        ?authorLabel 
        ?categoryLabel 
        ?ingredients 
        ?instructions
    """ % recipe
    
    non_indo_recipes = query_manager.execute_query(query)
    for row in non_indo_recipes:
        row['isIndo'] = False
        row['recipe'] = row['recipe'].replace('http://katsusort.org/', '')

    query = """
        PREFIX : <http://katsusort.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX v: <http://katsusort.org/vocab#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT 
        ?recipe 
        ?recipeLabel 
        ?url 
        ?loves 
        ?totalIngredients 
        ?totalSteps 
        ?instructions
        ?ingredients
        ?cleanTitle
        WHERE {
            ?recipe rdfs:label ?recipeLabel .
            FILTER(CONTAINS(LCASE(?recipeLabel), LCASE("%s")))
            
            ?recipe v:url ?url .
            ?recipe v:loves ?loves .
            ?recipe v:category ?category .
            ?recipe v:totalIngredients ?totalIngredients .
            ?recipe v:totalSteps ?totalSteps .
            ?recipe v:instructions ?instructions .
            ?recipe v:ingredients ?ingredients .
            ?recipe v:cleanTitle ?cleanTitle .
        }
    """ % recipe

    indo_recipes = query_manager.execute_query(query)
    for row in indo_recipes:
        row['isIndo'] = True
        # row['recipe'] = row['recipe'].replace('http://katsusort.org/', '')

    results = non_indo_recipes + indo_recipes

    return render(request, 'search-result.html', {'recipes': results, 'query_input': recipe})

def get_recipe_details(request, recipe_uri):
 
    endpoint = "http://localhost:7200/repositories/food-recipe"
    query_manager = SPARQLQueryManager(endpoint)
    
    is_indo_recipe = False
    context = {}

    # cek di non indonesian recipes
    query = """
        PREFIX : <http://katsusort.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX v: <http://katsusort.org/vocab#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT 
        ?recipe 
        ?recipeLabel
        ?url 
        ?recordHealthLabel 
        ?voteCount 
        ?rating 
        ?cuisineLabel 
        ?courseLabel 
        ?dietLabel 
        ?dietInfo
        ?prepTimeInMinutes 
        ?cookTimeInMinutes 
        ?authorLabel 
        ?categoryLabel 
        ?ingredients
        ?instructions 
        (GROUP_CONCAT(DISTINCT ?tagLabel; SEPARATOR="&") AS ?tags)
        WHERE {
            FILTER(STR(?recipe) = "http://katsusort.org/%s") .

            ?recipe rdfs:label ?recipeLabel .
            ?recipe v:url ?url .
            ?recipe v:recordHealth ?recordHealth .
            ?recordHealth rdfs:label ?recordHealthLabel .
            ?recipe v:voteCount ?voteCount .
            ?recipe v:rating ?rating .
            ?recipe v:cuisine ?cuisine .
            ?cuisine rdfs:label ?cuisineLabel .
            ?recipe v:course ?course .
            ?course rdfs:label ?courseLabel .
            ?recipe v:diet ?diet .
            ?diet rdfs:label ?dietLabel .
            ?diet rdfs:seeAlso ?dietInfo .
            ?recipe v:prepTimeInMinutes ?prepTimeInMinutes .
            ?recipe v:cookTimeInMinutes ?cookTimeInMinutes .
            ?recipe v:author ?author .
            ?author rdfs:label ?authorLabel .
            ?recipe v:category ?category .
            ?category rdfs:label ?categoryLabel .
            ?recipe v:ingredients ?ingredients .
            ?recipe v:instructions ?instructions .
            
            OPTIONAL {
                ?recipe v:tags ?tag .
                ?tag rdfs:label ?tagLabel .
            }
        }
        GROUP BY 
        ?recipe 
        ?recipeLabel
        ?url 
        ?recordHealthLabel 
        ?voteCount 
        ?rating 
        ?cuisineLabel 
        ?courseLabel 
        ?dietLabel 
        ?dietInfo
        ?prepTimeInMinutes 
        ?cookTimeInMinutes 
        ?authorLabel 
        ?categoryLabel 
        ?ingredients
        ?instructions
    """ % recipe_uri

    results = query_manager.execute_query(query)

    # kalau di non indonesian recipes
    if results:
        recipe = results[0]
        context['instructions'] = recipe['instructions'].split('\r\n')
        context['ingredients'] = recipe['ingredients'].split(', ')
        context['tags'] = recipe['tags'].split('&')

    # cek di indonesian recipes
    else:
        is_indo_recipe = True
        query = """
            PREFIX : <http://katsusort.org/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX v: <http://katsusort.org/vocab#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>

            SELECT 
            ?recipe
            ?recipeLabel 
            ?url 
            ?loves 
            ?totalIngredients 
            ?totalSteps 
            ?instructions
            ?ingredients
            ?cleanTitle
            WHERE {
                ?recipe rdfs:label ?recipeLabel .
                FILTER(STR(?recipe) = "http://katsusort.org/%s") .
                
                ?recipe v:url ?url .
                ?recipe v:loves ?loves .
                ?recipe v:category ?category .
                ?recipe v:totalIngredients ?totalIngredients .
                ?recipe v:totalSteps ?totalSteps .
                ?recipe v:instructions ?instructions .
                ?recipe v:ingredients ?ingredients .
                ?recipe v:cleanTitle ?cleanTitle .
            }
        """ % recipe_uri

        results = query_manager.execute_query(query)

        recipe = results[0]
        context['instructions'] = recipe['instructions'].split('\r\n')
        context['ingredients'] = [ingredient for ingredient in  recipe['ingredients'].split(', ') if ingredient != ""]
        

    if not results:
        raise Exception("Recipe not found")

    recipe['recipe'] = recipe['recipe'].replace('http://katsusort.org/', '')    
    context['recipe'] = recipe
    context['is_indo_recipe'] = is_indo_recipe

    return render(request, 'search-result-details.html', context)