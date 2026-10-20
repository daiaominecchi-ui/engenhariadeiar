from dataclasses import dataclass
from collections import deque
import math
import random

@dataclass
class Sample:
    t: float
    setpoint: float
    speed: float
    estimated_speed: float
    current: float
    temperature: float
    vibration: float
    command: float
    fault: str
    diagnosis: str

class Simulator:
    """Modelo educacional discreto, sem pretensão de representar máquina real."""
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.t = 0.0
        self.speed = 0.0
        self.temperature = 25.0
        self.command = 0.0
        self.integral = 0.0
        self.last_sensor = 0.0
        self.history = deque(maxlen=20000)
        self.events = []
        self.active_event = None
        self.last_fault = "Nenhuma"

    def step(self, setpoint=100.0, fault="Nenhuma", dt=0.2):
        dt = max(0.01, min(float(dt), 1.0))
        if fault != self.last_fault and fault != "Nenhuma":
            self.active_event = {"time": round(self.t, 2), "fault": fault, "pre": [vars(s).copy() for s in list(self.history)[-25:]], "post": []}
            self.events.append(self.active_event)
        self.last_fault = fault
        target = max(0.0, min(150.0, float(setpoint)))
        load = 0.8 if fault == "Sobrecarga mecânica" else 0.0
        # Controlador PI simples com saturação e anti-windup aproximado
        measured = self.last_sensor
        error = target - measured
        trial_integral = max(-100.0, min(100.0, self.integral + error * dt))
        raw = 0.55 * error + 0.18 * trial_integral + target * 0.45
        self.command = max(0.0, min(150.0, raw))
        if 0.0 < raw < 150.0:
            self.integral = trial_integral
        gain = 0.18 if fault == "Controle mal ajustado" else 1.0
        # A velocidade real é afetada pela carga e pelo acionamento
        effective_target = max(0.0, self.command * (1 - 0.58 * load))
        self.speed += (effective_target - self.speed) * min(1.0, dt * 1.8 * gain)
        current = 1.2 + 0.028 * self.command + 6.0 * load + self.rng.gauss(0, 0.08)
        self.temperature += dt * (0.025 * current**2 - 0.07 * (self.temperature - 25.0))
        vibration = 0.2 + 0.03 * current + 2.4 * load + abs(error) * 0.001 + self.rng.gauss(0, 0.035)
        speed_sensor = self.speed + self.rng.gauss(0, 0.5)
        if fault == "Sensor travado":
            speed_sensor = self.last_sensor
        elif fault == "Ruído no sensor":
            speed_sensor += self.rng.gauss(0, 25.0)
        elif fault == "Perda de comunicação":
            speed_sensor = float('nan')
        # Estimativa virtual baseada em corrente e comando, independente do sensor de velocidade
        load_est = max(0.0, (current - 1.2 - 0.028 * self.command) / 6.0)
        estimated = max(0.0, self.command * (1 - 0.58 * load_est))
        if not math.isnan(speed_sensor):
            self.last_sensor = speed_sensor
        diagnosis = diagnose(speed_sensor, estimated, current, vibration, fault, self.speed, target)
        sample = Sample(round(self.t, 2), target, speed_sensor, estimated, current,
                        self.temperature, vibration, self.command, fault, diagnosis)
        self.history.append(sample)
        if self.active_event is not None and len(self.active_event['post']) < 25:
            self.active_event['post'].append(vars(sample).copy())
            if len(self.active_event['post']) == 25:
                self.active_event = None
        self.t += dt
        return sample

def diagnose(speed, estimated, current, vibration, fault, actual, target):
    """Regras transparentes; fault é usado somente para identificar condição do controlador no simulador."""
    if math.isnan(speed):
        return "Comunicação: leitura de velocidade indisponível; verificar conexão e aquisição."
    if abs(speed - estimated) > 22 and current < 7.0:
        return "Sensor: velocidade incoerente com o sensor virtual; investigar ruído ou travamento."
    if current > 8.0 and vibration > 1.5 and speed < target * 0.8:
        return "Mecânica: corrente e vibração elevadas com queda de velocidade; provável sobrecarga."
    if fault == "Controle mal ajustado" and abs(target - speed) > 15:
        return "Controle: resposta lenta sem aumento significativo de carga; verificar ganhos PI."
    return "Operação sem evidência forte de falha pelos critérios atuais."
