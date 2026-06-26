"""
Week 7: Cost Optimization & Feedback Loop Starter Template

Implement three systems:
1. CostAnalyzer - analyze and track query costs
2. OptimizationStrategy - optimize costs through caching, model selection, etc.
3. FeedbackLoop - collect and validate user corrections
"""

import json
import logging
from typing import Dict, List, Any
from datetime import datetime
import statistics
from transformers import pipeline
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer # Edit made by Claude Sonnet 4.6
from sentence_transformers import CrossEncoder
from app_starter import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# TASK 1: Implement CostAnalyzer
# ============================================================================


class CostAnalyzer:
    """Analyze and track query costs by component."""

    def __init__(self):
        """Initialize cost analyzer.

        TODO: Initialize empty query history list
        """
        self.query_history = []

    def record_query(self, query: Dict[str, Any]):
        """Record a query and its cost breakdown.

        TODO: Store query dict with fields:
        - query_text: the user's question
        - retrieval_cost: cost of retrieving documents
        - llm_input_cost: input cost of LLM inference
        - llm_output_cost: output cost of LLM inference
        - llm_cost: cost of LLM inference
        - tool_cost: cost of tool calls
        - error_cost: cost of retries/errors
        - total_cost: sum of above
        - timestamp: when query was run (use datetime.utcnow().isoformat())
        """
        # TODO: implement
        self.query_history.append(query)

    def get_cost_breakdown(self) -> Dict[str, Any]:
        """Get breakdown of costs by component.

        TODO: Calculate totals for all queries:
        - retrieval_total
        - llm_total
        - tool_total
        - error_total
        - total_daily (sum of all)
        - query_count

        Return dict with these totals
        """
        # TODO: implement

        # Initialize the dict with these totals
        cost_breakdown = {}
        cost_breakdown["retrieval_total"] = 0.0
        cost_breakdown["llm_input_total"] = 0.0
        cost_breakdown["llm_output_total"] = 0.0
        cost_breakdown["llm_total"] = 0.0
        cost_breakdown["tool_total"] = 0.0
        cost_breakdown["error_total"] = 0.0
        cost_breakdown["query_count"] = 0

        # Update these total costs and the query count based on the queries stored in the query history
        for query in self.query_history:
            cost_breakdown["retrieval_total"] += query["retrieval_cost"]
            cost_breakdown["llm_input_total"] += query["llm_input_cost"]
            cost_breakdown["llm_output_total"] += query["llm_output_cost"]
            cost_breakdown["llm_total"] += query["llm_cost"]
            cost_breakdown["tool_total"] += query["tool_cost"]
            cost_breakdown["error_total"] += query["error_cost"]
            cost_breakdown["query_count"] += 1
        # Assuming that the total_daily field is the sum of the retrieval_total, llm_total, tool_total, and error_total fields
        cost_breakdown["total_daily"] = cost_breakdown["retrieval_total"] + cost_breakdown["llm_total"] + cost_breakdown["tool_total"] + cost_breakdown["error_total"]

        # Return the dict with these totals
        return cost_breakdown

    def identify_cost_spikes(self) -> List[Dict]:
        """Identify unusually expensive queries.

        TODO: Find statistical outliers:
        1. Calculate mean and standard deviation of query costs
        2. Find queries > mean + 2*stdev
        3. Return list of spike queries with details
        """
        # TODO: implement

        # 1. Calculate mean and standard deviation of query costs
        cost_breakdown = self.get_cost_breakdown()

        # Calculate the means for each component
        means = {}
        means["retrieval_cost"] = cost_breakdown["retrieval_total"]/cost_breakdown["query_count"]
        means["llm_cost"] = cost_breakdown["llm_total"]/cost_breakdown["query_count"]
        means["tool_cost"] = cost_breakdown["tool_total"]/cost_breakdown["query_count"]
        means["error_cost"] = cost_breakdown["error_total"]/cost_breakdown["query_count"]
        means["total_cost"] = cost_breakdown["total_daily"]/cost_breakdown["query_count"]

        # Calculate the standard deviations for each component
        retrieval_cost_data = []
        llm_cost_data = []
        tool_cost_data = []
        error_cost_data = []
        total_cost_data = []
        for query in self.query_history:
            retrieval_cost_data.append(query["retrieval_cost"])
            llm_cost_data.append(query["llm_cost"])
            tool_cost_data.append(query["tool_cost"])
            error_cost_data.append(query["error_cost"])
            total_cost_data.append(query["total_cost"])
        standard_deviations = {}
        standard_deviations["retrieval_cost"] = statistics.stdev(retrieval_cost_data)
        standard_deviations["llm_cost"] = statistics.stdev(llm_cost_data)
        standard_deviations["tool_cost"] = statistics.stdev(tool_cost_data)
        standard_deviations["error_cost"] = statistics.stdev(error_cost_data)
        standard_deviations["total_cost"] = statistics.stdev(total_cost_data)

        # 2. Find queries > mean + 2*stdev
        spike_queries = []
        for index, query in enumerate(self.query_history):
            components_to_flag = []
            if query["retrieval_cost"] > means["retrieval_cost"] + 2*standard_deviations["retrieval_cost"]:
                components_to_flag.append("retrieval cost")
            if query["llm_cost"] > means["llm_cost"] + 2*standard_deviations["llm_cost"]:
                components_to_flag.append("llm cost")
            if query["tool_cost"] > means["tool_cost"] + 2*standard_deviations["tool_cost"]:
                components_to_flag.append("tool cost")
            if query["error_cost"] > means["error_cost"] + 2*standard_deviations["error_cost"]:
                components_to_flag.append("error cost")
            if query["total_cost"] > means["total_cost"] + 2*standard_deviations["total_cost"]:
                components_to_flag.append("total cost")
            if len(components_to_flag) == 0:
                continue
            details = f"Query #{index} is unusually expensive in terms of "
            for i, component in enumerate(components_to_flag):
                if i == len(components_to_flag) - 1 and len(components_to_flag) > 1:
                    details += f"and {component}."
                elif i == len(components_to_flag) - 1 and len(components_to_flag) == 1:
                    details += f"{component}."
                elif len(components_to_flag) > 2:
                    details += f"{component}, "
                else:
                    details += f"{component} "
            spike_query = {}
            spike_query["query_history_index"] = index
            spike_query["query"] = query
            spike_query["details"] = details
            spike_queries.append(spike_query)
            
        # 3. Return list of spike queries with details
        return spike_queries


# ============================================================================
# TASK 2: Implement OptimizationStrategy
# ============================================================================


class OptimizationStrategy:
    """Optimize agent costs through multiple strategies."""

    def __init__(self):
        """Initialize optimization strategy.

        TODO: Initialize cache and strategy tracking
        """
        self.cache = {}  # {query: response}
        self.strategies_applied = []

        # Initialize a classifier for determining the complexity of a query.
        self.query_complexity_classifier = pipeline("zero-shot-classification", model="cross-encoder/nli-deberta-v3-small")

        # Initialize a dictionary that stores the savings estimate per strategy.
        self.breakdown = {}

        # Keep track of the number of total calls to the caching method as well as the number of cache hits.
        self.cache_calls = 0
        self.cache_hits = 0

    def apply_caching(self, query: str, response: str) -> tuple:
        """Cache query responses.

        TODO: Implement caching
        1. If query in cache, return (True, cached_response)
        2. Otherwise, store in cache and return (False, response)

        Args:
            query: user's question
            response: LLM's answer

        Returns:
            (is_cached_hit, response)
        """
        # TODO: implement

        # Record as strategy applied if not already recorded.
        self.cache_calls += 1
        if not("apply_caching" in self.strategies_applied):
            self.strategies_applied.append("apply_caching")

        # 1. If query in cache, return (True, cached_response)
        if query in self.cache:
            self.cache_hits += 1
            return (True, self.cache[query])
        
        # 2. Otherwise, store in cache and return (False, response)
        self.cache[query] = response

        return (False, response)

    def optimize_retrieval_count(self, num_docs: int) -> int:
        """Reduce number of documents retrieved.

        TODO: Reduce count intelligently
        - Input 15 docs → output 3 docs (top-k)
        - Reduces token cost

        Args:
            num_docs: original document count

        Returns:
            optimized document count
        """
        # TODO: implement

        # Record as strategy applied if not already recorded.
        if not("optimize_retrieval_count" in self.strategies_applied):
            self.strategies_applied.append("optimize_retrieval_count")
            self.breakdown["optimize_retrieval_count"] = 80.0

        return max(1, num_docs // 5)  # Simple: reduce by 5x

    def select_model_by_complexity(self, query: str) -> str:
        """Choose cheaper model for simple queries.

        TODO: Analyze query complexity
        - Simple queries ("What is X?") → "gemini-2.5-flash-lite" (cheaper, faster)
        - Complex queries ("Analyze...", "Compare...", "Design...") → gemini-3.1-flash-lite

        Args:
            query: user's question

        Returns:
            model name to use
        """
        # TODO: implement

        # Record as strategy applied if not already recorded.
        if not("select_model_by_complexity" in self.strategies_applied):
            self.strategies_applied.append("select_model_by_complexity")
            gemini_3_1_flash_lite_input_price_paid_tier_per_one_mil_tokens = 0.25
            gemini_3_1_flash_lite_output_price_paid_tier_per_one_mil_tokens = 1.50
            gemini_2_5_flash_lite_input_price_paid_tier_per_one_mil_tokens = 0.10
            gemini_2_5_flash_lite_output_price_paid_tier_per_one_mil_tokens = 0.40

            input_pct_reduction = 100*(gemini_3_1_flash_lite_input_price_paid_tier_per_one_mil_tokens - gemini_2_5_flash_lite_input_price_paid_tier_per_one_mil_tokens)/gemini_3_1_flash_lite_input_price_paid_tier_per_one_mil_tokens
            output_pct_reduction = 100*(gemini_3_1_flash_lite_output_price_paid_tier_per_one_mil_tokens - gemini_2_5_flash_lite_output_price_paid_tier_per_one_mil_tokens)/gemini_3_1_flash_lite_output_price_paid_tier_per_one_mil_tokens

            self.breakdown["select_model_by_complexity_input"] = input_pct_reduction
            self.breakdown["select_model_by_complexity_output"] = output_pct_reduction

        # Perform a basic check for simple question types in the query and return "gemini-2.5-flash-lite" right away if any are there.
        if "What is" in query or "Who is" in query or "Where is" in query or "When is" in query:
            return "gemini-2.5-flash-lite"

        # Perform a basic check for complex question types in the query and return "gemini-3.1-flash-lite" right away if any are there.
        if "Analyze" in query or "Compare" in query or "Design" in query:
            return "gemini-3.1-flash-lite"

        # If none of the basic checks pass, use nli-deberta-v3-small to determine whether the query is simple or complex.
        # Based on HuggingFace documentation: https://huggingface.co/cross-encoder/nli-deberta-v3-small 
        complexity_values = ["Simple query", "Complex query"]
        complexity_value = self.query_complexity_classifier(query, complexity_values)["labels"][0] # ["labels"][0] added due to debugging suggestion from Claude Sonnet 4.6
        if complexity_value == "Simple query":
            return "gemini-2.5-flash-lite"
        return "gemini-3.1-flash-lite"

    def enable_response_compression(self, response: str) -> str:
        """Compress long responses while keeping essential info.

        TODO: Reduce response length
        1. Split into sentences
        2. Keep only first N essential sentences
        3. Return compressed response

        Args:
            response: original response

        Returns:
            compressed response
        """
        # TODO: implement

        # Record the number of sentences in the response.
        sentences = response.split(".")
        num_sentences = len(sentences)
        n = 2

        # Record as strategy applied if not already recorded.
        if not("enable_response_compression" in self.strategies_applied):
            self.strategies_applied.append("enable_response_compression")
            self.breakdown["enable_response_compression"] = 100*(1.0 - float(n)/float(num_sentences))

        # Determine the top N most important sentences, append them, and return them as the compressed response (utilize the sumy library in order to achieve this).
        # sumy documentation: https://pypi.org/project/sumy/
        # sumy repo TextRankSummarizer class: https://github.com/miso-belica/sumy/blob/main/sumy/summarizers/text_rank.py
        parser = PlaintextParser.from_string(response, Tokenizer("english"))
        txt_rank_summarizer = TextRankSummarizer()
        compressed_response_sentences = txt_rank_summarizer(parser.document, n)
        compressed_response = ""
        for i, sentence in enumerate(compressed_response_sentences):
            compressed_response += str(sentence)
            if i < len(compressed_response_sentences) - 1:
                compressed_response += " "
        return compressed_response

    def get_optimization_impact(self, cost_analyzer: CostAnalyzer) -> Dict[str, Any]:
        """Estimate cost savings from applied optimizations.

        TODO: Return impact analysis:
        - total_savings_pct: estimated % cost reduction
        - strategies_applied: list of which strategies used
        - breakdown: savings estimate per strategy
        """
        # TODO: implement

        # Store the hit rate if caching was applied as a strategy.
        if "apply_caching" in self.strategies_applied:
            self.breakdown["apply_caching"] = self.cache_hits/self.cache_calls

        # Get the cost breakdown and the necessary percent contributions to the total cost.
        cost_breakdown = cost_analyzer.get_cost_breakdown()
        retrieval_cost_pct_contribution = cost_breakdown["retrieval_total"]/cost_breakdown["total_daily"]
        llm_cost_pct_contribution = cost_breakdown["llm_total"]/cost_breakdown["total_daily"]
        llm_output_cost_pct_contribution = cost_breakdown["llm_output_total"]/cost_breakdown["total_daily"]
        
        # Weight the savings estimates per strategy as appropriate.
        weighted_apply_caching_savings = self.breakdown["apply_caching"]
        weighted_optimize_retrieval_count_savings = retrieval_cost_pct_contribution*self.breakdown["optimize_retrieval_count"]
        weighted_select_model_by_complexity_savings = llm_cost_pct_contribution*(self.breakdown["select_model_by_complexity_input"] + self.breakdown["select_model_by_complexity_output"])
        weighted_enable_response_compression_savings = llm_output_cost_pct_contribution*self.breakdown["enable_response_compression"]
        
        # Calculate the estimated % cost reduction.
        total_savings_pct = weighted_apply_caching_savings + weighted_optimize_retrieval_count_savings + weighted_select_model_by_complexity_savings + weighted_enable_response_compression_savings
        
        # Return the estimated % cost reduction, list of which strategies used, and the savings estimate per strategy.
        return {
            "total_savings_pct": total_savings_pct,
            "strategies_applied": self.strategies_applied,
            "breakdown": self.breakdown,
        }


# ============================================================================
# TASK 3: Implement FeedbackLoop
# ============================================================================


class FeedbackLoop:
    """Collect and validate user corrections for continuous improvement."""

    def __init__(self):
        """Initialize feedback loop.

        TODO: Initialize corrections list, a list corresponding to the original versions of the corrections, a list corresponding to the roles of the users proposing the corrections, and validation rules
        """
        self.corrections = []
        self.original_versions = []
        self.roles_of_users_proposing_corrections = []
        # Authority hierarchy for role-based validation
        self.authority = {
            "engineer": 1,
            "hr": 2,
            "finance": 2,
            "manager": 3,
            "executive": 4,
        }
        # Initialize a classifier for determining how two statements relate to each other (entailment, contradiction, neutral).
        self.relation_classifier = CrossEncoder("cross-encoder/nli-deberta-v3-small")

        # Initialize a classifier for determining what type of information the correction pertains to.
        self.information_type = pipeline("zero-shot-classification", model="cross-encoder/nli-deberta-v3-small")

    def submit_correction(
        self,
        original_query: str,
        original_answer: str,
        corrected_answer: str,
        user_role: str,
    ) -> Dict[str, Any]:
        """Submit a correction to the agent's answer.

        TODO: Validate and store correction
        1. Check user_role has sufficient authority
        2. Check corrected_answer is detailed enough (longer than original)
        3. Store in corrections list
        4. Return acceptance status

        Args:
            original_query: the question
            original_answer: agent's incorrect answer
            corrected_answer: user's correction
            user_role: user's role (for authority check)

        Returns:
            {"accepted": True/False, "reason": "..."}
        """
        # TODO: implement
        
        """
        1. Check user_role has sufficient authority (Criteria set to be level 3 or above to be consistent 
        with the "1. User role has sufficient authority (manager+, i.e. level 3 or above)" comment from
        the validate_correction method).
        """
        has_sufficient_authority = self.authority[user_role] >= 3
        
        # 2. Check corrected_answer is detailed enough (longer than original)
        is_detailed = len(corrected_answer) > len(original_answer)

        # 3. Store in corrections list
        is_accepted = False
        if has_sufficient_authority and is_detailed:
            is_accepted = True
            self.corrections.append(corrected_answer)
            self.original_versions.append(original_answer)
            self.roles_of_users_proposing_corrections.append(user_role)
        
        # 4. Return acceptance status
        reason = ""
        if has_sufficient_authority and is_detailed:
            reason = f"The user has sufficient authority ({self.authority[user_role]}), and the corrected answer is detailed enough."
        if has_sufficient_authority and not(is_detailed):
            reason = f"The user has sufficient authority ({self.authority[user_role]}), but the corrected answer is not detailed enough."
        if not(has_sufficient_authority) and is_detailed:
            reason = f"The user's corrected answer is detailed enough, but the user does not have sufficient authority ({self.authority[user_role]})."
        if not(has_sufficient_authority) and not(is_detailed):  
            reason = f"The user does not have sufficient authority ({self.authority[user_role]}), and the corrected answer is not detailed enough."
        return {"accepted": is_accepted, "reason": reason}

    def validate_correction(self, index: int, agent, user_query) -> bool:
        """Validate a stored correction is accurate.

        TODO: Check correction quality:
        1. User role has sufficient authority (manager+, i.e. level 3 or above)
        2. Correction is more detailed than original
        3. Correction makes sense

        Args:
            index: index into corrections list

        Returns:
            True if correction is valid, False otherwise
        """
        # TODO: implement

        # Get the correction at index
        correction_at_index = self.corrections[index]

        # 1. User role has sufficient authority (manager+, i.e. level 3 or above)
        user_role = self.roles_of_users_proposing_corrections[index]
        has_sufficient_authority = self.authority[user_role] >= 3

        # 2. Correction is more detailed than original
        original_answer = self.original_versions[index]
        is_detailed = len(correction_at_index) > len(original_answer)

        # 3. Correction makes sense

        """
        If the correction is a repitition of the current answer, the correction does not make sense. Perform a basic check to account
        for this condition before reusing tools to verify the correctness of the proposed correction.
        """
        makes_sense = True
        relation_scores = self.relation_classifier.predict([(original_answer, correction_at_index)])
        relation_values = ["Contradiction", "Entailment", "Neutral"]
        relation_value = relation_values[relation_scores.argmax(axis=1)][0]
        if relation_value == "Entailment":
            makes_sense = False
        else:
            """
            Otherwise, perform the query again and assess whether correction is consistent with the new results. If the correction
            is not consistent with the new results, the correction will be considered as not making sense.
            """
            # Add 2 documents to the limit in case the ground truth document was not accounted for in generating the original response to the query.
            response = agent.query(user_query, limit_adder=2)["answer"]
            relation_scores = self.relation_classifier.predict([(response, correction_at_index)])
            relation_values = ["Contradiction", "Entailment", "Neutral"]
            relation_value = relation_values[relation_scores.argmax(axis=1)][0]
            if relation_value == "Contradiction":
                makes_sense = False

        # Return the results of the validation check
        if has_sufficient_authority and is_detailed and makes_sense:
            return True
        return False

    def get_feedback_metrics(self) -> Dict[str, Any]:
        """Compute metrics on feedback quality.

        TODO: Calculate:
        - total_corrections: number of corrections received
        - validation_rate: % of corrections that are valid
        - avg_correction_length: average length of corrections
        - top_error_patterns: most common mistakes corrected

        Returns:
            dict with feedback metrics
        """
        # TODO: implement

        # Initialize the list of mistakes made
        errors_made = {}
        
        # Count the number of valid corrections.
        num_valid_corrections = 0
        for i in range(len(self.corrections)):
            if self.validate_correction(i):
                num_valid_corrections += 1

                # Determine the information type of the correction and append that to the error patterns array.
                information_values = ["Employee Information", "Policy Document (HR)", "Policy Document (Finance)", "Policy Document (Engineering)", "Policy Document (Ops)", "Policy Document (Sales)", "Policy Document (Compliance)", "Policy Document (General)", "Policy Document (Internal)", "Expense Policy"]
                information_value = self.information_type(self.corrections[i], information_values)["labels"][0] # ["labels"][0] added due to debugging suggestion from Claude Sonnet 4.6
                if not(information_value in errors_made):
                    errors_made[information_value] = 1
                else:
                    errors_made[information_value] += 1
        
        # Get the top 3 kinds of error patterns found.
        sorted_error_patterns = sorted(errors_made.keys(), key=lambda k: errors_made[k], reverse=True) # lambda k: errors_made[k] portion added and reverse=True (to make sure error patterns are sorted in descending order) added based on debugging suggestions from Claude Sonnet 4.6
        top_3_error_patterns = []
        if len(sorted_error_patterns) > 3:
            top_3_error_patterns = sorted_error_patterns[:3]
        else:
            top_3_error_patterns = sorted_error_patterns
        
        # Get the total length of the corrections.
        total_length = 0
        for correction in self.corrections:
            total_length += len(correction)
        

        return {
            "total_corrections": len(self.corrections),
            "validation_rate": 100*(num_valid_corrections/len(self.corrections)),
            "avg_correction_length": total_length/len(self.corrections),
            "top_error_patterns": top_3_error_patterns,
        }


if __name__ == "__main__":
    # Basic structure is provided below. Add your own test cases to verify your implementation.
    # Run with: python3 cost_optimization_starter.py
    try:
        # Initialize agent
        agent = Agent("data/techcorp.db", api_key=GOOGLE_API_KEY)
        print("Agent initialized successfully")
        print("---------------------------------------------------------------------------------------------")

        """
        PART 1: CostAnalyzer Testing
        """
        # Test CostAnalyzer
        print("Testing CostAnalyzer...")
        analyzer = CostAnalyzer()
        # TODO: record a query and verify get_cost_breakdown() returns correct totals

        # Perform the Cost Analyzer Query
        print("\Testing Cost Analyzer Query..")
        result1 = agent.query(user_query="Can you summarize the TechCorp Employee Handbook?", user_id="4", user_role="hr")
        print(f"Answer: {result1['answer']}")
        print(f"Tokens: {result1['tokens_used']}")
        print(f"Cost: ${result1['total_cost']:.6f}")

        # Record the query
        analyzer.record_query(result1)

        # Get the totals for get_cost_breakdown()
        totals = analyzer.get_cost_breakdown()

        # Perform tests to verify the correctness of the totals
        print("Tests Results")
        test1 = totals["retrieval_total"] == result1["retrieval_cost"]
        print("test1:", test1)
        test2 = totals["llm_input_total"] == result1["llm_input_cost"]
        print("test2:", test2)
        test3 = totals["llm_output_total"] == result1["llm_output_cost"]
        print("test3:", test3)
        test4 = totals["llm_total"] == result1["llm_cost"]
        print("test4:", test4)
        test5 = totals["tool_total"] == result1["tool_cost"]
        print("test5:", test5)
        test6 = totals["error_total"] == result1["error_cost"]
        print("test6:", test6)
        test7 = totals["query_count"] == 1
        print("test7:", test7)
        test8 = totals["total_daily"] == result1["retrieval_cost"] + result1["llm_cost"] + result1["tool_cost"] + result1["error_cost"]
        print("test8:", test8)
        if test1 and test2 and test3 and test4 and test5 and test6 and test7 and test8:
            print("All tests for CostAnalyzer pass!")
        print("---------------------------------------------------------------------------------------------")


        """
        PART 2: OptimizationStrategy Testing
        """
        # Test OptimizationStrategy
        print("\nTesting OptimizationStrategy...")
        optimizer = OptimizationStrategy()
        # TODO: test apply_caching, select_model_by_complexity, and optimize_retrieval_count

        """
        apply_caching tests
        """
        # When trying to apply caching the first time, the response should not be in the cache to begin with and the response should remain the same
        is_cached_hit, response = optimizer.apply_caching(result1["query_text"], result1["answer"]) # query_text added as suggested by Claude Sonnet 4.6
        test9 = is_cached_hit == False
        print("test9:", test9)
        test10 = response == result1["answer"]
        print("test10:", test10)

        # When trying to apply caching another time, we should get a hit in the cache and the response we cached
        is_cached_hit_2, response_2 = optimizer.apply_caching(result1["query_text"], result1["answer"]) # query_text added as suggested by Claude Sonnet 4.6
        test11 = is_cached_hit_2 == True
        print("test11:", test11)
        test12 = response_2 == response
        print("test12:", test12)

        # Report if all apply_caching tests passed
        all_apply_caching_tests_pass = test9 and test10 and test11 and test12
        if all_apply_caching_tests_pass:
            print("All tests for apply_caching pass!")
        
        """
        select_model_complexity tests
        """
        # Test queries whose model types should be correctly determined from the basic if checks in select_model_by_complexity
        simple_query_1_basic = optimizer.select_model_by_complexity(query="Who is Paul Moss?")
        complex_query_1_basic = optimizer.select_model_by_complexity(query="Analyze the System Architecture Overview?")
        test13 = simple_query_1_basic == "gemini-2.5-flash-lite"
        print("test13:", test13)
        test14 = complex_query_1_basic == "gemini-3.1-flash-lite"
        print("test14:", test14)

        # Test queries whose model types should be correctly determined (not from the basic if checks in select_model_by_complexity but from the nli-deberta-v3-small model.
        simple_query_2_model = optimizer.select_model_by_complexity(query="Please provide the name of our VP Engineering.")
        complex_query_2_model = optimizer.select_model_by_complexity(query="Explore all of our documents on our sales territories and create a comprehensive report.")
        test15 = simple_query_2_model == "gemini-2.5-flash-lite"
        print("test15:", test15)
        test16 = complex_query_2_model == "gemini-3.1-flash-lite"
        print("test16:", test16)

        # Report if all select_model_by_complexity tests passed
        all_select_model_by_complexity_tests_pass = test13 and test14 and test15 and test16
        if all_select_model_by_complexity_tests_pass:
            print("All tests for select_model_by_complexity pass!")

        """
        optimize_retrieval_count tests
        """
        test17 = optimizer.optimize_retrieval_count(0) == 1
        print("test17:", test17)
        test18 = optimizer.optimize_retrieval_count(15) == 3
        print("test18:", test18)
        test19 = optimizer.optimize_retrieval_count(13) == 2
        print("test19:", test19)
        test20 = optimizer.optimize_retrieval_count(1) == 1
        print("test20:", test20)
        test21 = optimizer.optimize_retrieval_count(10) == 2
        print("test21:", test21)
        all_optimize_retrieval_count_tests_pass = test17 and test18 and test19 and test20 and test21
        # Report if all optimize_retrieval_count tests passed
        if all_optimize_retrieval_count_tests_pass:
            print("All tests for optimize_retrieval_count pass!")

        # Report if all OptimizationStrategy tests passed
        if all_select_model_by_complexity_tests_pass and all_optimize_retrieval_count_tests_pass and all_apply_caching_tests_pass:
            print("All tests for OptimizationStrategy pass!")
        print("---------------------------------------------------------------------------------------------")

        """
        PART 3: FeedbackLoop Testing

        AI Citation: Claude Sonnet 4.6 was used to put the necessary escape characters in lines 720, 725, 737, 768, and 769
        """
        # Test FeedbackLoop
        print("\nTesting FeedbackLoop...")
        feedback = FeedbackLoop()
        # TODO: submit corrections with different roles and verify accepted/rejected correctly

        # Test for does not have sufficient authority and does not have enough detail case
        correction_scenario_1 = feedback.submit_correction(
            original_query="Can you summarize the TechCorp handbook?",
            original_answer='TechCorp\'s Employee Handbook outlines the company\'s commitment to being an Equal Opportunity Employer, maintaining a workplace that does not discriminate based on race, color, religion, sex, national origin, age, disability, or other protected characteristics. Furthermore, the handbook specifies that employment at TechCorp is based on an "at-will" status, meaning the employment relationship can be terminated by either the employee or the company at any time.',
            corrected_answer="No longer operates at-will.",
            user_role= "hr",
        )
        test22 = correction_scenario_1["accepted"] == False
        test23 = correction_scenario_1["reason"] == f"The user does not have sufficient authority ({feedback.authority['hr']}), and the corrected answer is not detailed enough."
        print("test22:", test22)
        print("test23:", test23)

        # Test for detailed enough, but does not have sufficient authority case
        correction_scenario_2 = feedback.submit_correction(
            original_query="What is Brian Yang's position at TechCorp?",
            original_answer="Brian Yang is the VP of Engineering at the company.",
            corrected_answer= "Brian Yang does not have a position at TechCorp. He left the company one month ago.",
            user_role= "engineer"
        )
        test24 = correction_scenario_2["accepted"] == False
        test25 = correction_scenario_2["reason"] == f"The user's corrected answer is detailed enough, but the user does not have sufficient authority ({feedback.authority['engineer']})."
        print("test24:", test24)
        print("test25:", test25)

        # Test for has sufficient authority, but does not have enough detail case
        correction_scenario_3 = feedback.submit_correction(
            original_query="What is the expense approval limit for a manager at TechCorp?",
            original_answer="The approval limit for a manager is $5,000.",
            corrected_answer="$10,000.",
            user_role= "executive"
        )
        test26 = correction_scenario_3["accepted"] == False
        test27 = correction_scenario_3["reason"] == f"The user has sufficient authority ({feedback.authority['executive']}), but the corrected answer is not detailed enough."
        print("test26:", test26)
        print("test27:", test27)

        # Test for sufficient authority and enough detail case
        correction_scenario_4 = feedback.submit_correction(
            original_query="What is Austin Gentry's position at TechCorp?",
            original_answer="Austin Gentry is the VP of Sales at the company.",
            corrected_answer="Austin Gentry does not have a position at TechCorp. He left the company one month ago.",
            user_role= "manager"
        )
        test28 = correction_scenario_4["accepted"] == True
        test29 = correction_scenario_4["reason"] == f"The user has sufficient authority ({feedback.authority['manager']}), and the corrected answer is detailed enough."
        print("test28:", test28)
        print("test29:", test29)

        # Test for sufficient authority and enough detail case for a more detailed answer scenario
        correction_scenario_5 = feedback.submit_correction(
            original_query="What is Remote Work Policy?",
            original_answer='TechCorp\'s remote work policy classifies roles as either eligible or ineligible for remote work, with specific exclusions for Office Management, Facilities, and Reception staff due to their requirement for physical presence. Eligible employees may choose between a "Full Remote" arrangement, which requires adherence to core hours of 10am–3pm PT and attendance at quarterly in-person events, or a "Hybrid" model, which involves working from the office on Mondays, Tuesdays, and Wednesdays. While full remote work is available to all eligible staff, the hybrid arrangement is the preferred structure for managers with direct reports.',
            corrected_answer='Actually, with a recent change to the handbook, TechCorp\'s remote work policy classifies all roles as eligible for remote work, across Engineering, Sales, Product, Office Management, Facilities, and Reception staff due to their requirement for physical presence. Eligible employees may choose between a "Full Remote" arrangement, which requires adherence to core hours of 10am–3pm PT and attendance at quarterly in-person events, or a "Hybrid" model, which involves working from the office on Mondays, Tuesdays, and Wednesdays. While full remote work is available to all eligible staff, the hybrid arrangement is the preferred structure for managers with direct reports.',
            user_role= "executive"
        )
        test30 = correction_scenario_5["accepted"] == True
        test31 = correction_scenario_5["reason"] == f"The user has sufficient authority ({feedback.authority['executive']}), and the corrected answer is detailed enough."
        print("test30:", test30)
        print("test31:", test31)

        # Print whether all FeedbackLoop tests pass.
        if test22 and test23 and test24 and test25 and test26 and test27 and test28 and test29 and test30 and test31:
            print("All tests for FeedbackLoop pass!")
        print("---------------------------------------------------------------------------------------------")

    except Exception as e:
        print(f"Error: {e}")
        logger.exception("Error during test")
        sys.exit(1)