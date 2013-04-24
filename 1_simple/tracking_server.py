from wsgiref.simple_server import make_server


def tracking_server(environ, respond):
    """Function used to handle all requests made to
    this tracking server
    """
    if environ['PATH_INFO'] == '/track.js':
        return track_user(environ, respond)
    elif environ['PATH_INFO'] == '/favicon.ico':
        respond('204 NO CONTENT', [])
        return ['']
    else:
        return html_content(environ, respond)


def track_user(environ, respond):
    """Function used to handle the route: /track.js
    This will print environ information about the user
    to stdout and return back an empty string
    """
    headers = [('Content-Type', 'application/javascript')]
    respond('200 OK', headers)
    prefixes = ['PATH_', 'HTTP', 'REQUEST', 'QUERY']
    for key, value in environ.iteritems():
        if any(key.startswith(prefix) for prefix in prefixes):
            print '%s: %s' % (key, value)
    return ['']


def html_content(environ, respond):
    """Function used to handle any route that is not /track.js
    This will return to the user a very basic html page that has
    a script that to call /track.js
    """
    headers = [('Content-Type', 'text/html')]
    respond('200 OK', headers)
    return ['<html><head></head><body><h2>Welcome</h2><script src="/track.js"></script></body></html>\n']


if __name__ == '__main__':
    try:
        httpd = make_server('', 8000, tracking_server)
        print 'Tracking Server Listening on Port 8000...'
        httpd.serve_forever()
    except KeyboardInterrupt:
        print 'Exiting...'
