import json
import requests
import urllib.parse as urlparse

DDG_BANGS = 'https://duckduckgo.com/bang.v255.js'


def gen_bangs_json(bangs_file: str) -> None:
    """Generates a json file from the DDG bangs list

    Args:
        bangs_file: The str path to the new DDG bangs json file

    Returns:
        None

    """
    try:
        # Request full list from DDG
        r = requests.get(DDG_BANGS)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    # Convert to json
    data = json.loads(r.text)

    # Set up a json object (with better formatting) for all available bangs
    bangs_data = {}

    for row in data:
        bang_command = '!' + row['t']
        bangs_data[bang_command] = {
            'url': row['u'].replace('{{{s}}}', '{}'),
            'suggestion': bang_command + ' (' + row['s'] + ')'
        }

    json.dump(bangs_data, open(bangs_file, 'w'))
    print('* Finished creating ddg bangs json')


def resolve_bang(query: str, bangs_dict: dict) -> str:
    """Transform's a user's query to a bang search, if an operator is found

    Args:
        query: The search query
        bangs_dict: The dict of available bang operators, with corresponding
                    format string search URLs
                    (i.e. "!w": "https://en.wikipedia.org...?search={}")

    Returns:
        str: A formatted redirect for a bang search, or an empty str if there
             wasn't a match or didn't contain a bang operator

    """
    # Ensure bang search is case insensitive
    query = query.lower()
    split_query = query.split(' ')
    for operator in bangs_dict.keys():
        if operator not in split_query \
                and operator[1:] + operator[0] not in split_query:
            continue

        bang_query = query.replace(
            operator if operator in split_query else operator[1:] +
            operator[0], ''
        ).strip()

        bang_url = bangs_dict[operator]['url']

        if bang_query:
            return bang_url.replace('{}', bang_query, 1)
        else:
            parsed_url = urlparse.urlparse(bang_url)
            return f'{parsed_url.scheme}://{parsed_url.netloc}'
    return ''
