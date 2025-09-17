import locale

# Configura o locale brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def parse_quantidade(valor):
    if isinstance(valor, str):
        return locale.atof(valor)
    return float(valor)

# Teste com valores específicos
valores_de_teste = [
    "132,74",
    "5.743,09",
    "13.274,00",
    "1.000,50",
    "999",
    "2.5"
]

for quantidade_raw in valores_de_teste:
    try:
        print("Valor bruto:", quantidade_raw)
        print("Convertido:", parse_quantidade(quantidade_raw))
        print("-" * 30)
    except Exception as e:
        print(f"Erro ao converter '{quantidade_raw}': {e}")
