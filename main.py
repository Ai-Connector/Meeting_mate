from fastapi import FastAPI, WebSocket, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

app = FastAPI(title="Realtime Minutes Mock API")
# Allow CORS for frontend development
tmp_cors = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=tmp_cors, allow_methods=["*"], allow_headers=["*"])

# ----- Schemas -----
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class User(BaseModel):
    id: str
    name: str
    email: str

class Template(BaseModel):
    id: str
    name: str
    items: list[str]

class Meeting(BaseModel):
    id: str
    title: str
    datetime: str
    template_id: str | None = None

class RecordingStatus(BaseModel):
    status: str  # recording | stopped | processing

class Section(BaseModel):
    id: str
    title: str
    order: int

class Item(BaseModel):
    id: str
    section_id: str
    text: str
    order: int

class Task(BaseModel):
    id: str
    text: str
    assignee: str | None
    due_date: str | None
    status: str  # open | done

# ----- In-memory mock data -----
mock_user = User(id="u1", name="Alice", email="alice@example.com")
mock_templates = [Template(id="t1", name="Default", items=["議題", "決定事項", "アクションアイテム"])]
mock_meetings = [Meeting(id="m1", title="Mock Meeting", datetime="2025-06-22T16:00:00", template_id="t1")]
mock_sections = {
    "m1": [
        Section(id="s1", title="議題", order=1),
        Section(id="s2", title="決定事項", order=2),
    ]
}
mock_items = {
    "s1": [Item(id="i1", section_id="s1", text="ダミー項目1", order=1)],
    "s2": [Item(id="i2", section_id="s2", text="ダミー項目2", order=1)],
}
mock_tasks = {
    "m1": [Task(id="task1", text="フォローアップメール送信", assignee="Bob", due_date="2025-06-23", status="open")]
}
mock_rec_status = {"m1": "stopped"}

# ----- Dependency -----
def get_current_user():
    return mock_user

# ----- Auth Endpoints -----
@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest):
    return TokenResponse(access_token="mock-token", refresh_token="mock-refresh")

@app.post("/auth/refresh", response_model=TokenResponse)
def refresh():
    return TokenResponse(access_token="new-mock-token", refresh_token="new-mock-refresh")

@app.get("/users/me", response_model=User)
def read_user(user: User = Depends(get_current_user)):
    return user

@app.patch("/users/me", response_model=User)
def update_user(user_update: User, user: User = Depends(get_current_user)):
    return user_update

# ----- Template Endpoints -----
@app.get("/templates", response_model=list[Template])
def list_templates(user: User = Depends(get_current_user)):
    return mock_templates

@app.post("/templates", response_model=Template)
def create_template(t: Template, user: User = Depends(get_current_user)):
    mock_templates.append(t)
    return t

@app.get("/templates/{template_id}", response_model=Template)
def get_template(template_id: str, user: User = Depends(get_current_user)):
    for tpl in mock_templates:
        if tpl.id == template_id:
            return tpl
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.patch("/templates/{template_id}", response_model=Template)
def update_template(template_id: str, t: Template, user: User = Depends(get_current_user)):
    for idx, tpl in enumerate(mock_templates):
        if tpl.id == template_id:
            mock_templates[idx] = t
            return t
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.delete("/templates/{template_id}")
def delete_template(template_id: str, user: User = Depends(get_current_user)):
    for tpl in mock_templates:
        if tpl.id == template_id:
            mock_templates.remove(tpl)
            return {"detail": "deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# ----- Meeting Endpoints -----
@app.get("/meetings", response_model=list[Meeting])
def list_meetings(user: User = Depends(get_current_user)):
    return mock_meetings

@app.post("/meetings", response_model=Meeting)
def create_meeting(m: Meeting, user: User = Depends(get_current_user)):
    mock_meetings.append(m)
    return m

@app.get("/meetings/{meeting_id}", response_model=Meeting)
def get_meeting(meeting_id: str, user: User = Depends(get_current_user)):
    for meet in mock_meetings:
        if meet.id == meeting_id:
            return meet
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.patch("/meetings/{meeting_id}", response_model=Meeting)
def update_meeting(meeting_id: str, m: Meeting, user: User = Depends(get_current_user)):
    for idx, meet in enumerate(mock_meetings):
        if meet.id == meeting_id:
            mock_meetings[idx] = m
            return m
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.delete("/meetings/{meeting_id}")
def delete_meeting(meeting_id: str, user: User = Depends(get_current_user)):
    for meet in mock_meetings:
        if meet.id == meeting_id:
            mock_meetings.remove(meet)
            return {"detail": "deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# ----- Recording Endpoints -----
@app.post("/meetings/{meeting_id}/recording/start")
def start_recording(meeting_id: str, user: User = Depends(get_current_user)):
    mock_rec_status[meeting_id] = "recording"
    return {"status": "recording"}

@app.post("/meetings/{meeting_id}/recording/stop")
def stop_recording(meeting_id: str, user: User = Depends(get_current_user)):
    mock_rec_status[meeting_id] = "stopped"
    return {"status": "stopped"}

@app.get("/meetings/{meeting_id}/recording/status", response_model=RecordingStatus)
def recording_status(meeting_id: str, user: User = Depends(get_current_user)):
    return RecordingStatus(status=mock_rec_status.get(meeting_id, "stopped"))

# ----- Sections & Items Endpoints -----
@app.get("/meetings/{meeting_id}/sections", response_model=list[Section])
def list_sections(meeting_id: str, user: User = Depends(get_current_user)):
    return mock_sections.get(meeting_id, [])

@app.patch("/meetings/{meeting_id}/sections/{section_id}", response_model=Section)
def update_section(meeting_id: str, section_id: str, sec: Section, user: User = Depends(get_current_user)):
    for s in mock_sections.get(meeting_id, []):
        if s.id == section_id:
            s.order = sec.order
            s.title = sec.title
            return s
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.post("/meetings/{meeting_id}/sections/{section_id}/items", response_model=Item)
def add_item(meeting_id: str, section_id: str, it: Item, user: User = Depends(get_current_user)):
    mock_items.setdefault(section_id, []).append(it)
    return it

@app.patch("/meetings/{meeting_id}/sections/{section_id}/items/{item_id}", response_model=Item)
def update_item(meeting_id: str, section_id: str, item_id: str, it: Item, user: User = Depends(get_current_user)):
    items = mock_items.get(section_id, [])
    for existing in items:
        if existing.id == item_id:
            existing.order = it.order
            existing.text = it.text
            return existing
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.delete("/meetings/{meeting_id}/sections/{section_id}/items/{item_id}")
def delete_item(meeting_id: str, section_id: str, item_id: str, user: User = Depends(get_current_user)):
    items = mock_items.get(section_id, [])
    for existing in items:
        if existing.id == item_id:
            items.remove(existing)
            return {"detail": "deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# ----- Task Endpoints -----
@app.get("/meetings/{meeting_id}/tasks", response_model=list[Task])
def list_tasks(meeting_id: str, user: User = Depends(get_current_user)):
    return mock_tasks.get(meeting_id, [])

@app.post("/meetings/{meeting_id}/tasks", response_model=Task)
def add_task(meeting_id: str, t: Task, user: User = Depends(get_current_user)):
    mock_tasks.setdefault(meeting_id, []).append(t)
    return t

@app.patch("/meetings/{meeting_id}/tasks/{task_id}", response_model=Task)
def update_task(meeting_id: str, task_id: str, t: Task, user: User = Depends(get_current_user)):
    tasks = mock_tasks.get(meeting_id, [])
    for idx, existing in enumerate(tasks):
        if existing.id == task_id:
            tasks[idx] = t
            return t
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.delete("/meetings/{meeting_id}/tasks/{task_id}")
def delete_task(meeting_id: str, task_id: str, user: User = Depends(get_current_user)):
    tasks = mock_tasks.get(meeting_id, [])
    for existing in tasks:
        if existing.id == task_id:
            tasks.remove(existing)
            return {"detail": "deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# ----- Live WebSocket -----
@app.websocket("/meetings/{meeting_id}/live")
async def websocket_live(websocket: WebSocket, meeting_id: str):
    await websocket.accept()
    seq = 1
    try:
        while True:
            if seq == 5:
                # Section update to test reorder
                event = {"type": "section.update", "sectionId": "s2", "order": 1, "sequenceNumber": seq}
            elif seq == 7:
                # Item update to test item reorder
                event = {"type": "item.update", "sectionId": "s1", "itemId": "i1", "order": 2, "sequenceNumber": seq}
            else:
                event = {"type": "section.add", "sectionId": f"s{seq}", "title": f"セクション{seq}", "order": seq, "sequenceNumber": seq}
            await websocket.send_json(event)
            seq += 1
            await asyncio.sleep(2)
    finally:
        await websocket.close()