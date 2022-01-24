import json
from urllib.parse import parse_qs
import pytest

from playhouse.shortcuts import model_to_dict

from cocktaildb.recipe_scraper import Diffords
from cocktaildb.recipes_orm import db, RecipeListingScrape

@pytest.fixture
def proxies():
    return {'http': 'http://127.0.0.1:8888', 'https': 'http://127.0.0.1:8888'}


def test_get_with_proxy(proxies, tprint):
    d = Diffords()
    r = d.recipe_listing(proxies=proxies)
    assert r


def test_recipe_listing_orm(tprint):
    db.init(':memory', pragmas={'foreign_keys': 1})
    db.create_tables([RecipeListingScrape])
    offset = 0
    d = Diffords()
    r = d.recipe_listing(offset=offset)
    url, qs = r.url.split('?')
    
    rls = {
        'listing_base_url': url,
        'listing_query_params': json.dumps(parse_qs(qs)),
        'listing_html': r.text
    }

    assert rls is not None
    RecipeListingScrape.insert_many([rls]).execute()  
    query = RecipeListingScrape.select()
    assert query is not None
    tprint([model_to_dict(item)['listing_base_url'] for item in query])


def test_recipe_links(tprint):
    d = Diffords()
    listing = d.recipe_listing()
    links = d.recipe_links(listing)
    assert links
    tprint(links)
