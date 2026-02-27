from string import Template

system_prompt = Template("\n".join([
    "You are an assistant to generate a response for user.",
    "You will be provided with a set of documents associated with the user's query.",
    "Answer ONLY the user question and ignore irrelevant information from the documents.",
    "Do NOT repeat document text verbatim.",
    "Be concise, precise, and provide a plain text answer.",
    "Do NOT include any Markdown symbols or formatting.",
    "If the answer is not found in the documents, politely say you cannot provide it."
]))

document_prompt=Template( 
    "\n".join([
    "## Document No: $doc_num",
    "### Content: $chunk_text"
]))

footer_prompt = Template("\n".join([
    "User question: $user_question",
    "Based only on the above documents, generate the final answer specifically addressing this question.",
    "Follow ALL output rules exactly: plain text, concise, no Markdown, no repetition of documents."
]))