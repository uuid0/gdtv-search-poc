from openai import OpenAI
from pydantic import BaseModel

class Concept(BaseModel):
    name: str
    description: str
    keywords: list[str]
    share: float

class ConceptLists(BaseModel):
    newly_introduced: list[Concept]
    further_discussed: list[Concept]
    just_mentioned: list[Concept]

class OpenAIExplainer:
    _model: str
    _client: OpenAI

    def __init__(
            self,
            api_key: str,
            model: str = "gpt-5-mini",
    ):
        self._model = model
        self._client = OpenAI(api_key=api_key)

    def explain(
            self,
            course_name: str,
            full_text: str,
    ) -> any:
        # @todo add hints about the course
        messages = [
            {
                "role": "system",
                "content": "Your role is to extract information from the following text so it can be put into the search index.\n"
                           f"The text is a transcript of one lecture of an instructional video for the course named '{course_name}'.\n"
                           "People want to be able to find what concepts are covered in the video.\n"
                           "You must follow my instructions exactly.\n"
                           "Give me separate lists concepts, that are: 'newly introduced', 'further discussed', 'just mentioned'\n"
                           "Ensure that each list item has the name of the concept, a description, a list of keywords and what percentage of the whole video is this concept discussed. "
                           "These keywords will be used to create a document in an Elasticsearch index, so the video can be found by user search."
            },
            {
                "role": "user",
                "content": full_text,
            }
        ]
        response = self._client.responses.parse(
            model=self._model,
            input=messages,
            text_format=ConceptLists,
        )
        return response.output_parsed
