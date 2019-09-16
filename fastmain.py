# https://fastapi.tiangolo.com/tutorial/path-params/
from enum import Enum
from fastapi import FastAPI

import gclib
from private_vars import galil_ip_str


# class ModelName(str, Enum):
#     alexnet = "alexnet"
#     resnet = "resnet"
#     lenet = "lenet"

app = FastAPI()



@app.on_event("startup")
async def startup_event():
    g = gclib.py()
    print('gclib version:', g.GVersion())
    g.GOpen('%s --direct -s ALL' %(galil_ip_str))
    print(g.GInfo())
    c = g.GCommand #alias the command callable

@app.get("/")
async def root():
    return {"message": "Hello World"}

# @app.get("/items/{item_id}")
# async def read_item(item_id):
#     return {"item_id": item_id}
#
# @app.get("/users/me")
# async def read_user_me():
#     return {"user_id": "the current user"}
#
# @app.get("/users/{user_id}")
# async def read_user(user_id: str):
#     return {"user_id": user_id}
#
# @app.get("/model/{model_name}")
# async def get_model(model_name: ModelName):
#     if model_name == ModelName.alexnet:
#         return {"model_name": model_name, "message": "Deep Learning FTW!"}
#     if model_name.value == "lenet":
#         return {"model_name": model_name, "message": "LeCNN all the images"}
#     return {"model_name": model_name, "message": "Have some residuals"}



@app.on_event("shutdown")
def shutdown_event():
    g.GClose() #don't forget to close connections!
    # with open("log.txt", mode="a") as log:
    #     log.write("Application shutdown")
