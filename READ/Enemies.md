# 敌人与遭遇数据抽取
来源：`Models.Monsters` 与 `Models.Encounters`。复杂状态机的精确动作需要后续逐怪物翻译，本文件先记录 HP 表达式、意图片段、遭遇组成。

## 敌人 (116)
| id | min hp raw | max hp raw | intent snippets |
| --- | --- | --- | --- |
| Aeonglass | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 535, 512)` | `` | `<br>EbbDamage<br>EyeLasersDamage, EyeLasersRepeat` |
| Architect | `9999` | `9999` | `` |
| AssassinRubyRaider | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 19, 18)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 24, 23)` | `KillshotDamage` |
| AxeRubyRaider | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 21, 20)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 23, 22)` | `BigSwingDamage<br>SwingDamage` |
| Axebot | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 76, 70)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 86, 78)` | `<br>HammerUppercutDamage<br>OneTwoDamage, 2` |
| BattleFriendV1 | `75` | `75` | `` |
| BattleFriendV2 | `150` | `150` | `` |
| BattleFriendV3 | `300` | `300` | `` |
| BigDummy | `9999` | `9999` | `` |
| BowlbugEgg | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 23, 21)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 24, 22)` | `BiteDamage` |
| BowlbugNectar | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 36, 35)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 39, 38)` | `<br>ThrashDamage` |
| BowlbugRock | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 46, 45)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 49, 48)` | `HeadbuttDamage` |
| BowlbugSilk | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 41, 40)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 44, 43)` | `<br>ThrashDamage, 2` |
| BruteRubyRaider | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 31, 30)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 34, 33)` | `<br>BeatDamage` |
| BygoneEffigy | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 132, 127)` | `` | `<br>SlashDamage` |
| Byrdonis | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 90, 81)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 90, 84)` | `PeckDamage, PeckRepeat<br>SwoopDamage` |
| Byrdpip | `9999` | `9999` | `` |
| CalcifiedCultist | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 39, 38)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 42, 41)` | `<br>DarkStrikeDamage` |
| CeremonialBeast | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 262, 252)` | `` | `<br>CrushDamage<br>PlowDamage<br>StompDamage` |
| Chomper | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 63, 60)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 67, 64)` | `ClampDamage, 2` |
| CorpseSlug | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 27, 25)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 29, 27)` | `<br>GlompDamage<br>WhipSlapDamage, WhipSlapRepeat` |
| CrossbowRubyRaider | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 19, 18)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 22, 21)` | `FireDamage` |
| Crusher | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 219, 209)` | `` | `<br>BugStingDamage, BugStingTimes<br>EnlargingStrikeDamage<br>GuardedStrikeDamage` |
| CubexConstruct | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 70, 65)` | `` | `<br>BlastDamage<br>ExpelDamage, 2` |
| DampCultist | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 52, 51)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 54, 53)` | `<br>DarkStrikeDamage` |
| DeprecatedMonster | `0` | `0` | `` |
| DevotedSculptor | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 172, 162)` | `` | `<br>SavageDamage` |
| Entomancer | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 155, 145)` | `` | `<br>BeesDamage, BeesRepeat<br>SpearMoveDamage` |
| Exoskeleton | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 25, 24)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 29, 28)` | `<br>MandiblesDamage<br>SkitterDamage, SkitterRepeats` |
| EyeWithTeeth | `6` | `` | `` |
| Fabricator | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 155, 150)` | `` | `DisintegrateDamage<br>FabricatingStrikeDamage` |
| FakeMerchantMonster | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 175, 165)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 175, 165)` | `<br>2, 8<br>SwipeDamage<br>ThrowRelicDamage` |
| FatGremlin | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 14, 13)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 18, 17)` | `` |
| FlailKnight | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 108, 101)` | `` | `<br>FlailDamage, 2<br>RamDamage` |
| Flyconid | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 51, 47)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 53, 49)` | `<br>SmashDamage<br>SporeDamage` |
| Fogmog | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 78, 74)` | `` | `<br>HeadbuttDamage<br>SwipeDamage` |
| FossilStalker | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 54, 51)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 56, 53)` | `<br>LashDamage, LashRepeat<br>LatchDamage<br>TackleDamage` |
| FrogKnight | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 199, 191)` | `` | `<br>BeetleChargeDamage<br>StrikeDownEvilDamage<br>TongueLashDamage` |
| FuzzyWurmCrawler | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 58, 55)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 59, 57)` | `<br>AcidGoopDamage` |
| GasBomb | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 8, 7)` | `` | `` |
| GlobeHead | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 158, 148)` | `` | `<br>GalvanicBurstDamage<br>ShockingSlapDamage<br>ThunderStrikeDamage, 3` |
| GremlinMerc | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 51, 47)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 53, 49)` | `<br>DoubleSmashDamage, DoubleSmashRepeat<br>GimmeDamage, GimmeRepeat<br>HeheDamage` |
| Guardbot | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 17, 16)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 21, 20)` | `` |
| HauntedShip | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 67, 63)` | `` | `<br>StompDamage, StompRepeat<br>SwipeDamage` |
| HunterKiller | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 126, 121)` | `` | `<br>BiteDamage<br>PunctureDamage, 3` |
| InfestedPrism | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 171, 161)` | `` | `<br>JabDamage<br>PulsateDamage<br>RadiateDamage` |
| Inklet | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 12, 11)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 18, 17)` | `JabDamage<br>PiercingGazeDamage<br>WhirlwindDamage, 3` |
| KinFollower | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 62, 58)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 63, 59)` | `<br>BoomerangDamage, 2<br>QuickSlashDamage` |
| KinPriest | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 199, 190)` | `` | `<br>BeamDamage, 3<br>OrbOfFrailtyDamage<br>OrbOfWeaknessDamage` |
| KnowledgeDemon | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 399, 379)` | `` | `<br>KnowledgeOverwhelmingDamage, 3<br>PonderDamage<br>SlapDamage` |
| LagavulinMatriarch | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 233, 222)` | `` | `<br>DisembowelDamage, DisembowelRepeat<br>Slash2Damage<br>SlashDamage` |
| LeafSlimeM | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 33, 32)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 36, 35)` | `ClumpDamage` |
| LeafSlimeS | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 12, 11)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 16, 15)` | `TackleDamage` |
| LivingFog | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 82, 80)` | `` | `AdvancedGasDamage<br>BloatDamage<br>SuperGasBlastDamage` |
| LivingShield | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 65, 55)` | `` | `<br>ShieldSlamDamage<br>SmashDamage` |
| LouseProgenitor | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 138, 134)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 141, 136)` | `<br>PounceDamage<br>WebDamage` |
| MagiKnight | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 89, 82)` | `` | `<br>BombDamage<br>PowerShieldDamage<br>SpearDamage` |
| Mawler | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 76, 72)` | `` | `<br>ClawDamage, 2<br>RipAndTearDamage` |
| MechaKnight | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 320, 300)` | `` | `<br>ChargeDamage<br>HeavyCleaveDamage` |
| MultiAttackMoveMonster | `999` | `999` | `1, 5` |
| Myte | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 64, 61)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 69, 67)` | `<br>BiteDamage<br>SuckDamage` |
| Nibbit | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 44, 42)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 48, 46)` | `<br>ButtDamage<br>SliceDamage` |
| Noisebot | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 19, 18)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 24, 23)` | `` |
| OneHpMonster | `1` | `1` | `` |
| Osty | `1` | `1` | `` |
| Ovicopter | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 126, 124)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 132, 130)` | `<br>SmashDamage<br>TenderizerDamage` |
| OwlMagistrate | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 247, 231)` | `` | `<br>PeckAssaultDamage, 6<br>ScrutinyDamage<br>VerdictDamage` |
| PaelsLegion | `9999` | `9999` | `` |
| Parafright | `21` | `` | `SlamDamage` |
| PhantasmalGardener | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 27, 26)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 32, 31)` | `<br>BiteDamage<br>FlailDamage, FlailRepeat<br>LashDamage` |
| PhrogParasite | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 66, 61)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 68, 64)` | `LashDamage, 4` |
| PunchConstruct | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 60, 55)` | `` | `<br>FastPunchDamage, FastPunchRepeat<br>StrongPunchDamage` |
| Queen | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 419, 400)` | `` | `<br>ExecutionDamage<br>OffWithYourHeadDamage, 5` |
| Rocket | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 209, 199)` | `` | `<br>LaserDamage<br>PrecisionBeamDamage<br>TargetingReticleDamage` |
| ScrollOfBiting | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 33, 30)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 39, 37)` | `<br>ChewDamage, 2<br>ChompDamage` |
| Seapunk | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 47, 44)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 49, 46)` | `<br>SeaKickDamage<br>SpinningKickDamage, SpinningKickRepeat` |
| SewerClam | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 58, 56)` | `` | `<br>JetDamage` |
| ShrinkerBeetle | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 40, 38)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 42, 40)` | `ChompDamage<br>StompDamage<br>strong: true` |
| SingleAttackMoveMonster | `999` | `999` | `1` |
| SkulkingColony | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 80, 75)` | `` | `<br>InertiaDamage<br>PiercingStabsDamage, PiercingStabsRepeat<br>ZoomDamage` |
| SlimedBerserker | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 281, 261)` | `` | `<br>PummelingDamage, 4<br>SmotherDamage` |
| SlitheringStrangler | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 54, 53)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 56, 55)` | `<br>LashDamage<br>ThwackDamage` |
| SludgeSpinner | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 41, 37)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 42, 39)` | `<br>OilSprayDamage<br>RageDamage<br>SlamDamage` |
| SlumberingBeetle | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 89, 86)` | `` | `<br>RolloutDamage` |
| SnappingJaxfruit | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 34, 31)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 36, 33)` | `<br>EnergyDamage` |
| SneakyGremlin | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 11, 10)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 15, 14)` | `TackleDamage` |
| SoulFysh | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 221, 211)` | `` | `<br>DeGasDamage<br>GazeDamage<br>ScreamDamage` |
| SoulNexus | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 254, 234)` | `` | `DrainLifeDamage<br>MaelstromDamage, MaelstromRepeat<br>SoulBurnDamage<br>strong: true` |
| SpectralKnight | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 97, 93)` | `` | `<br>SoulFlameDamage, 3<br>SoulSlashDamage` |
| SpinyToad | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 121, 116)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 124, 119)` | `<br>ExplosionDamage<br>LashDamage` |
| Stabbot | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 19, 18)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 24, 23)` | `<br>StabDamage` |
| TenHpMonster | `10` | `10` | `` |
| TerrorEel | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 150, 140)` | `` | `<br>CrashDamage<br>ThrashDamage, ThrashRepeat` |
| TestSubject | `` | `` | `<br>BigPounceDamage<br>BiteDamage<br>MultiClawDamage, (` |
| TheAdversaryMkOne | `100` | `` | `<br>BarrageDamage, BarrageRepeat<br>BeamDamage<br>SmashDamage` |
| TheAdversaryMkThree | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 300, 300)` | `` | `<br>BarrageDamage, BarrageRepeat<br>CrashDamage<br>FlameBeamDamage` |
| TheAdversaryMkTwo | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 200, 200)` | `` | `<br>BarrageDamage, BarrageRepeat<br>BashDamage<br>FlameBeamDamage` |
| TheForgotten | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 111, 106)` | `` | `<br>(` |
| TheInsatiable | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 341, 321)` | `` | `<br>BiteDamage<br>ThrashDamage, 2` |
| TheLost | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 99, 93)` | `` | `<br>EyeLasersDamage, 2` |
| TheObscura | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 129, 123)` | `` | `<br>HardeningStrikeDamage<br>PiercingGazeDamage` |
| ThievingHopper | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 84, 79)` | `` | `<br>HatTrickDamage<br>NabDamage<br>TheftDamage` |
| Toadpole | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 22, 21)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 26, 25)` | `<br>SpikeSpitDamage, SpikeSpitRepeat<br>WhirlDamage` |
| TorchHeadAmalgam | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 211, 199)` | `` | `SoulBeamDamage, 3<br>TackleDamage<br>WeakTackleDamage` |
| ToughEgg | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 15, 14)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 19, 18)` | `NibbleDamage` |
| TrackerRubyRaider | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 22, 21)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 26, 25)` | `<br>HoundsDamage, HoundsRepeat` |
| Tunneler | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 92, 87)` | `` | `<br>BelowDamage<br>BiteDamage` |
| TurretOperator | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 51, 41)` | `` | `<br>FireDamage, 5` |
| TwigSlimeM | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 27, 26)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 29, 28)` | `ClumpDamage` |
| TwigSlimeS | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 8, 7)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 12, 11)` | `TackleDamage` |
| TwoTailedRat | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 18, 17)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 22, 21)` | `<br>DiseaseBiteDamage<br>ScratchDamage` |
| Vantom | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 183, 173)` | `` | `<br>DismemberDamage<br>InkBlotDamage<br>InkyLanceDamage, 2` |
| VineShambler | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 64, 61)` | `` | `ChompDamage<br>GraspingVinesDamage<br>SwipeDamage, 2` |
| WaterfallGiant | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 250, 240)` | `` | `<br>(<br>PressureUpDamage<br>RamDamage` |
| Wriggler | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 18, 17)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 22, 21)` | `<br>BiteDamage` |
| Zapbot | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 19, 18)` | `AscensionHelper.GetValueIfAscension(AscensionLevel.ToughEnemies, 24, 23)` | `ZapDamage` |

## 遭遇 (87)
| id | room | weak | monsters |
| --- | --- | --- | --- |
| AeonglassBoss | Boss | False | Aeonglass |
| AxebotsNormal | Monster | False | Axebot |
| BattlewornDummyEventEncounter | Monster | False | BattleFriendV1, BattleFriendV2, BattleFriendV3 |
| BowlbugsNormal | Monster | False | BowlbugEgg, BowlbugNectar, BowlbugRock, BowlbugSilk |
| BowlbugsWeak | Monster | True | BowlbugEgg, BowlbugNectar, BowlbugRock |
| BygoneEffigyElite | Elite | False | BygoneEffigy |
| ByrdonisElite | Elite | False | Byrdonis |
| CeremonialBeastBoss | Boss | False | CeremonialBeast |
| ChompersNormal | Monster | False | Chomper |
| ConstructMenagerieNormal | Monster | False | CubexConstruct, PunchConstruct |
| CorpseSlugsNormal | Monster | False | CorpseSlug |
| CorpseSlugsWeak | Monster | True | CorpseSlug |
| CubexConstructNormal | Monster | False | CubexConstruct |
| CultistsNormal | Monster | False | CalcifiedCultist, DampCultist |
| DecimillipedeElite | Elite | False | DecimillipedeSegmentBack, DecimillipedeSegmentFront, DecimillipedeSegmentMiddle |
| DenseVegetationEventEncounter | Monster | False | Wriggler |
| DeprecatedEncounter | Monster | False |  |
| DevotedSculptorWeak | Monster | True | DevotedSculptor |
| EntomancerElite | Elite | False | Entomancer |
| ExoskeletonsNormal | Monster | False | Exoskeleton |
| ExoskeletonsWeak | Monster | True | Exoskeleton |
| FabricatorNormal | Monster | False | Fabricator |
| FakeMerchantEventEncounter | Monster | False | FakeMerchantMonster |
| FlyconidNormal | Monster | False | Flyconid, LeafSlimeM, TwigSlimeM |
| FogmogNormal | Monster | False | EyeWithTeeth, Fogmog |
| FossilStalkerNormal | Monster | False | FossilStalker |
| FrogKnightNormal | Monster | False | FrogKnight |
| FuzzyWurmCrawlerWeak | Monster | True | FuzzyWurmCrawler |
| GlobeHeadNormal | Monster | False | GlobeHead |
| GremlinMercNormal | Monster | False | FatGremlin, GremlinMerc, SneakyGremlin |
| HauntedShipNormal | Monster | False | HauntedShip |
| HunterKillerNormal | Monster | False | HunterKiller |
| InfestedPrismsElite | Elite | False | InfestedPrism |
| InkletsNormal | Monster | False | Inklet |
| KaiserCrabBoss | Boss | False | Crusher, Rocket |
| KnightsElite | Elite | False | FlailKnight, MagiKnight, SpectralKnight |
| KnowledgeDemonBoss | Boss | False | KnowledgeDemon |
| LagavulinMatriarchBoss | Boss | False | LagavulinMatriarch |
| LivingFogNormal | Monster | False | GasBomb, LivingFog |
| LouseProgenitorNormal | Monster | False | LouseProgenitor |
| MawlerNormal | Monster | False | Mawler |
| MechaKnightElite | Elite | False | MechaKnight |
| MysteriousKnightEventEncounter | Monster | False | MysteriousKnight |
| MytesNormal | Monster | False | Myte |
| NibbitsNormal | Monster | False | Nibbit |
| NibbitsWeak | Monster | True | Nibbit |
| OvergrowthCrawlers | Monster | False | FuzzyWurmCrawler, ShrinkerBeetle |
| OvicopterNormal | Monster | False | Ovicopter, ToughEgg |
| OwlMagistrateNormal | Monster | False | OwlMagistrate |
| PhantasmalGardenersElite | Elite | False | PhantasmalGardener |
| PhrogParasiteElite | Elite | False | PhrogParasite, Wriggler |
| PunchConstructNormal | Monster | False | PunchConstruct |
| PunchOffEventEncounter | Monster | False | PunchConstruct |
| QueenBoss | Boss | False | Queen, TorchHeadAmalgam |
| RubyRaidersNormal | Monster | False | AssassinRubyRaider, AxeRubyRaider, BruteRubyRaider, CrossbowRubyRaider, TrackerRubyRaider |
| ScrollsOfBitingNormal | Monster | False | ScrollOfBiting |
| ScrollsOfBitingWeak | Monster | True | ScrollOfBiting |
| SeapunkNormal | Monster | False | CalcifiedCultist, Seapunk |
| SeapunkWeak | Monster | True | Seapunk |
| SewerClamNormal | Monster | False | SewerClam |
| ShrinkerBeetleWeak | Monster | True | ShrinkerBeetle |
| SkulkingColonyElite | Elite | False | SkulkingColony |
| SlimedBerserkerNormal | Monster | False | SlimedBerserker |
| SlimesNormal | Monster | False | LeafSlimeM, LeafSlimeS, TwigSlimeM, TwigSlimeS |
| SlimesWeak | Monster | True | LeafSlimeM, LeafSlimeS, TwigSlimeM, TwigSlimeS |
| SlitheringStranglerNormal | Monster | False | LeafSlimeM, LeafSlimeS, SlitheringStrangler, SnappingJaxfruit, TwigSlimeM, TwigSlimeS |
| SludgeSpinnerWeak | Monster | True | SludgeSpinner |
| SlumberingBeetleNormal | Monster | False | BowlbugRock, BowlbugSilk, SlumberingBeetle |
| SnappingJaxfruitNormal | Monster | False | Flyconid, SnappingJaxfruit |
| SoulFyshBoss | Boss | False | SoulFysh |
| SoulNexusElite | Elite | False | SoulNexus |
| SpinyToadNormal | Monster | False | SpinyToad |
| TerrorEelElite | Elite | False | TerrorEel |
| TestSubjectBoss | Boss | False | TestSubject |
| TheInsatiableBoss | Boss | False | TheInsatiable |
| TheKinBoss | Boss | False | KinFollower, KinPriest |
| TheLostAndForgottenNormal | Monster | False | TheForgotten, TheLost |
| TheObscuraNormal | Monster | False | Parafright, TheObscura |
| ThievingHopperWeak | Monster | True | ThievingHopper |
| ToadpolesWeak | Monster | True | Toadpole |
| TunnelerNormal | Monster | False | Chomper, Tunneler |
| TunnelerWeak | Monster | True | Tunneler |
| TurretOperatorWeak | Monster | True | LivingShield, TurretOperator |
| TwoTailedRatsNormal | Monster | False | TwoTailedRat |
| VantomBoss | Boss | False | Vantom |
| VineShamblerNormal | Monster | False | VineShambler |
| WaterfallGiantBoss | Boss | False | WaterfallGiant |
