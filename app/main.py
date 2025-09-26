from fastapi import FastAPI
from app.db import Base, engine
from app.routes.cats import router as cats_router
from app.routes.missions import router as missions_router


Base.metadata.create_all(engine)


app = FastAPI(title="Spy Cat Agency")
app.include_router(cats_router)
app.include_router(missions_router)
