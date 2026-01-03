from fastapi import APIRouter, HTTPException
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Models.TestProjects import TestProjects
from psycopg import AsyncConnection, connect
from psycopg.rows import dict_row
import asyncio

router = APIRouter(prefix="/api/test", tags=["test"])

async def get_db_connection():
    connection_string = os.getenv("DATABASE_URL")
    if not connection_string:
        raise ValueError("DATABASE_URL environment variable not set")
    try:
        # Use async connection for FastAPI async endpoints
        return await AsyncConnection.connect(connection_string, row_factory=dict_row)
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

@router.get("/")
async def get_all():
    conn = None
    try:
        conn = await get_db_connection()
        async with conn.cursor() as cur:
            await cur.execute('SELECT "Id", "Name" FROM "TestProjects" ORDER BY "Id"')
            results = await cur.fetchall()
            await conn.commit()
            return results
    except Exception as e:
        if conn:
            await conn.rollback()
        print(f"Error in get_all: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            await conn.close()

@router.get("/{id}")
async def get(id: int):
    conn = None
    try:
        conn = await get_db_connection()
        async with conn.cursor() as cur:
            await cur.execute('SELECT "Id", "Name" FROM "TestProjects" WHERE "Id" = %s', (id,))
            result = await cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Project not found")
            await conn.commit()
            return result
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            await conn.rollback()
        print(f"Error in get: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            await conn.close()

@router.post("/")
async def create(project: TestProjects):
    conn = None
    try:
        conn = await get_db_connection()
        async with conn.cursor() as cur:
            await cur.execute('INSERT INTO "TestProjects" ("Name") VALUES (%s) RETURNING "Id"', (project.name,))
            result = await cur.fetchone()
            project_id = result["Id"]
            await conn.commit()
            project.id = project_id
            return project
    except Exception as e:
        if conn:
            await conn.rollback()
        print(f"Error in create: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            await conn.close()

@router.put("/{id}")
async def update(id: int, project: TestProjects):
    conn = None
    try:
        conn = await get_db_connection()
        async with conn.cursor() as cur:
            await cur.execute('UPDATE "TestProjects" SET "Name" = %s WHERE "Id" = %s', (project.name, id))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Project not found")
            await conn.commit()
            return {{"message": "Updated successfully"}}
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            await conn.rollback()
        print(f"Error in update: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            await conn.close()

@router.delete("/{id}")
async def delete(id: int):
    conn = None
    try:
        conn = await get_db_connection()
        async with conn.cursor() as cur:
            await cur.execute('DELETE FROM "TestProjects" WHERE "Id" = %s', (id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Project not found")
            await conn.commit()
            return {{"message": "Deleted successfully"}}
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            await conn.rollback()
        print(f"Error in delete: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            await conn.close()
