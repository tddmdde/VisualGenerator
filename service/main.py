from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, FileResponse
from service.api.api_v1.api import router as api_router
from service.core.config import API_V1_STR, PROJECT_NAME
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title=PROJECT_NAME,
    docs_url=None,
    redoc_url=None
    # if not custom domain
    # openapi_prefix="/prod"
)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/resources", StaticFiles(directory="resources"), name="resources")
app.include_router(api_router, prefix=API_V1_STR)


@app.get("/ping", summary="Check that the service is operational")
def pong():
    """
    Sanity check - this will let the user know that the service is operational.

    It is also used as part of the HEALTHCHECK. Docker uses curl to check that the API service is still running, by exercising this endpoint.

    """
    return {"ping": "pong!"}


@app.get("/home", summary="Function to redirect to home")
def redirect_to_home():

    return RedirectResponse(url='/api/v1/home')


@app.get("/", summary="Function to redirect to home")
def redirect_to_home_2():

    return RedirectResponse(url='/api/v1/home')


@app.get('/favicon.ico')
async def favicon():

    return FileResponse('resources/favicon.ico')


