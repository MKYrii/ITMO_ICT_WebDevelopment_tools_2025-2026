from fastapi import FastAPI
from typing import List, Dict, Any
from typing_extensions import TypedDict
from models import Warrior, Profession, RaceType

app = FastAPI()

temp_bd: List[Dict[str, Any]] = [
    {
        "id": 1,
        "race": "director",
        "name": "Мартынов Дмитрий",
        "level": 12,
        "profession": {
            "id": 1,
            "title": "Влиятельный человек",
            "description": "Эксперт по всем вопросам"
        },
        "skills": [
            {"id": 1, "name": "Купле-продажа компрессоров", "description": ""},
            {"id": 2, "name": "Оценка имущества", "description": ""}
        ]
    },
    {
        "id": 2,
        "race": "worker",
        "name": "Андрей Косякин",
        "level": 12,
        "profession": {
            "id": 1,
            "title": "Дельфист-гребец",
            "description": "Уважаемый сотрудник"
        },
        "skills": []
    }
]

professions_bd: List[Dict[str, Any]] = [
    {"id": 1, "title": "Влиятельный человек", "description": "Эксперт по всем вопросам"},
    {"id": 2, "title": "Дельфист-гребец", "description": "Уважаемый сотрудник"}
]


@app.get("/")
def root():
    return {"message": "Hello, Yriy!"}

@app.get("/warriors_list")
def warriors_list() -> List[Warrior]:
    return temp_bd


@app.get("/warrior/{warrior_id}")
def warriors_get(warrior_id: int) -> List[Warrior]:
    return [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]


@app.post("/warrior")
def warriors_create(warrior: Warrior) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior_to_append = warrior.model_dump()
    temp_bd.append(warrior_to_append)
    return {"status": 200, "data": warrior}


@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}

@app.put("/warrior{warrior_id}", response_model=List[Warrior])
def warrior_update(warrior_id: int, warrior: Warrior) -> List[Warrior]:
    for war in temp_bd:
        if war.get("id") == warrior_id:
            warrior_to_append = warrior.model_dump()
            temp_bd.remove(war)
            temp_bd.append(warrior_to_append)
    return temp_bd

@app.get("/professions", response_model=List[Profession])
def get_professions() -> List[Profession]:
    return professions_bd

@app.get("/profession/{prof_id}", response_model=Profession)
def get_profession(prof_id: int):
    for p in professions_bd:
        if p["id"] == prof_id:
            return p
    return {"error": "Profession not found"}

@app.post("/profession", response_model=Profession)
def create_profession(profession: Profession):
    for p in professions_bd:
        if p["id"] == profession.id:
            return {"error": "ID already exists"}
    professions_bd.append(profession.model_dump())
    return profession

@app.put("/profession/{prof_id}", response_model=Profession)
def update_profession(prof_id: int, profession: Profession):
    for i, p in enumerate(professions_bd):
        if p["id"] == prof_id:
            professions_bd[i] = profession.model_dump()
            return profession
    return {"error": "Profession not found"}

@app.delete("/profession/{prof_id}")
def delete_profession(prof_id: int):
    for i, p in enumerate(professions_bd):
        if p["id"] == prof_id:
            professions_bd.pop(i)
            return {"status": "deleted"}
    return {"error": "Profession not found"}