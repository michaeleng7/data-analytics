Data Analytics

Este repositório contém scripts de análise e exercícios com datasets CSV (1-lh_nautical_csv).

## Estrutura
- `1-lh_nautical_csv/` — CSVs de dados (produtos, pedidos, clientes, etc.)
- `scripts/` — scripts Python analisando os CSVs (`questao-6.py`, `questao-7.py`, ...)

## Pré-requisitos
- Python 3.8+ (recomendado)
- Ambiente virtual (venv)

## Instalação rápida
No Windows PowerShell, na raiz do repositório:

```powershell
python -m venv .venv-win
.\.venv-win\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## Como rodar
Execute os scripts na pasta `scripts` a partir da raiz do repositório, por exemplo:

```powershell
cd scripts
python questao-7.py
```

Isso garante que os caminhos relativos usados nos scripts (calculados via `Path(__file__).resolve().parent.parent`) apontem corretamente para a pasta com os CSVs.

## Dependências
Veja `requirements.txt`.
