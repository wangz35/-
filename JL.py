import math
import matplotlib.pyplot as plt
import numpy as np
def plot_damage_change():
    speed_values = range(160, 120, -1)  # 从180降低到126
    damage_values = []
    max_damage = 0
    max_damage_speed = 0
    max_damage_attack = 0

    for speed in speed_values:
        attack = 2800 + (160 - speed) * 21
        kafka = Jingliu(attack, speed, 48.8, 0.5, 2.9, 0.5, 1.12)
        total_damage = kafka.calculate_total_damage(450)
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
    print(f"Maximum damage of {max_damage} is achieved with a speed of {max_damage_speed} and an attack of {max_damage_attack}.")
    plt.show()

class Jingliu0:
    def __init__(self, attack, speed, damage_increase, crit_rate, crit_damage, def_debuff, res_debuff):
        self.attack = attack
        self.speed = speed
        self.damage_increase = damage_increase
        self.def_debuff = def_debuff
        self.res_debuff = res_debuff
        self.crit_rate = crit_rate
        self.crit_damage = crit_damage

    def action_cost(self):
        return 10000 / self.speed

    def basic_attack_damage(self):
        # 考虑暴击的情况，使用暴击率和暴击伤害来计算平均伤害
        expected_crit_multiplier = 1*(1-self.crit_rate) + self.crit_rate * self.crit_damage 
        return self.attack * 2 * (1 + self.damage_increase / 100) * expected_crit_multiplier+self.attack * 2 * (1 + (self.damage_increase+60) / 100) * expected_crit_multiplier

    def big_attack_damage(self):
        expected_crit_multiplier = 1*(1-self.crit_rate-0.5) + (self.crit_rate+0.5) * (self.crit_damage+0.25)
        return (self.attack+2000) * 3 * (1 + (self.damage_increase+42+60+20) / 100) * expected_crit_multiplier

    def strong_attack_damage(self):
        # 考虑暴击的情况，使用暴击率和暴击伤害来计算平均伤害
        expected_crit_multiplier = 1*(1-self.crit_rate-0.5) + (self.crit_rate+0.5) * (self.crit_damage)
        expected_crit_multiplier2 = 1*(1-self.crit_rate-0.5) + (self.crit_rate+0.5) * (self.crit_damage+0.25)
        return (self.attack+2000) * 2.5 * (1 + (self.damage_increase+42) / 100) * expected_crit_multiplier+(self.attack+2000) * 2.5 * (1 + (self.damage_increase+42) / 100) * expected_crit_multiplier2+(self.attack+2000) * 2.5 * (1 + (self.damage_increase+60+42) / 100) * expected_crit_multiplier2

    def calculate_total_damage(self, action_value):
        action_times = math.floor(action_value / self.action_cost())
        basic_attack_times = action_times//2
        strong_attack_times = action_times//2
        big_attack_times = (action_times-1) // 2+1

        total_damage = 0

        total_damage += self.basic_attack_damage() * basic_attack_times*(200+10*80)/((200+10*90)*self.def_debuff+200+10*80)
        total_damage += self.strong_attack_damage()*strong_attack_times*(200+10*80)/((200+10*90)*(self.def_debuff-0.12)+200+10*80)
        total_damage += self.big_attack_damage() * big_attack_times*(200+10*80)/((200+10*90)*(self.def_debuff-0.12)+200+10*80)
        total_damage = total_damage*self.res_debuff
        return total_damage
    
class Jingliu:
    def __init__(self, attack, speed, damage_increase, crit_rate, crit_damage, def_debuff, res_debuff):
        self.attack = attack
        self.speed = speed
        self.damage_increase = damage_increase
        self.def_debuff = def_debuff
        self.res_debuff = res_debuff
        self.crit_rate = crit_rate
        self.crit_damage = crit_damage

    def action_cost(self):
        return 10000 / self.speed

    def basic_attack_damage(self):
        # 考虑暴击的情况，使用暴击率和暴击伤害来计算平均伤害
        expected_crit_multiplier = 1*(1-self.crit_rate) + self.crit_rate * self.crit_damage 
        return self.attack * 2 * (1 + self.damage_increase / 100) * expected_crit_multiplier+self.attack * 2 * (1 + (self.damage_increase+60) / 100) * expected_crit_multiplier

    def big_attack_damage(self):
        expected_crit_multiplier = 1*(1-self.crit_rate-0.5) + (self.crit_rate+0.5) * (self.crit_damage+0.25+0.24)
        return (self.attack+2000) * 3 * (1 + (self.damage_increase+42+60+20) / 100) * expected_crit_multiplier

    def strong_attack_damage(self):
        # 考虑暴击的情况，使用暴击率和暴击伤害来计算平均伤害
        expected_crit_multiplier = 1*(1-self.crit_rate-0.5) + (self.crit_rate+0.5) * (self.crit_damage+0.24)
        expected_crit_multiplier2 = 1*(1-self.crit_rate-0.5) + (self.crit_rate+0.5) * (self.crit_damage+0.25+0.24)
        return (self.attack+2000) * 2.5 * (1 + (self.damage_increase+42) / 100) * expected_crit_multiplier+(self.attack+2000) * 2.5 * (1 + (self.damage_increase+42) / 100) * expected_crit_multiplier2+(self.attack+2000) * 2.5 * (1 + (self.damage_increase+60+42) / 100) * expected_crit_multiplier2

    def calculate_total_damage(self, action_value):
        action_times = math.floor(action_value / self.action_cost())
        basic_attack_times = action_times//2
        strong_attack_times = action_times//2
        big_attack_times = (action_times-1) // 2+1

        total_damage = 0

        total_damage += self.basic_attack_damage() * basic_attack_times*(200+10*80)/((200+10*90)*self.def_debuff+200+10*80)
        total_damage += self.strong_attack_damage()*strong_attack_times*(200+10*80)/((200+10*90)*(self.def_debuff-0.12)+200+10*80)
        total_damage += self.big_attack_damage() * big_attack_times*(200+10*80)/((200+10*90)*(self.def_debuff-0.12)+200+10*80)
        total_damage = total_damage*self.res_debuff
        return total_damage

class Jingliu2:
    def __init__(self, attack, speed, damage_increase, crit_rate, crit_damage, def_debuff, res_debuff):
        self.attack = attack
        self.speed = speed
        self.damage_increase = damage_increase
        self.def_debuff = def_debuff
        self.res_debuff = res_debuff
        self.crit_rate = crit_rate
        self.crit_damage = crit_damage

    def action_cost(self):
        return 10000 / self.speed

    def basic_attack_damage(self):
        # 考虑暴击的情况，使用暴击率和暴击伤害来计算平均伤害
        expected_crit_multiplier = 1*(1-self.crit_rate) + self.crit_rate * self.crit_damage 
        return self.attack * 2 * (1 + self.damage_increase / 100) * expected_crit_multiplier+self.attack * 2 * (1 + (self.damage_increase+60) / 100) * expected_crit_multiplier

    def big_attack_damage(self):
        expected_crit_multiplier = 1*(1-self.crit_rate-0.5) + (self.crit_rate+0.5) * (self.crit_damage+0.25+0.24)
        return (self.attack+2000) * 3 * (1 + (self.damage_increase+42+60+20) / 100) * expected_crit_multiplier

    def strong_attack_damage(self):
        # 考虑暴击的情况，使用暴击率和暴击伤害来计算平均伤害
        expected_crit_multiplier = 1*(1-self.crit_rate-0.5) + (self.crit_rate+0.5) * (self.crit_damage+0.24)
        expected_crit_multiplier2 = 1*(1-self.crit_rate-0.5) + (self.crit_rate+0.5) * (self.crit_damage+0.25+0.24)
        return (self.attack+2000) * 2.5 * (1 + (self.damage_increase+42) / 100) * expected_crit_multiplier+(self.attack+2000) * 2.5 * (1 + (self.damage_increase+42) / 100) * expected_crit_multiplier2+(self.attack+2000) * 2.5 * (1 + (self.damage_increase+80+60+42) / 100) * expected_crit_multiplier2

    def calculate_total_damage(self, action_value):
        action_times = math.floor(action_value / self.action_cost())
        basic_attack_times = action_times//2
        strong_attack_times = action_times//2
        big_attack_times = (action_times-1) // 2+1

        total_damage = 0

        total_damage += self.basic_attack_damage() * basic_attack_times*(200+10*80)/((200+10*90)*self.def_debuff+200+10*80)
        print(strong_attack_times)
        total_damage += self.strong_attack_damage()*strong_attack_times*(200+10*80)/((200+10*90)*(self.def_debuff-0.12)+200+10*80)
        total_damage += self.big_attack_damage() * big_attack_times*(200+10*80)/((200+10*90)*(self.def_debuff-0.12)+200+10*80)
        total_damage = total_damage*self.res_debuff
        return total_damage



def main():
    jl0 = Jingliu0(2300, 135, 48.8, 0.5, 2.9, 0.5, 1.12)
    total_damage0 = jl0.calculate_total_damage(350)
    jingyuan = Jingliu(2300, 135, 48.8, 0.5, 2.9, 0.5, 1.12)
    total_damage = jingyuan.calculate_total_damage(350)
    jingyuan2 = Jingliu2(2300, 135, 48.8, 0.5, 2.9, 0.5, 1.12)
    total_damage2 = jingyuan2.calculate_total_damage(350)
    #plot_damage_change()
    print(f"0命镜鸭佩三回合输出期望: {total_damage0}")
    print(f"镜鸭佩三回合输出期望: {total_damage}")
    print(f"2命镜流三回合输出期望: {total_damage2}")

if __name__ == "__main__":
    main()



