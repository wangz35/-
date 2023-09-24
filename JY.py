import math
class Jingyuan:
    def __init__(self, attack, speed, damage_increase, crit_rate, crit_damage):
        self.attack = attack
        self.speed = speed
        self.damage_increase = damage_increase
        self.crit_rate = crit_rate
        self.crit_damage = crit_damage

    def action_cost(self):
        return 10000 / self.speed

    def basic_attack_damage(self):
        # 考虑暴击的情况，使用暴击率和暴击伤害来计算平均伤害
        expected_crit_multiplier = 1*(1-self.crit_rate) + self.crit_rate * self.crit_damage 
        return self.attack * 5.2 * (1 + self.damage_increase / 100) * expected_crit_multiplier+self.attack * 1 * (1 + (self.damage_increase+60) / 100) * expected_crit_multiplier

    def big_attack_damage(self):
        expected_crit_multiplier = 1*(1-self.crit_rate) + self.crit_rate * self.crit_damage
        return self.attack * 4.8 * (1 + self.damage_increase / 100) * expected_crit_multiplier

    def calculate_total_damage(self, action_value):
        action_times = math.floor(action_value / self.action_cost())
        basic_attack_times = action_times
        big_attack_times = (action_times-1) // 1+1

        total_damage = 0

        total_damage += self.basic_attack_damage() * basic_attack_times
        total_damage += self.big_attack_damage() * big_attack_times
        total_damage = total_damage*(200+10*80)/((200+10*90)+200+10*80)
        return total_damage


class Seele:
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
        return self.attack * 2.2 * (1 + self.damage_increase / 100) * expected_crit_multiplier

    def big_attack_damage(self):
        expected_crit_multiplier = 1*(1-self.crit_rate) + self.crit_rate * (self.crit_damage +0.6)
        return self.attack * 4.25 * (1 + self.damage_increase / 100) * expected_crit_multiplier

    def calculate_total_damage(self, action_value):
        action_times = math.floor(action_value / self.action_cost())
        basic_attack_times = action_times
        big_attack_times = (action_times-1) // 3 +1
        print(self.basic_attack_damage()*(200+10*80)/((200+10*90)*self.def_debuff+200+10*80)*self.res_debuff)
        total_damage = 0

        total_damage += self.basic_attack_damage() * basic_attack_times
        total_damage += self.big_attack_damage() * big_attack_times
        total_damage = total_damage*(200+10*80)/((200+10*90)*self.def_debuff+200+10*80)
        total_damage = total_damage*self.res_debuff
        return total_damage


def main():
    jingyuan = Jingyuan(4000, 109, 90, 0.7, 2.9)
    seele = Seele(3509, 170, 150, 0.8, 2.9, 0.1, 1.3)
    total_damage = jingyuan.calculate_total_damage(450)
    total_damage2 = seele.calculate_total_damage(450)
    print(f"景停鸭三回合输出期望四动一大: {total_damage}")
    print(f"希儿银狼三回合输出期望三动一大: {total_damage2}")

if __name__ == "__main__":
    main()



