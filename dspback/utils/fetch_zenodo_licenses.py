# This script will fetch the zenodo licenses controlled vocabulary and generate a JSON object that can be used to populate
# the `oneOf` subschema inside the license field of the zenodo schema file at `dspback\schemas\zenodo\schema.json`
# The schema file will be modified with the new object

# Example run `python fetch_zenodo_licenses.py`

import requests
import json

response = requests.get("https://zenodo.org/api/vocabularies/licenses?page=1&size=10000&sort=title")  # size query param must be an arbitrarily large number

vocabulary = response.json()
licenses = vocabulary["hits"]["hits"]

transformed_licenses = []
for license in licenses:
    transformed_license = { "const": license["id"], "title": license["title"]["en"]}
    transformed_licenses.append(transformed_license)

# Read the existing schema file
with open("../schemas/zenodo/schema.json", "r") as f:
    schema = json.load(f)
    # Replace the property
    schema["properties"]["license"]["oneOf"] = transformed_licenses

# Override the file
with open("../schemas/zenodo/schema.json", "w") as f:
    f.write(json.dumps(schema, indent=2))