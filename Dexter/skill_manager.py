"""
Dexter Simple v2 - Skills Management System

Handles code generation, testing, and permanent skill storage.
"""

import json
import sqlite3
import time
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class Skill:
    id: int
    name: str
    description: str
    code: str
    category: str
    created_at: float
    usage_count: int
    success_rate: float
    tags: List[str]

class SkillManager:
    """Manages skill generation, testing, and storage"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize storage
        self.skills_dir = Path(config['skills']['storage_path'])
        self.skills_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Categories
        self.categories = config['skills'].get('categories', {})
    
    def _init_database(self):
        """Initialize skills database"""
        db_path = self.config['skills']['database_path']
        
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                code TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                created_at REAL NOT NULL,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                tags TEXT
            )
        """)
        self.db.commit()
        
        self.logger.info("Skills database initialized")
    
    def generate_skill_code(self, request: str, llm_provider) -> Dict[str, Any]:
        """Generate Python code for a skill request"""
        
        # Enhanced prompt for code generation
        messages = [
            {
                "role": "system",
                "content": """You are an expert Python programmer. Generate clean, working Python code based on user requests.

The code should be complete and runnable."""
            },
            {
                "role": "user",
                "content": f"Create a Python script for: {request}\n\nMake it practical and robust."
            }
        ]
        
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            response = loop.run_until_complete(llm_provider.call(messages))
            
            # Extract code from response
            code = self._extract_code_from_response(response)
            
            if code:
                # Generate skill metadata
                skill_name = self._generate_skill_name(request)
                category = self._determine_category(request)
                
                return {
                    'name': skill_name,
                    'description': request,
                    'code': code,
                    'category': category,
                    'raw_response': response
                }
            else:
                return {
                    'error': 'Could not extract valid Python code from response',
                    'raw_response': response
                }
                
        except Exception as e:
            self.logger.error(f"Error generating skill code: {e}")
            return {'error': str(e)}
    
    def _extract_code_from_response(self, response: str) -> Optional[str]:
        """Extract Python code from LLM response"""
        
        # Look for code blocks
        if '```python' in response:
            start = response.find('```python') + len('```python')
            end = response.find('```', start)
            if end != -1:
                return response[start:end].strip()
        
        elif '```' in response:
            start = response.find('```') + len('```')
            end = response.find('```', start)
            if end != -1:
                return response[start:end].strip()
        
        # If no code blocks, look for lines starting with def, import, class
        lines = response.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            if line.strip().startswith(('def ', 'import ', 'from ', 'class ', '#')):
                in_code = True
            if in_code:
                code_lines.append(line)
        
        if code_lines:
            return '\n'.join(code_lines).strip()
        
        return None
    
    def _generate_skill_name(self, request: str) -> str:
        """Generate a skill name from the request"""
        
        # Simple name generation
        words = request.lower().split()
        # Remove common words
        stop_words = {'a', 'an', 'the', 'to', 'for', 'of', 'and', 'or', 'but', 'in', 'on', 'at', 'by'}
        words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Take first few meaningful words
        name_words = words[:3]
        name = '_'.join(name_words).replace(' ', '_')
        
        # Add timestamp to avoid conflicts
        timestamp = str(int(time.time()))[-4:]
        return f"{name}_{timestamp}"
    
    def _determine_category(self, request: str) -> str:
        """Determine skill category from request"""
        
        request_lower = request.lower()
        
        # Check against configured categories
        for category, info in self.categories.items():
            if any(keyword in request_lower for keyword in ['file', 'directory', 'folder']) and category == 'fileops':
                return 'fileops'
            elif any(keyword in request_lower for keyword in ['android', 'app', 'mobile']) and category == 'android_dev':
                return 'android_dev'
            elif any(keyword in request_lower for keyword in ['data', 'csv', 'analysis', 'plot']) and category == 'data_analysis':
                return 'data_analysis'
            elif any(keyword in request_lower for keyword in ['web', 'scrape', 'download', 'url']) and category == 'web_scraping':
                return 'web_scraping'
        
        return 'general'
    
    def test_skill_code(self, code: str, skill_name: str) -> Dict[str, Any]:
        """Test skill code in a safe environment"""
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Try to compile the code first
            try:
                compile(code, temp_file, 'exec')
            except SyntaxError as e:
                return {
                    'success': False,
                    'error': f'Syntax Error: {str(e)}',
                    'type': 'syntax'
                }
            
            # Try to run the code (basic test)
            try:
                result = subprocess.run(
                    ['python', temp_file], 
                    capture_output=True, 
                    text=True, 
                    timeout=10,
                    cwd=self.skills_dir
                )
                
                if result.returncode == 0:
                    return {
                        'success': True,
                        'output': result.stdout,
                        'message': 'Code executed successfully'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.stderr or 'Unknown execution error',
                        'type': 'runtime'
                    }
                    
            except subprocess.TimeoutExpired:
                return {
                    'success': False,
                    'error': 'Code execution timed out',
                    'type': 'timeout'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Testing error: {str(e)}',
                'type': 'system'
            }
        finally:
            # Clean up temp file
            try:
                Path(temp_file).unlink()
            except:
                pass
    
    def save_skill(self, skill_data: Dict[str, Any]) -> int:
        """Save a tested skill permanently"""
        
        timestamp = time.time()
        
        # Save to database
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO skills (name, description, code, category, created_at, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            skill_data['name'],
            skill_data['description'],
            skill_data['code'],
            skill_data['category'],
            timestamp,
            json.dumps(skill_data.get('tags', []))
        ))
        
        skill_id = cursor.lastrowid
        self.db.commit()
        
        # Save to file system
        skill_file = self.skills_dir / f"{skill_data['name']}.py"
        with open(skill_file, 'w') as f:
            f.write(f"# Skill: {skill_data['name']}\n")
            f.write(f"# Description: {skill_data['description']}\n")
            f.write(f"# Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))}\n")
            f.write(f"# Category: {skill_data['category']}\n\n")
            f.write(skill_data['code'])
        
        self.logger.info(f"Skill saved: {skill_data['name']}")
        return skill_id
    
    def list_skills(self, category: Optional[str] = None) -> List[Skill]:
        """List all saved skills"""
        
        cursor = self.db.cursor()
        if category:
            cursor.execute("SELECT * FROM skills WHERE category = ? ORDER BY created_at DESC", (category,))
        else:
            cursor.execute("SELECT * FROM skills ORDER BY created_at DESC")
        
        skills = []
        for row in cursor.fetchall():
            skill = Skill(
                id=row[0],
                name=row[1],
                description=row[2],
                code=row[3],
                category=row[4],
                created_at=row[5],
                usage_count=row[6],
                success_rate=row[7],
                tags=json.loads(row[8] or "[]")
            )
            skills.append(skill)
        
        return skills
    
    def get_skill_by_name(self, name: str) -> Optional[Skill]:
        """Get a specific skill by name"""
        
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM skills WHERE name = ?", (name,))
        row = cursor.fetchone()
        
        if row:
            return Skill(
                id=row[0],
                name=row[1],
                description=row[2],
                code=row[3],
                category=row[4],
                created_at=row[5],
                usage_count=row[6],
                success_rate=row[7],
                tags=json.loads(row[8] or "[]")
            )
        
        return None
    
    def execute_skill(self, skill_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a saved skill"""
        
        skill = self.get_skill_by_name(skill_name)
        if not skill:
            return {'error': f'Skill not found: {skill_name}'}
        
        try:
            # Create temp execution environment
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(skill.code)
                temp_file = f.name
            
            # Execute skill
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.skills_dir
            )
            
            # Update usage stats
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE skills 
                SET usage_count = usage_count + 1 
                WHERE name = ?
            """, (skill_name,))
            self.db.commit()
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout,
                    'skill': skill_name
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'skill': skill_name
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'skill': skill_name
            }
        finally:
            try:
                Path(temp_file).unlink()
            except:
                pass
    
    def search_skills(self, query: str) -> List[Skill]:
        """Search skills by name or description"""
        
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT * FROM skills 
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY usage_count DESC, created_at DESC
        """, (f"%{query}%", f"%{query}%"))
        
        skills = []
        for row in cursor.fetchall():
            skill = Skill(
                id=row[0],
                name=row[1],
                description=row[2],
                code=row[3],
                category=row[4],
                created_at=row[5],
                usage_count=row[6],
                success_rate=row[7],
                tags=json.loads(row[8] or "[]")
            )
            skills.append(skill)
        
        return skills

#IMPORTANT RULES: # type: ignore
#1. Always include a main function that demonstrates usage # type: ignore
#2. Add proper error handling # type: ignore
#3. Include docstrings # type: ignore
#4. Make code self-contained (import statements at top) # type: ignore
#5. Add comments explaining key steps # pyright: ignore[reportUndefinedVariable]
#6. Return code in this exact format:

