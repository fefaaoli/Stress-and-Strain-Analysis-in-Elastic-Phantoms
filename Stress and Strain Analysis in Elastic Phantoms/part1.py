import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.io import loadmat
from scipy.stats import linregress

# 1. Análise de Tensão e Deformação:

# Caminho do arquivo Excel com dados de tensão e deformação
file_path = 'C:/Users/mfmdo/OneDrive/Documentos/trabalho biomecância/venv/TensaoDeformacao.xlsx'

# Tentar carregar o arquivo Excel
try:
    data = pd.read_excel(file_path, engine='openpyxl')
    print("Arquivo carregado com sucesso!")
except FileNotFoundError:
    print(f"Erro: O arquivo não foi encontrado no caminho: {file_path}")
    exit()
except Exception as e:
    print(f"Erro ao carregar o arquivo: {e}")
    exit()

# Converte as colunas para numéricas
data['P_1'] = pd.to_numeric(data['P_1'], errors='coerce')
data['P_1.1'] = pd.to_numeric(data['P_1.1'], errors='coerce')
data['P_2'] = pd.to_numeric(data['P_2'], errors='coerce')
data['P_2.1'] = pd.to_numeric(data['P_2.1'], errors='coerce')
data['P_3'] = pd.to_numeric(data['P_3'], errors='coerce')
data['P_3.1'] = pd.to_numeric(data['P_3.1'], errors='coerce')

# Divide os dados para cada phantom
data_P1 = data[['P_1', 'P_1.1']].dropna()
data_P2 = data[['P_2', 'P_2.1']].dropna()
data_P3 = data[['P_3', 'P_3.1']].dropna()

# Função para calcular o Módulo de Young
def calculate_youngs_modulus(deformation, stress, phantom_name):
    if len(deformation) == 0 or len(stress) == 0:
        print(f"Erro: dados insuficientes para {phantom_name}.")
        return None
    slope, intercept, r_value, p_value, std_err = linregress(deformation, stress)
    youngs_modulus = slope
    print(f"Módulo de Young para {phantom_name}: {youngs_modulus:.2f} Pa")
    return youngs_modulus

# Calcular o Módulo de Young para cada phantom a partir da tensão e deformação
youngs_modulus_P1 = calculate_youngs_modulus(data_P1['P_1'], data_P1['P_1.1'], "P1")
youngs_modulus_P2 = calculate_youngs_modulus(data_P2['P_2'], data_P2['P_2.1'], "P2")
youngs_modulus_P3 = calculate_youngs_modulus(data_P3['P_3'], data_P3['P_3.1'], "P3")

# Plotar gráficos de tensão vs. deformação para cada phantom
plt.figure(figsize=(12, 8))

# Phantom 1
plt.subplot(3, 1, 1)
plt.plot(data['P_1'], data['P_1.1'], 'b-', label='P1')
plt.title('Tensão vs Deformação - Phantom 1')
plt.xlabel('Deformação (P_1)')
plt.ylabel('Tensão (P_1.1)')
plt.legend()
plt.grid()

# Phantom 2
plt.subplot(3, 1, 2)
plt.plot(data['P_2'], data['P_2.1'], 'g-', label='P2')
plt.title('Tensão vs Deformação - Phantom 2')
plt.xlabel('Deformação (P_2)')
plt.ylabel('Tensão (P_2.1)')
plt.legend()
plt.grid()

# Phantom 3
plt.subplot(3, 1, 3)
plt.plot(data['P_3'], data['P_3.1'], 'r-', label='P3')
plt.title('Tensão vs Deformação - Phantom 3')
plt.xlabel('Deformação (P_3)')
plt.ylabel('Tensão (P_3.1)')
plt.legend()
plt.grid()

# Ajustar o layout e mostrar os gráficos
plt.tight_layout()
plt.show()

# 2. Mapas de Deslocamento
# Função para carregar os mapas de deslocamento dos arquivos .mat
def load_displacement_map(file_name, phantom_name):
    try:
        mat_data = loadmat(file_name)
        disp_map = mat_data['disp_map']
        print(f"Mapa de deslocamento para {phantom_name} carregado com sucesso!")
        return disp_map
    except FileNotFoundError:
        print(f"Erro: O arquivo {file_name} não foi encontrado.")
        return None
    except KeyError:
        print(f"Erro: Variável 'disp_map' não encontrada no arquivo {file_name}.")
        return None

# Caminhos dos arquivos .mat para os phantoms P_A, P_B e P_C
file_path_A = 'C:/Users/mfmdo/OneDrive/Documentos/trabalho biomecância/venv/SRF-SWE-Phantom_P_A.mat'
file_path_B = 'C:/Users/mfmdo/OneDrive/Documentos/trabalho biomecância/venv/SRF-SWE-Phantom_P_B.mat'
file_path_C = 'C:/Users/mfmdo/OneDrive/Documentos/trabalho biomecância/venv/SRF-SWE-Phantom_P_C.mat'

# Carregar os mapas de deslocamento de cada phantom
disp_map_A = load_displacement_map(file_path_A, "Phantom A")
disp_map_B = load_displacement_map(file_path_B, "Phantom B")
disp_map_C = load_displacement_map(file_path_C, "Phantom C")

# 3. Estrutura dos Mapas de Deslocamento
# Função para analisar as dimensões e estrutura do mapa de deslocamento
def analyze_displacement_map(disp_map, phantom_name):
    if disp_map is None:
        print(f"Erro: Mapa de deslocamento para {phantom_name} não está disponível.")
        return

    # Verifica as dimensões do mapa de deslocamento
    frames, rows, cols = disp_map.shape
    print(f"Dimensões do mapa de deslocamento para {phantom_name}: {frames} frames, {rows} linhas, {cols} colunas")
    
    # Calcula as dimensões em mm
    lateral_dimension = cols * 0.2977  # dx
    axial_dimension = rows * 0.1885   # dz
    print(f"Dimensões laterais: {lateral_dimension:.2f} mm")
    print(f"Dimensões axiais: {axial_dimension:.2f} mm")
    
    # Taxa de aquisição de frames
    frame_rate = 10000  # frames por segundo
    dt = 1 / frame_rate
    print(f"Taxa de aquisição: {frame_rate} fps")
    
    return frames, rows, cols, lateral_dimension, axial_dimension

# Função para visualizar um frame específico do mapa de deslocamento
def visualize_frame(disp_map, frame_index, phantom_name):
    if disp_map is None:
        print(f"Erro: Mapa de deslocamento para {phantom_name} não está disponível.")
        return

    if frame_index < 0 or frame_index >= disp_map.shape[0]:
        print("Índice de frame inválido.")
        return

    plt.imshow(disp_map[frame_index, :, :], cmap='jet')
    plt.title(f'Frame {frame_index} - {phantom_name}')
    plt.colorbar(label='Deslocamento (mm)')
    plt.xlabel('Colunas (128)')
    plt.ylabel('Linhas (162)')
    plt.show()

# Analisar e visualizar os mapas de deslocamento para cada phantom
frames_A, rows_A, cols_A, lateral_dim_A, axial_dim_A = analyze_displacement_map(disp_map_A, "Phantom A")
frames_B, rows_B, cols_B, lateral_dim_B, axial_dim_B = analyze_displacement_map(disp_map_B, "Phantom B")
frames_C, rows_C, cols_C, lateral_dim_C, axial_dim_C = analyze_displacement_map(disp_map_C, "Phantom C")

# Visualizar o primeiro frame do mapa de deslocamento de cada phantom
visualize_frame(disp_map_A, 0, "Phantom A")
visualize_frame(disp_map_B, 0, "Phantom B")
visualize_frame(disp_map_C, 0, "Phantom C")

