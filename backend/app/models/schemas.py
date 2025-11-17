"""Pydantic schemas for API request/response validation."""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from .transaction import TransactionType
from .agent_session import AgentType


# ============================================================================
# Company Schemas
# ============================================================================

class CompanyBase(BaseModel):
    """Base schema for Company."""
    name: str = Field(..., min_length=1, max_length=255, description="Company name")
    industry: Optional[str] = Field(None, max_length=100, description="Industry sector")
    founded_date: Optional[date] = Field(None, description="Date company was founded")
    initial_capital: Optional[Decimal] = Field(None, ge=0, description="Initial capital/funding")


class CompanyCreate(CompanyBase):
    """Schema for creating a new company."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    founded_date: Optional[date] = None
    initial_capital: Optional[Decimal] = Field(None, ge=0)


class CompanyResponse(CompanyBase):
    """Schema for company response."""
    id: int
    created_at: datetime
    updated_at: datetime
    transaction_count: int = Field(0, description="Number of transactions")
    
    model_config = ConfigDict(from_attributes=True)


class CompanyDetail(CompanyResponse):
    """Detailed company response with relationships."""
    transactions: List["TransactionResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Transaction Schemas
# ============================================================================

class TransactionBase(BaseModel):
    """Base schema for Transaction."""
    date: date = Field(..., description="Transaction date")
    amount: Decimal = Field(..., gt=0, description="Transaction amount (always positive)")
    category: str = Field(..., min_length=1, max_length=100, description="Transaction category")
    type: TransactionType = Field(..., description="Transaction type (income or expense)")
    description: Optional[str] = Field(None, max_length=500, description="Transaction description")


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""
    company_id: int = Field(..., gt=0, description="Company ID")


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction."""
    date: Optional[date] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[TransactionType] = None
    description: Optional[str] = Field(None, max_length=500)


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    signed_amount: float = Field(..., description="Amount with sign (negative for expenses)")
    
    model_config = ConfigDict(from_attributes=True)


class TransactionBulkCreate(BaseModel):
    """Schema for bulk transaction creation (CSV upload)."""
    transactions: List[TransactionCreate]


# ============================================================================
# Agent Session Schemas
# ============================================================================

class AgentSessionBase(BaseModel):
    """Base schema for Agent Session."""
    session_id: str = Field(..., description="Unique session identifier")
    agent_type: AgentType = Field(..., description="Type of agent")
    input_data: Optional[str] = Field(None, description="Input data as JSON string")
    output_data: Optional[str] = Field(None, description="Output data as JSON string")


class AgentSessionCreate(AgentSessionBase):
    """Schema for creating an agent session."""
    company_id: int = Field(..., gt=0, description="Company ID")
    execution_time_ms: Optional[int] = Field(None, ge=0, description="Execution time in milliseconds")
    token_count: Optional[int] = Field(None, ge=0, description="LLM token count")
    status: str = Field("success", description="Execution status")
    error_message: Optional[str] = None


class AgentSessionResponse(AgentSessionBase):
    """Schema for agent session response."""
    id: int
    company_id: int
    execution_time_ms: Optional[int]
    token_count: Optional[int]
    status: str
    error_message: Optional[str]
    created_at: datetime
    execution_time_seconds: Optional[float]
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Agent Analysis Schemas (for API responses)
# ============================================================================

class FinancialAnalysisRequest(BaseModel):
    """Request schema for financial analysis."""
    start_date: Optional[date] = Field(None, description="Analysis start date")
    end_date: Optional[date] = Field(None, description="Analysis end date")
    categories: Optional[List[str]] = Field(None, description="Filter by categories")


class CategorySpending(BaseModel):
    """Category spending breakdown."""
    category: str
    total_amount: Decimal
    transaction_count: int
    percentage: float


class FinancialAnalysisResponse(BaseModel):
    """Response schema for financial analysis."""
    company_id: int
    session_id: str
    timestamp: datetime
    
    # Financial Metrics
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    
    # Category Breakdown
    spending_by_category: List[CategorySpending]
    income_by_category: List[CategorySpending]
    
    # Insights
    insights: str = Field(..., description="Natural language insights from agent")
    status: str = Field("success", description="Analysis status")


class RunwayPredictionRequest(BaseModel):
    """Request schema for runway prediction."""
    forecast_months: int = Field(12, ge=1, le=60, description="Number of months to forecast")


class RunwayPredictionResponse(BaseModel):
    """Response schema for runway prediction."""
    company_id: int
    session_id: str
    timestamp: datetime
    
    # Runway Metrics
    monthly_burn_rate: Decimal = Field(..., description="Average monthly burn rate")
    current_balance: Decimal
    runway_months: Optional[float] = Field(None, description="Months until runway ends")
    runway_date: Optional[date] = Field(None, description="Estimated date when runway ends")
    
    # Forecast Data
    forecast_data: List[dict] = Field(..., description="Monthly forecast data for charts")
    
    # Insights
    insights: str = Field(..., description="Natural language insights from agent")
    recommendations: List[str] = Field([], description="Actionable recommendations")
    status: str = Field("success", description="Prediction status")


class InvestmentRecommendationRequest(BaseModel):
    """Request schema for investment recommendations."""
    risk_tolerance: Optional[str] = Field(None, description="Risk tolerance: low, medium, high")
    investment_horizon: Optional[int] = Field(None, ge=1, description="Investment horizon in months")


class InvestmentOption(BaseModel):
    """Individual investment option."""
    name: str
    type: str = Field(..., description="Investment type (e.g., bonds, stocks, savings)")
    expected_return: str
    risk_level: str
    description: str


class InvestmentRecommendationResponse(BaseModel):
    """Response schema for investment recommendations."""
    company_id: int
    session_id: str
    timestamp: datetime
    
    # Financial Health
    can_invest: bool = Field(..., description="Whether company is in position to invest")
    current_balance: Decimal
    
    # Recommendations
    recommendations: List[InvestmentOption] = Field([], description="Investment options")
    insights: str = Field(..., description="Natural language insights from agent")
    next_steps: List[str] = Field([], description="Actionable next steps")
    status: str = Field("success", description="Recommendation status")


# ============================================================================
# Generic Response Schemas
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    timestamp: datetime
    database: str = "connected"


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Generic success response."""
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Forward reference resolution
CompanyDetail.model_rebuild()

