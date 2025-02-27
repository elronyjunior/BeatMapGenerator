import librosa
import numpy as np
import random
import json

# Caminho para o arquivo de música
audio_path = "taylor.mp3" 
y, sr = librosa.load(audio_path, sr=None)

# Detecta os tempos (beats) da música
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)

# Define padrões para as setas (cada um com uma sequência de setas)
padroes = [
    ["Cima", "Esquerda", "Baixo", "Direita"],  # Padrão 1
    ["Esquerda", "Direita", "Cima", "Baixo"],  # Padrão 2
    ["Baixo", "Cima", "Direita", "Esquerda"],  # Padrão 3
    ["Direita", "Baixo", "Esquerda", "Cima"],  # Padrão 4
    ["Cima", "Cima", "Baixo", "Esquerda"],     # Padrão 5
]

# Função para determinar a frequência dominante de um segmento de áudio
def obter_frequencia(segmento):
    fft = np.abs(np.fft.rfft(segmento))
    return np.argmax(fft) * (sr / len(segmento))

# Função para escolher um padrão de acordo com a frequência
def escolher_padrao(frequencia):
    if frequencia < 300:
        return padroes[0]  # Grave
    elif 300 <= frequencia < 600:
        return padroes[1]  # Médio-baixo
    elif 600 <= frequencia < 1000:
        return padroes[2]  # Médio-alto
    elif 1000 <= frequencia < 2000:
        return padroes[3]  # Agudo
    else:
        return padroes[4]  # Muito agudo

# Gera o beatmap com múltiplas setas para cada batida
beatmap = []
ultimo_padrao = None
duracao_padrao = 0  # Duração do padrão atual

# Número de setas a serem geradas para cada batida
num_setas_por_beat = 3  # Muda isso se você quiser mais ou menos setas
# Intervalo entre as notas (em segundos)
intervalo_entre_setas = 1 / 3  # Aproximadamente 0.333 segundos para 3 notas por segundo

# Para cada tempo de batida detectado
for beat_time in beat_times:
    for i in range(num_setas_por_beat):  # Gera múltiplas setas para cada batida
        # Calcula o tempo para a nova seta
        novo_tempo = beat_time + i * intervalo_entre_setas
        
        # Analisa um pequeno segmento ao redor do beat
        start = int(beat_time * sr)
        end = min(len(y), start + sr // 4)  # 0.25s ao redor do beat
        segmento = y[start:end]

        # Calcula a frequência dominante e escolhe o padrão adequado
        frequencia = obter_frequencia(segmento)
        padrao = escolher_padrao(frequencia)

        # Se o mesmo padrão durar mais de 10 segundos, muda para outro
        if padrao == ultimo_padrao:
            duracao_padrao += (novo_tempo - (beatmap[-1]["time"] if beatmap else 0))
            if duracao_padrao >= 10:
                padrao = random.choice(padroes)  # Muda o padrão aleatoriamente
                duracao_padrao = 0
        else:
            duracao_padrao = 0  # Reseta a duração se o padrão mudou

        # Escolhe a próxima seta do padrão atual
        seta = padrao[i % len(padrao)]  # Usando o módulo para pegar setas do padrão

        # Adiciona o beat e a seta correspondente ao beatmap
        beatmap.append({"time": float(novo_tempo), "arrow": seta})
        ultimo_padrao = padrao

# Salva o beatmap em um arquivo JSON
with open("beatmap.json", "w") as f:
    json.dump({"beats": beatmap}, f, indent=4)

print(f"Beatmap criado com {len(beatmap)} beats!")
