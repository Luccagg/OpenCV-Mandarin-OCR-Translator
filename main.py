import cv2
import easyocr
from deep_translator import GoogleTranslator
import re
import time

def processar_legendas_chinesas_completo(caminho_video):
    print("A carregar o EasyOCR para Mandarim Simplificado...")
    leitor_ocr = easyocr.Reader(['ch_sim', 'en'])
    
    # Traduz diretamente do Chinês (Mandarim) para Português ('pt') ou Inglês ('en')
    tradutor = GoogleTranslator(source='zh-CN', target='pt')

    cap = cv2.VideoCapture(caminho_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duracao_minutos = (total_frames / fps) / 60 if fps > 0 else 0
    
    contagem_frames = 0
    intervalo_segundos = 2 
    
    textos_limpos_set = set() 
    lista_mandarim = []  

    print(f"\n[Passo 1] A processar o filme COMPLETO (~{duracao_minutos:.1f} minutos)...")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if contagem_frames % int(fps * intervalo_segundos) == 0:
            altura, largura, _ = frame.shape
            
            # CORTE FOCADO: Pega de 78% a 98% da altura da imagem (Mandarim)
            regiao_chines = frame[int(altura * 0.78):int(altura * 0.98), :] 

            resultados_texto = leitor_ocr.readtext(regiao_chines, detail=0)
            texto_unido = " ".join(resultados_texto)

            # Só processa se contiver pelo menos um caractere chinês (\u4e00-\u9fff)
            if re.search(r'[\u4e00-\u9fff]', texto_unido):
                texto_limpo = re.sub(r'\s+', '', texto_unido)
                
                if texto_limpo not in textos_limpos_set:
                    textos_limpos_set.add(texto_limpo)
                    lista_mandarim.append(texto_unido)
                    
                    # Exibe a percentagem de progresso do vídeo no terminal
                    progresso_pct = (contagem_frames / total_frames * 100) if total_frames > 0 else 0
                    print(f"[{progresso_pct:.1f}%] Detetado: {texto_unido}") 

        contagem_frames += 1

    cap.release()
    print(f"\nLeitura de todo o filme concluída! Total de legendas em mandarim: {len(lista_mandarim)}")
    
    # --- PASSO 2: GUARDAR O TEXTO EM MANDARIM ---
    nome_ficheiro_chines = "legendas_mandarim_completo.txt"
    with open(nome_ficheiro_chines, "w", encoding="utf-8") as f:
        for linha in lista_mandarim:
            f.write(linha + "\n")
    print(f"Texto completo em mandarim guardado em '{nome_ficheiro_chines}'.")

    # --- PASSO 3: TRADUÇÃO EM PEQUENOS LOTES (CHUNKS DE 5) ---
    if len(lista_mandarim) > 0:
        print("\n[Passo 3] A traduzir o texto em mandarim em pequenos lotes com pausas...")
        
        tamanho_lote = 5
        traducoes = []
        
        for i in range(0, len(lista_mandarim), tamanho_lote):
            lote = lista_mandarim[i:i + tamanho_lote]
            try:
                sub_traducoes = tradutor.translate_batch(lote)
                traducoes.extend(sub_traducoes)
                
                progresso = min(i + tamanho_lote, len(lista_mandarim))
                print(f"Traduzidas {progresso}/{len(lista_mandarim)} frases...")
                
                # Pausa estratégica de 2 segundos para evitar bloqueio da API do Google
                time.sleep(2) 
                
            except Exception as e:
                print(f"Aviso no lote {i}: {e}. A tentar individualmente...")
                for item in lote:
                    try:
                        traducoes.append(tradutor.translate(item))
                        time.sleep(1.5)
                    except Exception as err_item:
                        traducoes.append(f"[Erro: {err_item}]")

        # Guardar o texto traduzido
        nome_ficheiro_traduzido = "legendas_traduzidas_completo.txt"
        with open(nome_ficheiro_traduzido, "w", encoding="utf-8") as f:
            for orig, trad in zip(lista_mandarim, traducoes):
                f.write(f"ZH: {orig}\nTRAD: {trad}\n\n")
        print(f"Tradução de todo o filme concluída e guardada em '{nome_ficheiro_traduzido}'.")

    else:
        print("Nenhuma legenda em chinês foi encontrada na região recortada.")

if __name__ == "__main__":
    caminho_do_seu_video = '/home/dirac/Downloads/Beautiful.mp4'  # Substitua pelo caminho do seu vídeo
    processar_legendas_chinesas_completo(caminho_do_seu_video)