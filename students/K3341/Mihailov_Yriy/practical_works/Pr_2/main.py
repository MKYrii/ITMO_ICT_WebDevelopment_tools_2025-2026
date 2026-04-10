from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlmodel import select
from typing import List, Dict, Any
from typing_extensions import TypedDict

from db import init_db, get_session
from models import (
    Warrior, WarriorDefault, WarriorWithProfession, WarriorWithSkills,
    Profession, Skill, RaceType, ProfessionDefault, SkillDefault
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Выполняется при запуске
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/warriors_list", response_model=List[Warrior])
def warriors_list(session=Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).all()

@app.get("/warrior/{warrior_id}", response_model=WarriorWithProfession)
def warriors_get(warrior_id: int, session=Depends(get_session)) -> Warrior:
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior

class WarriorCreateResponse(TypedDict):
    status: int
    data: Warrior

@app.post("/warrior", response_model=WarriorCreateResponse)
def warriors_create(warrior: WarriorDefault, session=Depends(get_session)) -> WarriorCreateResponse:
    new_warrior = Warrior.model_validate(warrior)  # преобразуем в модель таблицы
    session.add(new_warrior)
    session.commit()
    session.refresh(new_warrior)
    return {"status": 200, "data": new_warrior}

@app.patch("/warrior/{warrior_id}", response_model=WarriorDefault)
def warrior_update(warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)) -> WarriorDefault:
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")

    warrior_data = warrior.model_dump(exclude_unset=True)
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior

@app.delete("/warrior/{warrior_id}")
def warrior_delete(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}


#  Профессии
@app.get("/professions", response_model=List[Profession])
def get_professions(session=Depends(get_session)):
    return session.exec(select(Profession)).all()

@app.get("/profession/{prof_id}", response_model=Profession)
def get_profession(prof_id: int, session=Depends(get_session)):
    prof = session.get(Profession, prof_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profession not found")
    return prof

@app.post("/profession", response_model=Profession)
def create_profession(prof: ProfessionDefault, session=Depends(get_session)):
    new_prof = Profession.model_validate(prof)
    session.add(new_prof)
    session.commit()
    session.refresh(new_prof)
    return new_prof

@app.patch("/profession/{prof_id}", response_model=Profession)
def update_profession(prof_id: int, prof: ProfessionDefault, session=Depends(get_session)):
    db_prof = session.get(Profession, prof_id)
    if not db_prof:
        raise HTTPException(status_code=404, detail="Profession not found")
    prof_data = prof.model_dump(exclude_unset=True)
    for key, value in prof_data.items():
        setattr(db_prof, key, value)
    session.add(db_prof)
    session.commit()
    session.refresh(db_prof)
    return db_prof

@app.delete("/profession/{prof_id}")
def delete_profession(prof_id: int, session=Depends(get_session)):
    prof = session.get(Profession, prof_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profession not found")
    session.delete(prof)
    session.commit()
    return {"ok": True}


#  Умения
@app.get("/skills", response_model=List[Skill])
def get_skills(session=Depends(get_session)):
    return session.exec(select(Skill)).all()

@app.get("/skill/{skill_id}", response_model=Skill)
def get_skill(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@app.post("/skill", response_model=Skill)
def create_skill(skill: SkillDefault, session=Depends(get_session)):
    new_skill = Skill.model_validate(skill)
    session.add(new_skill)
    session.commit()
    session.refresh(new_skill)
    return new_skill

@app.patch("/skill/{skill_id}", response_model=Skill)
def update_skill(skill_id: int, skill: SkillDefault, session=Depends(get_session)):
    db_skill = session.get(Skill, skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    skill_data = skill.model_dump(exclude_unset=True)
    for key, value in skill_data.items():
        setattr(db_skill, key, value)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill

@app.delete("/skill/{skill_id}")
def delete_skill(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.delete(skill)
    session.commit()
    return {"ok": True}


# Привязка умений к воину
@app.post("/warrior/{warrior_id}/skills/{skill_id}")
def add_skill_to_warrior(warrior_id: int, skill_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    skill = session.get(Skill, skill_id)
    if not warrior or not skill:
        raise HTTPException(status_code=404, detail="Warrior or Skill not found")

    if skill not in warrior.skills:
        warrior.skills.append(skill)
        session.add(warrior)
        session.commit()
    return {"message": f"Skill {skill_id} added to warrior {warrior_id}"}

@app.delete("/warrior/{warrior_id}/skills/{skill_id}")
def remove_skill_from_warrior(warrior_id: int, skill_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    skill = session.get(Skill, skill_id)
    if not warrior or not skill:
        raise HTTPException(status_code=404, detail="Warrior or Skill not found")
    if skill in warrior.skills:
        warrior.skills.remove(skill)
        session.add(warrior)
        session.commit()
    return {"message": f"Skill {skill_id} removed from warrior {warrior_id}"}


# Вложенное отображение умений при запросе воина
@app.get("/warrior/{warrior_id}/with_skills", response_model=WarriorWithSkills)
def warrior_get_with_skills(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior