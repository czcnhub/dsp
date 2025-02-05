import functools
import json
import re
from collections import defaultdict
from datetime import datetime

import pandas
from fastapi import APIRouter, Query, Request
from fastapi.responses import FileResponse
from fuzzywuzzy import fuzz

from dspback.config import get_settings
from dspback.schemas.discovery import PathEnum, TypeAhead

router = APIRouter()

SUPPORTED_REPOSITORIES = ['HydroShare', 'EarthChem Library', 'Zenodo']

def is_one_char_off(str1, str2):
    if str1 == str2:
        return True
    length_difference = abs(len(str1) - len(str2))
    if length_difference > 1:
        return False
    mismatch_count = 0
    for i in range(min(len(str1), len(str2))):
        if str1[i] != str2[i]:
            mismatch_count += 1
            if mismatch_count > 1:
                return False
            if mismatch_count == 1 and length_difference == 1:
                return False
    return True


async def aggregate_stages(request, stages, pageNumber=1, pageSize=30):
    # Insert a `$facet` stage to extract the total count. We specify pagination here too.
    stages.append({"$facet": {"docs": [{"$skip": (pageNumber - 1) * pageSize},
                                       {"$limit": pageSize}], "totalCount": [{"$count": 'count'}]}})

    aggregation = await request.app.db[get_settings().mongo_database]["discovery"].aggregate(stages).to_list(None)
    total_count = aggregation[0]["totalCount"][0]["count"] if len(aggregation[0]["totalCount"]) else None

    if total_count is not None:
        return {"docs": aggregation[0]["docs"], "meta": {"count": {"total": total_count}}}
    
    return {"docs": aggregation[0]["docs"]}


@router.get("/search")
async def search(
    request: Request,
    term: str = None,
    sortBy: str = None,
    contentType: str = None,
    providerName: str = None,
    creatorName: str = None,
    dataCoverageStart: int = None,
    dataCoverageEnd: int = None,
    creationDateStart: int = None,
    creationDateEnd: int = None,
    publishedStart: int = None,
    publishedEnd: int = None,
    clusters: list[str] | None = Query(default=None),
    pageNumber: int = 1,
    pageSize: int = 30,
):
    filters, must, search_paths, stages = await base_search(
        clusters,
        contentType,
        creatorName,
        dataCoverageEnd,
        dataCoverageStart,
        providerName,
        creationDateStart,
        creationDateEnd,
        publishedEnd,
        publishedStart,
        sortBy,
    )

    compound = {}
    if filters:
        compound = {'filter': filters}
    if must:
        compound['must'] = must

    if term:
        should = [{'autocomplete': {'query': term, 'path': key, 'fuzzy': {'maxEdits': 1}}} for key in search_paths]
        compound['should'] = should

    if compound:
        stages.insert(
            0,
            {
                '$search': {
                    'index': 'fuzzy_search',
                    'compound': compound,
                }
            },
        )

    if term:
        stages[0]['$search']['highlight'] = {'path': search_paths}
        # get only results which meet minimum relevance score threshold
        score_threshold = get_settings().search_relevance_score_threshold
        stages.append({'$match': {'score': {'$gt': score_threshold}}})

    return await aggregate_stages(request, stages, pageNumber, pageSize)


@router.get("/search/fuzzy")
async def search(
    request: Request,
    term: str,
    sortBy: str = None,
    contentType: str = None,
    providerName: str = None,
    creatorName: str = None,
    dataCoverageStart: int = None,
    dataCoverageEnd: int = None,
    creationDateStart: int = None,
    creationDateEnd: int = None,
    publishedStart: int = None,
    publishedEnd: int = None,
    clusters: list[str] | None = Query(default=None),
    pageNumber: int = 1,
    pageSize: int = 30,
):
    filters, must, search_paths, stages = await base_search(
        clusters,
        contentType,
        creatorName,
        dataCoverageEnd,
        dataCoverageStart,
        providerName,
        creationDateStart,
        creationDateEnd,
        publishedEnd,
        publishedStart,
        sortBy,
    )

    should = [{'autocomplete': {'query': term, 'path': key, 'fuzzy': {'maxEdits': 1}}} for key in search_paths]

    stages.insert(
        0,
        {
            '$search': {
                'index': 'fuzzy_search',
                'compound': {'filter': filters, 'should': should, 'must': must, 'minimumShouldMatch': 1},
                'highlight': {'path': search_paths},
            }
        },
    )

    return await aggregate_stages(request, stages, pageNumber, pageSize)



@router.get("/search/fuzzy/feedback")
async def search_fuzzy_feedback(
    request: Request,
    term: str,
    sortBy: str = None,
    contentType: str = None,
    providerName: str = None,
    creatorName: str = None,
    dataCoverageStart: int = None,
    dataCoverageEnd: int = None,
    creationDateStart: int = None,
    creationDateEnd: int = None,
    publishedStart: int = None,
    publishedEnd: int = None,
    clusters: list[str] | None = Query(default=None),
    pageNumber: int = 1,
    pageSize: int = 30,
):
    filters, must, search_paths, stages = await base_search(
        clusters,
        contentType,
        creatorName,
        dataCoverageEnd,
        dataCoverageStart,
        providerName,
        creationDateStart,
        creationDateEnd,
        publishedEnd,
        publishedStart,
        sortBy,
    )

    should = [{'autocomplete': {'query': term, 'path': key}} for key in search_paths]

    stages.insert(
        0,
        {
            '$search': {
                'index': 'fuzzy_search',
                'compound': {'filter': filters, 'should': should, 'must': must, 'minimumShouldMatch': 1},
                'highlight': {'path': search_paths},
            }
        },
    )

    results = await aggregate_stages(request, stages, pageNumber, pageSize)

    if len(results["docs"]) == 0:
        fuzzy_should = [
            {'autocomplete': {'query': term, 'path': key, 'fuzzy': {'maxEdits': 1}}} for key in search_paths
        ]
        stages[0]['$search']['compound']['should'] = fuzzy_should
        results = await aggregate_stages(request, stages, pageNumber, pageSize)
        result_hits = await determine_fuzzy_result_terms(results["docs"], term)
        return {"results": results, "fuzzy_search_terms": result_hits}

    return {"results": results, "fuzzy_search_terms": {}}


async def base_search(
    clusters,
    contentType,
    creatorName,
    dataCoverageEnd,
    dataCoverageStart,
    providerName,
    creationDateStart,
    creationDateEnd,
    publishedEnd,
    publishedStart,
    sortBy,
):
    search_paths = PathEnum.values()
    must = []
    stages = []
    filters = []
    if creationDateStart:
        filters.append({'range': {'path': 'dateCreated', 'gte': datetime(creationDateStart, 1, 1)}})
    if creationDateEnd:
        filters.append({'range': {'path': 'dateCreated', 'lt': datetime(creationDateEnd + 1, 1, 1)}})
    if publishedStart:
        filters.append(
            {
                'range': {
                    'path': 'datePublished',
                    'gte': datetime(publishedStart, 1, 1),
                },
            }
        )
    if publishedEnd:
        filters.append(
            {
                'range': {
                    'path': 'datePublished',
                    'lt': datetime(publishedEnd + 1, 1, 1),  # +1 to include all of the publishedEnd year
                },
            }
        )
    if dataCoverageStart:
        filters.append({'range': {'path': 'temporalCoverage.start', 'gte': datetime(dataCoverageStart, 1, 1)}})
    if dataCoverageEnd:
        filters.append({'range': {'path': 'temporalCoverage.end', 'lt': datetime(dataCoverageEnd + 1, 1, 1)}})
    if creatorName:
        must.append({'text': {'path': 'creator.@list.name', 'query': creatorName}})
    if providerName:
        if providerName == 'Other':
            stages.append({'$match': {'provider.name': {'$nin': SUPPORTED_REPOSITORIES}}})
        else:
            must.append({'text': {'path': 'provider.name', 'query': providerName}})
    if contentType:
        must.append({'text': {'path': '@type', 'query': contentType}})
    if clusters:
        stages.append({'$match': {'clusters': {'$all': clusters}}})
    # Sort needs to happen before pagination, ignore all other values of sortBy
    if sortBy == "name":
        stages.append({'$sort': {"name": 1}})
    if sortBy == "dateCreated":
        stages.append({'$sort': {"dateCreated": -1}})

    stages.append({'$unset': ['_id']})
    stages.append(
        {'$set': {'score': {'$meta': 'searchScore'}, 'highlights': {'$meta': 'searchHighlights'}}},
    )
    return filters, must, search_paths, stages


async def determine_fuzzy_result_terms(results, term):
    def sanitize(dirty_word):
        return re.sub(r"^\W+|\W+$", "", dirty_word)

    def highest_result_highlight(result):
        highest_highlight = {"score": 0}
        for highlight in result["highlights"]:
            if highlight["score"] > highest_highlight["score"]:
                highest_highlight = highlight
        return highest_highlight

    def determine_hit_text(highlight):
        for text in highlight["texts"]:
            if text["type"] == "hit":
                return text

    fuzzy_result_terms = defaultdict(set)
    for result in results:
        highlight = highest_result_highlight(result)
        hit_text = determine_hit_text(highlight)
        highest_score = 0
        highest_hit = None
        highest_term = None
        for term_word in term.split():
            for hit_word in hit_text["value"].split():
                sanitized_term = sanitize(term_word.lower())
                sanitized_hit = sanitize(hit_word.lower())
                score = fuzz.ratio(sanitized_term, sanitized_hit)
                if score > highest_score:
                    highest_score = score
                    highest_hit = sanitized_hit
                    highest_term = sanitize(term_word)
        if highest_hit:
            fuzzy_result_terms[highest_term].add(highest_hit)
    return fuzzy_result_terms


@router.get("/typeahead", response_model=list[TypeAhead])
async def typeahead(request: Request, term: str, pageSize: int = 30):
    search_terms = PathEnum.values()

    should = [{'autocomplete': {'query': term, 'path': key, 'fuzzy': {'maxEdits': 1}}} for key in search_terms]

    project = {term: 1 for term in search_terms}
    project["highlights"] = {'$meta': 'searchHighlights'}
    project["_id"] = 0
    project["name"] = 0
    project["description"] = 0
    project["keywords"] = 0
    project["creator.@list.name"] = 0

    stages = [
        {
            '$search': {
                'index': 'fuzzy_search',
                'compound': {'should': should},
                'highlight': {'path': search_terms},
            }
        },
        {'$project': project},
    ]
    result = await request.app.db[get_settings().mongo_database]["typeahead"].aggregate(stages).to_list(pageSize)
    return result


@router.get("/creators")
async def creator_search(request: Request, name: str, pageSize: int = 30) -> list[str]:
    stages = [
        {
            '$search': {
                'index': 'fuzzy_search',
                'autocomplete': {"query": name, "path": "creator.@list.name", 'fuzzy': {'maxEdits': 1}},
                'highlight': {'path': 'creator.@list.name'},
            }
        },
        {'$project': {"_id": 0, "creator.@list.name": 1, "highlights": {'$meta': 'searchHighlights'}}},
    ]

    results = await request.app.db[get_settings().mongo_database]["discovery"].aggregate(stages).to_list(pageSize)

    names = []
    for result in results:
        for highlight in result['highlights']:
            for text in highlight['texts']:
                if text['type'] == 'hit':
                    for creator in result['creator']['@list']:
                        if text['value'] in creator['name']:
                            names.append(creator['name'])

    return set(names)


async def build_report(request: Request):
    project = [
        {
            '$project': {
                'name': 1,
                'description': 1,
                'keywords': 1,
                'datePublished': 1,
                'dateCreated': 1,
                'provider': 1,
                'funding': 1,
                'clusters': 1,
                'url': 1,
                'legacy': 1,
                '_id': 0,
            }
        }
    ]
    json_response = await request.app.db[get_settings().mongo_database]["discovery"].aggregate(project).to_list(None)
    for row in json_response:
        row['provider'] = row['provider']['name']
        if 'funding' in row:
            funding_ids = []
            for funding in row['funding']:
                if 'identifier' in funding:
                    funding_ids.append(funding['identifier'])
            row['funding'] = funding_ids
    return json_response


@router.get("/json")
async def report_json(request: Request):
    return await build_report(request)


@router.get("/csv")
async def csv(request: Request):
    json_response = await build_report(request)
    df = pandas.read_json(json.dumps(json_response, default=str))
    filename = "discover_report.csv"
    df.to_csv(filename)
    return FileResponse(filename, filename=filename, media_type='application/octet-stream')


def compare(c1: str, c2: str):
    if c1.startswith("CZO"):
        if c2.startswith("CZO"):
            return c1 < c2
        else:
            return 1
    if c2.startswith("CZO"):
        return -1
    return c1 < c2


@router.get("/clusters")
async def clusters(request: Request) -> list[str]:
    existing_clusters = await request.app.db[get_settings().mongo_database]["discovery"].find().distinct('clusters')
    return sorted(existing_clusters, key=functools.cmp_to_key(compare))
