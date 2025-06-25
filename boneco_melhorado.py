import pygame
import pymunk
import pymunk.pygame_util
import neat
import os
import math
import random

# --------- Parâmetros Visuais --------- #
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)

# --------- Ambiente de Simulação --------- #
def create_space():
    space = pymunk.Space()
    space.gravity = (0, 900)
    return space

def create_ground(space):
    # Criar um chão mais longo para permitir caminhadas mais longas
    ground_length = WIDTH * 10
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, (0, HEIGHT - 50), (ground_length, HEIGHT - 50), 5)
    shape.friction = 1.0
    shape.color = BROWN
    space.add(body, shape)
    return shape

# --------- Criação do Boneco Melhorado --------- #
class BonecoMelhorado:
    def __init__(self, space, x, y):
        self.space = space
        self.start_x = x
        
        # Tronco (corpo principal)
        self.body = pymunk.Body(8, pymunk.moment_for_box(8, (25, 50)))
        self.body.position = x, y
        self.body_shape = pymunk.Poly.create_box(self.body, (25, 50))
        self.body_shape.friction = 0.3
        self.body_shape.color = BLUE
        space.add(self.body, self.body_shape)

        # Cabeça
        self.head = pymunk.Body(2, pymunk.moment_for_circle(2, 0, 12))
        self.head.position = x, y - 35
        self.head_shape = pymunk.Circle(self.head, 12)
        self.head_shape.friction = 0.3
        self.head_shape.color = BLUE
        space.add(self.head, self.head_shape)
        
        # Conectar cabeça ao corpo
        head_joint = pymunk.PinJoint(self.body, self.head, (0, -25), (0, 12))
        space.add(head_joint)

        # Pernas (coxa e canela para cada perna)
        self.legs = []
        self.leg_shapes = []
        self.motors = []
        self.ground_sensors = []

        for i, side in enumerate([-1, 1]):  # Esquerda e direita
            # Coxa
            thigh = pymunk.Body(3, pymunk.moment_for_box(3, (12, 30)))
            thigh.position = x + side * 8, y + 40
            thigh_shape = pymunk.Poly.create_box(thigh, (12, 30))
            thigh_shape.friction = 0.3
            thigh_shape.color = GREEN
            space.add(thigh, thigh_shape)
            
            # Articulação do quadril
            hip_joint = pymunk.PinJoint(self.body, thigh, (side * 8, 25), (0, -15))
            hip_joint.collide_bodies = False
            space.add(hip_joint)
            
            # Motor do quadril para controle
            hip_motor = pymunk.SimpleMotor(self.body, thigh, 0)
            space.add(hip_motor)
            
            # Canela
            shin = pymunk.Body(2, pymunk.moment_for_box(2, (10, 30)))
            shin.position = x + side * 8, y + 75
            shin_shape = pymunk.Poly.create_box(shin, (10, 30))
            shin_shape.friction = 0.3
            shin_shape.color = GREEN
            space.add(shin, shin_shape)
            
            # Articulação do joelho
            knee_joint = pymunk.PinJoint(thigh, shin, (0, 15), (0, -15))
            knee_joint.collide_bodies = False
            space.add(knee_joint)
            
            # Motor do joelho para controle
            knee_motor = pymunk.SimpleMotor(thigh, shin, 0)
            space.add(knee_motor)
            
            # Pé
            foot = pymunk.Body(1, pymunk.moment_for_box(1, (20, 8)))
            foot.position = x + side * 8, y + 95
            foot_shape = pymunk.Poly.create_box(foot, (20, 8))
            foot_shape.friction = 1.0  # Mais atrito no pé
            foot_shape.color = BLACK
            space.add(foot, foot_shape)
            
            # Articulação do tornozelo
            ankle_joint = pymunk.PinJoint(shin, foot, (0, 15), (0, -4))
            ankle_joint.collide_bodies = False
            space.add(ankle_joint)
            
            # Sensor de contato com o chão no pé
            sensor = pymunk.Circle(foot, 3, (0, 4))
            sensor.sensor = True
            sensor.collision_type = i + 1  # Tipo de colisão único para cada pé
            space.add(sensor)
            
            self.legs.extend([thigh, shin, foot])
            self.leg_shapes.extend([thigh_shape, shin_shape, foot_shape])
            self.motors.extend([hip_motor, knee_motor])
            self.ground_sensors.append(sensor)
        
        # Variáveis para rastreamento
        self.ground_contact = [False, False]  # Para cada pé
        self.max_distance = 0
        self.energy_used = 0
        self.stability_penalty = 0

    def get_state(self):
        """Retorna o estado atual do boneco para a rede neural"""
        # Detectar contato com o chão baseado na posição dos pés
        ground_level = HEIGHT - 50
        for i, foot in enumerate([self.legs[2], self.legs[5]]):  # Pés esquerdo e direito
            self.ground_contact[i] = foot.position.y >= ground_level - 10
        
        # Posição e orientação do corpo
        body_x = (self.body.position.x - self.start_x) / 1000.0
        body_y = self.body.position.y / 1000.0
        body_angle = self.body.angle / math.pi
        body_vel_x = self.body.velocity.x / 100.0
        body_vel_y = self.body.velocity.y / 100.0
        body_angular_vel = self.body.angular_velocity / 10.0
        
        # Ângulos das pernas (quadril e joelho)
        leg_angles = []
        leg_angular_vels = []
        for i in range(0, len(self.legs), 3):  # A cada 3 (coxa, canela, pé)
            thigh = self.legs[i]
            shin = self.legs[i + 1]
            leg_angles.extend([thigh.angle / math.pi, shin.angle / math.pi])
            leg_angular_vels.extend([thigh.angular_velocity / 10.0, shin.angular_velocity / 10.0])
        
        # Estado dos sensores de contato
        ground_contacts = [float(contact) for contact in self.ground_contact]
        
        return [
            body_x, body_y, body_angle, body_vel_x, body_vel_y, body_angular_vel
        ] + leg_angles + leg_angular_vels + ground_contacts

    def apply_actions(self, actions):
        """Aplica as ações da rede neural aos motores das pernas"""
        if len(actions) < 4:
            actions = list(actions) + [0] * (4 - len(actions))
        
        # Limitar as ações para evitar forças excessivas
        max_torque = 50000
        for i, motor in enumerate(self.motors):
            torque = max(-max_torque, min(max_torque, float(actions[i]) * max_torque))
            motor.rate = torque / 10000  # Converter para velocidade angular
            self.energy_used += abs(torque) / 1000000  # Rastrear energia usada

    def get_distance(self):
        """Retorna a distância percorrida"""
        distance = self.body.position.x - self.start_x
        self.max_distance = max(self.max_distance, distance)
        return distance

    def get_fitness(self):
        """Calcula o fitness baseado em múltiplos critérios"""
        distance = self.get_distance()
        
        # Penalidade por queda
        # Penalidade por queda (mais severa)
        fall_penalty = 0
        if self.body.position.y > HEIGHT - 30:  # Se caiu
            fall_penalty = 5000  # Aumentar a penalidade por queda
        
        # Penalidade por instabilidade (ângulo do corpo muito inclinado)
        stability_penalty = abs(self.body.angle) * 200  # Aumentar a penalidade de estabilidade
        
        # Recompensa por velocidade constante e para frente
        velocity_reward = self.body.velocity.x * 2.0  # Recompensa direta pela velocidade X
        
        # Penalidade por uso excessivo de energia
        energy_penalty = self.energy_used * 0.05  # Reduzir um pouco a penalidade de energia para permitir mais exploração
        
        # Fitness final
        fitness = distance + velocity_reward - fall_penalty - stability_penalty - energy_penalty
        return max(fitness, 0.1)

    def is_fallen(self):
        """Verifica se o boneco caiu"""
        return self.body.position.y > HEIGHT - 30 or abs(self.body.angle) > math.pi/3

# --------- Câmera --------- #
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.smoothing = 0.1
    
    def update(self, target_x):
        self.target_x = target_x - WIDTH // 2
        self.x += (self.target_x - self.x) * self.smoothing
    
    def apply(self, pos):
        return (pos[0] - self.x, pos[1] - self.y)

# --------- Renderização Melhorada --------- #
def draw_pymunk_shape(screen, shape, camera):
    """Desenha uma forma do pymunk na tela"""
    body = shape.body
    
    if isinstance(shape, pymunk.Circle):
        pos = camera.apply(body.position)
        pygame.draw.circle(screen, shape.color, (int(pos[0]), int(pos[1])), int(shape.radius))
    elif isinstance(shape, pymunk.Poly):
        vertices = []
        for v in shape.get_vertices():
            world_v = body.local_to_world(v)
            screen_v = camera.apply(world_v)
            vertices.append((int(screen_v[0]), int(screen_v[1])))
        if len(vertices) > 2:
            pygame.draw.polygon(screen, shape.color, vertices)
    elif isinstance(shape, pymunk.Segment):
        start = camera.apply(body.local_to_world(shape.a))
        end = camera.apply(body.local_to_world(shape.b))
        pygame.draw.line(screen, shape.color, start, end, int(shape.radius * 2))

def draw_info(screen, font, boneco, generation, genome_id, fps):
    """Desenha informações na tela"""
    info_texts = [
        f"Geração: {generation}",
        f"Genoma: {genome_id}",
        f"Distância: {boneco.get_distance():.1f}",
        f"Fitness: {boneco.get_fitness():.1f}",
        f"Velocidade: {boneco.body.velocity.x:.1f}",
        f"Energia: {boneco.energy_used:.1f}",
        f"FPS: {fps:.1f}",
        f"Contato Chão: {boneco.ground_contact}"
    ]
    
    for i, text in enumerate(info_texts):
        surface = font.render(text, True, BLACK)
        screen.blit(surface, (10, 10 + i * 25))

# --------- Avaliação Melhorada --------- #
def evaluate_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        space = create_space()
        create_ground(space)
        boneco = BonecoMelhorado(space, 100, HEIGHT - 150)

        # Simulação mais longa para aprendizado mais robusto
        for step in range(600):  # 10 segundos a 60 FPS
            inputs = boneco.get_state()
            actions = net.activate(inputs)
            
            boneco.apply_actions(actions)
            space.step(1 / 60.0)

            # Parar se o boneco caiu
            if boneco.is_fallen():
                break

        genome.fitness = boneco.get_fitness()
        print(f"[{genome_id}] Fitness: {genome.fitness:.2f}, Distância: {boneco.get_distance():.1f}")

# --------- Visualização Melhorada --------- #
def test_winner_visual(winner, config):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Boneco Andante Melhorado - NEAT")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    space = create_space()
    ground_shape = create_ground(space)
    boneco = BonecoMelhorado(space, 100, HEIGHT - 150)
    camera = Camera()

    net = neat.nn.FeedForwardNetwork.create(winner, config)

    running = True
    paused = False
    
    while running:
        dt = clock.tick(FPS)
        fps = clock.get_fps()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    # Reiniciar simulação
                    space = create_space()
                    ground_shape = create_ground(space)
                    boneco = BonecoMelhorado(space, 100, HEIGHT - 150)

        if not paused:
            inputs = boneco.get_state()
            actions = net.activate(inputs)
            boneco.apply_actions(actions)
            space.step(1 / FPS)

        # Atualizar câmera
        camera.update(boneco.body.position.x)

        # Desenhar
        screen.fill(WHITE)
        
        # Desenhar chão
        draw_pymunk_shape(screen, ground_shape, camera)
        
        # Desenhar boneco
        draw_pymunk_shape(screen, boneco.body_shape, camera)
        draw_pymunk_shape(screen, boneco.head_shape, camera)
        for shape in boneco.leg_shapes:
            draw_pymunk_shape(screen, shape, camera)

        # Desenhar informações
        draw_info(screen, font, boneco, "Final", "Vencedor", fps)
        
        # Instruções
        instructions = [
            "ESPAÇO: Pausar/Continuar",
            "R: Reiniciar",
            "ESC: Sair"
        ]
        for i, instruction in enumerate(instructions):
            surface = font.render(instruction, True, GRAY)
            screen.blit(surface, (WIDTH - 200, 10 + i * 25))

        pygame.display.flip()

        # Verificar se caiu
        if boneco.is_fallen():
            print(f"Boneco caiu! Distância final: {boneco.get_distance():.1f}")

    pygame.quit()

# --------- Main --------- #
def run_neat():
    config_path = "config-neat-melhorado.txt"
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    
    # Criar população
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    
    # Adicionar checkpointing
    checkpoint_reporter = neat.Checkpointer(5)  # Salvar a cada 5 gerações
    pop.add_reporter(checkpoint_reporter)

    # Executar evolução
    winner = pop.run(evaluate_genomes, 100)  # Mais gerações para melhor aprendizado

    print("Treinamento finalizado. Abrindo visualização do vencedor...")
    test_winner_visual(winner, config)

if __name__ == "__main__":
    run_neat()

