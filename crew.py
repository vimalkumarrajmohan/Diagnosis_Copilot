import streamlit as st
from crewai import Crew, Process
from tasks import DiagnosisCopilotTasks
from agents import DiagnosisCopilotAgents


class DiagnosisCrew():

    def __init__(self, query, metadata, csv_path):
        self.query = query
        self.metadata = metadata
        self.csv_path = csv_path
        self.output_placeholder = st.empty()

    def run(self):
        try:
            agents = DiagnosisCopilotAgents()
            schema_understanding_agent = agents.schema_understanding_agent(metadata = self.metadata)
            code_generator_agent = agents.code_generator_agent(query = self.query)
            code_evaluator_agent = agents.code_evaluator_agent(metadata = self.metadata)
            final_code_agent = agents.final_code_agent()


            tasks = DiagnosisCopilotTasks()
            schema_understanding_task = tasks.schema_understanding_task(agent = schema_understanding_agent,
                                                                        metadata = self.metadata)
            code_generator_task = tasks.code_generator_task(agent = code_generator_agent,
                                                            context = [schema_understanding_task],
                                                            query = self.query)
            code_evaluator_task = tasks.code_evaluator_task(agent = code_evaluator_agent,
                                                            context = [schema_understanding_task, code_generator_task])
            final_code_task = tasks.final_code_task(agent = final_code_agent,
                                                    context = [schema_understanding_task, code_generator_task, code_evaluator_task],
                                                    csv_path = self.csv_path)
            
            
            
            crew = Crew(agents=[schema_understanding_agent, 
                                code_generator_agent, 
                                code_evaluator_agent, 
                                final_code_agent,
                                ],
                        tasks = [schema_understanding_task, 
                                code_generator_task,
                                code_evaluator_task, 
                                final_code_task,
                                ],
                        process = Process.sequential,
                        verbose = True,)
            
            result = crew.kickoff()

            return result
        
        except Exception as e:
            st.markdown(str(e))