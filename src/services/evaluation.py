import json
import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import select
from src.core.database import AsyncSessionLocal
from src.services.audit_logger import AuditLog
from src.models.evaluation import EvaluationReport
from src.services.factory import LLMFactory
from src.core.config import settings

class EvaluationService:
    def __init__(self):
        self.llm = LLMFactory.get_provider()

    async def run_evaluation(self, tenant_id: str) -> str:
        """
        Runs evaluation on shadow logs for a tenant and generates an EvaluationReport.
        Returns the report ID.
        """
        # 1. Fetch shadow logs
        async with AsyncSessionLocal() as db:
            stmt = select(AuditLog).where(
                AuditLog.tenant_id == tenant_id,
                AuditLog.action == "evaluation_shadow_log"
            ).order_by(AuditLog.created_at.desc()).limit(50)  # Limit to most recent 50 for report
            
            result = await db.execute(stmt)
            logs = result.scalars().all()
            
            if not logs:
                return None

            eval_items = [log.payload for log in logs]
            results = []
            
            # 2. Batch score via LLM (simulated batching)
            for item in eval_items:
                score = await self._score_triplet(item["query"], item["contexts"], item["answer"])
                results.append(score)

            # 3. Aggregate results
            report_id = str(uuid.uuid4())
            agg = self._aggregate_scores(results)
            summary_md = self._generate_markdown_report(tenant_id, agg, results)

            # 4. Save report
            report = EvaluationReport(
                id=report_id,
                tenant_id=tenant_id,
                avg_faithfulness=agg["faithfulness"],
                avg_answer_relevance=agg["relevance"],
                avg_context_precision=agg["precision"],
                report_json=results,
                summary_md=summary_md
            )
            db.add(report)
            await db.commit()
            
            return report_id

    async def _score_triplet(self, query: str, contexts: List[str], answer: str) -> Dict[str, Any]:
        """G-Eval style scoring."""
        context_str = "\n\n".join(contexts)
        
        prompt = f"""
        Evaluate the following RAG triplet based on Faithfulness, Relevance, and Context Precision.
        Give each a score from 0.0 to 1.0.
        
        Query: {query}
        Contexts: {context_str}
        Answer: {answer}
        
        Return ONLY a JSON object with keys: "faithfulness", "relevance", "precision", "feedback".
        """
        
        try:
            response = await self.llm.generate(prompt)
            # Basic JSON extraction
            import re
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
            
        return {"faithfulness": 0.0, "relevance": 0.0, "precision": 0.0, "feedback": "Failed to evaluate"}

    def _aggregate_scores(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        count = len(results)
        if count == 0:
            return {"faithfulness": 0.0, "relevance": 0.0, "precision": 0.0}
            
        return {
            "faithfulness": sum(r.get("faithfulness", 0) for r in results) / count,
            "relevance": sum(r.get("relevance", 0) for r in results) / count,
            "precision": sum(r.get("precision", 0) for r in results) / count,
        }

    def _generate_markdown_report(self, tenant_id: str, agg: Dict[str, float], details: List[Dict[str, Any]]) -> str:
        report = f"# RAG Evaluation Report - Tenant: {tenant_id}\n\n"
        report += f"**Date**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
        
        report += "## Aggregate Scores\n"
        report += f"- **Faithfulness**: {agg['faithfulness']:.2f}\n"
        report += f"- **Answer Relevance**: {agg['relevance']:.2f}\n"
        report += f"- **Context Precision**: {agg['precision']:.2f}\n\n"
        
        report += "## Critical Findings\n"
        for i, res in enumerate(details):
            if res.get("faithfulness", 1.0) < 0.7 or res.get("relevance", 1.0) < 0.7:
                report += f"### Sample {i+1} Alert\n"
                report += f"- **Issue**: Low score detected.\n"
                report += f"- **Feedback**: {res.get('feedback', 'N/A')}\n\n"
                
        return report

evaluation_service = EvaluationService()
