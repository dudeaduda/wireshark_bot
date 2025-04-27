import aiosqlite
import json
from pathlib import Path
from typing import Tuple, List, Optional

DATABASE_PATH = Path(__file__).parent / "user_progress.db"

async def init_db() -> None:
    """Инициализация базы данных"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id INTEGER PRIMARY KEY,
                current_module INTEGER DEFAULT 1,
                current_submodule INTEGER DEFAULT 1,
                current_page INTEGER DEFAULT 1,
                completed_modules TEXT DEFAULT '[]',
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_last_active 
            ON user_progress (last_active)
        """)
        await db.commit()

async def get_user_progress(user_id: int) -> Tuple[int, int, int, List[int]]:
    """Получение текущего прогресса пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM user_progress WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            await db.execute(
                "INSERT INTO user_progress (user_id) VALUES (?)",
                (user_id,)
            )
            await db.commit()
            return (1, 1, 1, [])
        
        completed = json.loads(row['completed_modules']) if row['completed_modules'] else []
        return (
            row['current_module'],
            row['current_submodule'],
            row['current_page'],
            completed
        )

async def update_user_progress(
    user_id: int,
    module: Optional[int] = None,
    submodule: Optional[int] = None,
    page: Optional[int] = None,
    mark_completed: bool = False
) -> None:
    """Обновление прогресса пользователя с исправленной логикой завершения модулей"""
    updates = []
    params = []
    
    if module is not None:
        updates.append("current_module = ?")
        params.append(module)
    if submodule is not None:
        updates.append("current_submodule = ?")
        params.append(submodule)
    if page is not None:
        updates.append("current_page = ?")
        params.append(page)
    
    if mark_completed:
        # Получаем текущий список завершенных модулей
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                "SELECT completed_modules FROM user_progress WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            completed = json.loads(row[0]) if row and row[0] else []
            
            # Добавляем модуль, если его еще нет в списке
            if module not in completed:
                completed.append(module)
                updates.append("completed_modules = ?")
                params.append(json.dumps(completed))
    
    updates.append("last_active = CURRENT_TIMESTAMP")
    params.append(user_id)
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        query = f"""
            UPDATE user_progress 
            SET {', '.join(updates)}
            WHERE user_id = ?
        """
        await db.execute(query, params)
        await db.commit()

async def reset_user_progress(user_id: int) -> None:
    """Сброс прогресса пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE user_progress 
            SET current_module = 1,
                current_submodule = 1,
                current_page = 1,
                completed_modules = '[]'
            WHERE user_id = ?
        """, (user_id,))
        await db.commit()

async def get_active_users(days: int = 30) -> List[int]:
    """Получение списка активных пользователей"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id FROM user_progress
            WHERE last_active >= date('now', ?)
        """, (f"-{days} days",))
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

async def get_user_progress(user_id: int) -> dict:
    """Получает полный прогресс пользователя с обработкой NULL значений"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT current_module, current_submodule, current_page, completed_modules, last_active "
            "FROM user_progress WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            return {
                'current_module': row[0] if row[0] is not None else 1,
                'current_submodule': row[1] if row[1] is not None else 1,
                'current_page': row[2] if row[2] is not None else 1,
                'completed_modules': json.loads(row[3]) if row[3] else [],
                'last_active': row[4] if row[4] is not None else None
            }
        else:
            # Создаем запись, если пользователя нет в базе
            await db.execute(
                "INSERT INTO user_progress (user_id) VALUES (?)",
                (user_id,)
            )
            await db.commit()
            return {
                'current_module': 1,
                'current_submodule': 1,
                'current_page': 1,
                'completed_modules': [],
                'last_active': None
            }

async def backup_database(backup_path: str) -> None:
    """Создание резервной копии базы данных"""
    async with aiosqlite.connect(DATABASE_PATH) as source:
        async with aiosqlite.connect(backup_path) as target:
            await source.backup(target)