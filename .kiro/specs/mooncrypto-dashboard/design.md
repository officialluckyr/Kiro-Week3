# MoonCrypto Dashboard Design Document

## Overview

The MoonCrypto dashboard is a Streamlit-based web application that explores the correlation between Bitcoin price movements and lunar phases. The application combines financial data analysis with astronomical calculations to create an engaging, interactive visualization that answers the playful question: "Do Full Moons Pump Bitcoin?"

The system architecture follows a modular approach with clear separation between data fetching, astronomical calculations, statistical analysis, and presentation layers. The application prioritizes user engagement through dynamic storytelling, interactive visualizations, and celebratory effects.

## Architecture

The application follows a layered architecture pattern:

```
┌─────────────────────────────────────┐
│           Presentation Layer        │
│     (Streamlit UI Components)       │
├─────────────────────────────────────┤
│          Business Logic Layer       │
│   (Correlation Analysis, Stories)   │
├─────────────────────────────────────┤
│           Data Layer               │
│  (Bitcoin Data, Moon Phase Data)   │
├─────────────────────────────────────┤
│          External APIs             │
│    (yfinance, ephem library)       │
└─────────────────────────────────────┘
```

### Key Architectural Principles

- **Single Responsibility**: Each module handles one specific concern (data fetching, calculations, visualization)
- **Dependency Injection**: External data sources are abstracted to enable testing and flexibility
- **Error Resilience**: Graceful degradation when external services are unavailable
- **Performance Optimization**: Caching mechanisms for expensive calculations and API calls

## Components and Interfaces

### 1. Data Fetching Module (`data_fetcher.py`)

**Purpose**: Handles retrieval of Bitcoin price data and moon phase calculations

**Key Functions**:
- `fetch_bitcoin_data(symbol: str, period: str) -> pd.DataFrame`
- `calculate_moon_phases(start_date: datetime, end_date: datetime) -> pd.DataFrame`
- `merge_datasets(bitcoin_df: pd.DataFrame, moon_df: pd.DataFrame) -> pd.DataFrame`

**Dependencies**: yfinance, ephem, pandas

### 2. Analysis Module (`analysis.py`)

**Purpose**: Performs statistical analysis and correlation calculations

**Key Functions**:
- `calculate_correlation(bitcoin_prices: pd.Series, moon_illumination: pd.Series) -> float`
- `identify_full_moon_periods(moon_data: pd.DataFrame, threshold: float = 0.95) -> List[Tuple[datetime, datetime]]`
- `generate_summary_stats(merged_data: pd.DataFrame) -> Dict[str, Any]`

### 3. Visualization Module (`visualization.py`)

**Purpose**: Creates interactive charts and visual components

**Key Functions**:
- `create_dual_axis_chart(merged_data: pd.DataFrame) -> plotly.graph_objects.Figure`
- `create_verdict_box(correlation: float) -> str`
- `apply_chart_styling(fig: plotly.graph_objects.Figure) -> plotly.graph_objects.Figure`

### 4. Story Generator Module (`story_generator.py`)

**Purpose**: Generates dynamic narrative content based on analysis results

**Key Functions**:
- `generate_story(correlation: float, summary_stats: Dict[str, Any]) -> str`
- `get_correlation_interpretation(correlation: float) -> str`
- `create_contextual_narrative(bitcoin_trend: str, moon_phase_trend: str) -> str`

### 5. Main Application (`app.py`)

**Purpose**: Orchestrates all components and manages Streamlit interface

**Key Responsibilities**:
- Initialize Streamlit page configuration
- Coordinate data fetching and analysis
- Render UI components
- Handle user interactions and state management

## Data Models

### Bitcoin Data Model
```python
@dataclass
class BitcoinData:
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame for analysis"""
```

### Moon Phase Data Model
```python
@dataclass
class MoonPhaseData:
    timestamp: datetime
    illumination_percentage: float
    phase_name: str
    is_full_moon: bool
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame for analysis"""
```

### Analysis Results Model
```python
@dataclass
class AnalysisResults:
    correlation_coefficient: float
    p_value: float
    full_moon_periods: List[Tuple[datetime, datetime]]
    summary_statistics: Dict[str, Any]
    
    @property
    def verdict_message(self) -> str:
        """Generate verdict message based on correlation"""
        if self.correlation_coefficient > 0.1:
            return "VERDICT: ASTROLOGY IS REAL? 😱"
        return "VERDICT: JUST COINCIDENCE 📉"
    
    @property
    def verdict_color(self) -> str:
        """Get color for verdict display"""
        return "green" if self.correlation_coefficient > 0.1 else "red"
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Based on the prework analysis, I've identified several properties that can be consolidated to eliminate redundancy:

**Property Reflection:**
- Properties 2.1, 2.3, and 3.1 can be combined into a comprehensive data fetching property
- Properties 2.2, 2.4, 3.4, 8.1, and 8.3 can be consolidated into a general error handling property
- Properties 4.2 and 4.3 are specific examples that can be combined into one chart styling property
- Properties 5.2 and 5.3 can be combined into one verdict logic property
- Properties 6.1 and 6.3 can be consolidated into one story generation property

### Property 1: Data Fetching Integrity
*For any* valid date range and symbol, the data fetching functions should return datasets with proper timestamps, valid price data, and moon illumination percentages within 0-100% range
**Validates: Requirements 2.1, 2.3, 3.1, 3.2**

### Property 2: Error Handling Consistency  
*For any* error condition (network failures, invalid data, computation errors), the system should provide appropriate error messages and graceful degradation without crashing
**Validates: Requirements 2.2, 2.4, 3.4, 8.1, 8.3, 8.4, 8.5**

### Property 3: Data Alignment Preservation
*For any* Bitcoin and moon phase datasets, when merged, the resulting dataset should maintain temporal alignment with matching or interpolated timestamps
**Validates: Requirements 3.3**

### Property 4: Chart Component Integrity
*For any* valid merged dataset, the dual-axis chart should contain both Bitcoin price and moon illumination data with proper axis scaling and labels
**Validates: Requirements 4.1, 4.5**

### Property 5: Correlation Calculation Accuracy
*For any* two numeric series, the Pearson correlation coefficient should be mathematically correct and fall within the valid range of -1 to 1
**Validates: Requirements 5.1, 5.4**

### Property 6: Verdict Logic Consistency
*For any* correlation coefficient value, the verdict message and color should follow the specified rules: green "ASTROLOGY IS REAL?" for >0.1, red "JUST COINCIDENCE" for ≤0.1
**Validates: Requirements 5.2, 5.3**

### Property 7: Story Generation Variability
*For any* correlation coefficient, the story generator should produce different narrative content for different correlation ranges (strong vs weak correlations)
**Validates: Requirements 6.1, 6.3**

### Property 8: Full Moon Detection Accuracy
*For any* moon phase dataset, periods where illumination exceeds 95% should be correctly identified as full moon periods
**Validates: Requirements 7.2**

### Property 9: Data Validation Completeness
*For any* input dataset, validation should verify data integrity (non-null values, proper data types, reasonable ranges) before analysis
**Validates: Requirements 8.2**

## Error Handling

The application implements comprehensive error handling across all layers:

### Data Layer Error Handling
- **Network Failures**: Retry logic with exponential backoff for API calls
- **Invalid Responses**: Validation of API response structure and content
- **Missing Data**: Graceful handling of gaps in historical data
- **Rate Limiting**: Respect API rate limits with appropriate delays

### Calculation Layer Error Handling
- **Astronomical Errors**: Fallback to approximate calculations if ephem fails
- **Statistical Errors**: Validation of input data before correlation analysis
- **Division by Zero**: Safe handling of edge cases in mathematical operations
- **Data Type Errors**: Type checking and conversion with error messages

### Presentation Layer Error Handling
- **Rendering Failures**: Fallback to simple text displays if charts fail
- **State Management**: Recovery from invalid UI states
- **User Input Validation**: Sanitization and validation of user selections
- **Resource Loading**: Graceful degradation if external resources fail

### Error Recovery Strategies
1. **Graceful Degradation**: Core functionality remains available even if some features fail
2. **User Communication**: Clear, actionable error messages for users
3. **Logging**: Comprehensive logging for debugging and monitoring
4. **Fallback Data**: Use cached or sample data when live data is unavailable

## Testing Strategy

The MoonCrypto dashboard employs a dual testing approach combining unit tests and property-based tests to ensure comprehensive coverage and correctness.

### Unit Testing Approach

Unit tests will verify specific examples, edge cases, and integration points:

- **Data Fetching**: Test specific API responses and error conditions
- **UI Components**: Verify correct rendering of specific elements
- **Integration**: Test component interactions with known data sets
- **Edge Cases**: Handle boundary conditions like empty datasets or extreme values

**Testing Framework**: pytest for Python unit testing
**Coverage Target**: 80% code coverage for core business logic

### Property-Based Testing Approach

Property-based tests will verify universal properties across all valid inputs using **Hypothesis** library:

- **Minimum Iterations**: Each property test runs 100 iterations minimum
- **Test Tagging**: Each property test includes a comment with format: `**Feature: mooncrypto-dashboard, Property {number}: {property_text}**`
- **Generator Strategy**: Smart generators that produce realistic Bitcoin prices, valid date ranges, and moon illumination percentages
- **Shrinking**: Automatic test case minimization when failures occur

**Property Test Requirements**:
- All correctness properties from the design document must be implemented as property-based tests
- Each property test must reference its corresponding design property
- Tests must use realistic data generators (e.g., Bitcoin prices in reasonable ranges, valid dates)
- Property tests complement unit tests by verifying behavior across input space

### Integration Testing

- **End-to-End Workflows**: Test complete user journeys from data loading to visualization
- **API Integration**: Verify correct interaction with yfinance and ephem libraries  
- **UI Integration**: Test Streamlit component interactions and state management
- **Performance Testing**: Ensure acceptable response times for data processing

### Test Data Strategy

- **Mock Data**: Controlled datasets for unit tests
- **Generated Data**: Property-based test generators for comprehensive coverage
- **Historical Data**: Real Bitcoin and moon phase data for integration tests
- **Edge Case Data**: Extreme values, empty sets, and boundary conditions

The testing strategy ensures that both specific behaviors (unit tests) and general correctness properties (property tests) are validated, providing confidence in the application's reliability and correctness.