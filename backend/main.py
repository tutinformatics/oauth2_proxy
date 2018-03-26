from aiohttp import web

async def handle(request):
    response = """
        <h1>Tere, %s!</h1>
        <div>Sinu mailiaadress on %s.</div>
    """ % (request.headers.get('X-Forwarded-User'), request.headers.get('X-Forwarded-Email'))
    return web.Response(content_type='text/html', text=response)

async def root(request):
    response = """
    <h1>Siin ei ole kasutaja sisse loginud.</h1
    <div>Päringu läbi oauth2_proxy suunamiseks <a href="/login">logi sisse</a></div>
    
    """
    return web.Response(content_type='text/html', text=response)

app = web.Application()
app.router.add_get('/', root)
app.router.add_get('/login', handle)

web.run_app(app)
