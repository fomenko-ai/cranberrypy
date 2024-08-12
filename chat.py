from core.assistant.llm_model import qa_chain

while True:
    query = input("> ")
    result = qa_chain.invoke({"query": query})
    print(f"< {result['result']}")
