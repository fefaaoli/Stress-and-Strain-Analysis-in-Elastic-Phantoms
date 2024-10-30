import numpy as np
import scipy.io

# Função para carregar mapas de deslocamento
def load_displacement_map(file_path):
    try:
        mat_data = scipy.io.loadmat(file_path)
        disp_map = mat_data['disp_map']  # Carrega a matriz 3D de deslocamento
        if disp_map.shape == (162, 128, 148):
            print(f"Mapa de deslocamento carregado de: {file_path}")
            print(f"Dimensões do mapa de deslocamento: {disp_map.shape}")
            return disp_map
        else:
            print(f"Erro: Dimensões do mapa de deslocamento inesperadas: {disp_map.shape}")
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado: {file_path}")
    except KeyError:
        print(f"Erro: A chave 'disp_map' não foi encontrada em: {file_path}")
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {file_path}. Detalhes: {e}")

# Carregar os dados de deslocamento para cada phantom
file_path_A = 'C:/Users/mfmdo/OneDrive/Documentos/trabalho biomecância/venv/SRF-SWE-Phantom_P_A.mat'
file_path_B = 'C:/Users/mfmdo/OneDrive/Documentos/trabalho biomecância/venv/SRF-SWE-Phantom_P_B.mat'
file_path_C = 'C:/Users/mfmdo/OneDrive/Documentos/trabalho biomecância/venv/SRF-SWE-Phantom_P_C.mat'

disp_map_A = load_displacement_map(file_path_A)
disp_map_B = load_displacement_map(file_path_B)
disp_map_C = load_displacement_map(file_path_C)

# Parâmetros
dt = 0.0001  # Intervalo de tempo entre frames (s)
dx = 0.2977  # Resolução lateral (mm)
densidade = 900  # Densidade do material (kg/m³)

# Função para calcular a velocidade da onda de cisalhamento usando o tempo ao pico
def calcular_velocidade_onda_tempo_ao_pico(disp_map, dt, dx):
    tempo_pico_por_coluna = np.zeros(disp_map.shape[1])

    for coluna in range(disp_map.shape[1]):
        deslocamento_temporal = disp_map[:, coluna, :]
        media_deslocamento_temporal = deslocamento_temporal.mean(axis=0)
        frame_pico = np.argmax(media_deslocamento_temporal)
        tempo_pico_por_coluna[coluna] = frame_pico * dt

    posicao_inicial = 0
    posicao_final = len(tempo_pico_por_coluna) - 1
    distancia_total = (posicao_final - posicao_inicial) * dx
    tempo_total = tempo_pico_por_coluna[posicao_final] - tempo_pico_por_coluna[posicao_inicial]
    velocidade_onda = distancia_total / tempo_total
    
    return velocidade_onda

# Função para calcular o módulo de Young a partir da velocidade da onda de cisalhamento
def calcular_modulo_de_young(velocidade_onda, densidade):
    velocidade_onda_m_s = velocidade_onda / 1000.0  # Conversão de mm/s para m/s
    modulo_de_young = 3 * densidade * (velocidade_onda_m_s ** 2)
    return modulo_de_young

# Lista de caminhos para os arquivos dos phantoms
file_paths = [
    "C:/Users/mfmdo/OneDrive/Documentos/trabalho biomecância/venv/SRF-SWE-Phantom_P_A.mat",
    "C:/Users/mfmdo/OneDrive/Documentos/trabalho biomecância/venv/SRF-SWE-Phantom_P_B.mat",
    "C:/Users/mfmdo/OneDrive/Documentos/trabalho biomecância/venv/SRF-SWE-Phantom_P_C.mat"
]

# Calcula e armazena os resultados para cada phantom
resultados = []

for file_path in file_paths:
    disp_map = load_displacement_map(file_path)
    if disp_map is not None:  # Verifica se o mapa de deslocamento foi carregado corretamente
        velocidade_onda = calcular_velocidade_onda_tempo_ao_pico(disp_map, dt, dx)
        modulo_de_young = calcular_modulo_de_young(velocidade_onda, densidade)

        resultados.append({
            "file_path": file_path,
            "velocidade_onda": velocidade_onda,
            "modulo_de_young": modulo_de_young
        })

# Exibe os resultados
for i, resultado in enumerate(resultados, 1):
    print(f"Phantom {i}:")
    print(f"  Velocidade da onda de cisalhamento: {resultado['velocidade_onda']:.2f} mm/s")
    print(f"  Módulo de Young: {resultado['modulo_de_young']:.2f} Pa\n")

# Resultados dos phantoms P_A, P_B e P_C (exemplo)
resultados_phantoms = {
    "P_A": {"modulo_de_young": 100000, "velocidade_onda": 6000},
    "P_B": {"modulo_de_young": 220000, "velocidade_onda": 9000},
    "P_C": {"modulo_de_young": 37000, "velocidade_onda": 3700},
}

# Função para encontrar a correspondência
def encontrar_correspondencia(resultados, referencias):
    correspondencias = []

    for i, resultado in enumerate(resultados, 1):
        modulo_de_young = resultado['modulo_de_young']
        velocidade_onda = resultado['velocidade_onda']

        # Encontrar o phantom correspondente
        for referencia, dados in referencias.items():
            if (
                abs(modulo_de_young - dados["modulo_de_young"]) < 5000 and  # Tolerância de 5000 Pa
                abs(velocidade_onda - dados["velocidade_onda"]) < 200      # Tolerância de 200 mm/s
            ):
                correspondencias.append({
                    "phantom_calculado": f"Phantom {i}",
                    "phantom_referencia": referencia,
                    "modulo_de_young": modulo_de_young,
                    "velocidade_onda": velocidade_onda
                })
                break

    return correspondencias

# Resultados obtidos
resultados_obtidos = [
    {"modulo_de_young": 100402.72, "velocidade_onda": 6098.05},
    {"modulo_de_young": 218791.42, "velocidade_onda": 9001.88},
    {"modulo_de_young": 37096.12, "velocidade_onda": 3706.66},
]

# Encontrar correspondências
correspondencias = encontrar_correspondencia(resultados_obtidos, resultados_phantoms)

# Exibir as correspondências
for correspondencia in correspondencias:
    print(f"Correspondência encontrada:")
    print(f"  {correspondencia['phantom_calculado']} correspondente a: {correspondencia['phantom_referencia']}")
    print(f"  Módulo de Young: {correspondencia['modulo_de_young']:.2f} Pa")
    print(f"  Velocidade da Onda: {correspondencia['velocidade_onda']:.2f} mm/s\n")

