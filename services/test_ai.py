from .ai_service import SkDuckyAIService
from .ai_service import AIRequest

ai = SkDuckyAIService()

ai.learn("give 1 diamond on join", "on join:\n    give 1 diamond to player")

request = AIRequest(prompt="when a player joins, he gets a diamond")
response = ai.generate_code(request)

print("Answer:")
print(response.code)
