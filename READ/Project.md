# 项目理解与下一步

## 目标

本项目要从 `decompiled/` 的《杀戮尖塔 2》反编译源码中提取卡牌、敌人、遭遇和战斗机制，构建一个适合 PPO / MaskablePPO 的简化战斗环境。长期目标是再接战斗外模型，完成路线、选牌、火堆等流程。

## 当前完成

- 建立 Python 包 `sls2_rl`。
- 完成战斗内 Gymnasium 风格环境 `SlS2CombatEnv`。
- 支持自定义卡组、指定敌人、指定遭遇池、随机追加卡。
- 支持动作 mask，适合 MaskablePPO。
- 完成规则基线，用于快速检查环境是否可赢。
- 编写抽取脚本，从反编译源码生成卡牌/敌人/遭遇 Markdown 与 JSON。
- 当前抽取规模：573 张卡、116 个敌人、87 个遭遇。

## 重要源码结论

- 卡牌基础元数据在 `CardModel` 子类构造函数：费用、类型、稀有度、目标。
- 卡牌数值常见于 `CanonicalVars`：`DamageVar`、`BlockVar`、`PowerVar<T>`。
- 卡牌真实效果在 `OnPlay`，需要逐张翻译，不应只靠数值元数据。
- 敌人 HP 在 `MonsterModel` 子类的 `MinInitialHp/MaxInitialHp`。
- 敌人行动在 `GenerateMoveStateMachine`，常见意图类包括 `SingleAttackIntent`、`BuffIntent` 等。
- 遭遇由 `EncounterModel` 子类给出房间类型、是否弱怪、可能怪物、生成怪物。

## 下一步建议

1. 把战士常见攻击/防御/抽牌牌完整翻译 20~30 张。
2. 实现多敌人目标选择，把动作空间扩展为 `手牌槽 x 目标槽 + 结束回合`。
3. 给敌人加入 `enemy_id one-hot/embedding` 和更完整的机制状态。
4. 将 `generated_data` 中的敌人状态机逐个转成可执行 Python move script。
5. 增加 pytest：卡牌效果、回合流程、action mask、固定 seed 对局回放。

