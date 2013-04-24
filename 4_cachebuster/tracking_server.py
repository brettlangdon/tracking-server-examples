from Cookie import SimpleCookie
from urlparse import parse_qs
from uuid import uuid4
from wsgiref.simple_server import make_server


def tracking_server(environ, respond):
    """Function used to handle all requests made to
    this tracking server
    """
    if environ['PATH_INFO'] == '/track.js':
        return track_user(environ, respond)
    elif environ['PATH_INFO'] == '/buster.js':
        return cache_buster(environ, respond)
    elif environ['PATH_INFO'] == '/favicon.ico':
        respond('204 NO CONTENT', [])
        return ['']
    else:
        return html_content(environ, respond)


def track_user(environ, respond):
    """Function used to handle the route: /track.js
    This will check to make sure that the user
    has a cookie id=<USER_ID>, if not then we will
    generate a new uuid4 id for them and set the
    cookie.
    This will also print to stdout when we generate
    a new cookie as well as what the user searched for.
    """
    cookies = SimpleCookie()
    cookies.load(environ.get('HTTP_COOKIE', ''))
    if not cookies.get('id'):
        user_id = uuid4()
        print 'User did not have id, giving: %s' % user_id
    else:
        user_id = cookies['id'].value

    query = parse_qs(environ['QUERY_STRING'])
    search = query.get('s', [''])[0]
    print 'User %s Searched For: %s' % (user_id, search)
    headers = [('Content-Type', 'application/javascript'),
               ('Set-Cookie', 'id=%s' % user_id)]
    respond('200 OK', headers)
    return ['']


def cache_buster(environ, respond):
    """Function used to handle the /buster.js route
    This will simply return our cache buster javascript
    to the user, which adds a script tag to call /track.js
    """
    headers = [('Content-Type', 'application/javascript')]
    respond('200 OK', headers)
    cb_js = """
            function getParameterByName(name){
                name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
                var regexS = "[\\?&]" + name + "=([^&#]*)";
                var regex = new RegExp(regexS);
                var results = regex.exec(window.location.search);
                if(results == null)
                    return "";
                else
                   return decodeURIComponent(results[1].replace(/\+/g, " "));
            }

            var now = new Date().getTime();
            var random = Math.random() * 99999999999;
            var search = getParameterByName('search');
            document.write('<script src="/track.js?t=' + now + '&r=' + random + '&s=' + search + '"></script>');
            """
    return [cb_js]


def html_content(environ, respond):
    """Function used to handle any route that is not /track.js
    This will return to the user a very basic html page that has
    a script that to call our /buster.js script
    """
    headers = [('Content-Type', 'text/html')]
    respond('200 OK', headers)
    return ['<html><head></head><body><h2>Welcome</h2><script src="/buster.js"></script></body></html>\n']


if __name__ == '__main__':
    try:
        httpd = make_server('', 8000, tracking_server)
        print 'Tracking Server Listening on Port 8000...'
        httpd.serve_forever()
    except KeyboardInterrupt:
        print 'Exiting...'
