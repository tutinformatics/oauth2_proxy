from aiohttp import web

async def handle(request):
    response = {
        'authorization': request.headers.get('Authorization'),
        'email': request.headers.get('X-Forwarded-Email'),
        'user': request.headers.get('X-Forwarded-User'),
    }
    return web.json_response(response)

async def root(request):
    response = """
    <h1>Tere, siin ei ole kasutaja sisse loginud.</h1
    <div>Päringu läbi oauth2_proxy suunamiseks <a href="/login">logi sisse</a></div>
    
    """
    return web.Response(content_type='text/html', text=response)

app = web.Application()
app.router.add_get('/', root)
app.router.add_get('/login', handle)

web.run_app(app)