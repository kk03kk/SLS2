# Slay the Spire 2 强化学习战斗智能体项目交接说明

## 1. 项目目标

我要做一个《Slay the Spire 2》的强化学习 / 搜索型战斗智能体。

之前尝试过让 AI 玩完整爬塔流程，包括：

* 战斗
* 选卡
* 路线
* 商店
* 事件
* 遗物
* Boss
* 整局通关

但这个目标太复杂，状态空间太大，奖励太稀疏，很难训练出有效结果。

现在新的思路是：**先只训练战斗，不训练完整爬塔流程。**

也就是说：

> 给定固定卡组、固定敌人、固定初始状态，让 AI 无限模拟战斗，找到胜率高且掉血最少的打法。

最终希望实现：

1. 输入一个卡组和敌人，AI 给出较优打法。
2. 输入一个卡组和敌人池，模拟大量战斗，输出卡组强度。
3. 输入当前卡组和候选卡，分别模拟：

   * 当前卡组 D
   * D + 候选卡 A
   * D + 候选卡 B
   * D + 候选卡 C
     比较平均掉血差，从而给出选牌建议。
4. 未来可以用这些模拟结果建立单卡评分、卡组评分、卡牌协同评分。

核心评价指标不是传统 reward，而是：

* 胜率
* 平均掉血
* 平均回合数
* 最差 10% 掉血
* 掉血方差
* 卡牌加入前后的战损差

---

## 2. 总体技术路线

不要一开始直接训练 PPO / DQN。推荐路线是：

```text
本地战斗环境
→ 规则 AI baseline
→ 本回合搜索 AI
→ 多回合搜索 / MCTS
→ 用搜索 AI 生成高质量数据
→ 模仿学习训练策略模型
→ 强化学习微调
→ 模型 + 搜索联合决策
```

最终不是“每个对局重新训练”，而是：

```text
离线训练一个通用战斗策略模型
在线只做快速推理 / 少量搜索 / 批量模拟
```

实时选牌时不应该重新训练，也不应该重度 MCTS 全量搜索。应该使用：

```text
训练好的模型 + 少量模拟 + 缓存 + 粗评后精评
```

---

## 3. 环境设计思想

重点不是直接复制游戏源码，而是做一个 **headless combat simulator**：

```text
无 UI
无动画
无音效
纯战斗逻辑
高速度
可批量并行模拟
适合强化学习和搜索
```

反编译出来的代码主要作为规则参考，不建议直接复制大段官方源码进项目。更合理的方式是：

```text
读取/参考解包数据和反编译逻辑
→ 提取规则、数值、行动表、卡牌效果
→ 自己实现适合 RL 的战斗环境
```

---

## 4. 目前我有已经尝试搭建过的环境版本思路

### v0.1：单敌人基础战斗环境

支持：

* 玩家 HP
* 玩家格挡
* 玩家能量
* 抽牌堆
* 手牌
* 弃牌堆
* 消耗堆
* Strike / Defend / Bash 等基础牌
* 一个敌人
* 出牌 / 结束回合
* 敌人行动
* 胜负判断
* 掉血统计

接口类似 Gym：

```python
obs = env.reset()
obs, reward, done, info = env.step(action)
```

---

### v0.2：多敌人 + 目标选择

action 从简单的“选择第几张牌”升级成：

```python
(card_index, target_index)
```

例如：

```python
(0, 1)      # 用第 0 张手牌打第 1 个敌人
(2, None)   # 用第 2 张手牌，不需要目标，例如 Defend
(-1, None)  # 结束回合
```

支持：

* 多敌人
* 只允许攻击存活敌人
* 防御牌不需要目标
* 死亡敌人不再行动

---

### v0.3：状态系统

新增基础状态：

* Strength 力量
* Dexterity 敏捷
* Vulnerable 易伤
* Weak 虚弱

伤害计算逻辑：

```text
基础伤害
+ 攻击者力量
× 攻击者虚弱修正
× 目标易伤修正
→ 扣格挡
→ 扣血
```

格挡计算：

```text
基础格挡 + 玩家敏捷
```

---

### v0.4：本回合动作序列搜索器

不再让 AI 贪心地一张一张出牌，而是：

```text
复制当前环境
枚举本回合所有可能出牌序列
每条序列最后默认结束回合
根据启发式评分函数打分
选择评分最高序列的第一步动作
```

这一步是后续 MCTS 和模仿学习的基础。

搜索器不是环境，而是 agent。环境是 `CombatEnv`，搜索器是 `TurnSearchAgent`。

---

### v0.5：Effect + Event + Power 架构

这是为了支持真实卡牌复杂机制。

不能把每张牌都写成：

```python
if card.name == "...":
    ...
```

而应该做成：

```text
通用战斗流程
+ 通用效果系统 Effect
+ 事件系统 Event
+ 持续效果系统 Power
+ 少量特殊机制 handler
```

卡牌只声明自己由哪些机制组成。

例如：

```python
CardDef(
    id="strike",
    name="Strike",
    cost=1,
    card_type="attack",
    target="enemy",
    effects=[
        {"type": "deal_damage", "amount": 6}
    ],
)
```

Bash：

```python
CardDef(
    id="bash",
    name="Bash",
    cost=2,
    card_type="attack",
    target="enemy",
    effects=[
        {"type": "deal_damage", "amount": 8},
        {"type": "apply_status", "status": "vulnerable", "amount": 2},
    ],
)
```

每回合开始随机获得一张攻击牌：

```python
CardDef(
    id="random_attack_power",
    name="Random Attack Power",
    cost=1,
    card_type="power",
    target="none",
    effects=[
        {"type": "gain_power", "power": "random_attack_each_turn", "amount": 1}
    ],
)
```

---

### v0.6：Effect Registry + Power Registry

进一步重构，把 effect 和 power 做成注册表。

目标：

> 新增机制时，不改 `engine.py`，只新增 effect handler 或 power handler。

推荐结构：

```text
sts2_env/
│
├── data.py       # CardDef / CardInstance / Enemy / Power
├── engine.py     # CombatEnv 主体
├── effects.py    # 一次性效果注册表
├── powers.py     # 持续效果注册表
├── cards.py      # 卡牌数据
├── enemies.py    # 敌人数据 / 敌人模型
├── agents.py     # rule / search / rl agent
└── evaluation.py # 批量模拟 / 卡组评分 / 选牌评分
```

目前已经设计过的 effect 类型包括：

```text
deal_damage              造成伤害
deal_damage_all          AOE 群体伤害
gain_block               获得格挡
draw_cards               抽牌
apply_status             施加易伤 / 虚弱
gain_strength            获得力量
gain_dexterity           获得敏捷
gain_energy              获得能量
lose_hp                  自损
add_card_to_hand         添加指定牌到手牌
add_random_card_to_hand  随机添加牌到手牌
gain_power               获得持续 Power
```

目前设计过的 Power 类型包括：

```text
random_attack_each_turn      每回合开始随机获得攻击牌
block_when_attack            每次打出攻击牌获得格挡
draw_extra_each_turn         每回合开始额外抽牌
strength_each_turn           每回合开始获得力量
damage_all_on_card_played    每打出一张牌，对所有敌人造成伤害
```

目前 Event 类型包括：

```text
combat_start
player_turn_start
player_turn_end
card_played
card_drawn
enemy_died
damage_dealt
```

---

## 5. 为什么要这样设计

因为真实 StS2 里很多牌都有独特机制，例如：

* 每回合开始随机获得一张牌
* 打出某类牌后触发额外效果
* 临时牌
* 消耗牌
* 保留牌
* 状态牌
* 诅咒牌
* 费用变化
* 多段攻击
* AOE
* 随机目标
* Power 持续效果
* 角色专属资源，比如灵魂、电球、姿态等
* 敌人特殊机制
* Boss 阶段变化

不能每张牌都硬编码。正确方式是：

```text
先写通用机制积木
再用卡牌数据组合这些机制
只有特别独特的牌才写 custom handler
```

---

## 6. 真实环境还需要继续补的机制

优先级如下：

### 第一优先级：通用战斗底座

```text
抽牌 / 弃牌 / 洗牌
手牌上限
能量
消耗
保留
临时牌
状态牌
诅咒牌
Power 牌
回合开始触发
回合结束触发
打出牌触发
抽牌触发
死亡触发
伤害结算
格挡结算
Artifact
Strength
Dexterity
Vulnerable
Weak
Frail
```

### 第二优先级：常见卡牌机制

```text
抽牌
加能量
改变费用
生成临时牌
复制牌
多段攻击
AOE
随机目标
条件效果
升级版本
```

### 第三优先级：角色专属机制

```text
灵魂 / Soul
电球 / Orb
姿态 / Stance
召唤物
特殊计数器
角色专属资源
```

建议做 `Resource System`：

```python
player_resources = {
    "soul": 0,
    "orb_slots": [],
}
```

然后 effect 可以支持：

```text
gain_resource
spend_resource
if_resource_at_least
channel_orb
evoke_orb
```

### 第四优先级：遗物、药水、事件

当前目标是战斗 AI，暂时可以后置。

---

## 7. 卡组评分 / 选牌评分设计

卡组强度不是训练出来的，而是模拟评估出来的。

```python
evaluate_deck(deck, enemy_pool, agent, num_runs)
```

输出：

```text
胜率
平均掉血
平均回合数
最差 10% 掉血
掉血标准差
```

选牌建议：

给定当前卡组 D 和候选卡 A/B/C，比较：

```text
D
D + A
D + B
D + C
```

同一批 enemy pool、同一批 random seeds，模拟后计算：

```text
卡 A 价值 = D 平均掉血 - (D + A) 平均掉血
卡 B 价值 = D 平均掉血 - (D + B) 平均掉血
卡 C 价值 = D 平均掉血 - (D + C) 平均掉血
```

注意应该使用相同随机种子，减少抽牌运气导致的噪声。

实时选牌不要重度搜索，建议：

```text
快速模型 / 轻搜索
少量代表性敌人
每个候选卡几十到几百次模拟
粗评后精评
缓存结果
```

---

## 8. 关于训练

不要每种对局都重新训练。

正确方式：

```text
离线训练通用战斗策略模型
在线评估时调用模型 / 搜索器打大量模拟
```

推荐训练路线：

```text
1. 先做规则 AI baseline
2. 做本回合搜索 AI
3. 做 MCTS / 多回合 rollout
4. 用搜索 AI 生成状态 → 最佳动作数据
5. 训练模型模仿搜索 AI
6. 再用 RL 微调
7. 实战时用模型 + 搜索联合决策
```

小对局可以训练一个模型过拟合测试，但不要指望它泛化。

---

以上是我目前的一些想法，但是我发现越往后越复杂了，所以我将游戏核心文件解包到了decompiled文件夹里，请你详细分析其中的内容，先给我讲解一下你可以得到的游戏逻辑以及你接下来的思路！
比如你是否能为我完整搭好战斗环境？
如果可以，后面我们就可以直接用一个特定卡组+一个特定小怪+随机ai出牌进行一次简单的模拟啦！关键就是环境必须搭好！这是后面的事，你先告诉我你目前的思路！
