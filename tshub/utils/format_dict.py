'''
@Author: WANG Maonan
@Date: 2023-08-24 17:34:14
@Description: 将 dict 转换为字符串, 带有环行
@LastEditTime: 2023-08-24 17:36:24
'''
import json

def dict_to_str(my_dict):
    """将字典转换为格式化的JSON字符串
    """
    json_str = json.dumps(my_dict, indent=4)
    return json_str
