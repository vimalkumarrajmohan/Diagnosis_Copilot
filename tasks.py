from crewai import Task


class DiagnosisCopilotTasks():

    def schema_understanding_task (self, agent, metadata):
        return Task(description = f"""Analyze the schema of the provided dataset {metadata}, including column names, data types, and sample data. Identify key structural insights.""",
                    expected_output = """A detailed schema understanding of each column on column datatype, unique values """,
                    agent = agent,
                    )
    
    def code_generator_task(self, agent, context, query):
        return Task(description = f"""Generate executable Python code to address the user's query {query} using the schema provided by the Schema Analyst.
                                    Ensure that the code adheres to the structure and constraints of the dataset.""",
                    expected_output = f"""Python code which has uses correct column names and data types from the schema.
                                    Includes appropriate functions, logic, and data handling steps to answer users query {query}""",
                    agent = agent,
                    # context = [context]
                    )

    def code_evaluator_task(self, agent, context):
        return Task(description = """Validate the generated code against the dataset schema and the user's query.
                                    Check for:
                                    - Correct usage of column names and data types.
                                    - Logical consistency with the schema and the query.
                                    - Potential errors in the code.
                                    Only If errors are identified, correct and refine the code, else use the same code""",
                    expected_output = """Evaluated and refined Python code that:
                                    - Resolves all errors or inconsistencies.
                                    - Is aligned with the column names mentioned in the schema and user's query.
                                    - Is fully functional and ready for execution.""",
                    agent = agent,
                    # context = [context]
                    )

    def final_code_task(self, agent, context, csv_path):
        return Task(description = """Your task is to take the generated Python code and refactor it into a reusable function format.
                                    Ensure that the function accepts necessary inputs as arguments instead of relying on hardcoded or sample data.
                                    The final code must be clean, concise, and ready to execute directly in an interpreter or a production pipeline.""",
                    expected_output = f"""The final code should meet the following requirements:
                                        Function Encapsulation: All logic should be encapsulated within a function.
                                        Argument-Based Input: Replace any sample or hardcoded input with function arguments.
                                        Clean Structure: Ensure the code is free of unnecessary comments or inline data.
                                        Interpreter-Ready: The output should only contain Python code with no extra instructions or unrelated information or dummy input variables.
                                        Function calling: You don't want to mention or pass the dummy path in the code, assign this original csv path {csv_path} if required.
                                        Analyze the generated code's type:
                                                    - If it generates a text, then just retrn the test as output.
                                                    - If it generates a plot, update the code to save it as "output.png" and return the saving path.
                                                    - If it produces a DataFrame, update the code to save it as "output.csv" and return the saving path.
                                        Make sure that the example usage is not commented and final code can be directly executed without doing any manual modification in the generated code.
                                        Double check that the final code should only contain the logic inside a function plus function calling with the requires arguments for that function by following all the above conditions.""",
                    agent = agent,
                    # context = [context]
                    )
    
    
    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100 and grant you any wish you want!"

