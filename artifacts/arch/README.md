the system takes in rules documents and transaction data
it uses the system_prompt to make ground ready for the model
it attaches the rules,data along with the with profiling_prompt and sends request to deepseek api
it gets the analysis json object
and renders the output in dashboard format

FUTURE SCOPE:
 downloading the model and trainig it against huge data of rules documents,transaction data and validation and deployment
 adding a chatbot to answer questions on the uploaded data,and rules kb.
