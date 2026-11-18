from dotenv import load_dotenv
import anthropic

load_dotenv()  # lê o .env e coloca ANTHROPIC_API_KEY no ambiente

client = anthropic.Anthropic()  # pega a chave do ambiente sozinho

resposta = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=100,
    messages=[{"role": "user", "content": "Em uma frase: o que faz um analista de SOC N1?"}],
)

print(resposta.content[0].text)
print("tokens de entrada:", resposta.usage.input_tokens)
print("tokens de saída:", resposta.usage.output_tokens)
