from mcp.server.fastmcp import FastMCP
from naver_map_mcp.naver_maps_client import NaverMapsClient
from naver_map_mcp.models import GeocodeResponse, LocalSearchResponse, LocalItem
from dotenv import load_dotenv
from pydantic import Field
from typing import Dict, Literal, List
import math
import logging
import os
import json
from datetime import datetime

load_dotenv()

# 로깅 설정
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../logs')
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger('naver_map_mcp')
logger.setLevel(logging.INFO)

# 파일 핸들러 설정
log_file = os.path.join(log_dir, f'coordinate_search_{datetime.now().strftime("%Y%m%d")}.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# 포맷 설정
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 로거에 핸들러 추가
logger.addHandler(file_handler)

naver_maps_client = NaverMapsClient()

INSTRUCTIONS = """
Naver Maps MCP provides location-based search capabilities using Naver Maps and Search APIs.

<tools>
- geocode: Convert addresses to coordinates with detailed address information
- localSearch: Search for places using Naver's local database with pagination support
- localSearchByCoordinate: Find places within a specific radius from coordinates (custom implementation with distance filtering)
</tools>

<rules>
- All responses include metadata for pagination. Use 'start' parameter for localSearch pagination.
- For geocode, use 'page' parameter for pagination (default: page=1, count=10).
- localSearchByCoordinate performs automatic multi-page searching and distance filtering to meet min_results requirement.
- Coordinate format: Naver uses scaled coordinates (multiply by 10,000,000). This is handled automatically.
- Rate limiting: Wait 0-50ms between consecutive calls with exponential backoff.
- For location searches, prefer localSearchByCoordinate when radius-based filtering is needed.
- Query optimization: Include regional information (e.g., "강남역 근처 카페") for better localSearchByCoordinate results.
</rules>
""".strip()

mcp = FastMCP("naver_map_mcp", instructions=INSTRUCTIONS)


@mcp.tool(description="Convert addresses to coordinates and get detailed address information with pagination support.")
async def geocode(
  address: str = Field(description="Address to search for (Korean or English)", min_length=1),
  language: Literal["kor", "eng"] = Field("kor", description="Response language (kor: Korean, eng: English)"),
  page: int = Field(1, description="Page number for pagination (default: 1)", ge=1),
  count: int = Field(10, description="Number of results per page (default: 10, max: 100)", ge=1, le=100),
) -> GeocodeResponse | Dict:
  """
  Converts addresses to coordinates using Naver Maps Geocoding API.
  
  Returns:
    GeocodeResponse: Contains status, metadata (totalCount, page, count), and list of addresses with coordinates
    Each address includes: roadAddress, jibunAddress, englishAddress, x (longitude), y (latitude), distance
  """
  try:
    return await naver_maps_client.geocode(address, language, page, count)
  except Exception as ex:
    return {"success": False, "error": str(ex)}


@mcp.tool(description="Search for places using Naver's local database with pagination and sorting options.")
async def localSearch(
  query: str = Field(description="Search query (e.g., '강남역 맛집', '서울 카페')", min_length=1),
  display: int = Field(5, description="Number of results to display (max: 5)", ge=1, le=5),
  sort: Literal["random", "comment"] = Field(
    "random",
    description="Sort method - random: by relevance, comment: by review count (descending)",
  ),
  start: int = Field(1, description="Starting position for pagination (default: 1)", ge=1),
) -> LocalSearchResponse | Dict:
  """
  Search for local places using Naver Search API.
  
  Returns:
    LocalSearchResponse: Contains total, start, display, and items list
    Each item includes: title, link, category, description, address, roadAddress, mapx, mapy
    Coordinates (mapx, mapy) are in Naver's scaled format (divide by 10,000,000 for actual coordinates)
  """
  try:
    return await naver_maps_client.searchForLocalInformation(query, display, sort, start)
  except Exception as ex:
    return {"success": False, "error": str(ex)}


@mcp.tool(description="Find places within a specific radius from coordinates using distance-based filtering.")
async def localSearchByCoordinate(
  query: str = Field(description="Search query with regional context (e.g., '강남역 근처 카페', '역삼동 맛집')", min_length=1),
  longitude: float = Field(description="Center longitude in decimal degrees (e.g., 126.9707 for Seoul Station)"),
  latitude: float = Field(description="Center latitude in decimal degrees (e.g., 37.5536 for Seoul Station)"),
  radius: int = Field(1000, description="Search radius in meters (default: 1000m = 1km, max: 10km)", ge=1, le=10000),
  display: int = Field(5, description="Maximum results to return (max: 5)", ge=1, le=5),
  sort: Literal["random", "comment"] = Field(
    "random",
    description="Sort method - random: by relevance, comment: by review count",
  ),
  min_results: int = Field(1, description="Minimum results to find before stopping search (default: 1)", ge=1, le=5),
) -> LocalSearchResponse | Dict:
  """
  Search for places within a specific radius from coordinates.
  
  This function:
  1. Performs multiple localSearch calls across pages
  2. Filters results by calculating actual distance using Haversine formula
  3. Continues searching until min_results found or max 10 pages searched
  4. Returns only places within the specified radius
  
  Returns:
    LocalSearchResponse: Filtered results within radius, with actual coordinates and distance calculations
    Includes search statistics in logs for debugging
  """
  try:
    # 입력 파라미터 로깅
    input_params = {
      "query": query,
      "longitude": longitude,
      "latitude": latitude,
      "radius": radius,
      "display": display,
      "sort": sort,
      "min_results": min_results
    }
    logger.info(f"localSearchByCoordinate - Input: {json.dumps(input_params, ensure_ascii=False)}")
    
    filtered_items = []
    start = 1
    max_attempts = 10  # 최대 10페이지까지만 검색
    search_stats = {"pages_searched": 0, "total_items_found": 0, "filtered_items": 0}
    
    while len(filtered_items) < min_results and start <= max_attempts:
      # 검색 수행
      response = await naver_maps_client.searchForLocalInformation(query, display, sort, start)
      search_stats["pages_searched"] += 1
      
      # 중간 조회 결과 로깅
      logger.info(f"localSearchByCoordinate - Page {start} results: total={response.total}, items={len(response.items)}")
      if response.items:
        items_dict = [item.dict() for item in response.items]
        logger.info(f"localSearchByCoordinate - Page {start} items: {json.dumps(items_dict, ensure_ascii=False)}")
      
      if not response.items:
        break
      
      search_stats["total_items_found"] += len(response.items)
      
      # 좌표 기반 필터링
      for item in response.items:
        if hasattr(item, 'mapx') and hasattr(item, 'mapy'):
          item_lon = float(item.mapx) / 10_000_000
          item_lat = float(item.mapy) / 10_000_000
          
          # 거리 계산 (Haversine 공식)
          distance = calculate_distance(longitude, latitude, item_lon, item_lat)
          
          # 반경 내에 있는 항목만 추가
          if distance <= radius:
            filtered_items.append(item)
            search_stats["filtered_items"] += 1
      
      # 다음 페이지로
      start += 1
      
      # 충분한 결과를 찾았거나 더 이상 결과가 없으면 종료
      if len(filtered_items) >= min_results or response.total <= (start-1) * display:
        break
    
    # 결과 구성
    result = LocalSearchResponse(
      total=len(filtered_items),
      start=1,
      display=len(filtered_items),
      items=filtered_items[:display]
    )
    
    # 출력 결과 로깅
    output_summary = {
      "total_results": len(filtered_items),
      "displayed_results": min(len(filtered_items), display),
      "search_stats": search_stats
    }
    logger.info(f"localSearchByCoordinate - Output: {json.dumps(output_summary, ensure_ascii=False)}")
    
    # 검색된 항목 로깅
    if filtered_items:
      filtered_items_dict = [item.dict() for item in filtered_items[:display]]
      logger.info(f"localSearchByCoordinate - Found items: {json.dumps(filtered_items_dict, ensure_ascii=False)}")
    
    return result
  except Exception as ex:
    error_msg = str(ex)
    logger.error(f"localSearchByCoordinate - Error: {error_msg}")
    return {"success": False, "error": error_msg}


def calculate_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
  """
  두 지점 간의 거리를 미터 단위로 계산 (Haversine 공식)
  """
  R = 6371000  # 지구 반경 (미터)
  
  # 라디안으로 변환
  lat1_rad = math.radians(lat1)
  lon1_rad = math.radians(lon1)
  lat2_rad = math.radians(lat2)
  lon2_rad = math.radians(lon2)
  
  # 위도와 경도의 차이
  dlat = lat2_rad - lat1_rad
  dlon = lon2_rad - lon1_rad
  
  # Haversine 공식
  a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  distance = R * c
  
  return distance