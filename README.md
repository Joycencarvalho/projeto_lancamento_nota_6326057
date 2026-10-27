# 🤖 Robô de Lançamento de Notas Acadêmicas

Projeto da disciplina **Automação Robótica de Processos (RPA)**, curso de Análise e Desenvolvimento de Sistemas, UNIFAAT.

**Aluna:** Joyce Carvalho, RA 6326057

---

## ⚡ Leia primeiro

O projeto **já está configurado**: o link do Google Forms e a planilha de respostas estão definidos no `main.py`. **Não é preciso editar nenhum arquivo** para rodar o robô.

Antes de começar, tenha em mãos:

- [ ] **Python 3** instalado no Windows (no terminal, `python --version` deve mostrar a versão)
- [ ] **Internet** funcionando
- [ ] O **navegador padrão** do Windows aberto, **maximizado** e com zoom em **100%** (`Ctrl+0`)
- [ ] **Cerca de 20 minutos** sem usar o computador para o lançamento completo. Para só testar, bastam 2 minutos.

> ⚠️ O robô controla **o mouse e o teclado** do computador. Durante o lançamento, não mexa em nada. Para interromper o robô a qualquer momento, **é só mexer o mouse**.

---

## 🚀 Passo a passo para rodar

### Passo 1: Baixar o projeto
```bash
git clone https://github.com/Joycencarvalho/projeto_lancamento_nota_6326057.git
cd projeto_lancamento_nota_6326057
```
> Também é possível baixar pelo GitHub em **Code → Download ZIP** e extrair a pasta.

Abra a pasta no **VS Code** e abra um terminal com **Ctrl+'** (aspas simples).

### Passo 2: Criar o ambiente virtual e instalar as bibliotecas
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Quando o ambiente virtual estiver ativo, aparece **`(venv)`** no começo da linha do terminal.

> **Se o PowerShell bloquear o `activate`** com o erro *"a execução de scripts foi desabilitada neste sistema"*, rode o comando abaixo e depois o `activate` de novo. A liberação vale só para essa janela do terminal.
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

### Passo 3: Iniciar o robô
```bash
python main.py
```

O menu aparece:
```
===== LANÇAMENTO DE NOTAS =====
1 - Lançar notas
2 - Consultar notas
0 - Sair
```

### Passo 4: Lançar as notas (opção 1)
1. Digite **`1`**.
2. O robô lê o CSV e mostra quantos alunos estão prontos para lançar e quantas pendências encontrou.
3. Responda quantos alunos lançar. **Para testar, digite `2`.** Para lançar todos, aperte **Enter**.
4. **Na primeira execução, o robô faz a calibração** (veja o passo 5).
5. O robô preenche e envia o formulário de cada aluno sozinho. No final, aparece um resumo no terminal. Exemplo do lançamento completo:
   ```
   ====================================================
                  RESUMO DO LANÇAMENTO
   ====================================================
     Alunos no arquivo CSV ............... 100
     [OK] Notas lançadas com sucesso ..... 76
     [!]  Pendentes (dados com erro) ..... 24
   ====================================================

     ATENÇÃO: 24 aluno(s) não foram lançados por erro nos dados.
     Verifique o arquivo 'pendencias.csv' para ver o motivo de cada um
     e corrigir os dados na origem.
   ====================================================
   ```
   Se o lançamento for parcial (teste com poucos alunos ou robô interrompido), o resumo também mostra quantos alunos válidos ficaram sem lançar e o motivo.

### Passo 5: Calibração do campo RA (só na primeira vez)
Cada tela tem uma resolução diferente, então o robô precisa aprender **onde fica o campo RA** no seu computador. Isso é feito uma única vez:

1. O robô mostra as instruções e pede para apertar **Enter**.
2. O formulário abre no navegador e começa uma contagem de **10 segundos**.
3. Durante a contagem, coloque o mouse **dentro da caixa de resposta do campo RA** (não precisa clicar) e **deixe parado**.
4. Ao fim da contagem, a posição é salva no arquivo `posicao.json` e **o lançamento começa na hora**.

Nas próximas execuções, o robô pergunta:
```
Posição do campo RA salva: (410, 438)
Enter = usar esta posição | C = calibrar de novo:
```
Aperte **Enter** para usar a posição salva ou **`C`** para calibrar de novo, por exemplo se o tamanho da janela, o zoom ou o monitor mudaram.

### Passo 6: Consultar as notas (opção 2)
1. Rode `python main.py` e digite **`2`**.
2. Digite o **RA** ou **parte do nome** do aluno:
   - por RA: `100004` (também aceita `RA100004` ou `0100004`);
   - por nome: `igor`, que traz todos os alunos com "Igor" no nome.
3. O robô mostra os dados, as notas, a média e a situação:
   ```
   ========================================
     RA:          100004
     Nome:        Igor Rodrigues
     Nota 1:      9.6
     Nota 2:      9.5
     TF01:        1.2
     TF02:        0.0
     Média Final: 8.24
     Situação:    Aprovado
   ========================================
   1 aluno(s) encontrado(s) - fonte: planilha Lançamento de notas (respostas)
   ```

A consulta lê os dados direto da **planilha de respostas do Google**, que funciona como banco de dados. Se a planilha não estiver acessível, por exemplo sem internet, a consulta usa o CSV local e avisa no terminal.

### Passo 7: Conferir os resultados
- **Planilha "Lançamento de notas (respostas)"**: recebe uma linha por aluno lançado.
- **`pendencias.csv`**: lista os alunos que **não** foram lançados e o motivo (veja [Relatório de pendências](#-relatório-de-pendências)).
- **`robo_notas.log`**: histórico de tudo o que o robô fez, com data e hora.

---

## 🆘 Problemas comuns

| O que aconteceu | Como resolver |
|---|---|
| O `activate` foi bloqueado pelo PowerShell | Veja a observação no passo 2 |
| `python` não é reconhecido | Tente `py` no lugar de `python`, ou reinstale o Python marcando **"Add Python to PATH"** |
| O robô digitou no lugar errado ou não clicou no campo RA | Rode de novo e digite **`C`** para recalibrar. Antes, confira se o navegador está maximizado e com zoom em 100% |
| O robô começou a digitar antes de a página carregar | Aumente `TEMPO_CARREGAR_PAGINA` no topo do `main.py` (ex.: de 4 para 6) |
| O robô parou sozinho | O mouse foi movido, e é assim que se interrompe o robô. Confira na planilha o último aluno lançado antes de rodar de novo, para não duplicar |
| A consulta mostra `fonte: arquivo local` | Sem acesso à planilha. Verifique a conexão com a internet |

---

## 📌 O desafio

No fim do semestre, o professor tem um arquivo com as notas de todos os alunos e precisa lançá-las num sistema que não aceita importação de arquivos. Fazer isso à mão é repetitivo e dá margem a erros de digitação.

Este robô lê o arquivo de notas, trata os dados, calcula a média e a situação de cada aluno e preenche o **Google Forms** sozinho usando **PyAutoGUI**. Também permite **consultar as notas** de um aluno pelo RA ou pelo nome.

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

O arquivo do cliente (`notas_alunos.csv`, separado por `;`) vem com dados inconsistentes. O robô trata cada caso assim:

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

### 📋 Relatório de pendências

O `pendencias.csv` é gerado a cada lançamento (opção 1) com os alunos que não puderam ser lançados, para que os dados sejam corrigidos na origem. Ele abre direto no Excel:

```
Linha;Nome;RA;Motivo
3;JULIA FERREIRA ALMEIDA;;RA vazio ou inválido: ''
12;Eduardo Rocha souza;100011;TF02 fora do intervalo 0 a 2: 4.4
32;IGOR LIMA;100031;Nota01 fora do intervalo 0 a 10: 12.3
```

---

## 🛡️ Segurança e logs

- **Parada ao mexer o mouse:** durante o lançamento, o mouse fica parado sobre o campo RA. Se ele for movido, o robô para na hora e registra no log em qual aluno parou.
- **Fail-Safe do PyAutoGUI:** levar o mouse a um dos cantos da tela também interrompe o robô.
- **Calibração salva fora do código:** a posição do campo RA fica no `posicao.json`, então ninguém precisa editar o código para rodar o robô em outro computador.
- **Logs:** todas as ações, avisos e erros ficam registrados em `robo_notas.log`.
- **Tratamento de exceções:** erros de dados (`DadoInvalido`), arquivo não encontrado, falha de conexão e interrupção pelo usuário são tratados sem travar o programa.

---

## 📁 Estrutura do projeto

```
├── main.py              # Robô: menu, calibração, lançamento e consulta
├── notas_alunos.csv     # Arquivo de notas fornecido pelo cliente
├── pendencias.csv       # Gerado pelo robô: alunos não lançados e o motivo
├── requirements.txt     # Bibliotecas necessárias
├── .gitignore
└── README.md
```

Arquivos criados ao rodar (não vão para o GitHub):
- `posicao.json`: posição do campo RA na tela deste computador
- `robo_notas.log`: histórico de execução
- `venv/`: ambiente virtual

---

## 🔧 Configurações (opcional)

Tudo já vem configurado. Se precisar ajustar, as configurações ficam no topo do `main.py`:

| Configuração | Para que serve |
|---|---|
| `URL_FORMS` | Link do formulário de lançamento |
| `ID_PLANILHA` | ID da planilha de respostas (trecho da URL entre `/d/` e `/edit`) |
| `TEMPO_CARREGAR_PAGINA` | Espera, em segundos, para o formulário carregar |
| `TEMPO_CALIBRACAO` | Tempo, em segundos, para posicionar o mouse na calibração |
| `MEDIA_APROVACAO` | Média mínima para aprovação (padrão: 7.0) |

> **Para usar outro formulário:** os campos precisam estar nesta ordem e com estes nomes: **RA, Nome, Nota 1, Nota 2, TF01, TF02, Média Final, Situação**, todos do tipo *resposta curta* e sem coleta de e-mail. A planilha precisa estar compartilhada como *"Qualquer pessoa com o link: Leitor"* para a consulta funcionar.

---

## 🧰 Tecnologias

- **Python 3**
- **PyAutoGUI**: automação de mouse e teclado
- **Pyperclip**: área de transferência (permite digitar acentos como ç, ã, é)
- **csv**, **json**, **logging**, **urllib**: bibliotecas nativas do Python
- **Google Forms** e **Google Sheets**: sistema de lançamento e banco de dados
- **Git** e **GitHub**: versionamento