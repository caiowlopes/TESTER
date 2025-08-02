import numpy as np
print()
# Constantes físicas #
mu_0 = 4 * np.pi * 1e-7  # Permeabilidade do vácuo [H/m]
rho_cobre = 1.68e-8  # Resistividade do cobre [Ohm·m]

def txt_save(parametro_in: dict, parametro_out: dict, txt_name: str = "dados_coilgun"):
    """
    Salvando os dados de entrada e saida.
    """
    with open(f"{txt_name}.txt", "a", encoding="utf-8") as arquivo:
        arquivo.write("Entradas:\n")
        for key, (descricao, value) in parametro_in.items(): 
            arquivo.write(f"{descricao} ({key}): {value:.3e}\n")

        arquivo.write("\nSaídas:\n")
        for key, (descricao, value) in parametro_out.items():
            arquivo.write(f"{descricao} ({key}): {value:.3e}\n")

        arquivo.write("\n" + "-" * 50 + "\n\n")  # separador entre execuções


def coilgun( 
    V0: float,
    C: float,
    r_projetil: float,
    l_bobina: float,
    isolamento: float,
    mu_r: float,
    A_fio: float,
    n_camadas: int,
    d_fio_total: float = 0,
):
    """
    Dimensioanmento da bobina.
    """

    # ==== Cálculo do fio ==== #
    A_fio = A_fio * 1e-6  # Convertendo mm² para m²
    d_fio = 2 * np.sqrt(A_fio / np.pi)
    if A_fio > 1.5e-6:  # Se a seção do fio for maior que 1.5 mm²
        isolamento = d_fio
    if d_fio_total==0:
        d_fio_total = d_fio + 2 * isolamento  # Diâmetro com isolamento


    # ==== Geometria da bobina ==== #
    r_interno = r_projetil + 0.25e-3  # Folga entre projétil e bobina mais a camada da impressora 3D
    r_externo_max = r_interno * 3  # Raio máximo da bobina
    # n_camadas = int((r_externo_max - r_interno) // d_fio_total)
    espiras_por_camada = int(l_bobina // d_fio_total)
    N = espiras_por_camada * n_camadas  # Total de espiras
    r_externo = r_interno + n_camadas * d_fio_total
    r_medio = (r_interno + r_externo) / 2

    # ==== Comprimento do fio e resistência ==== #
    comprimento_fio = 2 * np.pi * r_medio * N
    R = rho_cobre * comprimento_fio / A_fio

    # ==== Indutância ==== #
    A_bobina = np.pi * r_projetil**2
    mu = mu_0 * mu_r
    L = mu * N**2 * A_bobina / l_bobina

    # ==== Corrente máxima e energia ==== #
    Z = np.sqrt(L / C)
    I_max = V0 / Z
    # E_cap = 0.5 * C * V0**2

    # ==== Força magnética aproximada ==== #
    F_m = 0.5 * (mu * N**2 * A_bobina / l_bobina**2) * I_max**2

    # ==== Resultados ==== #
    def print_result():
        
        print(f"Camadas: {n_camadas}")
        print(f"Número total de espiras: {N}")
        print(f"Espiras por camada: {espiras_por_camada}")
        print(f"Raio interno da bobina: {r_interno*1e2} cm")
        print(f"Raio externo da bobina: {r_externo*1e2:.3f} cm")
        print(f"Comprimento do fio: {comprimento_fio:.3f} m")
        # print(f"Resistência total: {R:.5f} Ohm")
        # print(f"Indutância: {L:.5f} H")
        print(f"Corrente máxima estimada: {I_max:.4f} A")
        print(f"Força magnética aproximada: {F_m:.4f} N\n")
        print(f'Aceleraçao: {F_m / 10e-3:.2f} m/s²')  # Considerando um projétil de 10g

    print_result()
    parameters_out = {
        "N": ("Número total de espiras", N),
        "n_camadas": ("Número de camadas", n_camadas),
        "espiras_por_camada": ("Espiras por camada", espiras_por_camada),
        "r_interno": ("Raio interno da bobina [m]", r_interno),
        "r_externo": ("Raio externo da bobina [m]", r_externo),
        "comprimento_fio": ("Comprimento total do fio [m]", comprimento_fio),
        "R": ("Resistência total [Ohm]", R),
        "L": ("Indutância [H]", L),
        "I_max": ("\nCorrente máxima estimada [A]", I_max),
        "F_m": ("Força magnética aproximada [N]", F_m),
    }

    return parameters_out

# ==== Parâmetros do circuito ==== #
parameters_in = {
    "A_fio": ["Seção do fio [mm²]", 1],
    "l_bobina": ["Comprimento da bobina [m]", 1.7e-2],
    "V0": ["Tensão inicial [V]", 7.4],
    "n_camadas": ["Número de camadas", 3],
    # "isolamento": ["Espessura de isolamento do fio [m]", 0.05e-3],
    "isolamento": ["Espessura de isolamento do fio [m]", 0],
    "r_projetil": ["Raio do projétil [m]", 3e-3],
    "mu_r": ["Permeabilidade relativa do núcleo", 1000],  #  (ar = 1, ferro = 1000+),
    "C": ["Capacitância [F]", 470e-6],
    'Tamanho do fio [m]': ["Tamanho do fio [m]", 1.5],
}

 # === Iteração === #
valores_in = {k: v[1] for k, v in parameters_in.items()}
parameters_saida = coilgun(**valores_in)
txt_save(parameters_in, parameters_saida, txt_name='Final_dados_coilgun')
