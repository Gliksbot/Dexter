"""
Dexter Simple v2 - Bulletproof LLM Orchestrator with Agent API/Skills
"""

import asyncio
import json
import logging
import aiohttp
import os
from typing import Dict, List
from brain_system import BrainManager

class LLMProvider:
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"llm.{name}")
        self.endpoint = config.get('endpoint', 'http://localhost:11434')
        self.model = config.get('model', 'llama3.1:8b')
    
    async def call(self, messages: List[Dict]) -> str:
        url = f"{self.endpoint}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.config.get('params', {}).get('temperature', 0.7)
            }
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["message"]["content"]
                    else:
                        return f"Error: {response.status}"
        except Exception as e:
            return f"Connection error: {str(e)}"

class DexterOrchestrator:
    def __init__(self, config_path="dexter_simple_config.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        self.brain = BrainManager(config_path)
        self.dexter = LLMProvider("dexter", self.config['llms']['dexter'])
        self.partner = LLMProvider("partner", self.config['llms']['partner'])
        self.partner_proposals = []
    
    async def call_agent_api(self, endpoint, data=None):
        """Call local agent API with robust error handling"""
        try:
            api_config = self.config.get('agent_api', {})
            url = f"{api_config.get('endpoint', 'http://localhost:5001')}/agent/{endpoint}"
            headers = {"Authorization": f"Bearer {api_config.get('api_key', '')}"}
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data or {}, headers=headers) as response:
                    return await response.json()
        except Exception as e:
            return {"error": f"Agent API error: {str(e)}"}

    async def process_user_input(self, user_input: str) -> str:
        # Partner direct communication
        if user_input.startswith('@partner'):
            return await self._handle_partner_direct(user_input[8:].strip())

        # Direct file listing: zero hallucination
        if any(word in user_input.lower() for word in ['files', 'directory', 'list cwd']):
            files_result = await self.call_agent_api("list_files")
            if files_result.get("status") == "success":
                file_lines = "\n".join(
                    f"- {f['name']} ({f['type']}, {f['size']} bytes)"
                    for f in files_result['files']
                )
                response = "Here are the files in my current working directory:\n\n" + file_lines
            else:
                response = f"Error fetching files: {files_result.get('error', 'Unknown error')}"
            self.brain.process_conversation(user_input, response, 'dexter')
            return response

        # Read a file (if command matches e.g. 'read filename.txt')
        if user_input.lower().startswith("read "):
            filename = user_input[5:].strip()
            file_result = await self.call_agent_api("read_file", {"file_path": filename})
            if file_result.get("status") == "success":
                # Show up to 40 lines/4000 chars for safety
                content = file_result["content"]
                limited = content[:4000] + ("..." if len(content) > 4000 else "")
                response = f"Contents of `{filename}`:\n\n``````"
            else:
                response = f"Error reading `{filename}`: {file_result.get('error', 'Unknown error')}"
            self.brain.process_conversation(user_input, response, 'dexter')
            return response

        # Skill creation (e.g., 'create skill: ...' or 'make skill ...')
        if user_input.lower().startswith("create skill:") or user_input.lower().startswith("make skill"):
            request = user_input.split(":", 1)[1].strip() if ":" in user_input else user_input[10:].strip()
            code = await self._generate_skill_code(request)
            if code.get("success"):
                response = f"✅ Skill created! Name: `{code['name']}`\n\nCode preview:\n``````"
            else:
                response = f"Skill creation failed: {code.get('error', 'Unknown error')}"
            self.brain.process_conversation(user_input, response, 'dexter')
            return response

        # Config access
        if "config" in user_input.lower():
            config_result = await self.call_agent_api("read_config")
            if config_result.get("status") == "success":
                config_keys = [k for k in config_result['config'].keys()]
                response = (
                    "I accessed my configuration! Top-level sections are:\n\n"
                    + ", ".join(config_keys)
                )
            else:
                response = f"Error fetching configuration: {config_result.get('error', 'Unknown error')}"
            self.brain.process_conversation(user_input, response, 'dexter')
            return response
        
        # Fall-through: Chat/Q&A/code via LLM
        context = self.brain.get_context(user_input)
        messages = [{
            "role": "system",
            "content": f"{self.dexter.config['identity']}\n\nContext: {context}\n\nYou have Agent API file access. Only discuss files you've actually accessed."
        }, {
            "role": "user",
            "content": user_input
        }]
        response = await self.dexter.call(messages)
        self.brain.process_conversation(user_input, response, 'dexter')
        asyncio.create_task(self._partner_analysis(user_input, response))
        return response
    
    async def _generate_skill_code(self, request: str) -> dict:
        """Create Python code for a new skill, save to skills folder"""
        skill_name = "skill_" + "".join(e for e in request.lower() if e.isalnum() or e == "_")[:32]
        # Prompt LLM for code
        messages = [{
            "role": "system",
            "content": f"You are a Python skill code generator. Write valid, secure, self-contained code for the following skill request, and NOTHING ELSE:\n{request}"
        }]
        skill_code = await self.dexter.call(messages)
        # Validate code (basic - check for def or class or import)
        if "def " not in skill_code and "class " not in skill_code and "import " not in skill_code:
            return {"success": False, "error": "No valid code detected.", "code": skill_code}
        # Save skill to file
        try:
            skills_dir = os.path.abspath(self.config['skills']['storage_path'])
            os.makedirs(skills_dir, exist_ok=True)
            skill_file = os.path.join(skills_dir, f"{skill_name}.py")
            with open(skill_file, "w") as f:
                f.write(skill_code)
            return {"success": True, "name": skill_name, "code": skill_code, "file": skill_file}
        except Exception as e:
            return {"success": False, "error": str(e), "code": skill_code}

    async def _handle_partner_direct(self, user_input: str) -> str:
        context = self.brain.get_context(user_input)
        messages = [{
            "role": "system",
            "content": f"{self.partner.config['identity']}\n\nContext: {context}"
        }, {
            "role": "user",
            "content": user_input
        }]
        response = await self.partner.call(messages)
        self.brain.process_conversation(f"@partner {user_input}", response, 'partner')
        return f"[Partner]: {response}"

    async def _partner_analysis(self, user_input, dexter_response):
        try:
            messages = [{
                "role": "system",
                "content": "Analyze this conversation and suggest one brief improvement or next step."
            }, {
                "role": "user",
                "content": f"User: {user_input}\nDexter: {dexter_response}"
            }]
            suggestion = await self.partner.call(messages)
            self.partner_proposals.append({
                'timestamp': asyncio.get_event_loop().time(),
                'proposal': suggestion
            })
            if len(self.partner_proposals) > 3:
                self.partner_proposals.pop(0)
        except:
            pass

    def get_recent_proposals(self, limit=3):
        return [p['proposal'] for p in self.partner_proposals[-limit:]]
