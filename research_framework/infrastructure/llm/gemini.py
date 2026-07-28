import os
from typing import List, Any
from google import genai
from google.genai import types
from ...core.ports.llm import LLMProvider
from ...core.skill import Skill

class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_key: str = None, model_name: str = 'gemini-2.5-flash'):
        if not api_key:
            api_key = os.environ.get('GEMINI_API_KEY')
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        config = None
        if system_prompt:
            config = types.GenerateContentConfig(system_instruction=system_prompt)
            
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config
        )
        return response.text

    def execute_with_tools(self, prompt: str, system_prompt: str, tools: List[Skill], max_loops: int = 5) -> Any:
        function_declarations = []
        skill_map = {}
        for skill in tools:
            skill_map[skill.name] = skill
            function_declarations.append(
                types.FunctionDeclaration(
                    name=skill.name,
                    description=skill.description,
                    parameters=skill.parameters_schema
                )
            )
            
        tool = types.Tool(function_declarations=function_declarations) if function_declarations else None
        
        config = types.GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None,
            tools=[tool] if tool else None
        )
        
        # We simulate a chat loop
        messages = [
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        ]
        
        loops = 0
        while loops < max_loops:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=messages,
                config=config
            )
            
            messages.append(response.candidates[0].content)
            
            if response.function_calls:
                for fc in response.function_calls:
                    skill_name = fc.name
                    args = fc.args
                    
                    print(f"[LLM] Calling tool: {skill_name} with args: {args}")
                    
                    if skill_name in skill_map:
                        try:
                            # Execute the local function
                            result = skill_map[skill_name].execute(**args)
                        except Exception as e:
                            result = f"Error executing {skill_name}: {e}"
                    else:
                        result = f"Tool {skill_name} not found."
                        
                    print(f"[Tool] Result: {str(result)[:200]}...")
                    
                    # Append the function response
                    messages.append(
                        types.Content(
                            role="user", # The genai SDK expects function responses as user
                            parts=[types.Part.from_function_response(name=skill_name, response={"result": result})]
                        )
                    )
                loops += 1
            else:
                return response.text
                
        return "Error: Max tool calls limit reached before finishing the task."
