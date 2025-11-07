import requests

def buscar_endereco_por_cep(cep):
    """Consulta a API ViaCEP e retorna o endereço completo"""
    url = f"https://viacep.com.br/ws/{cep}/json/"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            print("❌ Erro na consulta da API.")
            return None
        dados = r.json()
        if "erro" in dados:
            print("⚠️ CEP não encontrado.")
            return None
        return {
            "cep": dados.get("cep"),
            "logradouro": dados.get("logradouro"),
            "bairro": dados.get("bairro"),
            "cidade": dados.get("localidade"),
            "uf": dados.get("uf")
        }
    except Exception as e:
        print(f"Erro ao consultar API: {e}")
        return None
