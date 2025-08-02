import numpy as np
from numpy import pi
print()
# Constantes físicas #
mu_0 = 4 * pi * 1e-7  # Permeabilidade do vácuo [H/m]
rho_cobre = 1.68e-8  # Resistividade do cobre [Ohm·m]

# ==== Parâmetros do circuito ==== #
parameters_in = {
    "altura_carretel": ["Comprimento da bobina [m]", 2.3e-2],
    'd_interno_bob': ["Diâmetro interno da bobina [m]", 2e-2],

    "C": ["Capacitância [F]", 470e-6],
    "V0": ["Tensão inicial [V]", 7.4],
    "A_fio": ["Seção do fio [mm²]", 1],
    'comp_total_fio': ["Comprimento do fio [m]", 1.5],
    'd_total_fio': ["Diâmetro do fio com isolamento [m]", 2e-3],
    
    # "d_projetil": ["Diâmetro do projétil [m]", 3e-3],
    # "mu_r": ["Permeabilidade relativa do núcleo", 1000],  
    #  (ar = 1, ferro = 1000+),
}


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


def espiras_e_camadas(altura_carretel, diam_fio, r1, tamanho_fio):
    voltas_por_camada = altura_carretel / diam_fio
    doispi = 2 * pi 
    camadas_completas = 0
    tamanho_restante_do_fio = tamanho_fio

    while True:
        raio_atual = r1 + camadas_completas * diam_fio
        circunferencia = doispi * raio_atual
        comprimento_necessario = circunferencia * voltas_por_camada

        if tamanho_restante_do_fio >= comprimento_necessario:
            tamanho_restante_do_fio -= comprimento_necessario
            camadas_completas += 1
        else:
            break

    # Verifica se há fio restante para uma camada parcial
    raio_ultima = r1 + camadas_completas * diam_fio
    circunferencia_ultima = doispi * raio_ultima
    voltas_ultima_camada = tamanho_restante_do_fio / circunferencia_ultima

    # Totais
    voltas_totais = camadas_completas * voltas_por_camada + voltas_ultima_camada

    # Camadas totais (com fração)
    camadas_total = camadas_completas + (voltas_ultima_camada / voltas_por_camada)

    print(f"\nCamadas completas: {camadas_completas}")
    print(f"Camadas totais: {camadas_total:.2f}")
    print(f"Voltas por camada (máximo): {voltas_por_camada:.2f}")
    print(f"Voltas na última camada: {voltas_ultima_camada:.2f}")
    print(f"Total de voltas: {voltas_totais:.2f}")
    print(f"Fio restante (m): {tamanho_restante_do_fio:.4f}")

    return voltas_por_camada, camadas_total, voltas_totais

# espiras_e_camadas(
#     altura_carretel=1.7e-2,
#     diam_fio=2e-3,
#     r1=2e-2 / 2,
#     tamanho_fio=1.5
# )


def coilgun( 
    V0: float,
    C: float,
    altura_carretel: float,
    A_fio: float,
    d_interno_bob: float,
    d_total_fio: float,
    comp_total_fio: float,
    mu_r: float = 1000, #  (ar = 1, ferro = 1000+)
):
    """
    Dimensioanmento da bobina.
    """
    # === Costantes === #
    # r_projetil = d_projetil / 2
    r_interno_bob = d_interno_bob / 2
    n_camadas = 0

    # ==== Cálculo do fio ==== #
    A_fio = A_fio * 1e-6  # Convertendo mm² para m²

    # ==== Espiras da bobina ==== #
    voltas_por_camada, n_camadas, Total_espiras = espiras_e_camadas(
        altura_carretel=altura_carretel,
        diam_fio=d_total_fio,
        r1=r_interno_bob,
        tamanho_fio=comp_total_fio
    )
    
    # ==== Resistência ==== #
    R = rho_cobre * comp_total_fio / A_fio
    # ==== Indutância ==== #
    A_bobina = pi * r_interno_bob**2
    mu = mu_0 * mu_r
    L = mu * Total_espiras**2 * A_bobina / altura_carretel

    # ==== Corrente máxima e energia ==== #
    Z = np.sqrt(L / C)
    I_max = V0 / Z
    # E_cap = 0.5 * C * V0**2

    # ==== Força magnética aproximada ==== #
    F_m = 0.5 * (mu * Total_espiras**2 * A_bobina / altura_carretel**2) * I_max**2

    # ==== Resultados ==== #
    def print_result():
        """        
        Exibe os resultados do cálculo.
        """
        print(f"Corrente máxima estimada: {I_max:.4f} A")
        print(f"Força magnética aproximada: {F_m:.4f} N")
        print(f'Aceleraçao: {F_m / 10e-3:.2f} m/s²\n')  # Considerando um projétil de 10g

    print_result()
    parameters_out = {
        "N": ("Número total de espiras", Total_espiras),
        "n_camadas": ("Número de camadas", n_camadas),
        "voltas_por_camada": ("Espiras por camada", voltas_por_camada),
        "R": ("Resistência total [Ohm]", R),
        "L": ("Indutância [H]", L),
        "I_max": ("\nCorrente máxima estimada [A]", I_max),
        "F_m": ("Força magnética aproximada [N]", F_m),
    }

    return parameters_out

# === Iteração === #
valores_in = {k: v[1] for k, v in parameters_in.items()}
parameters_saida = coilgun(**valores_in)
# txt_save(parameters_in, parameters_saida, txt_name='dados_coilgun_')

