'''
@Author: WANG Maonan
@Date: 2023-08-25 11:22:43
@Description: 定义每一个 traffic light 的信息
@LastEditTime: 2023-08-28 17:01:55
'''
from __future__ import annotations

import traci
from loguru import logger
from dataclasses import dataclass, fields
from typing import List, Dict, Any

from .traffic_light_action_type import tls_action_type
from .tls_type.choose_next_phase import choose_next_phase
from .tls_type.next_or_not import next_or_not
from ..utils.format_dict import dict_to_str

@dataclass
class TrafficLightInfo:
    id: str
    action_type: str
    delta_time:int
    last_step_mean_speed: List[float]
    jam_length_vehicle: List[float]
    jam_length_meters: List[float]
    last_step_occupancy: List[float]
    this_phase: List[bool]
    last_phase: List[bool]
    next_phase: List[bool]
    sumo: traci.connection.Connection # 与 sumo 的 connection
    movement_directions: Dict[str, str] = None, # 每一个 movement 的方向
    movement_lane_numbers: List[int] = None, # 每一个 movement 包含的车道数
    movement_ids: List[str] = None # 存储 movement id (fromEdge, toEdge)
    phase2movements: Dict[int, List[str]] = None # 记录每个 phase 控制的 connection
    can_perform_action: bool = False # 是否可以执行动作

    def __post_init__(self) -> None:
        """初始化 traffic light, 包括:
        1. 选择控制方案;
        2. 获得 movement 的基本信息
        3. 获得 movement 和 phase 之间的关系
        """
        _action = tls_action_type(self.action_type)
        if _action == tls_action_type.ChooseNextPhase:
            self.tls_action = choose_next_phase(ts_id=self.id, sumo=self.sumo, delta_time=self.delta_time)
        elif _action == tls_action_type.NextorNot:
            self.tls_action = next_or_not(ts_id=self.id, sumo=self.sumo, delta_time=self.delta_time)
        else:
            logger.error(f'SIM: 信号灯动作只支持 choose_next_phase 和 next_or_not, 现在是 {self.action_type}.')
            raise ValueError(f'SIM: 信号灯动作只支持 choose_next_phase 和 next_or_not, 现在是 {self.action_type}.')
        self.tls_action.build_phases()
        self.movement_ids = self.tls_action.movement_ids
        self.movement_directions = self.tls_action.movement_directions
        self.movement_lane_numbers = self.tls_action.movement_lane_numbers
        self.phase2movements = self.tls_action.phase2movements

        logger.debug(f'SIM: Phase to Movement: \n{dict_to_str(self.phase2movements)}')

    @classmethod
    def create_traffic_light(
            cls, id, action_type, delta_time,
            last_step_mean_speed, jam_length_vehicle, jam_length_meters, last_step_occupancy,
            this_phase, last_phase, next_phase, 
            sumo) -> TrafficLightInfo:
        """
        创建交通信号灯
        """
        logger.info(f'SIM: Init Traffic Light: {id}.')
        return cls(id, action_type, delta_time,
                   last_step_mean_speed, jam_length_vehicle, jam_length_meters, last_step_occupancy,
                   this_phase, last_phase, next_phase, sumo)
    
    def __update_this_phase(self, phase_index:int) -> None:
        """根据 phase_index 更新 this_phase, 将目前控制的 movement 设置为 True

        Args:
            phase_index (int): phase index
        """
        if phase_index in self.phase2movements:
            movements = self.phase2movements[phase_index]
            for movement in movements:
                from_edge = movement.split('--')[0]
                direction = movement.split('--')[1]
                movement_id = f'{from_edge}_{direction}'
                movement_index = self.movement_ids.index(movement_id)
                self.this_phase[movement_index] = True

    def update_features(self, tls_data):
        """
        更新交通信号灯的属性
        """
        # 更新路况信息（道路拥堵程度）
        for i, key in enumerate(self.movement_ids):
            if key in tls_data:
                self.last_step_mean_speed[i] = tls_data[key]['last_step_mean_speed']
                self.jam_length_vehicle[i] = tls_data[key]['jam_length_vehicle']
                self.jam_length_meters[i] = tls_data[key]['jam_length_meters']
                self.last_step_occupancy[i] = tls_data[key]['last_step_occupancy']
        # 更新 phase 的信息
        self.__update_this_phase(self.tls_action.phase_index)
        # 当前的 traffic light 是否可以执行动作
        self.can_perform_action = (self.tls_action.sim_step == self.tls_action.next_action_time)

    def get_features(self) -> Dict[str, Any]:
        """
        返回交通信号灯的特征, 不需要包含 SUMO 的连接
        """
        output_dict = {}
        for field in fields(self):
            field_name = field.name
            field_value = getattr(self, field_name)
            if field_name != 'sumo':
                output_dict[field_name] = field_value
        return output_dict


    def control_traffic_light(self, action) -> None:
        """
        控制交通信号灯
        """
        if self.can_perform_action:
            self.tls_action.set_next_phases(action)
        else:
            self.tls_action.update()