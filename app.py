from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from routes import router


app = FastAPI()


# include routes
app.include_router(router)

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")
