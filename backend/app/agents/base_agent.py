"""Base agent class with common functionality for all Cash Horizon agents."""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime

from google import genai
from google.genai import types

from app.config import settings
from app.models.agent_session import AgentSession, AgentStatus, AgentType
from app.database import get_async_session

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all AI agents in Cash Horizon.
    
    Provides common functionality:
    - Gemini API integration
    - Session management
    - Observability and logging
    - Error handling
    - Tool execution framework
    """
    
    def __init__(
        self,
        agent_type: AgentType,
        company_id: int,
        session_id: Optional[str] = None
    ):
        """
        Initialize base agent.
        
        Args:
            agent_type: Type of agent (analyst, runway, investment)
            company_id: ID of the company being analyzed
            session_id: Optional session ID for conversation continuity
        """
        self.agent_type = agent_type
        self.company_id = company_id
        self.session_id = session_id or f"{agent_type.value}_{company_id}_{int(time.time())}"
        
        # Initialize Gemini client
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model
        
        # Agent state
        self.execution_start_time: Optional[float] = None
        self.agent_session_record: Optional[AgentSession] = None
        
        logger.info(
            f"Initialized {self.agent_type.value} agent",
            extra={
                "company_id": company_id,
                "session_id": self.session_id,
                "agent_type": agent_type.value
            }
        )
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        
        Each agent must define its own system prompt that describes
        its role, capabilities, and constraints.
        
        Returns:
            System prompt string
        """
        pass
    
    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get the list of tools available to this agent.
        
        Tools should be defined in Google ADK format with:
        - name: Tool identifier
        - description: What the tool does
        - parameters: JSON schema for parameters
        
        Returns:
            List of tool definitions
        """
        pass
    
    @abstractmethod
    async def process_tool_call(
        self,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool call and return results.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            
        Returns:
            Tool execution results
        """
        pass
    
    async def execute(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the agent with a user message and optional context.
        
        This is the main entry point for agent execution. It:
        1. Starts observability tracking
        2. Prepares the prompt with system instructions
        3. Calls Gemini with tools
        4. Handles tool calls if needed
        5. Saves results to database
        6. Returns formatted response
        
        Args:
            user_message: User's input message
            context: Optional context data (transaction data, company info, etc.)
            
        Returns:
            Dictionary containing agent response and metadata
        """
        self.execution_start_time = time.time()
        
        try:
            logger.info(
                f"Starting {self.agent_type.value} agent execution",
                extra={
                    "session_id": self.session_id,
                    "company_id": self.company_id
                }
            )
            
            # Prepare input data for logging
            input_data = {
                "user_message": user_message,
                "context": context or {}
            }
            
            # Create agent session record
            await self._create_session_record(input_data)
            
            # Build the full prompt
            system_prompt = self.get_system_prompt()
            full_prompt = self._build_prompt(user_message, context)
            
            # Get tools for this agent
            tools = self.get_tools()
            
            # Call Gemini API with tools
            response = await self._call_gemini(
                system_prompt=system_prompt,
                user_prompt=full_prompt,
                tools=tools
            )
            
            # Process the response
            result = await self._process_response(response)
            
            # Update session record with success
            await self._update_session_record(
                output_data=result,
                status=AgentStatus.COMPLETED
            )
            
            logger.info(
                f"Completed {self.agent_type.value} agent execution",
                extra={
                    "session_id": self.session_id,
                    "execution_time_ms": self._get_execution_time_ms()
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error in {self.agent_type.value} agent execution",
                extra={
                    "session_id": self.session_id,
                    "error": str(e)
                },
                exc_info=True
            )
            
            # Update session record with failure
            await self._update_session_record(
                output_data={"error": str(e)},
                status=AgentStatus.FAILED
            )
            
            raise
    
    def _convert_tools_to_gemini_format(
        self,
        tools: List[Dict[str, Any]]
    ) -> List[types.Tool]:
        """
        Convert tool definitions to Gemini ADK format.
        
        Args:
            tools: List of tool definitions (simple dict format)
            
        Returns:
            List of Gemini Tool objects with FunctionDeclarations
        """
        gemini_tools = []
        
        for tool in tools:
            try:
                # Create FunctionDeclaration for each tool
                function_declaration = types.FunctionDeclaration(
                    name=tool["name"],
                    description=tool["description"],
                    parameters=tool.get("parameters", {
                        "type": "object",
                        "properties": {},
                        "required": []
                    })
                )
                
                # Wrap in Tool object
                gemini_tool = types.Tool(
                    function_declarations=[function_declaration]
                )
                gemini_tools.append(gemini_tool)
                
            except Exception as e:
                logger.warning(f"Failed to convert tool {tool.get('name', 'unknown')}: {e}")
                continue
        
        logger.debug(f"Converted {len(gemini_tools)} tools to Gemini format")
        return gemini_tools
    
    async def _call_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: List[Dict[str, Any]]
    ) -> Any:
        """
        Call Gemini API with proper ADK function calling support.
        
        This implements the full function calling flow:
        1. Initial call with tools available
        2. If function called, execute it
        3. Return results to Gemini for final response
        
        Args:
            system_prompt: System instructions for the agent
            user_prompt: User's input prompt
            tools: List of available tools
            
        Returns:
            Gemini API response with final text or tool results
        """
        try:
            # Convert tools to Gemini format
            gemini_tools = self._convert_tools_to_gemini_format(tools)
            
            # Configure function calling behavior
            tool_config = types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode=types.FunctionCallingConfig.Mode.AUTO  # Gemini decides when to use tools
                )
            )
            
            # Build config with tools
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2048,
                tools=gemini_tools if gemini_tools else None,
                tool_config=tool_config if gemini_tools else None
            )
            
            # Initial call to Gemini
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config
            )
            
            # Check if Gemini wants to call a function
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        # Check if this part is a function call
                        if hasattr(part, 'function_call') and part.function_call:
                            function_call = part.function_call
                            logger.info(
                                f"Gemini requested function call: {function_call.name}",
                                extra={"session_id": self.session_id}
                            )
                            
                            # Execute the tool
                            tool_result = await self.process_tool_call(
                                tool_name=function_call.name,
                                tool_args=dict(function_call.args)
                            )
                            
                            # Build multi-turn conversation with function result
                            final_response = await self._call_gemini_with_tool_result(
                                system_prompt=system_prompt,
                                user_prompt=user_prompt,
                                function_call=function_call,
                                function_result=tool_result,
                                config=config
                            )
                            
                            return final_response
            
            # No function call - return direct response
            return response
            
        except Exception as e:
            logger.error(
                f"Gemini API call failed",
                extra={
                    "session_id": self.session_id,
                    "error": str(e)
                }
            )
            raise
    
    async def _call_gemini_with_tool_result(
        self,
        system_prompt: str,
        user_prompt: str,
        function_call: Any,
        function_result: Dict[str, Any],
        config: types.GenerateContentConfig
    ) -> Any:
        """
        Make second Gemini call with tool execution results.
        
        This completes the function calling flow by providing the tool
        results back to Gemini for final response generation.
        
        Args:
            system_prompt: System instructions
            user_prompt: Original user prompt
            function_call: The function call from Gemini
            function_result: Results from executing the tool
            config: Generation config to reuse
            
        Returns:
            Final Gemini response with tool results incorporated
        """
        try:
            # Build multi-turn conversation history
            contents = [
                # Turn 1: User's request
                types.Content(
                    role="user",
                    parts=[types.Part(text=user_prompt)]
                ),
                # Turn 2: Model's function call
                types.Content(
                    role="model",
                    parts=[types.Part(function_call=function_call)]
                ),
                # Turn 3: Function result
                types.Content(
                    role="user",
                    parts=[types.Part(
                        function_response=types.FunctionResponse(
                            name=function_call.name,
                            response=function_result
                        )
                    )]
                )
            ]
            
            # Make final call with tool results
            final_response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )
            
            logger.info(
                f"Received final response after tool execution",
                extra={"session_id": self.session_id}
            )
            
            return final_response
            
        except Exception as e:
            logger.error(
                f"Failed to process tool result with Gemini",
                extra={
                    "session_id": self.session_id,
                    "error": str(e)
                }
            )
            raise
    
    def _build_prompt(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build the full prompt including context.
        
        Args:
            user_message: User's input message
            context: Optional context data
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # Add context if provided
        if context:
            prompt_parts.append("CONTEXT:")
            for key, value in context.items():
                prompt_parts.append(f"{key}: {value}")
            prompt_parts.append("")
        
        # Add user message
        prompt_parts.append("USER REQUEST:")
        prompt_parts.append(user_message)
        
        return "\n".join(prompt_parts)
    
    async def _process_response(self, response: Any) -> Dict[str, Any]:
        """
        Process the Gemini response and format it for return.
        
        Args:
            response: Raw Gemini API response
            
        Returns:
            Formatted response dictionary
        """
        try:
            # Extract text from response
            if hasattr(response, 'text'):
                text_response = response.text
            else:
                text_response = str(response)
            
            return {
                "agent_type": self.agent_type.value,
                "session_id": self.session_id,
                "company_id": self.company_id,
                "status": "success",
                "response": text_response,
                "timestamp": datetime.utcnow().isoformat(),
                "execution_time_ms": self._get_execution_time_ms()
            }
            
        except Exception as e:
            logger.error(
                f"Error processing response",
                extra={"session_id": self.session_id, "error": str(e)}
            )
            raise
    
    async def _create_session_record(self, input_data: Dict[str, Any]) -> None:
        """
        Create an agent session record in the database for observability.
        
        Args:
            input_data: Input data for the session
        """
        try:
            async for db in get_async_session():
                session_record = AgentSession(
                    company_id=self.company_id,
                    session_id=self.session_id,
                    agent_type=self.agent_type,
                    status=AgentStatus.RUNNING,
                    input_data=input_data,
                    output_data={},
                    execution_time_ms=0,
                    token_count=0
                )
                
                db.add(session_record)
                await db.commit()
                await db.refresh(session_record)
                
                self.agent_session_record = session_record
                break
                
        except Exception as e:
            logger.warning(
                f"Failed to create session record",
                extra={"session_id": self.session_id, "error": str(e)}
            )
            # Don't fail the agent execution if logging fails
    
    async def _update_session_record(
        self,
        output_data: Dict[str, Any],
        status: AgentStatus
    ) -> None:
        """
        Update the agent session record with results.
        
        Args:
            output_data: Output data from the agent
            status: Final status of the execution
        """
        if not self.agent_session_record:
            return
        
        try:
            async for db in get_async_session():
                self.agent_session_record.output_data = output_data
                self.agent_session_record.status = status
                self.agent_session_record.execution_time_ms = self._get_execution_time_ms()
                
                await db.commit()
                break
                
        except Exception as e:
            logger.warning(
                f"Failed to update session record",
                extra={"session_id": self.session_id, "error": str(e)}
            )
            # Don't fail the agent execution if logging fails
    
    def _get_execution_time_ms(self) -> int:
        """
        Calculate execution time in milliseconds.
        
        Returns:
            Execution time in milliseconds
        """
        if self.execution_start_time is None:
            return 0
        return int((time.time() - self.execution_start_time) * 1000)

