# MCP Naver Maps

A Model Context Protocol (MCP) server that connects to [Naver Maps API](https://www.ncloud.com/product/applicationService/maps) and [Naver Search API](https://developers.naver.com/products/service-api/search/search.md). 네이버 지도 API와 검색 API에 연결하는 MCP 서버입니다.

## Features

### 🗺️ Geocoding
- Convert addresses to coordinates with detailed information
- Support for Korean and English addresses
- Pagination support (up to 100 results per page)
- Returns road address, land-lot address, and English address

### 🔍 Local Search
- Search for places using Naver's comprehensive local database
- Pagination and sorting options (by relevance or review count)
- Detailed place information including category, description, and addresses

### 📍 Coordinate-based Search (Advanced)
- **Smart radius filtering**: Find places within specific distance from coordinates
- **Multi-page search**: Automatically searches multiple pages to meet minimum results
- **Distance calculation**: Uses Haversine formula for accurate distance filtering
- **Comprehensive logging**: Detailed search statistics and debugging information

## Prerequisites

### Required Software
- **Python**: Version 3.13 or higher
- **uv**: Fast Python package manager ([installation guide](https://github.com/astral-sh/uv))

### API Credentials
You need API credentials from two sources:

1. **Naver Cloud Platform**: For Maps/Geocoding API
   - Get credentials from [Naver Cloud Platform console](https://www.ncloud.com/)
   - Required: Client ID and Client Secret

2. **Naver Developers**: For Local Search API
   - Get credentials from [Naver Developers](https://developers.naver.com/main/)
   - Required: Client ID and Client Secret

## Installation

### 1. Install uv (if not already installed)

**macOS:**
```bash
# Using Homebrew
brew install uv

# Or using curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
# Using PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip
pip install uv
```

### 2. Clone and Setup Project

```bash
git clone <repository-url>
cd mcp-naver-maps
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Naver Maps API (for geocoding)
NAVER_MAPS_CLIENT_ID="YOUR_NAVER_MAPS_CLIENT_ID"
NAVER_MAPS_CLIENT_SECRET="YOUR_NAVER_MAPS_CLIENT_SECRET"

# Naver Developers API (for local search)
NAVER_CLIENT_API="YOUR_NAVER_CLIENT_API"
NAVER_CLIENT_SECRET="YOUR_NAVER_CLIENT_SECRET"
```

### 4. Install Dependencies

```bash
uv sync
```

## Running the MCP Server

### Production Mode
```bash
uv run src/naver_map_mcp
```

### Development Mode
```bash
source .venv/bin/activate
mcp dev src/naver_map_mcp/server.py
```

## MCP Client Configuration

Add this configuration to your MCP client:

```json
{
  "mcpServers": {
    "mcp-naver-location": {
      "command": "uv",
      "args": ["run", "/path/to/mcp-naver-maps/src/naver_map_mcp"],
      "env": {
        "NAVER_MAPS_CLIENT_ID": "<YOUR_NAVER_MAPS_CLIENT_ID>",
        "NAVER_MAPS_CLIENT_SECRET": "<YOUR_NAVER_MAPS_CLIENT_SECRET>",
        "NAVER_CLIENT_API": "<YOUR_NAVER_CLIENT_API>",
        "NAVER_CLIENT_SECRET": "<YOUR_NAVER_CLIENT_SECRET>"
      }
    }
  }
}
```

## API Tools

### 🗺️ `geocode`
Convert addresses to coordinates with detailed address information.

**Parameters:**
- `address` (required): Address to search (Korean or English)
- `language` (optional): Response language ("kor" or "eng", default: "kor")
- `page` (optional): Page number for pagination (default: 1)
- `count` (optional): Results per page (default: 10, max: 100)

**Example:**
```
Find coordinates for "서울역"
```

### 🔍 `localSearch`
Search for places using Naver's local database.

**Parameters:**
- `query` (required): Search query (e.g., "강남역 맛집", "서울 카페")
- `display` (optional): Number of results (max: 5, default: 5)
- `sort` (optional): "random" (relevance) or "comment" (review count)
- `start` (optional): Starting position for pagination (default: 1)

**Example:**
```
Search for "강남역 근처 카페"
```

### 📍 `localSearchByCoordinate`
Find places within a specific radius from coordinates with advanced filtering.

**Parameters:**
- `query` (required): Search query with regional context
- `longitude` (required): Center longitude (e.g., 126.9707 for Seoul Station)
- `latitude` (required): Center latitude (e.g., 37.5536 for Seoul Station)
- `radius` (optional): Search radius in meters (default: 1000m, max: 10km)
- `display` (optional): Maximum results to return (max: 5)
- `sort` (optional): "random" or "comment"
- `min_results` (optional): Minimum results before stopping search (default: 1)

**How it works:**
1. Performs multiple `localSearch` calls across pages
2. Calculates actual distance using Haversine formula
3. Filters results within specified radius
4. Continues until `min_results` found or 10 pages searched

**Example:**
```
Find restaurants within 1km of Seoul Station (126.9707, 37.5536)
```

## Usage Examples

### Basic Address Search
```
서울특별시 중구 세종대로 18 (서울역) 의 좌표를 찾아줘
```

### Local Place Search
```
강남역 근처 맛집 5곳 추천해줘
```

### Radius-based Search
```
서울역(경도: 126.9707, 위도: 37.5536) 주변 1km 이내의 카페를 찾아줘
```

### Advanced Coordinate Search
```
센터필드 EAST 좌표를 찾아서 반경 700m 이내의 맛집을 추천해줘. 
검색할 때는 '역삼동 근처 고기구이'처럼 지역명을 포함해서 검색해줘.
```

## Logging and Debugging

The server automatically logs detailed information for `localSearchByCoordinate` operations:

- **Location**: `logs/coordinate_search_YYYYMMDD.log`
- **Content**: Input parameters, search statistics, and filtered results
- **Format**: JSON format for easy parsing and analysis

## Error Handling

All tools return structured error responses:
```json
{
  "success": false,
  "error": "Error description"
}
```

Common error scenarios:
- Missing or invalid API credentials
- Rate limiting (HTTP 420)
- Invalid coordinates or parameters
- Network connectivity issues

## Development

### Project Structure
```
mcp-naver-maps/
├── src/naver_map_mcp/
│   ├── server.py          # Main MCP server
│   ├── naver_maps_client.py  # API client
│   ├── models.py          # Pydantic models
│   └── __main__.py        # Entry point
├── logs/                  # Auto-generated logs
├── .env                   # Environment variables
├── pyproject.toml         # Project configuration
└── requirements.txt       # Dependencies
```

### Dependencies
- `httpx[http2]`: HTTP client with HTTP/2 support
- `mcp[cli]`: Model Context Protocol framework
- `python-dotenv`: Environment variable management
- `pydantic`: Data validation and modeling

### Running Tests
```bash
# Install development dependencies
uv sync --group dev

# Run linting
uv run ruff check
```

## Coordinate System Notes

- **Input coordinates**: Standard decimal degrees (WGS84)
- **Naver API coordinates**: Scaled by 10,000,000 (handled automatically)
- **Distance calculations**: Haversine formula for accurate results
- **Coordinate examples**:
  - Seoul Station: 126.9707, 37.5536
  - Gangnam Station: 127.0276, 37.4979

## Rate Limiting

The server implements intelligent rate limiting:
- 0-50ms delay between consecutive calls
- Exponential backoff for failed requests
- Automatic retry logic for transient errors

## License

This project is licensed under the MIT License.