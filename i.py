import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Função para carregar imagem em escala de cinza
def carregar_imagem_em_escala_de_cinza(caminho_imagem):
    try:
        return cv2.imread(caminho_imagem, cv2.IMREAD_GRAYSCALE)
    except cv2.error as e:
        messagebox.showerror("Erro", f"Erro ao carregar imagem: {e}")
        return None

# Função para cálculo do expoente de Hurst
def calc_hurst_exponent(data):
    N = len(data)
    if N <= 1:  # Lidar com casos de vetores com 1 ou menos elementos
        return 0.0
    log_N = np.log(N)
    desvio_padrao = np.std(data)
    if desvio_padrao == 0:  # Lidar com desvio padrão zero
        return 0.0
    dados_acumulados = np.cumsum(data - np.mean(data))
    R = np.max(dados_acumulados) - np.min(dados_acumulados)
    try:
        H = np.log(R / desvio_padrao) / log_N
        return H
    except ValueError:  # Lidar com possíveis erros de log(0)
        return 0.0


# Função para contar pixels brancos e pretos
def contar_pixels_brancos_e_pretos(imagem):
    if imagem is None:
        return 0, 0
    b = np.count_nonzero(imagem == 255)
    d = np.count_nonzero(imagem == 0)
    return b, d

# Função para calcular porcentagem de saturação
def calcular_porcentagem_saturacao(imagem, limiar=255):
    if imagem is None:
        return 0.0
    pixels_saturados = np.sum(imagem >= limiar)
    total_pixels = imagem.shape[0] * imagem.shape[1]
    porcentagem_saturacao = (pixels_saturados / total_pixels) * 100
    return porcentagem_saturacao

# Função para binarização da imagem
def binarizar_imagem(imagem, metodo, limiar=None):
    if imagem is None:
        return None
    if metodo == 'especifico':
        _, imagem_binarizada = cv2.threshold(imagem, limiar, 255, cv2.THRESH_BINARY)
    elif metodo == 'otsu':
        _, imagem_binarizada = cv2.threshold(imagem, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif metodo == 'adaptativo_medio':
        imagem_binarizada = cv2.adaptiveThreshold(imagem, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    elif metodo == 'adaptativo_gaussiano':
        imagem_binarizada = cv2.adaptiveThreshold(imagem, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    else:
        return None
    return imagem_binarizada

# Função para salvar imagem binarizada
def salvar_imagem(imagem, nome_arquivo, limiar, metodo, contador_imagem):
    if imagem is None:
        return
    pasta_bin = 'Bin'
    os.makedirs(pasta_bin, exist_ok=True)
    nome_base, extensao = os.path.splitext(nome_arquivo)
    caminho_destino = os.path.join(pasta_bin, f"{nome_base}_limiar_{limiar if limiar is not None else 'otsu'}_{metodo}.png")
    cv2.imwrite(caminho_destino, imagem)
    print(f"Imagem binarizada salva em {caminho_destino}")


# Função para plotar gráfico B/D x Propriedade com regressão linear
def plot_b_d_vs_property(b_d_values, propriedade_values, metodos):
    if not b_d_values or not propriedade_values:
        return
    os.makedirs('graficos', exist_ok=True)

    # Função para a regressão linear (y = a*x + b)
    def func_linear(x, a, b):
        return a * x + b

    fig, ax = plt.subplots()
    for i, metodo in enumerate(metodos):
        y_data = [bd[i] for bd in b_d_values]
        ax.plot(propriedade_values, y_data, marker='o', label=metodo)
        # Regressão Linear
        params, covariance = curve_fit(func_linear, propriedade_values, y_data)
        a, b = params
        x_fit = np.linspace(min(propriedade_values), max(propriedade_values), 100)
        y_fit = func_linear(x_fit, a, b)
        ax.plot(x_fit, y_fit, label=f'{metodo} - Fit: y = {a:.2f}x + {b:.2f}')


    ax.set_title('Gráfico B/D vs Propriedade')
    ax.set_xlabel('Propriedade')
    ax.set_ylabel('B/D')
    ax.legend()
    ax.grid(True)
    caminho_grafico = os.path.join('graficos', 'grafico_bd_vs_propriedade.png')
    plt.savefig(caminho_grafico)
    plt.show()


# Função para gerar gráfico de Hurst
def plot_hurst(values, eixo, nome_grafico, contador_imagem):
    if not values:
        return
    os.makedirs('graficos', exist_ok=True)
    plt.plot(values)
    plt.title(f'Expoente de Hurst por {eixo}')
    plt.xlabel(f'Índice de {eixo}')
    plt.ylabel('Expoente de Hurst')
    plt.grid(True)
    caminho_grafico = os.path.join('graficos', f'hurst_{contador_imagem}.png')
    plt.savefig(caminho_grafico)
    plt.show()


# Função principal de processamento
def processar_imagem(caminho_imagem, nome_propriedade, valor_propriedade, metodos, calcular_hurst_linhas=False, calcular_hurst_colunas=False, contador_imagem=0):
    imagem = carregar_imagem_em_escala_de_cinza(caminho_imagem)
    if imagem is None:
        return None, None, None, None, None, None

    valores_hurst_linhas = None
    valores_hurst_colunas = None

    if calcular_hurst_linhas:
        valores_hurst_linhas = [calc_hurst_exponent(linha) for linha in imagem]

    if calcular_hurst_colunas:
        valores_hurst_colunas = [calc_hurst_exponent(coluna) for coluna in imagem.T]

    resultados_binarizacao = []
    b_d_valores = []
    imagens_binarizadas = []
    metodos_usados = [] # adicionado para guardar os metodos usados

    for metodo, limiar in metodos:
        imagem_binarizada = binarizar_imagem(imagem, metodo, limiar)
        if imagem_binarizada is None:
            continue
        b, d = contar_pixels_brancos_e_pretos(imagem_binarizada)
        bd = b / d if d != 0 else 0
        resultados_binarizacao.append(f"Método: {metodo}, Limiar: {limiar if limiar is not None else 'Otsu'}, B: {b}, D: {d}, B/D: {bd:.4f}")
        b_d_valores.append(bd)
        imagens_binarizadas.append(imagem_binarizada)
        salvar_imagem(imagem_binarizada, os.path.basename(caminho_imagem), limiar if limiar is not None else "otsu", metodo, contador_imagem)
        metodos_usados.append(metodo) # adicionado para guardar os metodos usados

    porcentagem_saturacao = calcular_porcentagem_saturacao(imagem)

    hurst_medio_linhas = np.mean(valores_hurst_linhas) if valores_hurst_linhas is not None and len(valores_hurst_linhas) > 0 else None
    hurst_medio_colunas = np.mean(valores_hurst_colunas) if valores_hurst_colunas is not None and len(valores_hurst_colunas) > 0 else None

    resultado_texto = f"Propriedade: {nome_propriedade}, Valor: {valor_propriedade}\n"
    resultado_texto += f"Saturação: {porcentagem_saturacao:.2f}%\n"
    resultado_texto += "\n".join(resultados_binarizacao) + "\n"
    resultado_texto += f"Hurst Médio por Linhas: {hurst_medio_linhas:.4f}\n" if hurst_medio_linhas is not None else ""
    resultado_texto += f"Hurst Médio por Colunas: {hurst_medio_colunas:.4f}\n" if hurst_medio_colunas is not None else ""

    return resultado_texto, valores_hurst_linhas, valores_hurst_colunas, b_d_valores, imagens_binarizadas, metodos_usados


# Variáveis para armazenar dados de múltiplas imagens
resultados_processamento = []  # Armazena todos os resultados para múltiplos limiares e métodos
contador_imagens = 0  # Contador para nomear arquivos de forma única


# Interface gráfica com tkinter
def mostrar_resultados(resultado):
    text_resultados.delete(1.0, tk.END)
    text_resultados.insert(tk.END, resultado)

def gerar_histograma(imagem, contador_imagem):
    if imagem is None:
        messagebox.showerror("Erro", "Nenhuma imagem disponível para gerar histograma.")
        return
    plt.hist(imagem.ravel(), bins=256, range=(0, 255), color='black', histtype='step', linestyle='solid')
    plt.title('Histograma da Imagem Original')
    plt.xlabel('Intensidade de Cinza')
    plt.ylabel('Número de Pixels')
    caminho_grafico = os.path.join('graficos', f'histograma_imagem_{contador_imagem}.png')
    os.makedirs('graficos', exist_ok=True)
    plt.savefig(caminho_grafico)
    plt.show()

def gerar_grafico_hurst(eixo, valores_hurst, contador_imagem):
    if valores_hurst is None:
        messagebox.showerror("Erro", "Nenhum dado de Hurst disponível para gerar gráfico.")
        return
    plot_hurst(valores_hurst, eixo, "hurst", contador_imagem)


def gerar_grafico_bd_vs_propriedade():
    if not resultados_processamento:
        messagebox.showwarning("Aviso", "Nenhuma imagem processada ainda.")
        return

    try:
        propriedade_values = [r[1] for r in resultados_processamento]
        b_d_values = [r[3] for r in resultados_processamento]
        # Encontra todos os métodos usados para garantir que o gráfico seja consistente
        todos_metodos = set()
        for resultado in resultados_processamento:
            todos_metodos.update(resultado[4])
        metodos = sorted(list(todos_metodos))

        plot_b_d_vs_property(b_d_values, propriedade_values, metodos)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar gráfico: {e}")


def selecionar_imagem():
    global resultados_processamento, contador_imagens
    caminho_imagem = filedialog.askopenfilename(title="Selecione uma Imagem", filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp"), ("Todos os Arquivos", "*.*")])
    if caminho_imagem:
        nome_propriedade = entry_nome_propriedade.get()
        try:
            valor_propriedade = float(entry_valor_propriedade.get())
        except ValueError:
            messagebox.showerror("Erro", "Insira um valor numérico para a propriedade.")
            return

        metodos = []
        if var_otsu.get():
            metodos.append(('otsu', None))
        if var_especifico.get():
            try:
                limiar_especifico = int(entry_limiar_especifico.get())
                metodos.append(('especifico', limiar_especifico))
            except ValueError:
                messagebox.showerror("Erro", "Insira um valor inteiro para o limiar específico.")
                return
        if var_adaptativo_medio.get():
            metodos.append(('adaptativo_medio', None))
        if var_adaptativo_gaussiano.get():
            metodos.append(('adaptativo_gaussiano', None))

        if not metodos:
            messagebox.showerror("Erro", "Selecione pelo menos um método de binarização.")
            return

        calcular_hurst_linhas = var_hurst_linhas.get()
        calcular_hurst_colunas = var_hurst_colunas.get()


        try:
            resultado_texto, valores_hurst_linhas, valores_hurst_colunas, b_d_valores, imagens_binarizadas, metodos_usados = processar_imagem(
                caminho_imagem, nome_propriedade, valor_propriedade, metodos, calcular_hurst_linhas, calcular_hurst_colunas, contador_imagens
            )
            mostrar_resultados(resultado_texto)
            gerar_histograma(carregar_imagem_em_escala_de_cinza(caminho_imagem), contador_imagens)

            if valores_hurst_linhas:
                gerar_grafico_hurst("linhas", valores_hurst_linhas, contador_imagens)
            if valores_hurst_colunas:
                gerar_grafico_hurst("colunas", valores_hurst_colunas, contador_imagens)

            resultados_processamento.append((nome_propriedade, valor_propriedade, resultado_texto, b_d_valores, metodos_usados))

            #Salvar em arquivo de texto - APPEND
            with open('resultados.txt', 'a', encoding='utf-8') as f: #encoding adicionado para lidar com caracteres especiais
                f.write(resultado_texto + "\n--- Nova Imagem ---\n")


        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro durante o processamento: {e}")

        contador_imagens += 1


# Interface gráfica com tkinter
janela = tk.Tk()
janela.title("Processamento de Imagem")

frame = tk.Frame(janela)
frame.pack(padx=10, pady=10)

label_nome_propriedade = tk.Label(frame, text="Nome da Propriedade:")
label_nome_propriedade.grid(row=0, column=0, sticky="w")
entry_nome_propriedade = tk.Entry(frame)
entry_nome_propriedade.grid(row=0, column=1, sticky="ew")

label_valor_propriedade = tk.Label(frame, text="Valor da Propriedade:")
label_valor_propriedade.grid(row=1, column=0, sticky="w")
entry_valor_propriedade = tk.Entry(frame)
entry_valor_propriedade.grid(row=1, column=1, sticky="ew")

var_otsu = tk.BooleanVar()
check_otsu = tk.Checkbutton(frame, text="Otsu", variable=var_otsu)
check_otsu.grid(row=2, column=0, sticky="w")

var_especifico = tk.BooleanVar()
check_especifico = tk.Checkbutton(frame, text="Limiar Específico", variable=var_especifico)
check_especifico.grid(row=3, column=0, sticky="w")
label_limiar_especifico = tk.Label(frame, text="Limiar:")
label_limiar_especifico.grid(row=3, column=1, sticky="w")
entry_limiar_especifico = tk.Entry(frame)
entry_limiar_especifico.grid(row=3, column=2, sticky="ew")

var_adaptativo_medio = tk.BooleanVar()
check_adaptativo_medio = tk.Checkbutton(frame, text="Adaptativo Médio", variable=var_adaptativo_medio)
check_adaptativo_medio.grid(row=4, column=0, sticky="w")

var_adaptativo_gaussiano = tk.BooleanVar()
check_adaptativo_gaussiano = tk.Checkbutton(frame, text="Adaptativo Gaussiano", variable=var_adaptativo_gaussiano)
check_adaptativo_gaussiano.grid(row=5, column=0, sticky="w")

var_hurst_linhas = tk.BooleanVar()
check_hurst_linhas = tk.Checkbutton(frame, text="Calcular Hurst (Linhas)", variable=var_hurst_linhas)
check_hurst_linhas.grid(row=6, column=0, sticky="w")

var_hurst_colunas = tk.BooleanVar()
check_hurst_colunas = tk.Checkbutton(frame, text="Calcular Hurst (Colunas)", variable=var_hurst_colunas)
check_hurst_colunas.grid(row=7, column=0, sticky="w")


botao_selecionar = tk.Button(frame, text="Selecionar Imagem", command=selecionar_imagem)
botao_selecionar.grid(row=8, column=0, columnspan=3, pady=10)

botao_grafico_bd = tk.Button(frame, text="Gerar Gráfico B/D vs Propriedade", command=gerar_grafico_bd_vs_propriedade)
botao_grafico_bd.grid(row=9, column=0, columnspan=3, pady=10)

text_resultados = tk.Text(janela, height=10, width=50)
text_resultados.pack(padx=10, pady=10)

janela.mainloop()
