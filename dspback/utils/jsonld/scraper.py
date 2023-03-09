import html
import json

import aiohttp
from bs4 import BeautifulSoup

from dspback.pydantic_schemas import RepositoryType
from dspback.utils.jsonld.formatter import format_fields
from dspback.utils.jsonld.pydantic_schemas import JSONLD


def scrape_jsonld(resource_data, script_match):
    resource_soup = BeautifulSoup(resource_data, "html.parser")
    resource_json_ld = resource_soup.find("script", script_match)
    resource_json_ld = json.loads(html.unescape(resource_json_ld.text))
    resource_json_ld = format_fields(resource_json_ld)

    return resource_json_ld


async def fetch_landing_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None
            return await response.text()


async def retrieve_discovery_jsonld(identifier, repository_type, url):
    resource_data = await fetch_landing_page(url)
    if not resource_data:
        return None
    script_match = (
        {"id": "schemaorg"} if repository_type == RepositoryType.HYDROSHARE else {"type": "application/ld+json"}
    )
    resource_json_ld = scrape_jsonld(resource_data, script_match=script_match)
    # only Zenodo does not have provider in the json ld
    if repository_type == RepositoryType.ZENODO:
        resource_json_ld['provider'] = {'name': 'Zenodo'}
    return JSONLD(**resource_json_ld, repository_identifier=identifier)
