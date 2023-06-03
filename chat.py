from fastapi import FastAPI, Request,APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import json 
import numpy as np
from fastapi import FastAPI, Request, Form
import random
import time
time.clock = time.time
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
import openai
import pickle
import os 
import tiktoken
from fastapi.staticfiles import StaticFiles
from langchain.callbacks import get_openai_callback
import atexit
import asyncio
import time
import csv
import requests
import threading
from BotUser import User 
app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="")
########
import re
import os
script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")
app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")



def save_data(user_object):
    filename = 'user_info.csv'  # Set the filename to use
    fieldnames = ['name', 'Total Token', 'Cost', 'Total Chat Duration']  # Define the fieldnames for the CSV

    total_tokens = 0
    total_cost = 0

    for bill in user_object.bills:
        total_tokens += bill.total_tokens
        total_cost += bill.total_cost

    # Create a dictionary for the last result
    last_result = {
        'name': user_object.full_name,
        'Total Token': total_tokens,
        'Cost': total_cost,
        'Total Chat Duration': user_object.total_chat_duration
    }

    # Read the existing data from the file
    existing_data = []
    try:
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            existing_data = list(reader)
    except FileNotFoundError:
        pass

    # Append the last result to the existing data
    existing_data.append(last_result)

    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()  # Write the header row

        # Write the updated data to the file
        writer.writerows(existing_data)

    print("Data saved to CSV file: {}".format(filename))


class static:
  users={}
  

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    user_object=User()
    current_user='user'+str(random.randint(0,9999))
    static.users[current_user]=user_object
    app.include_router(router, prefix="/{}".format(current_user))
    print(current_user)
    return templates.TemplateResponse("index.html", {"request": request,'user':current_user})

@router.get("/getStart", response_class=HTMLResponse)
def start(request: Request):
    
    return templates.TemplateResponse("start.html", {"request": request})

response_timer = None

@app.get("/getChatBotResponse")
def get_bot_response(msg: str,request: Request):
    current_user=str(request.headers.get("referer")).split('/')[3]
    result = static.users[current_user].conversation(msg)

    global response_timer
    if response_timer is not None:
        response_timer.cancel()  # إلغاء المؤقت السابق إذا كان قائمًا

    # إنشاء مؤقت جديد لاستدعاء save_data بعد مرور 20 ثانية
    response_timer = threading.Timer(20, save_data(static.users[current_user]))
    response_timer.start()

    return result      

if __name__ == "__main__":
    uvicorn.run("chat:app")