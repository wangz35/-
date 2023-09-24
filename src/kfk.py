import math
import matplotlib.pyplot as plt
import numpy as np

def plot_damage_change():
    speed_values = range(180, 126, -1)  # 从180降低到126
    damage_values = []
    max_damage = 0
    max_damage_speed = 0
    max_damage_attack = 0

    for speed in speed_values:
        attack = 3286+0.2*1266 + (180 - speed) * 21
        kafka = Kafka_serval(attack, speed, 65, 0.6, 1.3, 1.13, 2)
        total_damage = kafka.calculate_total_damage(550)
        damage_values.append(total_damage)

        if total_damage > max_damage:
            max_damage = total_damage
            max_damage_speed = speed
            max_damage_attack = attack

    plt.plot(speed_values, damage_values)
    plt.xlabel('Speed')
    plt.ylabel('Total Damage')
    plt.title('Change in Total Damage as Speed Decreases')
    plt.grid(True)
    print(f"Maximum damage of {max_damage} is achieved with a speed of {max_damage_speed-12} and an attack of {max_damage_attack-0.2*1266}.")
    plt.show()


class Kafka_serval:
    def __init__(self, attack, speed, damage_increase, def_debuff, damage_debuff, res_debuff, times):#攻击, 速度， 增伤， 降防， 易伤， 减抗, 几动一大
        self.attack = attack
        self.speed = speed
        self.damage_increase = damage_increase
        self.def_debuff = def_debuff
        self.damage_debuff = damage_debuff
        self.res_debuff = res_debuff
        self.times = times

    def action_cost(self):#速度转行动值
        return 10000 / self.speed

    def basic_attack_damage(self):#160%战技直伤+140%追击直伤
        return self.attack * 3 * (1 + self.damage_increase / 100)

    def big_attack_damage(self):#大招80倍率脑残直伤，最弱大招没有之一
        return self.attack * 0.80 * (1 + self.damage_increase / 100)

    def buff_damage(self):#290常驻dot+60专武dot+希露瓦100倍率dot，2命卡的25增伤
        return self.attack * 5.5 * (1 + (self.damage_increase+25) / 100)

    def break_buff_damage(self):#击破dot
        return 3767.55 * 2.8 * 2

    def explode_damage(self):#e技能引爆dot
        return self.buff_damage() * 0.75

    def explode_damage_big_attack(self):#大招引爆dot
        return self.buff_damage()

    def break_explode_damage(self):#e技能引爆击破dot
        return self.break_buff_damage() * 0.75

    def break_explode_damage_big_attack(self):#大招引爆击破dot
        return self.break_buff_damage()

    
    def calculate_total_damage(self, action_value):
        action_times = math.floor(action_value / self.action_cost())#行动次数
        enemy_action_times = math.floor(action_value / (10000 / 140))#混沌10 140速怪行动次数
        basic_attack_times = action_times#引爆次数
        big_attack_times = action_times // self.times  #4命卡夫卡 2动一大
        total_damage = 0
        total_damage += self.basic_attack_damage() * basic_attack_times
        total_damage += self.big_attack_damage() * big_attack_times

        total_damage = total_damage*self.damage_debuff#易伤率
        
        total_buff_damage = 0
        total_buff_damage += self.buff_damage() * enemy_action_times
        total_buff_damage += self.explode_damage() * action_times
        total_buff_damage += self.explode_damage_big_attack() * big_attack_times
        total_buff_damage += self.break_buff_damage()*(enemy_action_times-2)
        total_buff_damage += self.break_explode_damage()*(action_times-2)
        total_buff_damage += self.break_explode_damage_big_attack()*(big_attack_times-1)

        total_damage += total_buff_damage*1.3
        total_damage = total_damage*(200+10*80)/((200+10*90)*self.def_debuff+200+10*80)#减防公式：(200+10*攻击者等级)/((200+10*受击者等级)*（1-减防系数）+200+10*攻击者等级)
        total_damage = total_damage*self.res_debuff#抗性衰减
        return total_damage

class Kafka_serval1:
    def __init__(self, attack, speed, damage_increase, def_debuff, damage_debuff, res_debuff, times):#攻击, 速度， 增伤， 降防， 易伤， 减抗, 几动一大
        self.attack = attack
        self.speed = speed
        self.damage_increase = damage_increase
        self.def_debuff = def_debuff
        self.damage_debuff = damage_debuff
        self.res_debuff = res_debuff
        self.times = times

    def action_cost(self):#速度转行动值
        return 10000 / self.speed

    def basic_attack_damage(self):#160%战技直伤+140%追击直伤
        return self.attack * 3 * (1 + self.damage_increase / 100)

    def big_attack_damage(self):#大招80倍率脑残直伤，最弱大招没有之一
        return self.attack * 0.80 * (1 + self.damage_increase / 100)

    def buff_damage(self):#290常驻dot+60专武dot+希露瓦100倍率dot，2命卡的25增伤
        return self.attack * 5.5 * (1 + (self.damage_increase+25) / 100)

    def break_buff_damage(self):#击破dot
        return 3767.55 * 2.8 * 2

    def explode_damage(self):#e技能引爆dot
        return self.buff_damage() * 0.75

    def explode_damage_big_attack(self):#大招引爆dot
        return self.buff_damage()

    def break_explode_damage(self):#e技能引爆击破dot
        return self.break_buff_damage() * 0.75

    def break_explode_damage_big_attack(self):#大招引爆击破dot
        return self.break_buff_damage()

    
    def calculate_total_damage(self, action_value):
        action_times = math.floor(action_value / self.action_cost())#行动次数
        enemy_action_times = math.floor(action_value / (10000 / 140))#混沌10 140速怪行动次数
        basic_attack_times = action_times#引爆次数
        big_attack_times = action_times // self.times  #4命卡夫卡 2动一大
        total_damage = 0
        total_damage += self.basic_attack_damage() * basic_attack_times
        total_damage += self.big_attack_damage() * big_attack_times

        total_damage = total_damage*self.damage_debuff#易伤率
        
        total_buff_damage = 0
        total_buff_damage += self.buff_damage() * enemy_action_times
        total_buff_damage += self.explode_damage() * action_times
        total_buff_damage += self.explode_damage_big_attack() * big_attack_times
        total_buff_damage += self.break_buff_damage()*(enemy_action_times-2)
        total_buff_damage += self.break_explode_damage()*(action_times-2)
        total_buff_damage += self.break_explode_damage_big_attack()*(big_attack_times-1)

        total_damage += total_buff_damage*1.3
        total_damage = total_damage*(200+10*80)/((200+10*90)*self.def_debuff+200+10*80)#减防公式：(200+10*攻击者等级)/((200+10*受击者等级)*（1-减防系数）+200+10*攻击者等级)
        total_damage = total_damage*self.res_debuff#抗性衰减
        return total_damage


class Kafka_d:
    def __init__(self, attack, speed, damage_increase, def_debuff, damage_debuff, res_debuff, times):#卡夫卡配桑博，没有减防减抗，持续伤害易伤从1.3提到1.6，依然没有通用易伤
        self.attack = attack
        self.speed = speed
        self.damage_increase = damage_increase
        self.def_debuff = def_debuff
        self.damage_debuff = damage_debuff
        self.res_debuff = res_debuff
        self.times = times

    def action_cost(self):
        return 10000 / self.speed

    def basic_attack_damage(self):
        return self.attack * 3.00 * (1 + self.damage_increase / 100)

    def big_attack_damage(self):
        return self.attack * 0.80 * (1 + self.damage_increase / 100)

    def buff_damage(self):
        return self.attack * 5.5 * (1 + (self.damage_increase+25)/ 100)+ 3000*3.5*(1 + (40+25)/ 100)#桑博面板350的风伤，保守估计250常驻加上卡夫卡4+1的350触电


    def explode_damage(self):
        return self.buff_damage() * 0.75

    def explode_damage_big_attack(self):
        return self.buff_damage()


    
    def calculate_total_damage(self, action_value):
        action_times = math.floor(action_value / self.action_cost())
        enemy_action_times = math.floor(action_value / (10000 / 140))
        basic_attack_times = action_times
        big_attack_times = action_times // self.times
        total_damage = 0

        total_damage += self.basic_attack_damage() * basic_attack_times
        total_damage += self.big_attack_damage() * big_attack_times
        total_damage = total_damage*self.damage_debuff
        total_buff_damage = 0
        total_buff_damage += self.buff_damage() * enemy_action_times
        total_buff_damage += self.explode_damage() * action_times
        total_buff_damage += self.explode_damage_big_attack() * big_attack_times
        total_damage += total_buff_damage*1.6

        total_damage = total_damage*(200+10*80)/((200+10*90)*self.def_debuff+200+10*80)
        total_damage = total_damage*self.res_debuff
        return total_damage

class Kafka_asta_sw:
    def __init__(self, attack, speed, damage_increase, def_debuff, damage_debuff, res_debuff, times):#攻击, 速度， 增伤， 降防， 易伤， 减抗, 循环
        self.attack = attack
        self.speed = speed
        self.damage_increase = damage_increase
        self.def_debuff = def_debuff
        self.damage_debuff = damage_debuff
        self.res_debuff = res_debuff
        self.times = times

    def action_cost(self):#速度转行动值
        return 10000 / self.speed

    def basic_attack_damage(self):#160%战技直伤+140%追击直伤
        return self.attack * 3 * (1 + self.damage_increase / 100)

    def big_attack_damage(self):#大招80倍率脑残直伤
        return self.attack * 0.80 * (1 + self.damage_increase / 100)

    def buff_damage(self):#290常驻dot+60专武dot
        return self.attack * 3.5 * (1 + (self.damage_increase+25) / 100)


    def explode_damage(self):#e技能引爆dot
        return self.buff_damage() * 0.75

    def explode_damage_big_attack(self):#大招引爆dot
        return self.buff_damage()


    
    def calculate_total_damage(self, action_value):
        action_times = math.floor(action_value / self.action_cost())#行动次数
        enemy_action_times = math.floor(action_value / (10000 / 140))#混沌10 140速怪行动次数
        basic_attack_times = action_times#引爆次数
        big_attack_times = action_times // self.times  #4命卡夫卡 2动一大
        total_damage = 0
        total_damage += self.basic_attack_damage() * basic_attack_times
        total_damage += self.big_attack_damage() * big_attack_times
        total_damage = total_damage*self.damage_debuff#通常易伤率
        total_buff_damage = 0
        total_buff_damage += self.buff_damage() * (enemy_action_times-0.5)
        total_buff_damage += self.explode_damage() * (action_times-0.5)
        total_buff_damage += self.explode_damage_big_attack() * (big_attack_times-0.2)
        total_damage += total_buff_damage*1.3#卡夫卡1命30易伤

        total_damage = total_damage*(200+10*80)/((200+10*90)*self.def_debuff+200+10*80)#减防公式：(200+10*攻击者等级)/((200+10*受击者等级)*（1-减防系数）+200+10*攻击者等级)
        total_damage = total_damage*self.res_debuff#抗性衰减
        return total_damage


def main():
    kafka = Kafka_serval(4000, 140, 72.8, 0.6, 1.0, 1.13, 2)#速度鞋，能量链
    kafka10 = Kafka_serval(4600, 140, 72.8, 0.6, 1.0, 1.13, 3)
    kafka2 = Kafka_serval(4200, 200, 65, 1, 1.0, 1, 2)
    kafka0 = Kafka_asta_sw(4200, 200, 65, 0.6, 1.0, 1.13, 2)
    kafka3 = Kafka_d(4000, 140, 72.8, 0.6, 1.0, 1, 2)
    kafka4 = Kafka_d(4200, 200, 65, 1, 1.0, 0.9, 2)
    total_damage = kafka.calculate_total_damage(450)
    total_damage7 = kafka10.calculate_total_damage(450)
    total_damage3 = kafka2.calculate_total_damage(450)
    total_damage2 = kafka0.calculate_total_damage(450)
    total_damage4 = kafka3.calculate_total_damage(450)
    total_damage5 = kafka4.calculate_total_damage(450)
    print(f"卡夫卡希露瓦银狼\t450行动值总伤: {total_damage}")
    print(f"2命卡夫卡希露瓦银狼\t450行动值总伤: {total_damage7}")
    print(f"卡夫卡希露瓦艾斯妲\t450行动值总伤: {total_damage3}")
    print(f"卡夫卡艾斯妲银狼\t450行动值总伤: {total_damage2}")
    print(f"卡夫卡桑博银狼\t\t450行动值总伤: {total_damage4}")
    print(f"卡夫卡桑博艾斯妲\t450行动值总伤: {total_damage5}")


    action_values = np.arange(150, 851, 100)  # 250到650的行动值，步长为100

    # 对于每个行动值，计算相应的伤害值
    damages_kafka = [(kafka.calculate_total_damage(av))/((av-50)/100) for av in action_values]
    damages_kafka7 = [(kafka10.calculate_total_damage(av))/((av-50)/100) for av in action_values]
    damages_kafka2 = [(kafka2.calculate_total_damage(av))/((av-50)/100) for av in action_values]
    damages_kafka0 = [(kafka0.calculate_total_damage(av))/((av-50)/100) for av in action_values]
    damages_kafka3 = [(kafka3.calculate_total_damage(av))/((av-50)/100) for av in action_values]
    damages_kafka4 = [(kafka4.calculate_total_damage(av))/((av-50)/100) for av in action_values]

    # 使用matplotlib进行绘图
    plt.figure(figsize=(10, 6))
    plt.plot(action_values, damages_kafka, label="sw&serval")
    plt.plot(action_values, damages_kafka7, label="2sw&serval")
    """plt.plot(action_values, damages_kafka2, label="asta&serval")
    plt.plot(action_values, damages_kafka0, label="asta&sw")"""
    plt.plot(action_values, damages_kafka3, label="sw&sambo")
    """
    plt.plot(action_values, damages_kafka4, label="asta&sambo")"""

    plt.xlabel('Action value')
    plt.ylabel('Damage')
    plt.title('Change in damage per round as Action value changes')
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
    #plot_damage_change()