import tkinter as tk
import pandas as pd
from itertools import product
from PIL import Image, ImageTk  

paises = {
    "EUA": ["F-22", "F-35A", "F-15E", "F-15C", "F-15EX", "F-16C", "F/A-18E", "F/A-18G", "A-10C", "U-2"],
    "Rússia": ["Su-57", "Su-35S", "Su-30SM", "Su-34", "MiG-29SMT", "MiG-31BM"],
    "China": ["J-20", "J-16", "J-10C", "FC-31", "Y-20", "JH-7"],
    "França": ["Rafale", "Mirage 2000D", "Mirage 2000C", "Tornado ECR"],
    "Reino Unido": ["Typhoon", "F-35B", "F-35C", "Tornado GR4"],
    "Suécia": ["Gripen C", "Gripen E", "Draken", "Viggen", "JAS 39D"],
    "Japão": ["F-2", "F-15J", "F-35A", "E-2C Hawkeye"]
}

climas = ["Bom", "Nublado", "Chuva"]
distancias = ["Curta", "Média", "Longa"]
tipoMissao = ["Bombardeio estratégico", "Reconhecimento estratégico", "Combate", "Defesa Aérea", "Interceptação", "Combate BVR", "Guerra eletrônica"]

missoes_por_aeronave = {
    # EUA
    "F-22": ["Combate", "Defesa Aérea", "Interceptação", "Combate BVR"],
    "F-35A": ["Combate", "Defesa Aérea", "Interceptação", "Combate BVR", "Guerra eletrônica"],
    "F-15E": ["Bombardeio estratégico", "Combate", "Combate BVR"],
    "F-15C": ["Defesa Aérea", "Interceptação", "Combate BVR"],
    "F-15EX": ["Defesa Aérea", "Interceptação", "Combate", "Combate BVR"],
    "F-16C": ["Combate", "Defesa Aérea", "Combate BVR"],
    "F/A-18E": ["Combate", "Defesa Aérea", "Combate BVR"],
    "F/A-18F": ["Combate", "Defesa Aérea", "Combate BVR"],
    "F/A-18G": ["Guerra eletrônica", "Defesa Aérea"],
    "A-10C": ["Combate", "Bombardeio estratégico"],
    "U-2": ["Reconhecimento estratégico"],

    # Rússia
    "Su-57": ["Combate", "Defesa Aérea", "Interceptação", "Combate BVR"],
    "Su-35S": ["Combate", "Defesa Aérea", "Combate BVR"],
    "Su-30SM": ["Combate", "Defesa Aérea", "Combate BVR"],
    "Su-34": ["Bombardeio estratégico", "Combate"],
    "MiG-29SMT": ["Combate", "Defesa Aérea"],
    "MiG-31BM": ["Interceptação", "Combate BVR"],

    # China
    "J-20": ["Combate", "Defesa Aérea", "Interceptação", "Combate BVR"],
    "J-16": ["Combate", "Defesa Aérea", "Bombardeio estratégico", "Combate BVR"],
    "J-10C": ["Combate", "Defesa Aérea", "Combate BVR"],
    "FC-31": ["Combate", "Interceptação", "Combate BVR"],
    "JH-7": ["Bombardeio estratégico", "Combate"],

    # França
    "Rafale": ["Combate", "Defesa Aérea", "Bombardeio estratégico", "Combate BVR", "Guerra eletrônica"],
    "Mirage 2000D": ["Bombardeio estratégico", "Combate BVR"],
    "Mirage 2000C": ["Defesa Aérea", "Interceptação"],
    "Tornado ECR": ["Bombardeio estratégico", "Guerra eletrônica"],

    # Reino Unido
    "Typhoon": ["Combate", "Defesa Aérea", "Combate BVR"],
    "F-35B": ["Combate", "Interceptação", "Guerra eletrônica", "Combate BVR"],
    "F-35C": ["Combate", "Interceptação", "Guerra eletrônica", "Combate BVR"],
    "Tornado GR4": ["Bombardeio estratégico"],

    # Suécia
    "Gripen C": ["Combate", "Defesa Aérea", "Combate BVR"],
    "Gripen E": ["Combate", "Defesa Aérea", "Combate BVR", "Guerra eletrônica"],
    "Draken": ["Combate"],
    "Viggen": ["Bombardeio estratégico", "Combate"],
    "JAS 39D": ["Combate", "Defesa Aérea", "Combate BVR"],

    # Japão
    "F-2": ["Combate", "Defesa Aérea", "Combate BVR"],
    "F-15J": ["Defesa Aérea", "Interceptação", "Combate BVR"],
    "E-2C Hawkeye": ["Reconhecimento estratégico"]
}

stats_aeronaves = {
    "F-22": {"Velocidade Máx": 2414, "Alcance": 2960, "Stealth": 1.0, "Manobrabilidade": 1.0, "Radar": 9.0, "RCS": 0.0001},
    "F-35A": {"Velocidade Máx": 1930, "Alcance": 2220, "Stealth": 0.9, "Manobrabilidade": 0.8, "Radar": 8.5, "RCS": 0.001},
    "F-15E": {"Velocidade Máx": 2655, "Alcance": 1271, "Stealth": 0.1, "Manobrabilidade": 0.6, "Radar": 8.0, "RCS": 5.0},
    "F-15C": {"Velocidade Máx": 2655, "Alcance": 1950, "Stealth": 0.0, "Manobrabilidade": 0.65, "Radar": 7.5, "RCS": 10.0},
    "F-15EX": {"Velocidade Máx": 2655, "Alcance": 2400, "Stealth": 0.2, "Manobrabilidade": 0.7, "Radar": 8.5, "RCS": 4.0},
    "F-16C": {"Velocidade Máx": 2120, "Alcance": 4220, "Stealth": 0.0, "Manobrabilidade": 0.85, "Radar": 7.0, "RCS": 5.0},
    "F/A-18E": {"Velocidade Máx": 1915, "Alcance": 2346, "Stealth": 0.1, "Manobrabilidade": 0.8, "Radar": 7.8, "RCS": 1.0},
    "F/A-18F": {"Velocidade Máx": 1915, "Alcance": 2346, "Stealth": 0.1, "Manobrabilidade": 0.8, "Radar": 7.8, "RCS": 1.0},
    "A-10C": {"Velocidade Máx": 706, "Alcance": 1300, "Stealth": 0.0, "Manobrabilidade": 0.4, "Radar": 4.0, "RCS": 10.0},
    "U-2": {"Velocidade Máx": 805, "Alcance": 10300, "Stealth": 0.1, "Manobrabilidade": 0.3, "Radar": 6.5, "RCS": 30.0},
    "Su-57": {"Velocidade Máx": 2600, "Alcance": 3500, "Stealth": 0.8, "Manobrabilidade": 0.95, "Radar": 8.0, "RCS": 0.01},
    "Su-35S": {"Velocidade Máx": 2778, "Alcance": 3600, "Stealth": 0.2, "Manobrabilidade": 0.9, "Radar": 8.0, "RCS": 4.0},
    "Su-30SM": {"Velocidade Máx": 2120, "Alcance": 3000, "Stealth": 0.1, "Manobrabilidade": 0.85, "Radar": 7.5, "RCS": 5.0},
    "Su-34": {"Velocidade Máx": 1900, "Alcance": 4500, "Stealth": 0.1, "Manobrabilidade": 0.6, "Radar": 6.0, "RCS": 15.0},
    "MiG-29SMT": {"Velocidade Máx": 2400, "Alcance": 2100, "Stealth": 0.0, "Manobrabilidade": 0.85, "Radar": 6.8, "RCS": 5.0},
    "MiG-31BM": {"Velocidade Máx": 3000, "Alcance": 1450, "Stealth": 0.0, "Manobrabilidade": 0.5, "Radar": 9.0, "RCS": 15.0},
    "J-20": {"Velocidade Máx": 2100, "Alcance": 5500, "Stealth": 0.9, "Manobrabilidade": 0.85, "Radar": 8.5, "RCS": 0.05},
    "J-16": {"Velocidade Máx": 2450, "Alcance": 3900, "Stealth": 0.3, "Manobrabilidade": 0.75, "Radar": 7.5, "RCS": 6.0},
    "J-10C": {"Velocidade Máx": 2300, "Alcance": 2940, "Stealth": 0.2, "Manobrabilidade": 0.8, "Radar": 7.0, "RCS": 3.0},
    "FC-31": {"Velocidade Máx": 2200, "Alcance": 2000, "Stealth": 0.8, "Manobrabilidade": 0.85, "Radar": 8.0, "RCS": 0.3},
    "JH-7": {"Velocidade Máx": 1800, "Alcance": 3700, "Stealth": 0.1, "Manobrabilidade": 0.6, "Radar": 6.0, "RCS": 8.0},
    "Rafale": {"Velocidade Máx": 2130, "Alcance": 3700, "Stealth": 0.2, "Manobrabilidade": 0.85, "Radar": 7.5, "RCS": 1.0},
    "Mirage 2000D": {"Velocidade Máx": 2338, "Alcance": 1550, "Stealth": 0.1, "Manobrabilidade": 0.7, "Radar": 6.5, "RCS": 2.0},
    "Mirage 2000C": {"Velocidade Máx": 2338, "Alcance": 1550, "Stealth": 0.1, "Manobrabilidade": 0.7, "Radar": 6.5, "RCS": 2.0},
    "Tornado ECR": {"Velocidade Máx": 2400, "Alcance": 1400, "Stealth": 0.1, "Manobrabilidade": 0.5, "Radar": 6.0, "RCS": 6.0},
    "Typhoon": {"Velocidade Máx": 2495, "Alcance": 2900, "Stealth": 0.2, "Manobrabilidade": 0.9, "Radar": 8.0, "RCS": 1.5},
    "F-35B": {"Velocidade Máx": 1930, "Alcance": 1670, "Stealth": 0.9, "Manobrabilidade": 0.75, "Radar": 8.5, "RCS": 0.001},
    "F-35C": {"Velocidade Máx": 1930, "Alcance": 2520, "Stealth": 0.9, "Manobrabilidade": 0.75, "Radar": 8.5, "RCS": 0.001},
    "Tornado GR4": {"Velocidade Máx": 2338, "Alcance": 1390, "Stealth": 0.1, "Manobrabilidade": 0.5, "Radar": 6.0, "RCS": 6.0},
    "Gripen C": {"Velocidade Máx": 2470, "Alcance": 3200, "Stealth": 0.1, "Manobrabilidade": 0.85, "Radar": 7.2, "RCS": 1.0},
    "Gripen E": {"Velocidade Máx": 2470, "Alcance": 4000, "Stealth": 0.2, "Manobrabilidade": 0.9, "Radar": 8.0, "RCS": 0.8},
    "Draken": {"Velocidade Máx": 2124, "Alcance": 1200, "Stealth": 0.0, "Manobrabilidade": 0.6, "Radar": 4.5, "RCS": 6.0},
    "Viggen": {"Velocidade Máx": 2230, "Alcance": 2000, "Stealth": 0.0, "Manobrabilidade": 0.7, "Radar": 5.5, "RCS": 6.0},
    "JAS 39D": {"Velocidade Máx": 2470, "Alcance": 3200, "Stealth": 0.1, "Manobrabilidade": 0.85, "Radar": 7.2, "RCS": 1.0},
    "F-2": {"Velocidade Máx": 2100, "Alcance": 3000, "Stealth": 0.2, "Manobrabilidade": 0.8, "Radar": 7.0, "RCS": 2.0},
    "F-15J": {"Velocidade Máx": 2655, "Alcance": 3000, "Stealth": 0.0, "Manobrabilidade": 0.7, "Radar": 7.5, "RCS": 5.0},
    "E-2C Hawkeye": {"Velocidade Máx": 648, "Alcance": 2700, "Stealth": 0.0, "Manobrabilidade": 0.2, "Radar": 9.0, "RCS": 20.0}
}

pesos_por_missao = {
    "Bombardeio estratégico": {
        "Velocidade": 0.2,
        "Alcance": 0.4,
        "Stealth": 0.3,
        "Manobrabilidade": 0.1
    },
    "Reconhecimento estratégico": {
        "Velocidade": 0.3,
        "Alcance": 0.4,
        "Stealth": 0.3,
        "Manobrabilidade": 0.0
    },
    "Combate": {
        "Velocidade": 0.25,
        "Alcance": 0.2,
        "Stealth": 0.25,
        "Manobrabilidade": 0.3
    },
    "Defesa Aérea": {
        "Velocidade": 0.3,
        "Alcance": 0.2,
        "Stealth": 0.2,
        "Manobrabilidade": 0.3
    },
    "Interceptação": {
        "Velocidade": 0.5,
        "Alcance": 0.2,
        "Stealth": 0.1,
        "Manobrabilidade": 0.2
    },
    "Combate BVR": {
        "Velocidade": 0.5,
        "Alcance": 0.4,
        "Stealth": 0.8,
        "Manobrabilidade": 0.2
    },
    "Guerra eletrônica": {
        "Velocidade": 0.6,
        "Alcance": 0.7,
        "Stealth": 0.65,
        "Manobrabilidade": 0.2
    }
}

def normalizar(valor, minimo, maximo):
    return max(0, min(1, (valor - minimo) / (maximo - minimo)))

def calcular_probabilidade(nome_aeronave, clima, distancia, missao):
    if nome_aeronave not in stats_aeronaves:
        return 0

    pesos = pesos_por_missao.get(missao)
    if pesos is None:
        return 0

    s = stats_aeronaves[nome_aeronave]
    stealth = s["Stealth"]
    alcance = normalizar(s["Alcance"], 500, 4000)
    velocidade = normalizar(s["Velocidade Máx"], 900, 3000)
    manobrab = s.get("Manobrabilidade", 0.5)

    indice = (
        stealth * pesos["Stealth"] +
        alcance * pesos["Alcance"] +
        velocidade * pesos["Velocidade"] +
        manobrab * pesos["Manobrabilidade"]
    )

    penalidades_clima = {"Bom": 0.0, "Nublado": 0.1, "Chuva": 0.2}
    penalidades_dist = {"Curta": 0.0, "Média": 0.1, "Longa": 0.2}
    penalidade = penalidades_clima.get(clima, 0) + penalidades_dist.get(distancia, 0)

    final = max(0, indice - penalidade)
    return round(final * 100, 1)

def calcular_probabilidade_reconhecimento(stats, clima, distancia):
    stealth = stats["Stealth"]
    alcance = normalizar(stats["Alcance"], 500, 4000)
    manobrab = stats.get("Manobrabilidade", 0.5)
    velocidade = normalizar(stats["Velocidade Máx"], 900, 3000)
    penalidades_clima = {"Bom": 0.0, "Nublado": 0.1, "Chuva": 0.2}

    coleta = stealth * alcance
    nao_detectado = stealth * manobrab * (1 - penalidades_clima.get(clima, 0))
    retorno = alcance * velocidade * manobrab

    prob_final = 0.4 * coleta + 0.4 * nao_detectado + 0.2 * retorno

    return {
        "final": round(prob_final * 100, 1),
        "coleta": round(coleta * 100, 1),
        "discricao": round(nao_detectado * 100, 1),
        "retorno": round(retorno * 100, 1)
    }

def calcular_probabilidade_bvr(stats, clima="Bom", distancia="Longa"):
    rcs = stats["RCS"]
    radar = stats["Radar"]

    visibilidade_relativa = rcs / radar 

    min_vis = 0.00001 / 500  
    max_vis = 25 / 150      

    indice_base = 1 - normalizar(visibilidade_relativa, min_vis, max_vis)

    penalidades_clima = {"Bom": 0.0, "Nublado": 0.1, "Chuva": 0.2}
    penalidades_dist = {"Curta": 0.0, "Média": 0.05, "Longa": 0.1}

    penalidade = penalidades_clima.get(clima, 0) + penalidades_dist.get(distancia, 0)

    final = max(0, indice_base - penalidade)
    return round(final * 100, 1)


janela = tk.Tk()
janela.title("Simulador Aéreo")
janela.geometry("1000x400")
janela.configure(bg="#1e1e1e")

fundo_cor = "#1e1e1e"
texto_cor = "white"

frame_esquerda = tk.Frame(janela, bg=fundo_cor, width=300)
frame_centro   = tk.Frame(janela, bg=fundo_cor, width=400)
frame_direita  = tk.Frame(janela, bg=fundo_cor, width=300)

frame_esquerda.pack(side="left", fill="both", expand=False, padx=20, pady=20)
frame_centro.pack(side="left", fill="both", expand=True, padx=20, pady=20)
frame_direita.pack(side="left", fill="both", expand=False, padx=20, pady=20)

pais_var = tk.StringVar(value="EUA")
aeronave_var = tk.StringVar()
clima_var = tk.StringVar(value="Bom")
distancia_var = tk.StringVar(value="Curta")
missao_var = tk.StringVar()
missao_var.set(tipoMissao[0])

tk.Label(frame_esquerda, text="País:", fg=texto_cor, bg=fundo_cor, font=("Arial", 12)).pack(pady=5)
menu_pais = tk.OptionMenu(frame_esquerda, pais_var, *paises.keys())
menu_pais.config(font=("Arial", 14), width=22)
menu_pais.pack()

tk.Label(frame_esquerda, text="Missão:", fg=texto_cor, bg=fundo_cor, font=("Arial", 12)).pack(pady=5)
menu_missao = tk.OptionMenu(frame_esquerda, missao_var, *tipoMissao)
menu_missao.config(font=("Arial", 14), width=22)
menu_missao.pack()

tk.Label(frame_esquerda, text="Aeronave:", fg=texto_cor, bg=fundo_cor, font=("Arial", 12)).pack(pady=5)
menu_aeronave = tk.OptionMenu(frame_esquerda, aeronave_var, "")
menu_aeronave.config(font=("Arial", 12), width=20)
menu_aeronave.pack()

tk.Label(frame_esquerda, text="Clima:", fg=texto_cor, bg=fundo_cor, font=("Arial", 12)).pack(pady=5)
menu_clima = tk.OptionMenu(frame_esquerda, clima_var, *climas)
menu_clima.config(font=("Arial", 12), width=20)
menu_clima.pack()

tk.Label(frame_esquerda, text="Distância:", fg=texto_cor, bg=fundo_cor, font=("Arial", 12)).pack(pady=5)
menu_distancia = tk.OptionMenu(frame_esquerda, distancia_var, *distancias)
menu_distancia.config(font=("Arial", 12), width=20)
menu_distancia.pack()


def calcular():
    nome = aeronave_var.get()
    clima = clima_var.get()
    distancia = distancia_var.get()
    missao = missao_var.get()

    if nome not in stats_aeronaves:
        resultado_label.config(text="Aeronave não encontrada.")
        return

    stats = stats_aeronaves[nome]

    if missao == "Combate BVR":
        prob = calcular_probabilidade_bvr(stats, clima=clima, distancia=distancia)
    elif missao == "Reconhecimento estratégico":
        resultado = calcular_probabilidade_reconhecimento(stats, clima, distancia)
        resultado_label.config(
            text=(
                f"Probabilidade para missão '{missao}': {resultado['final']}%\n\n"
                f"- Coleta de dados: {resultado['coleta']}%\n"
                f"- Não ser detectado: {resultado['discricao']}%\n"
                f"- Retorno seguro: {resultado['retorno']}%"
            )
        )
    else:
        prob = calcular_probabilidade(nome, clima, distancia, missao)

    resultado_label.config(
        text=f"Probabilidade para missão '{missao}': {prob}%"
    )

    atualizar_imagem()

def atualizar_imagem():
    nome = aeronave_var.get().lower().replace("-", "").replace(" ", "").replace("/", "")
    caminho = f"img/{nome}.png"
    try:
        img = Image.open(caminho)

        max_width, max_height = 300, 150

        img.thumbnail((max_width, max_height), Image.LANCZOS)
        
        foto = ImageTk.PhotoImage(img)
        imagem_label.configure(image=foto, text="") 
        imagem_label.image = foto
    except:
        imagem_label.configure(image="", text="Imagem não encontrada", fg="red", bg=fundo_cor, font=("Arial", 12))
    
    nome_exibido = aeronave_var.get()
    if nome_exibido in stats_aeronaves:
        stats = stats_aeronaves[nome_exibido]
        texto_stats = "\n".join([f"{chave}: {valor}" for chave, valor in stats.items()])
        stats_label.config(text=texto_stats)
    else:
        stats_label.config(text="Estatísticas não disponíveis.")

tk.Button(
    frame_esquerda,
    text="Calcular Probabilidade",
    font=("Arial", 12),
    width=22,
    height=2,
    command=calcular
).pack(pady=20)

imagem_label = tk.Label(frame_centro, bg=fundo_cor)
imagem_label.pack(pady=20)

stats_label = tk.Label(frame_centro, text="", fg="white", bg=fundo_cor, font=("Arial", 12), justify="left")
stats_label.pack(pady=10)

def atualizar_aeronaves(*args):
    pais = pais_var.get()
    missao = missao_var.get()

    if not missao:
        return  

    todas = paises[pais]
    validas = [a for a in todas if a in missoes_por_aeronave and missao in missoes_por_aeronave[a]]

    menu = menu_aeronave["menu"]
    menu.delete(0, "end")

    if not validas:
        aeronave_var.set("")
        menu.add_command(label="Nenhuma disponível", command=lambda: aeronave_var.set(""))
        stats_label.config(text="Nenhuma aeronave compatível com essa missão.")
        imagem_label.configure(image="", text="")
        return

    for aeronave in validas:
        menu.add_command(label=aeronave, command=lambda value=aeronave: aeronave_var.set(value))

    aeronave_var.set(validas[0])
    atualizar_imagem()

aeronave_var.trace("w", lambda *args: atualizar_imagem())
pais_var.trace("w", atualizar_aeronaves)
atualizar_aeronaves()

tk.Label(frame_direita, text="Resultado da Missão:", fg=texto_cor, bg=fundo_cor, font=("Arial", 14)).pack(pady=10)
resultado_label = tk.Label(frame_direita, text="Aguardando simulação...", fg="lime", bg=fundo_cor, font=("Arial", 12), wraplength=250)
resultado_label.pack(pady=10)

missao_var.trace("w", atualizar_aeronaves)

janela.mainloop()