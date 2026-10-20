"""Digital twin for educational use only. All units are documented in README."""
from dataclasses import dataclass, asdict
from collections import deque
import math
import random

SCENARIOS = ['Normal', 'Sobrecarga mecânica', 'Sensor de velocidade travado', 'Ruído no sensor', 'Falha de comunicação', 'Controle mal ajustado', 'Atrito crescente', 'Falha de ventilação']

@dataclass
class State:
    t: float = 0.0
    speed: float = 0.0  # rpm
    temperature: float = 25.0  # Celsius
    wear: float = 0.02  # 0..1
    current: float = 0.0  # A
    vibration: float = 0.0  # mm/s, illustrative
    integral: float = 0.0
    last_sensor: float = 0.0
    estimated_speed: float = 0.0
    drive: float = 0.0

class Twin:
    def __init__(self, seed=7, dt=0.2):
        self.rng = random.Random(seed)
        self.dt = dt
        self.state = State()
        self.history = []
        self.events = []
        self.last_alert = None
        self.scenario = 'Normal'
        self.target = 1200.0
        self.enabled = True
        self._scenario_since = 0.0
        self._pre = deque(maxlen=int(10/dt))
        self._last_diagnosis = None
        self._alarm_active = False
        self._event_window = None

    def set_scenario(self, scenario):
        if scenario not in SCENARIOS: raise ValueError('Cenário desconhecido')
        if scenario != self.scenario:
            self.scenario = scenario
            self._scenario_since = self.state.t
            self._last_diagnosis = None

    def step(self):
        s = self.state; dt = self.dt
        sc = self.scenario
        age = s.t - self._scenario_since
        load = 0.28 + (0.48 if sc == 'Sobrecarga mecânica' else 0)
        if sc == 'Atrito crescente': load += min(0.48, age * 0.008)
        kp, ki = (0.00025, 0.00008) if sc == 'Controle mal ajustado' else (0.00125, 0.00035)
        error = self.target - s.speed
        s.integral = max(-600, min(600, s.integral + error * dt))
        s.drive = max(0, min(1, 0.42 + kp*error + ki*s.integral)) if self.enabled else 0
        # First-order electromechanical approximation, not a calibrated motor model.
        acceleration = (1750*s.drive - s.speed - 420*load) / 2.5
        s.speed = max(0, s.speed + acceleration*dt)
        s.current = max(0, 0.7 + 6.5*s.drive + 5.2*load + self.rng.gauss(0, 0.06)) if self.enabled else 0.0
        cooling = 0.012 if sc == 'Falha de ventilação' else 0.055
        s.temperature += dt*(0.27*s.current*s.current/5 - cooling*(s.temperature-25))
        s.temperature = max(20, s.temperature)
        s.wear = min(1, s.wear + dt*(0.000008 + max(0, load-0.35)*0.000065))
        s.vibration = max(0, 0.55 + 3.8*s.wear + 2.5*load + self.rng.gauss(0, 0.10))
        sensor = s.speed + self.rng.gauss(0, 3)
        if sc == 'Sensor de velocidade travado':
            sensor = s.last_sensor if age > dt else s.speed
        if sc == 'Ruído no sensor': sensor += self.rng.gauss(0, 145)
        if sc == 'Falha de comunicação' and int(age / dt) % 5 in (0,1): sensor = None
        # Independent model-based virtual sensor; deliberately approximate.
        s.estimated_speed += dt*(1750*s.drive - s.estimated_speed - 420*0.28)/2.5
        if sensor is not None: s.last_sensor = sensor
        s.t = round(s.t+dt, 6)
        row = {'t': round(s.t,2), 'scenario': sc, 'target_rpm': self.target,
               'speed_rpm': round(s.speed,2), 'sensor_rpm': round(sensor,2) if sensor is not None else None,
               'virtual_rpm': round(s.estimated_speed,2), 'current_a': round(s.current,3),
               'temp_c': round(s.temperature,2), 'vibration_mms': round(s.vibration,3),
               'wear_pct': round(s.wear*100,3), 'drive_pct': round(s.drive*100,2)}
        self.history.append(row)
        self._pre.append(dict(row))
        diagnosis = self.diagnose()
        if diagnosis and diagnosis['code'] != self._last_diagnosis:
            self.events.append({'time_s':s.t, 'diagnosis': diagnosis['title'], 'confidence':diagnosis['confidence'], 'evidence':diagnosis['evidence'], 'action':diagnosis['action'], 'scenario':sc, 'pre_samples':list(self._pre), 'post_samples':[]})
            self._event_window = self.events[-1]
            self._last_diagnosis = diagnosis['code']
        if self._event_window and self._event_window['time_s'] < s.t and len(self._event_window['post_samples']) < int(10/dt):
            self._event_window['post_samples'].append(dict(row))
        if not diagnosis: self._last_diagnosis = None
        return row

    def run(self, n):
        return [self.step() for _ in range(n)]

    def diagnose(self):
        h = self.history
        if len(h) < 12: return None
        recent = h[-12:]
        valid = [r['sensor_rpm'] for r in recent if r['sensor_rpm'] is not None]
        if len(valid) < 9:
            return self._diag('comm','Perda intermitente de comunicação', 'Alta', 'Amostras ausentes no canal de velocidade.', 'Verificar conexão, alimentação e protocolo do sensor.')
        measured = recent[-1]['sensor_rpm']
        speed = recent[-1]['speed_rpm']; current = recent[-1]['current_a']
        vib = recent[-1]['vibration_mms']; temp = recent[-1]['temp_c']
        if len(valid) >= 10 and max(valid)-min(valid) < 0.01 and abs(recent[-1]['virtual_rpm']-measured) > 60:
            return self._diag('stuck','Sensor de velocidade possivelmente travado', 'Alta', 'Leitura constante enquanto o sensor virtual diverge.', 'Inspecionar sensor, cabeamento e aquisição.')
        if len(valid) >= 10 and (sum((x-sum(valid)/len(valid))**2 for x in valid)/len(valid))**0.5 > 65:
            return self._diag('noise','Ruído excessivo no sensor', 'Média', 'Variabilidade incompatível com a dinâmica esperada.', 'Verificar aterramento, blindagem e filtragem.')
        if temp > 78 and current < 8.0:
            return self._diag('cool','Refrigeração insuficiente', 'Média', 'Temperatura elevada sem corrente proporcionalmente alta.', 'Inspecionar ventilação e dissipação térmica.')
        if current > 8.5 and speed < 0.83*self.target and recent[-1]['drive_pct'] > 85:
            return self._diag('load','Sobrecarga mecânica provável', 'Alta', 'Corrente elevada, queda de rotação e comando alto.', 'Reduzir carga e verificar atrito ou obstrução.')
        if vib > 3.4 and current > 7.8:
            return self._diag('friction','Atrito ou desgaste crescente', 'Média', 'Vibração e corrente elevadas simultaneamente.', 'Inspecionar rolamentos, alinhamento e lubrificação.')
        if len(h)>35 and abs(speed-self.target)>0.16*self.target and recent[-1]['drive_pct'] < 75:
            return self._diag('control','Controle possivelmente mal ajustado', 'Baixa', 'Erro persistente de velocidade sem saturação do comando.', 'Revisar ganhos PI e resposta transitória.')
        return None

    @staticmethod
    def _diag(code,title,confidence,evidence,action):
        return {'code':code,'title':title,'confidence':confidence,'evidence':evidence,'action':action}

    def metrics(self):
        if not self.history: return {'events':0,'detections':0,'false_alarms':0,'mean_delay_s':None}
        changes=[]
        previous='Normal'
        for r in self.history:
            if r['scenario'] != previous:
                if r['scenario'] != 'Normal': changes.append((r['t'],r['scenario']))
                previous=r['scenario']
        delays=[]; matched=set()
        for idx,(t,scenario) in enumerate(changes):
            next_t=changes[idx+1][0] if idx+1<len(changes) else float('inf')
            ev=next((e for e in self.events if t<=e['time_s']<next_t),None)
            if ev: delays.append(round(ev['time_s']-t,2)); matched.add(id(ev))
        return {'events':len(changes),'detections':len(delays), 'false_alarms':sum(1 for e in self.events if e['scenario']=='Normal'), 'mean_delay_s':round(sum(delays)/len(delays),2) if delays else None}
