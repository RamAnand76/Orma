import logging
import time

logger = logging.getLogger("ORMA_TASK_MANAGER")

class TaskManager:
    def __init__(self, engine):
        self.engine = engine # Access to tools, memory, etc.
        self.planner = engine.planner
        self.history = []

    def execute_plan(self, plan):
        """
        Executes a list of steps sequentially.
        """
        final_results = []
        
        print(f"\n📋 Plan Accepted: {len(plan)} steps.\n")
        
        for i, step in enumerate(plan):
            print(f"🔹 Step {i+1}/{len(plan)}: {step}")
            logger.info(f"Executing Step {i+1}: {step}")
            
            # Context for this step includes previous results
            step_context = "\n".join([f"Step {k+1} Result: {r}" for k, r in enumerate(final_results)])
            
            # We treat each step as a mini-query to the main engine
            # But we need to bypass the "Planner" trigger to avoid infinite recursion
            # So we might need a modified process_step method in engine, or just use the LLM + Tools directly here.
            
            # For simplicity in V1, we ask the Engine to "Perform this action"
            # We inject the context of previous steps into the query
            
            step_query = f"""
            [BACKGROUND CONTEXT FROM PREVIOUS STEPS]
            {step_context}
            
            [CURRENT TASK]
            {step}
            
            [INSTRUCTION]
            Execute this specific task. Use tools if necessary. Return the result/answer for this step only.
            """
            
            # Recursively call engine process? 
            # DANGER: Infinite loops if not careful.
            # Better: Call a simplified execution method in Engine that skips planning.
            
            result = self.engine.process_step(step_query) 
            final_results.append(result)
            print(f"   ✅ Done.\n")
            
        return final_results
