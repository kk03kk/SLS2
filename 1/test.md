分析结果：差距大有两层原因。
第一层是正常随机性：
seed 93 起手有 Armaments+ + Bash + Body Slam+ + Defend + Anger，非常强，第一回合直接升级、上易伤、打伤害，后面顺利触发 Shriek。
seed 13 起手没有 Bash / Armaments+ / Dominate，前两回合节奏差很多，所以本来就更难。
第二层是我发现了一个蒙特卡洛评分问题：
之前如果未来模拟最后都输了，很多候选动作都会被打成差不多的 -1003，于是 AI 分不清“这步虽然可能输，但更接近翻盘”和“这步纯摆烂”。所以 seed 13 里会出现很多候选分数完全糊成一团。
我已经修了 [ppo_mc.py](D:/SLS2/sts2_sim/ppo_mc.py)：现在失败也会按剩余敌人血量、玩家血量、格挡、力量等继续细分，不再所有输法一个分。
修完后我用 seed 13 重新测了一次，小样本 --mc-rollouts 8 已经能赢了，最终 7 血，战损 25。说明问题确实主要在 MC 评分太粗。
接下来建议：
python trace_ppo.py --scenario ironclad_terror_eel_a9_32 --seed 13 --mc-rollouts 32 --mc-depth 80
然后不要只看两个种子，要批量评估。短期你可以多测几个：
python trace_ppo.py --scenario ironclad_terror_eel_a9_32 --seed 93 --mc-rollouts 32 --mc-depth 80
python trace_ppo.py --scenario ironclad_terror_eel_a9_32 --seed 13 --mc-rollouts 32 --mc-depth 80
python trace_ppo.py --scenario ironclad_terror_eel_a9_32 --seed 1 --mc-rollouts 32 --mc-depth 80
训练方面继续加量是必要的，这个精英战比海洋混混难很多：
python train_ppo.py --scenario ironclad_terror_eel_a9_32 --resume --timesteps 500000 --eval-episodes 100
一句话：
两个种子差距大是正常的，但之前 MC 对失败局评分太粗会放大这个问题；现在已修，后面用更多训练步数 + 更多种子评估。

(DL) PS D:\SLS2> python trace_ppo.py --scenario ironclad_terror_eel_a9_32 --seed 93 --mc-rollouts 32 --mc-depth 80
========================================================================
回合 1 | 玩家 HP 32/32 格挡 0 能量 3 力量 0
敌人 Terror Eel HP 150/150 格挡 0 力量 0 易伤 0 | 意图 attack 18
手牌: ['Anger', 'Armaments+', 'Bash', 'Body Slam+', 'Defend']
抽牌堆 10 | 弃牌堆: [] | 消耗堆: []
蒙特卡洛候选估分，rollouts=32:
  打出手牌1: Armaments+ | 平均 1115.19 最好 1116.00 最差 1115.00
  打出手牌4: Defend | 平均 -540.81 最好 1115.00 最差 -1005.00
  打出手牌2: Bash，目标: Terror Eel | 平均 -937.00 最好 1115.00 最差 -1005.00
  结束回合 | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌0: Anger，目标: Terror Eel | 平均 -1003.00 最好 -1003.00 最差 -1003.00
AI 第 1 步选择: 打出手牌1: Armaments+
  Player plays Armaments+
  Ironclad gains 5 block from Armaments+
  Defend upgrades to Defend+
  Bash upgrades to Bash+
  Anger upgrades to Anger+
本步奖励: -0.010
========================================================================
回合 1 | 玩家 HP 32/32 格挡 5 能量 2 力量 0
敌人 Terror Eel HP 150/150 格挡 0 力量 0 易伤 0 | 意图 attack 18
手牌: ['Anger+', 'Bash+', 'Body Slam+', 'Defend+']
抽牌堆 10 | 弃牌堆: ['Armaments+'] | 消耗堆: []
蒙特卡洛候选估分，rollouts=32:
  打出手牌1: Bash+，目标: Terror Eel | 平均 1115.06 最好 1116.00 最差 1115.00
  打出手牌2: Body Slam+，目标: Terror Eel | 平均 1113.59 最好 1116.00 最差 1065.00
  打出手牌0: Anger+，目标: Terror Eel | 平均 1048.91 最好 1116.00 最差 -1005.00
  结束回合 | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌3: Defend+ | 平均 -1003.00 最好 -1003.00 最差 -1003.00
AI 第 2 步选择: 打出手牌1: Bash+，目标: Terror Eel
  Player plays Bash+ -> Terror Eel
  Bash+ deals 10 to Terror Eel
  Terror Eel gains vulnerable 3
本步奖励: 0.790
========================================================================
回合 1 | 玩家 HP 32/32 格挡 5 能量 0 力量 0
敌人 Terror Eel HP 140/150 格挡 0 力量 0 易伤 3 | 意图 attack 18
手牌: ['Anger+', 'Body Slam+', 'Defend+']
抽牌堆 10 | 弃牌堆: ['Armaments+', 'Bash+'] | 消耗堆: []
蒙特卡洛候选估分，rollouts=32:
  打出手牌1: Body Slam+，目标: Terror Eel | 平均 1115.19 最好 1116.00 最差 1115.00
  打出手牌0: Anger+，目标: Terror Eel | 平均 1115.12 最好 1116.00 最差 1115.00
  结束回合 | 平均 -870.62 最好 1115.00 最差 -1003.00
AI 第 3 步选择: 打出手牌1: Body Slam+，目标: Terror Eel
  Player plays Body Slam+ -> Terror Eel
  Body Slam+ deals 7 to Terror Eel
本步奖励: 0.550
========================================================================
回合 1 | 玩家 HP 32/32 格挡 5 能量 0 力量 0
敌人 Terror Eel HP 133/150 格挡 0 力量 0 易伤 3 | 意图 attack 18
手牌: ['Anger+', 'Defend+']
抽牌堆 10 | 弃牌堆: ['Armaments+', 'Bash+', 'Body Slam+'] | 消耗堆: []
蒙特卡洛候选估分，rollouts=32:
  打出手牌0: Anger+，目标: Terror Eel | 平均 1115.22 最好 1116.00 最差 1115.00
  结束回合 | 平均 187.50 最好 1115.00 最差 -1005.00
AI 第 4 步选择: 打出手牌0: Anger+，目标: Terror Eel
  Player plays Anger+ -> Terror Eel
  Anger+ deals 12 to Terror Eel
  Anger+ adds 1 Anger+ to discard
本步奖励: 0.950
========================================================================
回合 1 | 玩家 HP 32/32 格挡 5 能量 0 力量 0
敌人 Terror Eel HP 121/150 格挡 0 力量 0 易伤 3 | 意图 attack 18
手牌: ['Defend+']
抽牌堆 10 | 弃牌堆: ['Armaments+', 'Bash+', 'Body Slam+', 'Anger+', 'Anger+'] | 消耗堆: []
蒙特卡洛候选估分，rollouts=32:
  结束回合 | 平均 1115.16 最好 1116.00 最差 1115.00
AI 第 5 步选择: 结束回合
  Player ends turn
  Terror Eel uses crash
  Terror Eel hits player for 13
  -- Turn 2 --
  Draw Strike
  Draw Dominate
  Draw Stomp
  Draw Ascender's Bane
  Draw Defend
本步奖励: -13.010
========================================================================
回合 2 | 玩家 HP 19/32 格挡 0 能量 3 力量 0
敌人 Terror Eel HP 121/150 格挡 0 力量 0 易伤 2 | 意图 attack 4x3 + Vigor 6
手牌: ['Strike', 'Dominate', 'Stomp', "Ascender's Bane", 'Defend']
抽牌堆 5 | 弃牌堆: ['Armaments+', 'Bash+', 'Body Slam+', 'Anger+', 'Anger+', 'Defend+'] | 消耗堆: []
蒙特卡洛候选估分，rollouts=32:
  打出手牌1: Dominate，目标: Terror Eel | 平均 1115.09 最好 1116.00 最差 1115.00
  打出手牌0: Strike，目标: Terror Eel | 平均 1115.06 最好 1116.00 最差 1115.00
  打出手牌4: Defend | 平均 1115.03 最好 1116.00 最差 1115.00
  打出手牌2: Stomp | 平均 -616.88 最好 1065.00 最差 -1005.00
  结束回合 | 平均 -1003.00 最好 -1003.00 最差 -1003.00
AI 第 6 步选择: 打出手牌1: Dominate，目标: Terror Eel
  Player plays Dominate -> Terror Eel
  Terror Eel gains vulnerable 1
  Ironclad gains strength 3
  Dominate exhausts
本步奖励: -0.010
========================================================================
回合 2 | 玩家 HP 19/32 格挡 0 能量 2 力量 3
敌人 Terror Eel HP 121/150 格挡 0 力量 0 易伤 3 | 意图 attack 4x3 + Vigor 6
手牌: ['Strike', 'Stomp', "Ascender's Bane", 'Defend']
抽牌堆 5 | 弃牌堆: ['Armaments+', 'Bash+', 'Body Slam+', 'Anger+', 'Anger+', 'Defend+'] | 消耗堆: ['Dominate']
蒙特卡洛候选估分，rollouts=32:
  打出手牌0: Strike，目标: Terror Eel | 平均 1115.06 最好 1116.00 最差 1115.00
  打出手牌3: Defend | 平均 1048.88 最好 1116.00 最差 -1005.00
  结束回合 | 平均 612.34 最好 1066.00 最差 -1005.00
AI 第 7 步选择: 打出手牌0: Strike，目标: Terror Eel
  Player plays Strike -> Terror Eel
  Strike deals 13 to Terror Eel
本步奖励: 1.030
========================================================================
回合 2 | 玩家 HP 19/32 格挡 0 能量 1 力量 3
敌人 Terror Eel HP 108/150 格挡 0 力量 0 易伤 3 | 意图 attack 4x3 + Vigor 6
手牌: ['Stomp', "Ascender's Bane", 'Defend']
抽牌堆 5 | 弃牌堆: ['Armaments+', 'Bash+', 'Body Slam+', 'Anger+', 'Anger+', 'Defend+', 'Strike'] | 消耗堆: ['Dominate']
蒙特卡洛候选估分，rollouts=32:
  打出手牌2: Defend | 平均 1115.12 最好 1116.00 最差 1115.00
  结束回合 | 平均 1065.22 最好 1066.00 最差 1065.00
AI 第 8 步选择: 打出手牌2: Defend
  Player plays Defend
  Ironclad gains 5 block from Defend
本步奖励: -0.010
========================================================================
回合 2 | 玩家 HP 19/32 格挡 5 能量 0 力量 3
敌人 Terror Eel HP 108/150 格挡 0 力量 0 易伤 3 | 意图 attack 4x3 + Vigor 6
手牌: ['Stomp', "Ascender's Bane"]
抽牌堆 5 | 弃牌堆: ['Armaments+', 'Bash+', 'Body Slam+', 'Anger+', 'Anger+', 'Defend+', 'Strike', 'Defend'] | 消耗堆: ['Dominate']
蒙特卡洛候选估分，rollouts=32:
  结束回合 | 平均 1048.88 最好 1116.00 最差 -1005.00
AI 第 9 步选择: 结束回合
  Player ends turn
  Ascender's Bane exhausts at end of turn
  Terror Eel uses thrash
  Terror Eel hits player for 0
  Terror Eel hits player for 3
  Terror Eel hits player for 4
  Terror Eel gains vigor 6
  -- Turn 3 --
  Draw Strike+
  Draw Strike
  Draw Defend
  Draw Strike+
  Draw Headbutt
本步奖励: -7.010
========================================================================
回合 3 | 玩家 HP 12/32 格挡 0 能量 3 力量 3
敌人 Terror Eel HP 108/150 格挡 0 力量 0 易伤 2 | 意图 attack 18
手牌: ['Strike+', 'Strike', 'Defend', 'Strike+', 'Headbutt']
抽牌堆 0 | 弃牌堆: ['Armaments+', 'Bash+', 'Body Slam+', 'Anger+', 'Anger+', 'Defend+', 'Strike', 'Defend', 'Stomp'] | 消耗堆: ['Dominate', "Ascender's Bane"]
蒙特卡洛候选估分，rollouts=32:
  打出手牌4: Headbutt，目标: Terror Eel，从弃牌堆选: Anger+ | 平均 1116.00 最好 1116.00 最差 1116.00
  打出手牌4: Headbutt，目标: Terror Eel，从弃牌堆选: Stomp | 平均 1116.00 最好 1116.00 最差 1116.00
  打出手牌4: Headbutt，目标: Terror Eel，从弃牌堆选: Anger+ | 平均 1115.97 最好 1116.00 最差 1115.00
  打出手牌1: Strike，目标: Terror Eel | 平均 1115.16 最好 1116.00 最差 1115.00
  打出手牌0: Strike+，目标: Terror Eel | 平均 1115.12 最好 1116.00 最差 1115.00
AI 第 10 步选择: 打出手牌4: Headbutt，目标: Terror Eel，从弃牌堆选: Anger+
  Player plays Headbutt -> Terror Eel
  Headbutt deals 18 to Terror Eel
  Headbutt puts Anger+ on top of draw pile
本步奖励: 1.430
========================================================================
回合 3 | 玩家 HP 12/32 格挡 0 能量 2 力量 3
敌人 Terror Eel HP 90/150 格挡 0 力量 0 易伤 2 | 意图 attack 18
手牌: ['Strike+', 'Strike', 'Defend', 'Strike+']
抽牌堆 1 | 弃牌堆: ['Armaments+', 'Bash+', 'Body Slam+', 'Anger+', 'Defend+', 'Strike', 'Defend', 'Stomp', 'Headbutt'] | 消耗堆: ['Dominate', "Ascender's Bane"]
蒙特卡洛候选估分，rollouts=32:
  打出手牌0: Strike+，目标: Terror Eel | 平均 1116.00 最好 1116.00 最差 1116.00
  打出手牌1: Strike，目标: Terror Eel | 平均 1116.00 最好 1116.00 最差 1116.00
  打出手牌3: Strike+，目标: Terror Eel | 平均 1115.97 最好 1116.00 最差 1115.00
  打出手牌2: Defend | 平均 717.81 最好 1115.00 最差 -1005.00
  结束回合 | 平均 -1003.00 最好 -1003.00 最差 -1003.00
AI 第 11 步选择: 打出手牌0: Strike+，目标: Terror Eel
  Player plays Strike+ -> Terror Eel
  Terror Eel's Shriek triggers a stun
  Strike+ deals 18 to Terror Eel
本步奖励: 1.430
========================================================================
回合 3 | 玩家 HP 12/32 格挡 0 能量 1 力量 3
敌人 Terror Eel HP 72/150 格挡 0 力量 0 易伤 2 | 意图 stunned
手牌: ['Strike', 'Defend', 'Strike+']
抽牌堆 1 | 弃牌堆: ['Armaments+', 'Bash+', 'Body Slam+', 'Anger+', 'Defend+', 'Strike', 'Defend', 'Stomp', 'Headbutt', 'Strike+'] | 消耗堆: ['Dominate', "Ascender's Bane"]
蒙特卡洛候选估分，rollouts=32:
  打出手牌0: Strike，目标: Terror Eel | 平均 1116.00 最好 1116.00 最差 1116.00
  打出手牌2: Strike+，目标: Terror Eel | 平均 1116.00 最好 1116.00 最差 1116.00
  结束回合 | 平均 1115.00 最好 1115.00 最差 1115.00
  打出手牌1: Defend | 平均 916.25 最好 1115.00 最差 -1005.00
AI 第 12 步选择: 打出手牌0: Strike，目标: Terror Eel
  Player plays Strike -> Terror Eel
  Strike deals 13 to Terror Eel
本步奖励: 1.030
========================================================================
回合 3 | 玩家 HP 12/32 格挡 0 能量 0 力量 3
敌人 Terror Eel HP 59/150 格挡 0 力量 0 易伤 2 | 意图 stunned
手牌: ['Defend', 'Strike+']
抽牌堆 1 | 弃牌堆: ['Armaments+', 'Bash+', 'Body Slam+', 'Anger+', 'Defend+', 'Strike', 'Defend', 'Stomp', 'Headbutt', 'Strike+', 'Strike'] | 消耗堆: ['Dominate', "Ascender's Bane"]
蒙特卡洛候选估分，rollouts=32:
  结束回合 | 平均 1115.97 最好 1116.00 最差 1115.00
AI 第 13 步选择: 结束回合
  Player ends turn
  Terror Eel uses stun
  -- Turn 4 --
  Draw Anger+
  Discard pile shuffled into draw pile
  Draw Strike
  Draw Strike+
  Draw Strike
  Draw Defend
本步奖励: -0.010
========================================================================
回合 4 | 玩家 HP 12/32 格挡 0 能量 3 力量 3
敌人 Terror Eel HP 59/150 格挡 0 力量 0 易伤 1 | 意图 vulnerable 99
手牌: ['Anger+', 'Strike', 'Strike+', 'Strike', 'Defend']
抽牌堆 9 | 弃牌堆: [] | 消耗堆: ['Dominate', "Ascender's Bane"]
蒙特卡洛候选估分，rollouts=32:
  打出手牌0: Anger+，目标: Terror Eel | 平均 1116.00 最好 1116.00 最差 1116.00
  打出手牌1: Strike，目标: Terror Eel | 平均 1116.00 最好 1116.00 最差 1116.00
  打出手牌2: Strike+，目标: Terror Eel | 平均 1116.00 最好 1116.00 最差 1116.00
  打出手牌3: Strike，目标: Terror Eel | 平均 1115.97 最好 1116.00 最差 1115.00
  打出手牌4: Defend | 平均 1115.00 最好 1115.00 最差 1115.00
AI 第 14 步选择: 打出手牌0: Anger+，目标: Terror Eel
  Player plays Anger+ -> Terror Eel
  Anger+ deals 16 to Terror Eel
  Anger+ adds 1 Anger+ to discard
本步奖励: 1.270
========================================================================
回合 4 | 玩家 HP 12/32 格挡 0 能量 3 力量 3
敌人 Terror Eel HP 43/150 格挡 0 力量 0 易伤 1 | 意图 vulnerable 99
手牌: ['Strike', 'Strike+', 'Strike', 'Defend']
抽牌堆 9 | 弃牌堆: ['Anger+', 'Anger+'] | 消耗堆: ['Dominate', "Ascender's Bane"]
蒙特卡洛候选估分，rollouts=32:
  打出手牌0: Strike，目标: Terror Eel | 平均 1116.00 最好 1116.00 最差 1116.00
  打出手牌1: Strike+，目标: Terror Eel | 平均 1116.00 最好 1116.00 最差 1116.00
  打出手牌2: Strike，目标: Terror Eel | 平均 1116.00 最好 1116.00 最差 1116.00
  打出手牌3: Defend | 平均 1115.00 最好 1115.00 最差 1115.00
  结束回合 | 平均 -1005.00 最好 -1005.00 最差 -1005.00
AI 第 15 步选择: 打出手牌0: Strike，目标: Terror Eel
  Player plays Strike -> Terror Eel
  Strike deals 13 to Terror Eel
本步奖励: 1.030
========================================================================
回合 4 | 玩家 HP 12/32 格挡 0 能量 2 力量 3
敌人 Terror Eel HP 30/150 格挡 0 力量 0 易伤 1 | 意图 vulnerable 99
手牌: ['Strike+', 'Strike', 'Defend']
抽牌堆 9 | 弃牌堆: ['Anger+', 'Anger+', 'Strike'] | 消耗堆: ['Dominate', "Ascender's Bane"]
蒙特卡洛候选估分，rollouts=32:
  打出手牌0: Strike+，目标: Terror Eel | 平均 1116.00 最好 1116.00 最差 1116.00
  打出手牌1: Strike，目标: Terror Eel | 平均 1116.00 最好 1116.00 最差 1116.00
  打出手牌2: Defend | 平均 1115.00 最好 1115.00 最差 1115.00
  结束回合 | 平均 121.25 最好 1115.00 最差 -1005.00
AI 第 16 步选择: 打出手牌0: Strike+，目标: Terror Eel
  Player plays Strike+ -> Terror Eel
  Strike+ deals 18 to Terror Eel
本步奖励: 1.430
========================================================================
回合 4 | 玩家 HP 12/32 格挡 0 能量 1 力量 3
敌人 Terror Eel HP 12/150 格挡 0 力量 0 易伤 1 | 意图 vulnerable 99
手牌: ['Strike', 'Defend']
抽牌堆 9 | 弃牌堆: ['Anger+', 'Anger+', 'Strike', 'Strike+'] | 消耗堆: ['Dominate', "Ascender's Bane"]
蒙特卡洛候选估分，rollouts=32:
  打出手牌0: Strike，目标: Terror Eel | 平均 1116.00 最好 1116.00 最差 1116.00
  结束回合 | 平均 1115.00 最好 1115.00 最差 1115.00
  打出手牌1: Defend | 平均 1115.00 最好 1115.00 最差 1115.00
AI 第 17 步选择: 打出手牌0: Strike，目标: Terror Eel
  Player plays Strike -> Terror Eel
  Strike deals 13 to Terror Eel
本步奖励: 26.150
========================================================================
结果: 胜利 | 最终 HP 12 | 战损 20 | 回合 4






(DL) PS D:\SLS2> python trace_ppo.py --scenario ironclad_terror_eel_a9_32 --seed 13 --mc-rollouts 32 --mc-depth 80 
========================================================================
回合 1 | 玩家 HP 32/32 格挡 0 能量 3 力量 0
敌人 Terror Eel HP 150/150 格挡 0 力量 0 易伤 0 | 意图 attack 18
手牌: ['Defend', 'Anger', 'Stomp', 'Headbutt', 'Strike+']
抽牌堆 10 | 弃牌堆: [] | 消耗堆: []
蒙特卡洛候选估分，rollouts=32:
  打出手牌4: Strike+，目标: Terror Eel | 平均 -939.81 最好 1065.00 最差 -1005.00
  结束回合 | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌2: Stomp | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌3: Headbutt，目标: Terror Eel | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌1: Anger，目标: Terror Eel | 平均 -1003.62 最好 -1003.00 最差 -1005.00
AI 第 1 步选择: 打出手牌4: Strike+，目标: Terror Eel
  Player plays Strike+ -> Terror Eel
  Strike+ deals 9 to Terror Eel
本步奖励: 0.710
========================================================================
回合 1 | 玩家 HP 32/32 格挡 0 能量 2 力量 0
敌人 Terror Eel HP 141/150 格挡 0 力量 0 易伤 0 | 意图 attack 18
手牌: ['Defend', 'Anger', 'Stomp', 'Headbutt']
抽牌堆 10 | 弃牌堆: ['Strike+'] | 消耗堆: []
蒙特卡洛候选估分，rollouts=32:
  打出手牌3: Headbutt，目标: Terror Eel，从弃牌堆选: Strike+ | 平均 -939.56 最好 1065.00 最差 -1005.00
  结束回合 | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌2: Stomp | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌0: Defend | 平均 -1003.31 最好 -1003.00 最差 -1005.00
  打出手牌1: Anger，目标: Terror Eel | 平均 -1003.88 最好 -1003.00 最差 -1005.00
AI 第 2 步选择: 打出手牌3: Headbutt，目标: Terror Eel，从弃牌堆选: Strike+
  Player plays Headbutt -> Terror Eel
  Headbutt deals 9 to Terror Eel
  Headbutt puts Strike+ on top of draw pile
本步奖励: 0.710
========================================================================
回合 1 | 玩家 HP 32/32 格挡 0 能量 1 力量 0
敌人 Terror Eel HP 132/150 格挡 0 力量 0 易伤 0 | 意图 attack 18
手牌: ['Defend', 'Anger', 'Stomp']
抽牌堆 11 | 弃牌堆: ['Headbutt'] | 消耗堆: []
蒙特卡洛候选估分，rollouts=32:
  打出手牌1: Anger，目标: Terror Eel | 平均 -939.75 最好 1065.00 最差 -1005.00
  结束回合 | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌2: Stomp | 平均 -1003.88 最好 -1003.00 最差 -1005.00
  打出手牌0: Defend | 平均 -1004.19 最好 -1003.00 最差 -1005.00
AI 第 3 步选择: 打出手牌1: Anger，目标: Terror Eel
  Player plays Anger -> Terror Eel
  Anger deals 6 to Terror Eel
  Anger adds 1 Anger to discard
本步奖励: 0.470
========================================================================
回合 1 | 玩家 HP 32/32 格挡 0 能量 1 力量 0
敌人 Terror Eel HP 126/150 格挡 0 力量 0 易伤 0 | 意图 attack 18
手牌: ['Defend', 'Stomp']
抽牌堆 11 | 弃牌堆: ['Headbutt', 'Anger', 'Anger'] | 消耗堆: []
蒙特卡洛候选估分，rollouts=32:
  打出手牌0: Defend | 平均 -939.50 最好 1065.00 最差 -1005.00
  结束回合 | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌1: Stomp | 平均 -1004.00 最好 -1003.00 最差 -1005.00
AI 第 4 步选择: 打出手牌0: Defend
  Player plays Defend
  Ironclad gains 5 block from Defend
本步奖励: -0.010
========================================================================
回合 1 | 玩家 HP 32/32 格挡 5 能量 0 力量 0
敌人 Terror Eel HP 126/150 格挡 0 力量 0 易伤 0 | 意图 attack 18
手牌: ['Stomp']
抽牌堆 11 | 弃牌堆: ['Headbutt', 'Anger', 'Anger', 'Defend'] | 消耗堆: []
蒙特卡洛候选估分，rollouts=32:
  结束回合 | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌0: Stomp | 平均 -1004.19 最好 -1003.00 最差 -1005.00
AI 第 5 步选择: 结束回合
  Player ends turn
  Terror Eel uses crash
  Terror Eel hits player for 13
  -- Turn 2 --
  Draw Strike+
  Draw Strike+
  Draw Dominate
  Draw Body Slam+
  Draw Defend
本步奖励: -13.010
========================================================================
回合 2 | 玩家 HP 19/32 格挡 0 能量 3 力量 0
敌人 Terror Eel HP 126/150 格挡 0 力量 0 易伤 0 | 意图 attack 4x3 + Vigor 6
手牌: ['Strike+', 'Strike+', 'Dominate', 'Body Slam+', 'Defend']
抽牌堆 6 | 弃牌堆: ['Headbutt', 'Anger', 'Anger', 'Defend', 'Stomp'] | 消耗堆: []
蒙特卡洛候选估分，rollouts=32:
  结束回合 | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌0: Strike+，目标: Terror Eel | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌1: Strike+，目标: Terror Eel | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌2: Dominate，目标: Terror Eel | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌3: Body Slam+，目标: Terror Eel | 平均 -1003.00 最好 -1003.00 最差 -1003.00
AI 第 6 步选择: 结束回合
  Player ends turn
  Terror Eel uses thrash
  Terror Eel hits player for 4
  Terror Eel hits player for 4
  Terror Eel hits player for 4
  Terror Eel gains vigor 6
  -- Turn 3 --
  Draw Defend
  Draw Strike
  Draw Armaments+
  Draw Strike
  Draw Ascender's Bane
本步奖励: -12.010
========================================================================
回合 3 | 玩家 HP 7/32 格挡 0 能量 3 力量 0
敌人 Terror Eel HP 126/150 格挡 0 力量 0 易伤 0 | 意图 attack 18
手牌: ['Defend', 'Strike', 'Armaments+', 'Strike', "Ascender's Bane"]
抽牌堆 1 | 弃牌堆: ['Headbutt', 'Anger', 'Anger', 'Defend', 'Stomp', 'Strike+', 'Strike+', 'Dominate', 'Body Slam+', 'Defend'] | 消耗堆: []
蒙特卡洛候选估分，rollouts=32:
  结束回合 | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌0: Defend | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌1: Strike，目标: Terror Eel | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌2: Armaments+ | 平均 -1003.00 最好 -1003.00 最差 -1003.00
  打出手牌3: Strike，目标: Terror Eel | 平均 -1003.00 最好 -1003.00 最差 -1003.00
AI 第 7 步选择: 结束回合
  Player ends turn
  Ascender's Bane exhausts at end of turn
  Terror Eel uses crash
  Terror Eel's Vigor adds 6 damage
  Terror Eel hits player for 24
本步奖励: -42.010
========================================================================
结果: 失败 | 最终 HP 0 | 战损 32 | 回合 3

