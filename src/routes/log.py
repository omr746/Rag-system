from fastapi import FastAPI,APIRouter,Depends,UploadFile,status,Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from routes.schemes.log import MachineLogRequest
from models.ProjectModel import ProjectModel
from models.MachineLogModel import MachineLogModel
from models.db_schemes import MachineLog
from typing import List
from models import ResponseSignal
import logging

logger=logging.getLogger('uvicorn.error')
log_router=APIRouter(
    prefix="/api/v1/log",
    tags=["api_v1","log"]
)

@log_router.post("/machine-logs/bulk-insert/{project_id}")
async def insert_many_machine_logs(request:Request,project_id:str,logs: List[MachineLogRequest]):
    project_model=await ProjectModel.create_instance(
         db_client= request.app.db_client
    )
    project=await project_model.get_project_or_create_one(
         project_id=project_id)
    machine_log_model=await MachineLogModel.create_instance(
         db_client= request.app.db_client
    )
    log_records=[
            MachineLog(
                stream_id=log.stream_id,
                ts=log.ts,
                machine_project_id=project.id,
                data=log.data
                
            )
            for log in (logs)
        ]
    no_records=await  machine_log_model.insert_many_logs(logs=log_records)
    return JSONResponse(
         content={
              "signal":ResponseSignal.INSERTED_LOGS_SUCCESS.value,
              "inserted_logs":no_records,
             
         }
    )

@log_router.get("/get_logs/{project_id}")
async def get_logs_by_machine_project_id(
    request: Request,
    project_id: str
):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )

    machine_log_model = await MachineLogModel.create_instance(
        db_client=request.app.db_client
    )

    page_no = 1
    log_records = []

    while True:
        page_logs = await machine_log_model.get_machine_project_logs(
            project_id=project.id,
            page_no=page_no
        )

        if not page_logs:
            break

        log_records.extend(page_logs)
        page_no += 1

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "signal": ResponseSignal.LOGS_RETRIVED.value,
            "logs_record": log_records
        })
    )