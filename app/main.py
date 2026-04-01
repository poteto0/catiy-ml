from app.api import health
from app.api.v1 import yolo as v1yolo
from app.factory.app import create_app
from app.infra.lifespan.ml import set_ml_model

app = create_app(
    lifespan=set_ml_model,
)

app.include_router(health.router, tags=["Health"], prefix="/health")
app.include_router(v1yolo.router, tags=["v1", "yolo"], prefix="/v1/yolo")
