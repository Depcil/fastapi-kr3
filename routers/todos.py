# Задание 8.2
from fastapi import APIRouter, HTTPException
from schemas import TodoCreate, TodoUpdate
from database import get_db_connection

router = APIRouter(prefix="/todos", tags=["8.2 Todo CRUD"])


@router.post("", status_code=201)
def create_todo(todo: TodoCreate):
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, 0)",
        (todo.title, todo.description)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "title": todo.title, "description": todo.description, "completed": False}


@router.get("/{todo_id}")
def get_todo(todo_id: int):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"id": row["id"], "title": row["title"], "description": row["description"], "completed": bool(row["completed"])}


@router.put("/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    conn.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (todo.title, todo.description, int(todo.completed), todo_id)
    )
    conn.commit()
    conn.close()
    return {"id": todo_id, "title": todo.title, "description": todo.description, "completed": todo.completed}


@router.delete("/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    return {"message": f"Todo {todo_id} deleted successfully"}
