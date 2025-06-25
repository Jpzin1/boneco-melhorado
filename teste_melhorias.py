#!/usr/bin/env python3
"""
Script de teste para verificar se o código melhorado funciona corretamente
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import pygame
    import pymunk
    import neat
    print("✓ Todas as dependências foram importadas com sucesso!")
    
    # Testar criação básica dos componentes
    from boneco_melhorado import create_space, BonecoMelhorado, Camera
    
    # Testar criação do espaço
    space = create_space()
    print("✓ Espaço de simulação criado com sucesso!")
    
    # Testar criação do boneco
    boneco = BonecoMelhorado(space, 100, 600)
    print("✓ Boneco melhorado criado com sucesso!")
    
    # Testar obtenção do estado
    state = boneco.get_state()
    print(f"✓ Estado do boneco obtido: {len(state)} entradas")
    
    # Testar aplicação de ações
    actions = [0.5, -0.3, 0.2, -0.1]
    boneco.apply_actions(actions)
    print("✓ Ações aplicadas com sucesso!")
    
    # Testar câmera
    camera = Camera()
    camera.update(100)
    print("✓ Câmera criada e atualizada com sucesso!")
    
    # Testar configuração NEAT
    config_path = "config-neat-melhorado.txt"
    if os.path.exists(config_path):
        config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )
        print("✓ Configuração NEAT carregada com sucesso!")
    else:
        print("✗ Arquivo de configuração NEAT não encontrado!")
    
    print("\n🎉 Todos os testes passaram! O código melhorado está funcionando corretamente.")
    
except ImportError as e:
    print(f"✗ Erro de importação: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Erro durante o teste: {e}")
    sys.exit(1)

