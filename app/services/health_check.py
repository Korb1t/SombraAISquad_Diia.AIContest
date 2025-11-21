"""
Health check service
"""
from sqlmodel import Session, text
from app.core.logging import get_logger
from app.core.db import engine
from app.llm.client import get_llm, get_embeddings, get_gemini_client

logger = get_logger(__name__)


class HealthCheckService:
    """Service for checking application health status"""
    
    @staticmethod
    def check_database() -> dict:
        """
        Check database connectivity and pgvector extension
        
        Returns:
            dict with status and details
        """
        try:
            with Session(engine) as session:
                # Check basic connectivity
                result = session.exec(text("SELECT 1")).first()
                if not result:
                    return {"status": "unhealthy", "error": "Database query failed"}
                
                # Check pgvector extension
                try:
                    pgvector_check = session.exec(
                        text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")
                    ).first()
                    has_pgvector = bool(pgvector_check)
                except Exception as e:
                    logger.warning(f"pgvector check failed: {str(e)}")
                    has_pgvector = False
                
                return {
                    "status": "healthy",
                    "pgvector": "enabled" if has_pgvector else "disabled"
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    def check_codemie_api() -> dict:
        """
        Check CodeMie API availability (LLM, Embeddings, Transcription)
        
        All models use the same CodeMie endpoint, so we check each model separately
        
        Returns:
            dict with overall status and details for each model
        """
        result = {
            "status": "healthy",
            "models": {}
        }
        
        # Check LLM
        try:
            llm = get_llm()
            response = llm.invoke("test")
            if response and response.content:
                result["models"]["llm"] = {
                    "status": "healthy",
                    "model": llm.model
                }
            else:
                result["models"]["llm"] = {"status": "unhealthy", "error": "Empty response"}
                result["status"] = "degraded"
        except Exception as e:
            logger.error(f"LLM check failed: {str(e)}")
            result["models"]["llm"] = {"status": "unhealthy", "error": str(e)}
            result["status"] = "degraded"
        
        # Check Embeddings
        try:
            embeddings = get_embeddings()
            emb_result = embeddings.embed_query("test")
            if emb_result and len(emb_result) > 0:
                result["models"]["embeddings"] = {
                    "status": "healthy",
                    "model": embeddings.model,
                    "dimension": len(emb_result)
                }
            else:
                result["models"]["embeddings"] = {"status": "unhealthy", "error": "Empty embedding"}
                result["status"] = "degraded"
        except Exception as e:
            logger.error(f"Embeddings check failed: {str(e)}")
            result["models"]["embeddings"] = {"status": "unhealthy", "error": str(e)}
            result["status"] = "degraded"
        
        # Check Transcription (Gemini)
        try:
            gemini = get_gemini_client()
            if gemini and gemini.client and gemini.model:
                result["models"]["transcription"] = {
                    "status": "healthy",
                    "model": gemini.model.model_name
                }
            else:
                result["models"]["transcription"] = {"status": "unhealthy", "error": "Client initialization failed"}
                result["status"] = "degraded"
        except Exception as e:
            logger.error(f"Transcription check failed: {str(e)}")
            result["models"]["transcription"] = {"status": "unhealthy", "error": str(e)}
            result["status"] = "degraded"
        
        return result
    
    @staticmethod
    def get_overall_status(db_status: dict, codemie_status: dict) -> str:
        """
        Determine overall application status
        
        Args:
            db_status: Database health status
            codemie_status: CodeMie API health status
            
        Returns:
            "healthy" if all critical components are healthy, "degraded" or "unhealthy" otherwise
        """
        # Database is critical
        if db_status.get("status") != "healthy":
            logger.warning("Health check: database is unhealthy")
            return "unhealthy"
        
        # CodeMie API status
        if codemie_status.get("status") == "degraded":
            logger.warning("Health check: some CodeMie models are unavailable")
            return "degraded"
        elif codemie_status.get("status") == "unhealthy":
            logger.error("Health check: CodeMie API is completely unavailable")
            return "unhealthy"
        
        return "healthy"


def get_health_check_service() -> HealthCheckService:
    """Get health check service instance"""
    return HealthCheckService()
