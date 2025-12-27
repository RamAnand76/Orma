import logging

logger = logging.getLogger("ORMA_PLANNER")

class Planner:
    def __init__(self, llm_function):
        self.llm_func = llm_function

    def generate_plan(self, user_goal, context=""):
        """
        Decomposes a complex goal into a list of steps.
        """
        prompt = f"""
        [SYSTEM: MASTER PLANNER]
        You are the Planning Cortex of an autonomous agent.
        Your job is to break down a COMPLEX user goal into a sequential list of SIMPLE, EXECUTABLE steps.
        
        [CONTEXT]
        {context}

        [USER GOAL]
        "{user_goal}"

        [INSTRUCTIONS]
        1. Return ONLY a numbered list of steps.
        2. Each step must be a single specific action (e.g., "Search for X", "Calculate Y").
        3. Do not include preamble or explanation.
        4. Make the plan as efficient as possible (3-5 steps max usually).
        
        [FORMAT EXAMPLE]
        1. Search for "current CEO of Google".
        2. Extract the name of the CEO.
        3. Search for "net worth of [CEO Name]".
        4. Summarize the findings.
        """
        
        response = self.llm_func(prompt, "")
        
        # Parse the response into a list
        plan = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering (e.g., "1. " or "- ")
                clean_step = line.split('.', 1)[-1].strip() if '.' in line else line.split('-', 1)[-1].strip()
                plan.append(clean_step)
                
        logger.info(f"Generated Plan: {plan}")
        return plan
