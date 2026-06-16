# SLS2 Battle AI

这是一个基于《Slay the Spire 2》战斗规则的强化学习项目。当前目标不是完整爬塔，而是先构建一个可高速运行的 headless 战斗模拟器，并在这个环境上训练、微调和测试战斗策略模型。

项目目前聚焦铁甲战士卡组和暗港遭遇。`decompiled/` 和 `backup/` 不是当前运行主线：`decompiled/` 更适合作为规则参考，`backup/` 是遗弃内容，日常训练和测试不用管。


上传github
git add .
git commit -m "06"
git push

## 项目结构

```text
SLS2/
  train_ppo.py              # 通用战斗 PPO 训练
  custom_train_ppo.py       # 固定牌组 + 固定遭遇微调
  custom_test.py            # 加载模型，打一场固定战斗并输出详细战报
  battle_ai/                # Gymnasium / MaskablePPO 环境封装
  sts2_sim/                 # 战斗模拟器、卡牌、敌人、效果、Power
  battle_ai_models/         # 模型保存目录
  battle_ai_runs/           # TensorBoard 训练日志
  battle_ai_reports/        # 测试战报和评估报告
```

## 环境

推荐使用你的 `DL` conda 环境。PowerShell 中可以这样进入环境：

```powershell
(D:\Anaconda\shell\condabin\conda-hook.ps1)
conda activate DL
```

如果当前 PowerShell 因用户名编码导致 `conda activate` 报错，也可以直接调用环境里的 Python：

```powershell
D:\Anaconda\envs\DL\python.exe train_ppo.py --help
```

下面示例默认都在项目根目录 `D:\SLS2` 执行。

## 入口 1：通用战斗训练

脚本：

```powershell
D:\Anaconda\envs\DL\python.exe train_ppo.py
```

常用命令：

```powershell
D:\Anaconda\envs\DL\python.exe train_ppo.py --timesteps 1000000 --stage all
```

默认模型路径：

```text
battle_ai_models/ppo_generic_battle.zip
```

重要规则：

- 如果模型文件已经存在，默认自动续训。
- 不需要手动加 `--resume`，它只是为了兼容旧命令。
- 只有明确传入 `--fresh` 时，才会从零开始训练，并在训练结束后覆盖目标模型。

常用参数：

```text
--timesteps          本次继续训练多少步
--stage              weak / regular / elite / boss / all
--min-bonus-cards    每局随机额外奖励牌下限
--max-bonus-cards    每局随机额外奖励牌上限
--max-turns          单场战斗最大回合数
--model-path         模型保存/读取路径
--tensorboard-log    TensorBoard 日志目录
--fresh              强制从零训练
```

PPO 参数也可以直接调：

```text
--n-steps
--batch-size
--n-epochs
--gamma
--gae-lambda
--learning-rate
--ent-coef
--clip-range
```

当前默认值偏稳：

```text
n_steps=2048
batch_size=512
n_epochs=8
gamma=0.985
gae_lambda=0.95
learning_rate=3e-4
ent_coef=0.015
clip_range=0.2
```

## 入口 2：固定战斗微调

脚本：

```powershell
D:\Anaconda\envs\DL\python.exe custom_train_ppo.py
```

默认会用根目录脚本里的固定卡组打：

```python
ENCOUNTER_ID = "seapunk_weak"
```

常用命令：

```powershell
D:\Anaconda\envs\DL\python.exe custom_train_ppo.py --timesteps 50000
```

指定遭遇：

```powershell
D:\Anaconda\envs\DL\python.exe custom_train_ppo.py --encounter-id corpse_slugs_weak --timesteps 50000
```

指定玩家血量和最大回合：

```powershell
D:\Anaconda\envs\DL\python.exe custom_train_ppo.py --encounter-id seapunk_weak --player-hp 80 --player-max-hp 80 --max-turns 100
```

重要规则和 `train_ppo.py` 一样：

- 已有模型默认自动续训。
- 只有 `--fresh` 会从零训练。
- 固定战斗微调默认更保守，避免把通用模型一下子训偏。

固定战斗默认 PPO 参数：

```text
n_steps=1024
batch_size=256
n_epochs=8
gamma=0.98
gae_lambda=0.95
learning_rate=1e-4
ent_coef=0.01
clip_range=0.15
```

## 入口 3：打一场固定战斗并输出战报

脚本：

```powershell
D:\Anaconda\envs\DL\python.exe custom_test.py
```

默认输出：

```text
battle_ai_reports/custom_battle_trace.txt
```

指定遭遇：

```powershell
D:\Anaconda\envs\DL\python.exe custom_test.py --encounter-id seapunk_weak
```

指定输出文件：

```powershell
D:\Anaconda\envs\DL\python.exe custom_test.py --encounter-id corpse_slugs_weak --output-path battle_ai_reports/corpse_slugs_trace.txt
```

战报会按回合显示：

- Turn 1 开局抽牌
- 当前手牌和费用
- 玩家 HP、格挡、能量、Power
- 敌人 HP、格挡、Power、攻击意图
- 模型每一步打了什么牌、打谁
- 敌人行动日志
- 每步后的双方状态

默认是确定性出牌。如果想从策略分布里采样，可以加：

```powershell
D:\Anaconda\envs\DL\python.exe custom_test.py --stochastic
```

## ENCOUNTER_ID 怎么填

`ENCOUNTER_ID` 填的是“遭遇标签”，不是单个敌人的 id。例如：

```python
ENCOUNTER_ID = "seapunk_weak"
```

也可以在命令行里传：

```powershell
D:\Anaconda\envs\DL\python.exe custom_test.py --encounter-id seapunk_weak
```

下面是当前模拟器里已经登记的暗港遭遇。

### Weak

| 标签 | 敌人 |
| --- | --- |
| `corpse_slugs_weak` | Corpse Slug x2 |
| `seapunk_weak` | Seapunk |
| `sludge_spinner_weak` | Sludge Spinner |
| `toadpoles_weak` | Toadpole x2 |

### Regular

| 标签 | 敌人 |
| --- | --- |
| `corpse_slugs_normal` | Corpse Slug x3 |
| `cultists_normal` | Calcified Cultist, Damp Cultist |
| `fossil_stalker_normal` | Fossil Stalker |
| `gremlin_merc_normal` | Gremlin Merc |
| `haunted_ship_normal` | Haunted Ship |
| `living_fog_normal` | Living Fog |
| `punch_construct_normal` | Punch Construct |
| `seapunk_normal` | Calcified Cultist, Seapunk |
| `sewer_clam_normal` | Sewer Clam |
| `two_tailed_rats_normal` | Two-Tailed Rat x3 |

### Elite

| 标签 | 敌人 |
| --- | --- |
| `phantasmal_gardeners_elite` | Phantasmal Gardener x4 |
| `skulking_colony_elite` | Skulking Colony |
| `terror_eel_elite` | Terror Eel |
| `terror_eel_a9_elite` | Terror Eel A9 variant |

### Boss

| 标签 | 敌人 |
| --- | --- |
| `lagavulin_matriarch_boss` | Lagavulin Matriarch |
| `soul_fysh_boss` | Soul Fysh |
| `waterfall_giant_boss` | Waterfall Giant |

## 额外测试用遭遇

这些不是暗港主线遭遇，主要用于快速冒烟测试：

| 标签 | 敌人 |
| --- | --- |
| `single_small_slime` | Small Twig Slime |
| `two_small_slimes` | Small Leaf Slime, Small Twig Slime |
| `medium_slime` | Medium Twig Slime |
| `cultist` | Calcified Cultist |

## 常见工作流

先继续训练通用模型：

```powershell
D:\Anaconda\envs\DL\python.exe train_ppo.py --timesteps 1000000 --stage all
```

再针对某个固定战斗微调：

```powershell
D:\Anaconda\envs\DL\python.exe custom_train_ppo.py --encounter-id seapunk_weak --timesteps 50000
```

最后输出一场详细战报：

```powershell
D:\Anaconda\envs\DL\python.exe custom_test.py --encounter-id seapunk_weak
```

打开：

```text
battle_ai_reports/custom_battle_trace.txt
```

就能检查模型每回合抽了什么、打了什么、敌人意图是什么，以及最后损血和胜负结果。
