# Boneco Andante com NEAT

Este repositório contém a versão original de um projeto de boneco que aprende a andar utilizando o algoritmo NEAT (NeuroEvolution of Augmenting Topologies) e a biblioteca Pygame para visualização.

## 🚀 Visão Geral do Projeto

O objetivo principal é simular um boneco simples que, através de uma rede neural evoluída pelo NEAT, aprende a se mover para frente. A visualização é feita em tempo real usando Pygame, permitindo observar o comportamento do boneco durante e após o treinamento.

## ✨ Funcionalidades

-   **Simulação Física:** Utiliza a biblioteca `Pymunk` para simular a física do boneco (corpo e duas pernas) e o ambiente (chão).
-   **Aprendizado por Evolução:** Emprega o algoritmo NEAT para evoluir redes neurais que controlam os movimentos do boneco.
-   **Visualização Básica:** Renderiza o boneco e o chão usando `Pygame`.
-   **Avaliação de Fitness:** O desempenho do boneco é avaliado com base na distância percorrida.

## 📁 Estrutura do Projeto

-   `boneco_melhorado.py`: Contém o código Python principal para a simulação do boneco, a integração com NEAT e a visualização.
-   `config-neat-melhorado.txt`: Arquivo de configuração para o algoritmo NEAT, definindo seus parâmetros de evolução.

-   ## 🛠️ Instalação

Para rodar este projeto, você precisará ter Python instalado, juntamente com as seguintes bibliotecas:

-   `pygame`
-   `pymunk`
-   `neat-python`

Você pode instalá-las usando pip:

```bash
pip install pygame pymunk neat-python
```

Se tiver problemas de permissão, tente:

```bash
pip install --user pygame pymunk neat-python
```

## 🎮 Como Usar

1.  **Salve os arquivos:** Certifique-se de que `pasted_content.txt` (renomeie para `main.py` ou `boneco.py` para facilitar) e `config-neat.txt` estejam na mesma pasta.
2.  **Execute o script:** Abra um terminal na pasta onde você salvou os arquivos e execute o comando:

    ```bash
    python pasted_content.txt
    ```
    (Ou o nome que você deu ao arquivo Python)

O programa iniciará o treinamento do NEAT. Você verá o progresso no terminal. Após o treinamento, uma janela do Pygame será aberta mostrando a visualização do boneco vencedor.

## ⚙️ Configuração do NEAT (`config-neat.txt`)

Este arquivo define como o algoritmo NEAT irá operar:

-   `fitness_criterion`: Define como o fitness é avaliado (neste caso, `max` para maximizar a distância).
-   `fitness_threshold`: O valor de fitness que, se atingido, encerra o treinamento.
-   `pop_size`: O número de indivíduos (redes neurais) em cada geração.
-   `num_inputs`: Número de entradas para a rede neural (5: posição do corpo, ângulos das pernas, velocidades angulares das pernas).
-   `num_outputs`: Número de saídas da rede neural (2: forças aplicadas nas pernas).
-   Outros parâmetros controlam as taxas de mutação, adição/remoção de nós e conexões, e a estagnação das espécies.
