"""
Atividade Aula 08 - RPA com Python
Robô de lançamento e consulta de notas (Google Forms + Google Sheets)
Aluna: Joyce Carvalho - RA 6326057
"""

import csv
import io
import logging
import time
import urllib.request
import webbrowser

import pyautogui
import pyperclip

# ============================================================
# CONFIGURAÇÕES (ajuste antes de rodar)
# ============================================================
ARQUIVO_CSV = "notas_alunos.csv"          # arquivo enviado pelo professor
ARQUIVO_LOG = "robo_notas.log"
ARQUIVO_PENDENCIAS = "pendencias.csv"     # alunos que NÃO foram lançados e o motivo

# Link de RESPOSTA do formulário (o que termina em /viewform)
URL_FORMS = "https://forms.gle/eoCDGDVYoFKHuck49"

# ID da planilha de respostas: é o trecho da URL entre /d/ e /edit
# Ex.: https://docs.google.com/spreadsheets/d/ESTE_TRECHO_AQUI/edit
ID_PLANILHA = "1qeOim-AWL8sFf7O5Us_tePQFzP64PMMT6XOaxo0qLOE"

# Posição (x, y) do campo RA na tela - descubra com descobrir_posicao.py
POSICAO_CAMPO_RA = (410, 438)

# Tempos de espera em segundos (aumente se a internet estiver lenta)
TEMPO_CARREGAR_PAGINA = 4
TEMPO_APOS_ENVIAR = 3

# Pesos da média
PESO_NOTA = 8   # Nota01 e Nota02
PESO_TF = 2     # TF01 e TF02

# Notas máximas aceitas. Acima disso o aluno vai para pendencias.csv
NOTA_MAXIMA = 10.0
# Se o professor confirmar que o TF vale até 2 pontos, mude para 2.0:
# o script converte o TF para a escala 0-10 antes de aplicar o peso.
NOTA_MAXIMA_TF = 2.0

# Média mínima para aprovação: >= 7 Aprovado, < 7 Reprovado
MEDIA_APROVACAO = 7.0

# O forms tem o campo "Situação" logo depois de "Média Final"
FORMS_TEM_CAMPO_SITUACAO = True

# Textos que significam "aluno sem nota" -> considerados 0 (zero)
MARCADORES_AUSENCIA = {"", "FALTOU", "FALTA", "N/A", "NA", "-"}

# Segurança do PyAutoGUI: jogar o mouse no canto superior esquerdo da tela
# interrompe o robô na hora
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5   # pausa entre cada ação do PyAutoGUI


class DadoInvalido(Exception):
    """Erro de regra de negócio: o dado do CSV não pode ser lançado."""


# ============================================================
# LOG
# ============================================================
def configurar_log():
    """Grava o log no arquivo e também mostra no terminal."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
        handlers=[
            logging.FileHandler(ARQUIVO_LOG, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


# ============================================================
# LIMPEZA E VALIDAÇÃO DOS DADOS
# ============================================================
def limpar_nome(texto):
    """Remove espaços sobrando e padroniza: '  LUCAS  RODRIGUES ' -> 'Lucas Rodrigues'."""
    minusculas = {"da", "de", "do", "das", "dos", "e"}
    palavras = texto.split()   # split() sem argumento já remove espaços duplicados
    if not palavras:
        raise DadoInvalido("nome vazio")
    resultado = []
    for i, palavra in enumerate(palavras):
        if i > 0 and palavra.lower() in minusculas:
            resultado.append(palavra.lower())
        else:
            resultado.append(palavra.capitalize())
    return " ".join(resultado)


def limpar_ra(texto):
    """Padroniza o RA: 'RA100004', '0100001', ' 100005 ', '100019-0' -> '100004' etc."""
    ra = texto.strip().upper().replace("RA", "")
    ra = ra.split("-")[0].strip()     # remove o sufixo '-0'
    ra = ra.lstrip("0")               # remove zeros à esquerda
    if not ra.isdigit():
        raise DadoInvalido(f"RA vazio ou inválido: '{texto.strip()}'")
    return ra


def limpar_nota(texto, campo, maximo, avisos):
    """Converte a nota em float. Ausência (FALTOU, falta, N/A, -, vazio) vira 0.
    Nota que não é número ou está fora de 0 a 'maximo' gera DadoInvalido."""
    valor = texto.strip()
    if valor.upper() in MARCADORES_AUSENCIA:
        avisos.append(f"{campo} sem nota ('{valor}') considerado 0")
        return 0.0
    try:
        nota = float(valor.replace(",", "."))
    except ValueError:
        raise DadoInvalido(f"{campo} não é um número: '{valor}'")
    if nota < 0 or nota > maximo:
        raise DadoInvalido(f"{campo} fora do intervalo 0 a {maximo:g}: {nota}")
    return nota


def calcular_media(nota1, nota2, tf01, tf02):
    """Média ponderada: Nota01 e Nota02 com peso 8, TF01 e TF02 com peso 2.
    O TF é convertido para a escala 0-10 caso NOTA_MAXIMA_TF seja diferente de 10."""
    fator_tf = 10 / NOTA_MAXIMA_TF
    soma = (nota1 * PESO_NOTA) + (nota2 * PESO_NOTA) \
        + (tf01 * fator_tf * PESO_TF) + (tf02 * fator_tf * PESO_TF)
    soma_pesos = (PESO_NOTA * 2) + (PESO_TF * 2)
    return round(soma / soma_pesos, 2)


def verificar_situacao(media):
    """Devolve 'Aprovado' (média >= 7) ou 'Reprovado' (média < 7)."""
    if media >= MEDIA_APROVACAO:
        return "Aprovado"
    return "Reprovado"


def formatar(valor, casas=1):
    """Formata o número com ponto como separador decimal (ex.: 7.5)."""
    return f"{valor:.{casas}f}"


# ============================================================
# LEITURA DO CSV
# ============================================================
def ler_linhas_csv(caminho):
    """Lê o CSV separado por ';'. Tenta UTF-8 e, se falhar, o padrão do Excel no Windows."""
    for codificacao in ("utf-8-sig", "cp1252"):
        try:
            with open(caminho, "r", encoding=codificacao) as arquivo:
                return list(csv.DictReader(arquivo, delimiter=";"))
        except UnicodeDecodeError:
            continue
    raise DadoInvalido(f"Não foi possível ler a codificação do arquivo {caminho}")


def preparar_alunos(caminho):
    """Lê, limpa e valida o CSV.
    Devolve (alunos_validos, pendencias). Cada aluno já vem com média e situação."""
    alunos = []
    pendencias = []
    ras_vistos = set()

    for numero_linha, linha in enumerate(ler_linhas_csv(caminho), start=2):
        avisos = []
        try:
            nome = limpar_nome(linha.get("Nome") or "")
            ra = limpar_ra(linha.get("RA") or "")
            if ra in ras_vistos:
                raise DadoInvalido(f"RA {ra} repetido no arquivo")

            nota1 = limpar_nota(linha.get("Nota01") or "", "Nota01", NOTA_MAXIMA, avisos)
            tf01 = limpar_nota(linha.get("TF01") or "", "TF01", NOTA_MAXIMA_TF, avisos)
            nota2 = limpar_nota(linha.get("Nota02") or "", "Nota02", NOTA_MAXIMA, avisos)
            tf02 = limpar_nota(linha.get("TF02") or "", "TF02", NOTA_MAXIMA_TF, avisos)

            media = calcular_media(nota1, nota2, tf01, tf02)
            ras_vistos.add(ra)
            alunos.append({
                "RA": ra,
                "Nome": nome,
                "Nota 1": formatar(nota1),
                "Nota 2": formatar(nota2),
                "TF01": formatar(tf01),
                "TF02": formatar(tf02),
                "Média Final": formatar(media, 2),
                "Situação": verificar_situacao(media),
            })
            for aviso in avisos:
                logging.warning(f"Linha {numero_linha} (RA {ra}): {aviso}")

        except DadoInvalido as erro:
            pendencias.append({
                "Linha": numero_linha,
                "Nome": " ".join((linha.get("Nome") or "").split()),
                "RA": (linha.get("RA") or "").strip(),
                "Motivo": str(erro),
            })
            logging.warning(f"Linha {numero_linha} NÃO será lançada: {erro}")

    return alunos, pendencias


def salvar_pendencias(pendencias):
    """Gera o relatório pendencias.csv para conferência manual."""
    with open(ARQUIVO_PENDENCIAS, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=["Linha", "Nome", "RA", "Motivo"], delimiter=";")
        escritor.writeheader()
        escritor.writerows(pendencias)


# ============================================================
# AÇÕES NA TELA (PyAutoGUI)
# ============================================================
def digitar(texto):
    """Cola o texto via área de transferência.
    O pyautogui.write() não digita acentos (ç, ã, é), por isso usamos o pyperclip."""
    pyperclip.copy(str(texto))
    pyautogui.hotkey("ctrl", "v")


def abrir_formulario():
    """Abre o formulário em branco na mesma aba, pela barra de endereço."""
    pyautogui.hotkey("ctrl", "l")
    digitar(URL_FORMS)
    pyautogui.press("enter")
    time.sleep(TEMPO_CARREGAR_PAGINA)


def preencher_formulario(aluno):
    """Clica no campo RA e vai preenchendo os campos com TAB, na ordem do forms."""
    campos = ["RA", "Nome", "Nota 1", "Nota 2", "TF01", "TF02", "Média Final"]
    if FORMS_TEM_CAMPO_SITUACAO:
        campos.append("Situação")
    pyautogui.click(POSICAO_CAMPO_RA)
    for campo in campos:
        digitar(aluno[campo])
        pyautogui.press("tab")
    # Depois do último campo, o TAB cai no botão "Enviar"
    pyautogui.press("enter")
    time.sleep(TEMPO_APOS_ENVIAR)


# ============================================================
# OPÇÃO 1 - LANÇAR NOTAS
# ============================================================
def configuracao_ok():
    if URL_FORMS.startswith("COLE_AQUI") or POSICAO_CAMPO_RA == (0, 0):
        print("\n⚠ Configure URL_FORMS e POSICAO_CAMPO_RA no topo do main.py antes de lançar.")
        return False
    return True


def lancar_notas():
    if not configuracao_ok():
        return

    try:
        alunos, pendencias = preparar_alunos(ARQUIVO_CSV)
    except FileNotFoundError:
        logging.error(f"Arquivo '{ARQUIVO_CSV}' não encontrado.")
        return
    except DadoInvalido as erro:
        logging.error(str(erro))
        return

    salvar_pendencias(pendencias)
    logging.info(
        f"CSV lido: {len(alunos)} alunos prontos para lançar, "
        f"{len(pendencias)} pendências (veja {ARQUIVO_PENDENCIAS})."
    )
    if not alunos:
        logging.error("Nenhum aluno válido para lançar.")
        return

    # Permite testar com poucos registros antes de lançar todos
    resposta = input(f"Quantos alunos lançar? (Enter = todos os {len(alunos)}): ").strip()
    if resposta.isdigit() and int(resposta) > 0:
        alunos = alunos[: int(resposta)]

    print("\nNão mexa no mouse nem no teclado durante o lançamento.")
    print("Para interromper: jogue o mouse no canto superior esquerdo da tela.")
    webbrowser.open(URL_FORMS)
    for segundos in range(5, 0, -1):
        print(f"Começando em {segundos}...")
        time.sleep(1)

    enviados = 0
    for indice, aluno in enumerate(alunos):
        try:
            if indice > 0:
                abrir_formulario()
            preencher_formulario(aluno)
            enviados += 1
            logging.info(
                f"[{indice + 1}/{len(alunos)}] RA {aluno['RA']} lançado "
                f"- Média {aluno['Média Final']} - {aluno['Situação']}"
            )
        except pyautogui.FailSafeException:
            logging.warning(f"Robô interrompido pelo usuário no RA {aluno['RA']}.")
            break
        except Exception as erro:
            logging.error(f"Falha ao lançar o RA {aluno['RA']}: {erro}")

    logging.info(f"Lançamento finalizado: {enviados} de {len(alunos)} enviados.")


# ============================================================
# OPÇÃO 2 - CONSULTAR NOTAS
# ============================================================
def buscar_planilha():
    """Baixa a planilha de respostas como CSV e devolve uma lista de dicionários.
    A planilha precisa estar compartilhada como 'Qualquer pessoa com o link'."""
    url = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv"
    with urllib.request.urlopen(url, timeout=15) as resposta:
        conteudo = resposta.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(conteudo)))


def carregar_registros():
    """Busca na planilha (banco de dados). Se falhar, usa o CSV local já tratado."""
    try:
        return buscar_planilha(), "planilha Lançamento de notas (respostas)"
    except Exception as erro:
        logging.warning(f"Não foi possível acessar a planilha ({erro}). Consultando o CSV local.")
    try:
        alunos, _ = preparar_alunos(ARQUIVO_CSV)
        return alunos, f"arquivo local {ARQUIVO_CSV}"
    except (FileNotFoundError, DadoInvalido) as erro:
        logging.error(f"Também não foi possível ler o CSV local: {erro}")
        return None, None


def remover_repetidos(registros):
    """Se um RA foi lançado mais de uma vez, mantém só o lançamento mais recente."""
    ultimos = {}
    for registro in registros:
        ultimos[registro.get("RA", "").strip()] = registro
    return list(ultimos.values())


def situacao_do_registro(registro):
    """Usa a coluna Situação se existir; senão calcula pela Média Final."""
    if registro.get("Situação"):
        return registro["Situação"]
    try:
        media = float(str(registro.get("Média Final", "")).replace(",", "."))
        return verificar_situacao(media)
    except ValueError:
        return "Não informada"


def exibir_aluno(aluno):
    print("\n" + "=" * 40)
    print(f"  RA:          {aluno.get('RA', '')}")
    print(f"  Nome:        {aluno.get('Nome', '')}")
    print(f"  Nota 1:      {aluno.get('Nota 1', '')}")
    print(f"  Nota 2:      {aluno.get('Nota 2', '')}")
    print(f"  TF01:        {aluno.get('TF01', '')}")
    print(f"  TF02:        {aluno.get('TF02', '')}")
    print(f"  Média Final: {aluno.get('Média Final', '')}")
    print(f"  Situação:    {situacao_do_registro(aluno)}")
    print("=" * 40)


def consultar_notas():
    busca = input("\nDigite o RA ou o Nome do aluno: ").strip()
    if not busca:
        print("Nada foi digitado.")
        return

    registros, origem = carregar_registros()
    if registros is None:
        return
    registros = remover_repetidos(registros)

    # Se parece um RA (ex.: 100004, RA100004, 0100004), busca pelo RA padronizado
    try:
        ra_busca = limpar_ra(busca)
    except DadoInvalido:
        ra_busca = None

    if ra_busca:
        encontrados = [r for r in registros if r.get("RA", "").strip().lstrip("0") == ra_busca]
    else:
        # Busca por Nome: aceita parte do nome, sem diferenciar maiúsculas
        termo = " ".join(busca.lower().split())
        encontrados = [r for r in registros if termo in " ".join(r.get("Nome", "").lower().split())]

    if not encontrados:
        print(f"Nenhum aluno encontrado para '{busca}'.")
        logging.info(f"Consulta: '{busca}' não encontrado.")
        return

    for aluno in encontrados:
        exibir_aluno(aluno)
    print(f"{len(encontrados)} aluno(s) encontrado(s) - fonte: {origem}")
    logging.info(f"Consulta: '{busca}' - {len(encontrados)} resultado(s).")


# ============================================================
# MENU
# ============================================================
def menu():
    while True:
        print("\n===== LANÇAMENTO DE NOTAS =====")
        print("1 - Lançar notas")
        print("2 - Consultar notas")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            lancar_notas()
        elif opcao == "2":
            consultar_notas()
        elif opcao == "0":
            print("Encerrando o robô. Até mais!")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    configurar_log()
    logging.info("Robô iniciado.")
    menu()
    logging.info("Robô encerrado.")