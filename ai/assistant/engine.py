"""AI Assistant Engine: orchestrates guardrail checks, RAG retrieval, and grounded response synthesis."""

from typing import Dict, Any, List, Optional
from ai.assistant.guardrails import AssistantGuardrailChecker, STANDARD_DISCLAIMER
from ai.assistant.rag_knowledge import RAGKnowledgeRetriever
from ai.assistant.context_assembler import PatientContextAssembler

class AIAssistantEngine:
    """Core conversational engine for WellNexa AI Assistant."""

    @staticmethod
    def process_query(
        user_query: str,
        patient_context: str,
        chat_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Evaluate query against guardrails, retrieve knowledge, and generate response with citations."""
        # 1. Check Safety Guardrails First
        guardrail_result = AssistantGuardrailChecker.check_query(user_query)
        if guardrail_result["is_blocked"]:
            return {
                "content": guardrail_result["response"],
                "cited_sources": [],
                "disclaimer": guardrail_result["disclaimer"],
                "is_safety_triggered": True,
            }

        # 2. Retrieve Evidence-Based RAG Knowledge
        rag_snippets = RAGKnowledgeRetriever.retrieve_relevant_snippets(user_query, max_results=2)
        cited_sources = [{"title": s["topic"], "source": s["source"]} for s in rag_snippets]

        # 3. Contextual Synthesis
        response_paragraphs = []

        # Grounding with patient context
        query_low = user_query.lower()
        if "medication" in query_low or "medicine" in query_low or "eat" in query_low or "food" in query_low:
            if "Active Medications:" in patient_context:
                med_line = [l for l in patient_context.split("\n") if "Active Medications:" in l]
                if med_line and "None recorded" not in med_line[0]:
                    response_paragraphs.append(
                        f"Based on your health profile ({med_line[0].strip('- ')}), it is always best to maintain consistency with prescribed timing instructions."
                    )

        # Knowledge integration
        if rag_snippets:
            for s in rag_snippets:
                response_paragraphs.append(s["content"])
        else:
            response_paragraphs.append(
                f"Regarding your question about '{user_query}': Evidence-based health guidance emphasizes balanced nutrition, "
                "consistent hydration, moderate daily physical activity, and adequate restorative sleep as core foundations of vitality."
            )

        # Doctor prep suggestion
        response_paragraphs.append(
            "\n💡 **Suggested question for your doctor**: 'How do these lifestyle measures best fit with my current clinical profile and health targets?'"
        )

        full_content = "\n\n".join(response_paragraphs)

        return {
            "content": full_content,
            "cited_sources": cited_sources,
            "disclaimer": STANDARD_DISCLAIMER,
            "is_safety_triggered": False,
        }
