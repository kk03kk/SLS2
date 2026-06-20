# 强化学习训练/测试说明

## Observation 维度

环境 observation 是固定 `176` 维 float 向量：

- `0..31`：全局战斗状态。
- `32..111`：最多 10 张手牌，每张 8 维。
- `112..175`：最多 64 种卡的 deck/hand/discard 计数摘要。

全局状态当前包含：

- 玩家：HP 比例、格挡、能量、力量、虚弱、易伤。
- 敌人：HP 比例、格挡、力量、虚弱、易伤。
- 敌方下一意图：伤害、段数、格挡、力量、易伤、虚弱。
- 进度：回合数、抽牌堆/弃牌堆/消耗堆规模。
- 余下维度保留，方便后续加入药水、遗物、敌人 ID、多敌人等信息。

手牌每张 8 维：

- cost、damage、block、vulnerable、weak、strength、draw、present。

## Action 与 Mask

动作空间是 `Discrete(11)`：

- `0..9`：打出对应手牌槽位。
- `10`：结束回合。

环境提供 `action_masks()`，非法动作包括空手牌槽、费用不足、无合法目标。推荐使用 `MaskablePPO`，普通 PPO 也可训练，但会浪费样本学习非法动作。

## 推荐安装

```powershell
pip install -e .[rl]
```

如果只想跑规则基线，不安装 RL extras 也可以：

```powershell
python -m sls2_rl.evaluate --episodes 20 --pool weak
```

## 分阶段训练

与 `TASK.md` 对齐的课程学习入口：

```powershell
python -m sls2_rl.train --stage 01 --algo maskableppo --timesteps 50000 --out runs/stage01
python -m sls2_rl.train --stage 02 --algo maskableppo --timesteps 100000 --out runs/stage02
python -m sls2_rl.train --stage 03 --algo maskableppo --timesteps 200000 --out runs/stage03
python -m sls2_rl.train --stage 04 --algo maskableppo --timesteps 300000 --out runs/stage04
```

阶段含义：

- `01`：战士 A0 初始卡组 vs 弱怪池。
- `02`：战士 A0 初始卡组 + 随机 1 张战士奖励牌 vs 弱怪池。
- `03`：战士 A0 初始卡组 + 随机 3~5 张牌 vs 强怪池。
- `04`：战士 A0 初始卡组 + 随机 5~10 张牌 vs 精英池。

测试：

```powershell
python -m sls2_rl.evaluate --model runs/stage01 --algo maskableppo --episodes 100 --pool weak
python -m sls2_rl.evaluate --episodes 100 --pool weak
```

第二条不传模型时运行规则基线，可作为 sanity check。

## 是否直接训练通用大模型

建议不要一开始直接上全卡全怪通用模型。理由：

- 卡牌和怪物机制跨度很大，早期 reward 极稀疏，模型会先学到大量“无意义失败”。
- 动作含义依赖手牌槽位，组合空间随卡组增加快速变大。
- 怪物 ID 和意图都重要：意图解决短期决策，怪物 ID/机制记忆解决长期策略，例如提前防某个蓄力回合。

推荐路线：

- 先用课程学习训练通用策略骨架：从初始卡组和弱怪开始。
- Observation 同时保留“当前意图”和未来的“敌人 ID/机制 embedding”位置。
- 每扩展一批卡牌/怪物，先用规则基线和短训练验证环境没有不可赢或奖励错误。
- 后期再合并成一个通用模型，并用 encounter pool、deck composition、enemy id 做条件输入。

