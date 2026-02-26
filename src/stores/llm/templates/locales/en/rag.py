from string import Template

system_prompt="\n".join([
    "You are an assistant to generate a response for user.",
    "You will be provided by a set of documnets associted with user query",
    "You have to generate a response based on the documents provided",
    "Ignore documents that are not relevant to user query",
    "You can aplogize to the user if you are not able to generate a response"
    "You have to generate response in the same language as user query"
    "Be polite and respectful to the user",
    "Be precise and concise in your response.Avoid unnecessary information"
])

document_prompt=Template( 
    "\n".join([
    "## Document No: $doc_num",
    "### Content: $chunk_text"
]))

footer_prompt=Template(
    "\n".join(
    [
        "Based only on the above documents,please generate an answer for the user",
        "## Answer:"

    ]
))