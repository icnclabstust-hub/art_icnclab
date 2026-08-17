#!/usr/bin/env python3
"""
統一RAG管理API
提供REST API接口來管理所有RAG組件
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import asdict

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from integrated_rag_optimizer import IntegratedRAGOptimizer, RAGStrategy, RAGQueryResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic 模型定義
class QueryRequest(BaseModel):
    query: str = Field(..., description="查詢文本")
    strategy: Optional[str] = Field(None, description="指定RAG策略")
    top_k: Optional[int] = Field(5, description="返回結果數量")
    include_sources: bool = Field(True, description="是否包含來源信息")
    timeout: Optional[int] = Field(30, description="超時時間(秒)")

class BatchQueryRequest(BaseModel):
    queries: List[str] = Field(..., description="查詢列表")
    strategy: Optional[str] = Field(None, description="統一RAG策略")
    max_parallel: int = Field(3, description="最大並行數")

class ConfigUpdateRequest(BaseModel):
    vector_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    graph_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    top_k_vector: Optional[int] = Field(None, ge=1, le=50)
    top_k_graph: Optional[int] = Field(None, ge=1, le=20)
    enable_cache: Optional[bool] = None
    cache_max_size: Optional[int] = Field(None, ge=100, le=10000)

class QueryResponse(BaseModel):
    success: bool
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    strategy_used: str
    processing_time: float
    confidence_score: float
    cache_hit: bool = False
    metadata: Dict[str, Any] = {}

class SystemStatusResponse(BaseModel):
    timestamp: str
    components: Dict[str, str]
    configuration: Dict[str, Any]
    performance: Dict[str, Any]
    cache_stats: Dict[str, Any]
    strategy_performance: Dict[str, Any]

# FastAPI 應用初始化
app = FastAPI(
    title="藝術史RAG統一管理API",
    description="整合多模態RAG系統的統一管理接口",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全域變量
rag_optimizer: Optional[IntegratedRAGOptimizer] = None

@app.on_event("startup")
async def startup_event():
    """應用啟動時初始化RAG優化器"""
    global rag_optimizer
    try:
        logger.info("🚀 初始化RAG統一管理系統...")
        rag_optimizer = IntegratedRAGOptimizer()

        if rag_optimizer.initialize_components():
            logger.info("✅ RAG系統初始化成功")
        else:
            logger.error("❌ RAG系統初始化失敗")
    except Exception as e:
        logger.error(f"❌ 啟動失敗: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉時清理資源"""
    global rag_optimizer
    if rag_optimizer:
        rag_optimizer.cleanup()
        logger.info("✅ RAG系統資源清理完成")

# API 端點定義

@app.get("/")
async def root():
    """根端點"""
    return {
        "service": "藝術史RAG統一管理API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康檢查"""
    global rag_optimizer

    if not rag_optimizer:
        raise HTTPException(status_code=503, detail="RAG系統未初始化")

    status = rag_optimizer.get_system_status()

    # 檢查組件狀態
    all_ready = all(
        status == "ready" for status in status["components"].values()
        if status != "disabled"
    )

    return {
        "status": "healthy" if all_ready else "degraded",
        "components": status["components"],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/query", response_model=QueryResponse)
async def single_query(request: QueryRequest):
    """單個查詢處理"""
    global rag_optimizer

    if not rag_optimizer:
        raise HTTPException(status_code=503, detail="RAG系統未初始化")

    try:
        # 準備查詢參數
        query_kwargs = {}
        if request.strategy:
            query_kwargs["strategy"] = request.strategy
        if request.top_k:
            query_kwargs["top_k"] = request.top_k

        # 執行查詢
        result = await rag_optimizer.query(request.query, **query_kwargs)

        # 構造響應
        response = QueryResponse(
            success=True,
            query=result.query,
            answer=result.answer,
            sources=result.sources if request.include_sources else [],
            strategy_used=result.strategy_used.value,
            processing_time=result.processing_time,
            confidence_score=result.confidence_score,
            cache_hit=result.cache_hit,
            metadata=result.metadata
        )

        return response

    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="查詢超時")
    except Exception as e:
        logger.error(f"❌ 查詢處理失敗: {e}")
        raise HTTPException(status_code=500, detail=f"查詢處理失敗: {str(e)}")

@app.post("/query/batch")
async def batch_query(request: BatchQueryRequest):
    """批次查詢處理"""
    global rag_optimizer

    if not rag_optimizer:
        raise HTTPException(status_code=503, detail="RAG系統未初始化")

    if len(request.queries) > 20:
        raise HTTPException(status_code=400, detail="批次查詢數量不能超過20")

    try:
        # 準備查詢參數
        query_kwargs = {}
        if request.strategy:
            query_kwargs["strategy"] = request.strategy

        # 執行批次查詢
        results = await rag_optimizer.batch_query(request.queries, **query_kwargs)

        # 構造響應
        responses = []
        for result in results:
            response = {
                "success": result.confidence_score > 0,
                "query": result.query,
                "answer": result.answer,
                "strategy_used": result.strategy_used.value,
                "processing_time": result.processing_time,
                "confidence_score": result.confidence_score,
                "cache_hit": result.cache_hit
            }
            responses.append(response)

        return {
            "success": True,
            "total_queries": len(request.queries),
            "successful_queries": sum(1 for r in responses if r["success"]),
            "results": responses,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 批次查詢失敗: {e}")
        raise HTTPException(status_code=500, detail=f"批次查詢失敗: {str(e)}")

@app.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """獲取系統狀態"""
    global rag_optimizer

    if not rag_optimizer:
        raise HTTPException(status_code=503, detail="RAG系統未初始化")

    try:
        status = rag_optimizer.get_system_status()

        return SystemStatusResponse(
            timestamp=status["timestamp"],
            components=status["components"],
            configuration=status["configuration"],
            performance=status["performance"],
            cache_stats=status["cache_stats"],
            strategy_performance=status["strategy_performance"]
        )

    except Exception as e:
        logger.error(f"❌ 獲取系統狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取系統狀態失敗: {str(e)}")

@app.post("/system/optimize")
async def optimize_system(background_tasks: BackgroundTasks):
    """執行系統優化"""
    global rag_optimizer

    if not rag_optimizer:
        raise HTTPException(status_code=503, detail="RAG系統未初始化")

    try:
        # 在後台執行優化
        def run_optimization():
            optimization_report = rag_optimizer.optimize_configuration()
            logger.info(f"✅ 系統優化完成: {len(optimization_report['optimizations_applied'])} 項調整")
            return optimization_report

        background_tasks.add_task(run_optimization)

        return {
            "success": True,
            "message": "系統優化已啟動，將在後台執行",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 系統優化失敗: {e}")
        raise HTTPException(status_code=500, detail=f"系統優化失敗: {str(e)}")

@app.put("/system/config")
async def update_configuration(request: ConfigUpdateRequest):
    """更新系統配置"""
    global rag_optimizer

    if not rag_optimizer:
        raise HTTPException(status_code=503, detail="RAG系統未初始化")

    try:
        config = rag_optimizer.config
        updated_fields = []

        # 更新配置字段
        if request.vector_weight is not None:
            config.vector_weight = request.vector_weight
            config.graph_weight = 1.0 - request.vector_weight
            updated_fields.append("vector_weight")

        if request.graph_weight is not None:
            config.graph_weight = request.graph_weight
            config.vector_weight = 1.0 - request.graph_weight
            updated_fields.append("graph_weight")

        if request.top_k_vector is not None:
            config.top_k_vector = request.top_k_vector
            updated_fields.append("top_k_vector")

        if request.top_k_graph is not None:
            config.top_k_graph = request.top_k_graph
            updated_fields.append("top_k_graph")

        if request.enable_cache is not None:
            config.enable_cache = request.enable_cache
            updated_fields.append("enable_cache")

        if request.cache_max_size is not None:
            config.cache_max_size = request.cache_max_size
            updated_fields.append("cache_max_size")

        # 驗證權重總和
        if abs(config.vector_weight + config.graph_weight - 1.0) > 0.001:
            raise ValueError("向量權重和圖譜權重總和必須為1.0")

        return {
            "success": True,
            "message": f"配置更新成功，共更新 {len(updated_fields)} 個字段",
            "updated_fields": updated_fields,
            "current_config": {
                "vector_weight": config.vector_weight,
                "graph_weight": config.graph_weight,
                "top_k_vector": config.top_k_vector,
                "top_k_graph": config.top_k_graph,
                "enable_cache": config.enable_cache,
                "cache_max_size": config.cache_max_size
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 配置更新失敗: {e}")
        raise HTTPException(status_code=400, detail=f"配置更新失敗: {str(e)}")

@app.get("/system/performance")
async def get_performance_metrics():
    """獲取性能指標"""
    global rag_optimizer

    if not rag_optimizer:
        raise HTTPException(status_code=503, detail="RAG系統未初始化")

    try:
        current_stats = rag_optimizer.monitor.get_current_stats()

        return {
            "success": True,
            "metrics": current_stats,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 獲取性能指標失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取性能指標失敗: {str(e)}")

@app.get("/system/strategies")
async def get_available_strategies():
    """獲取可用的RAG策略"""
    return {
        "success": True,
        "strategies": [
            {
                "name": strategy.value,
                "description": {
                    "vector_only": "純向量檢索，適合內容相似性查詢",
                    "graph_only": "純知識圖譜檢索，適合關係和結構化查詢",
                    "hybrid_balanced": "平衡混合策略，適合大多數查詢",
                    "adaptive": "自適應策略，基於歷史性能選擇",
                    "specialized": "專門化策略，基於查詢類型自動選擇",
                    "advanced_rag": "Advanced RAG多級檢索，包含查詢擴展和重排序",
                    "self_rag": "Self-RAG自我反思策略，具備質量評估和迭代改進",
                    "agentic_rag": "Agentic RAG智能代理策略，具備多步推理和自主決策能力",
                    "naive_rag": "Naive RAG最簡單策略，基礎關鍵詞匹配，極速響應"
                }.get(strategy.value, "暫無描述")
            }
            for strategy in RAGStrategy
        ],
        "default_strategy": "hybrid_balanced",
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/system/cache")
async def clear_cache():
    """清空查詢快取"""
    global rag_optimizer

    if not rag_optimizer:
        raise HTTPException(status_code=503, detail="RAG系統未初始化")

    try:
        cache_size_before = len(rag_optimizer.query_cache)
        rag_optimizer.query_cache.clear()
        rag_optimizer.cache_stats = {"hits": 0, "misses": 0, "total": 0}

        return {
            "success": True,
            "message": f"快取清空成功，清除 {cache_size_before} 個快取項目",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 清空快取失敗: {e}")
        raise HTTPException(status_code=500, detail=f"清空快取失敗: {str(e)}")

# 主程序
def create_app():
    """創建FastAPI應用"""
    return app

if __name__ == "__main__":
    print("🚀 啟動藝術史RAG統一管理API...")
    print("📚 API文檔: http://localhost:8002/docs")
    print("🔄 健康檢查: http://localhost:8002/health")

    uvicorn.run(
        "unified_rag_manager:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )