# 🤖 Robô de Lançamento de Notas Acadêmicas

Projeto da disciplina **Automação Robótica de Processos (RPA)**, curso de Análise e Desenvolvimento de Sistemas, UNIFAAT.

**Aluna:** Joyce Carvalho, RA 6326057

---

## 📌 O desafio

No fim do semestre, o professor tem um arquivo com as notas de todos os alunos e precisa lançá-las num sistema que não aceita importação de arquivos. Fazer isso à mão é repetitivo e dá margem a erros de digitação.

Este robô lê o arquivo de notas, trata os dados, calcula a média e a situação de cada aluno e preenche o **Google Forms** sozinho usando **PyAutoGUI**. As respostas vão para uma planilha do Google, que funciona como banco de dados. O robô também permite **consultar as notas** de um aluno pelo RA ou pelo nome.

---

## ⚙️ Funcionalidades

**Menu principal**
```
===== LANÇAMENTO DE NOTAS =====
1 - Lançar notas
2 - Consultar notas
0 - Sair
```

**1 - Lançar notas**
- Lê o `notas_alunos.csv` (separado por `;`).
- Limpa e valida os dados (veja [Tratamento dos dados](#-tratamento-dos-dados)).
- Calcula a **Média Final** e a **Situação** (Aprovado/Reprovado).
- Preenche e envia o Google Forms aluno por aluno.
- Permite escolher quantos alunos lançar, para testar antes do lançamento completo.
- Gera o `pendencias.csv` com os alunos que não puderam ser lançados e o motivo.

**2 - Consultar notas**
- Busca por **RA** (`100004`, `RA100004` ou `0100004`) ou por **parte do nome** (`igor` traz todos os Igors).
- Lê os dados direto da planilha de respostas do Google.
- Se a planilha não estiver acessível, consulta o CSV local.

---

## 🧮 Regras de cálculo

| Avaliação | Nota máxima | Peso |
|---|---|---|
| Nota01 | 10 | 8 |
| Nota02 | 10 | 8 |
| TF01 | 2 | 2 |
| TF02 | 2 | 2 |

Antes de aplicar o peso, o TF é convertido para a escala de 0 a 10. Na prática:

```
Média Final = Nota01 × 0,4 + Nota02 × 0,4 + TF01 × 0,5 + TF02 × 0,5
```

- **Média ≥ 7.0 → Aprovado**
- **Média < 7.0 → Reprovado**

As notas são lançadas no formato decimal com ponto (ex.: `7.5`), e a média com 2 casas (ex.: `7.60`).

---

## 🧹 Tratamento dos dados

O arquivo do cliente vem com dados inconsistentes. O robô trata cada caso assim:

| Problema | Exemplo | Tratamento |
|---|---|---|
| Espaços sobrando e maiúsculas misturadas no nome | `  LUCAS  RODRIGUES ` | Padroniza: `Lucas Rodrigues` |
| RA em formatos diferentes | `RA100004`, `0100001`, `100019-0` | Padroniza: `100004`, `100001`, `100019` |
| Decimal com vírgula ou espaços | ` 2,1 ` | Converte: `2.1` |
| Aluno sem nota | `FALTOU`, `falta`, `N/A`, `-`, vazio | Considera **0** e registra aviso no log |
| RA vazio | | **Não lança**, vai para `pendencias.csv` |
| Nota acima de 10 | `12.3` | **Não lança**, vai para `pendencias.csv` |
| TF acima de 2 | `4,4` | **Não lança**, vai para `pendencias.csv` |
| RA repetido | | **Não lança**, vai para `pendencias.csv` |

Com o arquivo fornecido (100 alunos), o resultado é **76 alunos lançados** e **24 pendências**.

---

## 🛡️ Segurança e logs

- **Parada ao mexer o mouse:** durante o lançamento, o mouse fica parado sobre o campo RA. Se ele for movido, o robô para na hora.
- **Fail-Safe do PyAutoGUI:** levar o mouse a um dos cantos da tela também interrompe o robô.
- **Logs:** todas as ações, avisos e erros ficam registrados em `robo_notas.log`, com data e hora.
- **Tratamento de exceções:** erros de dados (`DadoInvalido`), arquivo não encontrado, falha de conexão e interrupção pelo usuário são tratados sem travar o programa.

---

## 📁 Estrutura do projeto

```
├── main.py                 # Robô: menu, lançamento e consulta
├── descobrir_posicao.py    # Auxiliar: descobre a posição (x, y) do campo RA na tela
├── notas_alunos.csv        # Arquivo de notas fornecido pelo cliente
├── pendencias.csv          # Gerado pelo robô: alunos não lançados e o motivo
├── requirements.txt        # Bibliotecas necessárias
├── .gitignore
└── README.md
```

---

## 🚀 Como executar

### 1. Pré-requisitos
- Python 3 instalado
- Navegador aberto e **maximizado**, com zoom em 100%

### 2. Criar o ambiente virtual e instalar as dependências
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
> Se o PowerShell bloquear o `activate`, rode antes:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

### 3. Configurar o `main.py`
No topo do arquivo:
```python
URL_FORMS = "link do Google Forms"
ID_PLANILHA = "ID da planilha de respostas"   # trecho da URL entre /d/ e /edit
POSICAO_CAMPO_RA = (x, y)                       # obtido com descobrir_posicao.py
```
> A planilha precisa estar compartilhada como "Qualquer pessoa com o link: Leitor" para a consulta funcionar.

### 4. Descobrir a posição do campo RA
```bash
python descobrir_posicao.py
```
Durante a contagem, deixe o mouse parado sobre o campo RA do formulário.

### 5. Rodar o robô
```bash
python main.py
```
Na primeira vez, faça um teste lançando só 2 alunos. Durante o lançamento, **não mexa no mouse nem no teclado**.

---

## 🧰 Tecnologias

- **Python 3**
- **PyAutoGUI**: automação de mouse e teclado
- **Pyperclip**: área de transferência (permite digitar acentos como ç, ã, é)
- **csv**, **logging**, **urllib**: bibliotecas nativas do Python
- **Google Forms** e **Google Sheets**: sistema de lançamento e banco de dados
- **Git** e **GitHub**: versionamento