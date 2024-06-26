'''
@Author: WANG Maonan
@Date: 2023-09-01 13:45:26
@Description: 给场景生成路网
@LastEditTime: 2024-04-08 16:56:27
'''
from tshub.utils.get_abs_path import get_abs_path
from tshub.utils.init_log import set_logger
from tshub.sumo_tools.generate_routes import generate_route

# 初始化日志
current_file_path = get_abs_path(__file__)
set_logger(current_file_path('./'), file_log_level='WARNING', terminal_log_level='INFO')

# 开启仿真 --> 指定 net 文件
sumo_net = current_file_path("../sumo_env/three_junctions/env/3junctions.net.xml")

# 指定要生成的路口 id 和探测器保存的位置
generate_route(
    sumo_net=sumo_net,
    interval=[5,10,15], 
    edge_flow_per_minute={
        'E0': [15, 15, 15],
        '-E3': [15, 15, 15],
        '-E9': [7, 7, 7],
        '-E4': [7, 7, 7],
        '-E5': [3, 3, 3],
        '-E8': [3, 3, 3],
        '-E6': [3, 3, 3],
        '-E7': [3, 3, 3]
    }, # 每分钟每个 edge 有多少车
    edge_turndef={
        '-E9__E4': [0.7, 0.7, 1],
        '-E9__-E0': [0.1, 0.1, 0],
    },
    veh_type={
        'ego': {'color':'26, 188, 156', 'accel':1, 'decel':1, 'probability':0.3},
        'background': {'color':'155, 89, 182', 'speed':15, 'probability':0.7},
    },
    output_trip=current_file_path('./testflow.trip.xml'),
    output_turndef=current_file_path('./testflow.turndefs.xml'),
    output_route=current_file_path('./testflow.rou.xml'),
    interpolate_flow=False,
    interpolate_turndef=False,
)