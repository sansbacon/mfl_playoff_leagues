from mfl_playoff_leagues import MFL


def run(request):
    """Responds to any HTTP request.
    
    Args:
        request (flask.Request): HTTP request object.

    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.

    """
    # get the query string parsed as a dict
    request_json = request.get_json(silent=True)
    args = request.args
    m = MFL(year=args['year'], league=args['league'])

    if request.args and 'live_scoring' in request.args:
        return m.live_scoring_html()
    
    if request.args and 'league' in request.args:
        return m.league_html()

    return {}
