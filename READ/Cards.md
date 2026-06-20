# 卡牌数据抽取
来源：`decompiled/MegaCrit.Sts2.Core.Models.Cards` 与 `CardPools`。当前环境先实现战士核心子集，其余卡牌已抽取基础元数据，后续逐张补效果。

## colorless (64)
| id | cost | type | rarity | target | vars |
| --- | ---: | --- | --- | --- | --- |
| Alchemize | 1 | Skill | Rare | Self |  |
| Anointed | 1 | Skill | Rare | Self |  |
| Automation | 1 | Power | Uncommon | Self |  |
| BeaconOfHope | 1 | Power | Rare | Self |  |
| BeatDown | 3 | Skill | Rare | RandomEnemy |  |
| BelieveInYou | 0 | Skill | Uncommon | AnyAlly |  |
| Bolas | 0 | Attack | Rare | AnyEnemy | Damage=3 |
| Calamity | 3 | Power | Rare | Self |  |
| Catastrophe | 2 | Skill | Uncommon | Self |  |
| Coordinate | 1 | Skill | Uncommon | AnyAlly | StrengthPower=5 |
| DarkShackles | 0 | Skill | Uncommon | AnyEnemy |  |
| Discovery | 1 | Skill | Uncommon | Self |  |
| DramaticEntrance | 0 | Attack | Uncommon | AllEnemies | Damage=11 |
| Entropy | 1 | Power | Rare | Self |  |
| Equilibrium | 2 | Skill | Uncommon | Self | Block=13 |
| EternalArmor | 3 | Power | Rare | Self | PlatingPower=9 |
| Fasten | 1 | Power | Uncommon | Self |  |
| Finesse | 0 | Skill | Uncommon | Self | Block=4 |
| Fisticuffs | 1 | Attack | Uncommon | AnyEnemy | Damage=7 |
| FlashOfSteel | 0 | Attack | Uncommon | AnyEnemy | Damage=5 |
| GangUp | 1 | Attack | Uncommon | AnyEnemy |  |
| GoldAxe | 1 | Attack | Rare | AnyEnemy |  |
| HandOfGreed | 2 | Attack | Rare | AnyEnemy | Damage=20 |
| HiddenGem | 1 | Skill | Rare | Self |  |
| HuddleUp | 1 | Skill | Uncommon | AllAllies |  |
| Impatience | 0 | Skill | Uncommon | Self |  |
| Intercept | 1 | Skill | Uncommon | AnyAlly | Block=9 |
| JackOfAllTrades | 0 | Skill | Uncommon | Self |  |
| Jackpot | 3 | Attack | Rare | AnyEnemy | Damage=25 |
| Knockdown | 3 | Attack | Rare | AnyEnemy | Damage=10, KnockdownPower=2 |
| Lift | 1 | Skill | Uncommon | AnyAlly | Block=11 |
| MasterOfStrategy | 0 | Skill | Rare | Self |  |
| Mayhem | 2 | Power | Rare | Self |  |
| Mimic | 1 | Skill | Rare | AnyAlly |  |
| MindBlast | 1 | Attack | Uncommon | AnyEnemy |  |
| Nostalgia | 1 | Power | Rare | Self |  |
| Omnislice | 0 | Attack | Uncommon | AnyEnemy | Damage=8 |
| Panache | 0 | Power | Uncommon | Self |  |
| PanicButton | 0 | Skill | Uncommon | Self | Block=30 |
| PrepTime | 1 | Power | Uncommon | Self | PrepTimePower=4 |
| Production | 0 | Skill | Uncommon | Self |  |
| Prolong | 0 | Skill | Uncommon | Self |  |
| Prowess | 1 | Power | Uncommon | Self | StrengthPower=1, DexterityPower=1 |
| Purity | 0 | Skill | Uncommon | Self |  |
| Rally | 2 | Skill | Rare | AllAllies | Block=12 |
| Rend | 2 | Attack | Rare | AnyEnemy |  |
| Restlessness | 0 | Skill | Uncommon | Self |  |
| RollingBoulder | 3 | Power | Rare | Self | RollingBoulderPower=5 |
| Salvo | 1 | Attack | Rare | AnyEnemy | Damage=12 |
| Scrawl | 1 | Skill | Rare | Self |  |
| SecretTechnique | 0 | Skill | Rare | Self |  |
| SecretWeapon | 0 | Skill | Rare | Self |  |
| SeekerStrike | 1 | Attack | Uncommon | AnyEnemy | Damage=9 |
| Shockwave | 2 | Skill | Uncommon | AllEnemies |  |
| Splash | 1 | Skill | Uncommon | Self |  |
| Stratagem | 1 | Power | Uncommon | Self |  |
| TagTeam | 2 | Attack | Uncommon | AnyEnemy | Damage=11 |
| TheBomb | 2 | Skill | Uncommon | Self |  |
| TheGambit | 0 | Skill | Rare | Self | Block=50 |
| ThinkingAhead | 0 | Skill | Uncommon | Self |  |
| ThrummingHatchet | 1 | Attack | Uncommon | AnyEnemy | Damage=11 |
| UltimateDefend | 1 | Skill | Uncommon | Self | Block=11 |
| UltimateStrike | 1 | Attack | Uncommon | AnyEnemy | Damage=14 |
| Volley | 0 | Attack | Uncommon | RandomEnemy | Damage=10 |

## curse (16)
| id | cost | type | rarity | target | vars |
| --- | ---: | --- | --- | --- | --- |
| BadLuck | -1 | Curse | Curse | None |  |
| Clumsy | -1 | Curse | Curse | None |  |
| CurseOfTheBell | -1 | Curse | Curse | None |  |
| Debt | -1 | Curse | Curse | None |  |
| Decay | -1 | Curse | Curse | None | Damage=2 |
| Doubt | -1 | Curse | Curse | None | WeakPower=1 |
| Enthralled | 2 | Curse | Curse | None |  |
| Folly | -1 | Curse | Curse | None |  |
| Guilty | -1 | Curse | Curse | None |  |
| Injury | -1 | Curse | Curse | None |  |
| Normality | -1 | Curse | Curse | None |  |
| PoorSleep | -1 | Curse | Curse | None |  |
| Regret | -1 | Curse | Curse | None |  |
| Shame | -1 | Curse | Curse | None |  |
| SporeMind | 1 | Curse | Curse | None |  |
| Writhe | -1 | Curse | Curse | None |  |

## defect (88)
| id | cost | type | rarity | target | vars |
| --- | ---: | --- | --- | --- | --- |
| AdaptiveStrike | 2 | Attack | Rare | AnyEnemy | Damage=18 |
| AllForOne | 2 | Attack | Rare | AnyEnemy | Damage=10 |
| BallLightning | 1 | Attack | Common | AnyEnemy | Damage=7 |
| Barrage | 1 | Attack | Common | AnyEnemy | Damage=5 |
| BeamCell | 0 | Attack | Common | AnyEnemy | Damage=3, VulnerablePower=1 |
| BiasedCognition | 1 | Power | Ancient | Self | FocusPower=4, BiasedCognitionPower=1 |
| BoostAway | 0 | Skill | Common | Self | Block=6 |
| BootSequence | 0 | Skill | Uncommon | Self | Block=10 |
| Buffer | 2 | Power | Rare | Self | BufferPower=1 |
| BulkUp | 2 | Power | Uncommon | Self | StrengthPower=2, DexterityPower=2 |
| Capacitor | 1 | Power | Uncommon | Self |  |
| Chaos | 1 | Skill | Uncommon | Self |  |
| ChargeBattery | 1 | Skill | Common | Self | Block=7 |
| Chill | 0 | Skill | Uncommon | Self |  |
| Claw | 0 | Attack | Common | AnyEnemy | Damage=3 |
| ColdSnap | 1 | Attack | Common | AnyEnemy | Damage=6 |
| Compact | 1 | Skill | Uncommon | Self | Block=6 |
| CompileDriver | 1 | Attack | Common | AnyEnemy | Damage=7 |
| ConsumingShadow | 2 | Power | Rare | Self | ConsumingShadowPower=1 |
| Coolant | 1 | Power | Rare | Self | CoolantPower=2 |
| Coolheaded | 1 | Skill | Common | Self |  |
| CreativeAi | 3 | Power | Rare | Self |  |
| Darkness | 1 | Skill | Uncommon | Self |  |
| DefendDefect | 1 | Skill | Basic | Self | Block=5 |
| Defragment | 1 | Power | Rare | Self | FocusPower=1 |
| DoubleEnergy | 1 | Skill | Uncommon | Self |  |
| Dualcast | 1 | Skill | Basic | Self |  |
| EchoForm | 3 | Power | Rare | Self |  |
| EnergySurge | 1 | Skill | Uncommon | AllAllies |  |
| Feral | 2 | Power | Uncommon | Self | FeralPower=1 |
| FightThrough | 1 | Skill | Uncommon | Self | Block=13 |
| FlakCannon | 2 | Attack | Rare | RandomEnemy | Damage=8 |
| FocusedStrike | 1 | Attack | Common | AnyEnemy | Damage=9, FocusPower=1 |
| Ftl | 0 | Attack | Uncommon | AnyEnemy | Damage=5 |
| Fusion | 1 | Skill | Uncommon | Self |  |
| GeneticAlgorithm | 1 | Skill | Rare | Self |  |
| Glacier | 2 | Skill | Uncommon | Self | Block=6 |
| Glasswork | 1 | Skill | Uncommon | Self | Block=5 |
| GoForTheEyes | 0 | Attack | Common | AnyEnemy | Damage=3, WeakPower=1 |
| GunkUp | 1 | Attack | Common | AnyEnemy | Damage=4 |
| Hailstorm | 1 | Power | Uncommon | Self | HailstormPower=6 |
| HelixDrill | 0 | Attack | Rare | AnyEnemy | Damage=3 |
| Hologram | 1 | Skill | Common | Self | Block=3 |
| Hotfix | 0 | Skill | Common | Self | FocusPower=2 |
| Hyperbeam | 2 | Attack | Rare | AllEnemies | Damage=28, FocusPower=3 |
| IceLance | 3 | Attack | Rare | AnyEnemy | Damage=19 |
| Ignition | 1 | Skill | Rare | AnyAlly |  |
| Iteration | 1 | Power | Uncommon | Self | IterationPower=2 |
| Leap | 1 | Skill | Common | Self | Block=9 |
| LightningRod | 1 | Skill | Common | Self | Block=4, LightningRodPower=2 |
| Loop | 1 | Power | Uncommon | Self |  |
| MachineLearning | 1 | Power | Rare | Self |  |
| MeteorStrike | 5 | Attack | Rare | AnyEnemy | Damage=24 |
| Modded | 0 | Skill | Rare | Self |  |
| MomentumStrike | 1 | Attack | Common | AnyEnemy | Damage=10 |
| MultiCast | 0 | Skill | Rare | Self |  |
| Null | 2 | Attack | Uncommon | AnyEnemy | Damage=10, WeakPower=2 |
| Overclock | 0 | Skill | Uncommon | Self |  |
| Quadcast | 1 | Skill | Ancient | Self |  |
| Rainbow | 2 | Skill | Rare | Self |  |
| Reboot | 0 | Skill | Rare | Self |  |
| Refract | 3 | Attack | Uncommon | AnyEnemy | Damage=9 |
| RocketPunch | 2 | Attack | Uncommon | AnyEnemy | Damage=13 |
| Scavenge | 1 | Skill | Uncommon | Self |  |
| Scrape | 1 | Attack | Uncommon | AnyEnemy | Damage=7 |
| ShadowShield | 2 | Skill | Uncommon | Self | Block=11 |
| Shatter | 1 | Attack | Rare | AllEnemies | Damage=7 |
| SignalBoost | 1 | Skill | Rare | Self | SignalBoostPower=1 |
| Skim | 1 | Skill | Uncommon | Self |  |
| Smokestack | 1 | Power | Uncommon | Self | SmokestackPower=5 |
| Spinner | 1 | Power | Rare | Self | SpinnerPower=1 |
| Storm | 1 | Power | Uncommon | Self | StormPower=1 |
| StrikeDefect | 1 | Attack | Basic | AnyEnemy | Damage=6 |
| Subroutine | 1 | Power | Uncommon | Self |  |
| Sunder | 3 | Attack | Uncommon | AnyEnemy | Damage=24 |
| Supercritical | 0 | Skill | Rare | Self |  |
| SweepingBeam | 1 | Attack | Common | AllEnemies | Damage=6 |
| Synchronize | 1 | Skill | Uncommon | Self |  |
| Synthesis | 2 | Attack | Uncommon | AnyEnemy | Damage=14 |
| Tempest | 0 | Skill | Uncommon | Self |  |
| TeslaCoil | 0 | Attack | Uncommon | AnyEnemy | Damage=3 |
| Thunder | 1 | Power | Uncommon | Self | ThunderPower=6 |
| TrashToTreasure | 1 | Power | Rare | Self |  |
| Turbo | 0 | Skill | Common | Self |  |
| Uproar | 2 | Attack | Common | AnyEnemy | Damage=6 |
| Voltaic | 3 | Skill | Rare | Self |  |
| WhiteNoise | 1 | Skill | Uncommon | Self |  |
| Zap | 1 | Skill | Basic | Self |  |

## event (26)
| id | cost | type | rarity | target | vars |
| --- | ---: | --- | --- | --- | --- |
| Apotheosis | 2 | Skill | Ancient | Self |  |
| Apparition | 1 | Skill | Ancient | Self | IntangiblePower=1 |
| BrightestFlame | 0 | Skill | Ancient | Self |  |
| ByrdSwoop | 0 | Attack | Event | AnyEnemy | Damage=14 |
| Caltrops | 1 | Power | Event | Self | ThornsPower=3 |
| Clash | 0 | Attack | Event | AnyEnemy | Damage=14 |
| Distraction | 1 | Skill | Event | Self |  |
| DualWield | 1 | Skill | Event | Self |  |
| Enlightenment | 0 | Skill | Event | Self |  |
| Entrench | 2 | Skill | Event | Self |  |
| Exterminate | 1 | Attack | Event | AllEnemies | Damage=3 |
| FeedingFrenzy | 0 | Skill | Event | Self | StrengthPower=5 |
| HelloWorld | 1 | Power | Event | Self |  |
| Maul | 1 | Attack | Ancient | AnyEnemy | Damage=5 |
| Metamorphosis | 2 | Skill | Event | Self |  |
| NeowsFury | 1 | Attack | Ancient | AnyEnemy | Damage=10 |
| Outmaneuver | 1 | Skill | Event | Self |  |
| Peck | 1 | Attack | Event | AnyEnemy | Damage=2 |
| Rebound | 1 | Attack | Event | AnyEnemy | Damage=9 |
| Relax | 3 | Skill | Ancient | Self | Block=15 |
| RipAndTear | 1 | Attack | Event | RandomEnemy | Damage=7 |
| Squash | 1 | Attack | Event | AnyEnemy | Damage=10, VulnerablePower=2 |
| Stack | 1 | Skill | Event | Self |  |
| ToricToughness | 2 | Skill | Event | Self | Block=5 |
| Whistle | 3 | Attack | Ancient | AnyEnemy | Damage=33 |
| Wish | 0 | Skill | Ancient | Self |  |

## ironclad (87)
| id | cost | type | rarity | target | vars |
| --- | ---: | --- | --- | --- | --- |
| Aggression | 1 | Power | Rare | Self |  |
| Anger | 0 | Attack | Common | AnyEnemy | Damage=6 |
| Armaments | 1 | Skill | Common | Self | Block=5 |
| AshenStrike | 1 | Attack | Uncommon | AnyEnemy |  |
| Barricade | 3 | Power | Rare | Self |  |
| Bash | 2 | Attack | Basic | AnyEnemy | Damage=8, VulnerablePower=2 |
| BattleTrance | 0 | Skill | Uncommon | Self |  |
| BloodWall | 2 | Skill | Common | Self | Block=16 |
| Bloodletting | 0 | Skill | Common | Self |  |
| Bludgeon | 3 | Attack | Uncommon | AnyEnemy | Damage=32 |
| BodySlam | 1 | Attack | Common | AnyEnemy |  |
| Brand | 0 | Skill | Rare | Self | StrengthPower=1 |
| Break | 1 | Attack | Ancient | AnyEnemy | Damage=20, VulnerablePower=5 |
| Breakthrough | 1 | Attack | Common | AllEnemies | Damage=9 |
| Bully | 0 | Attack | Uncommon | AnyEnemy |  |
| BurningPact | 1 | Skill | Uncommon | Self |  |
| Cascade | -1 | Skill | Rare | Self |  |
| Cinder | 2 | Attack | Common | AnyEnemy | Damage=18 |
| Colossus | 1 | Skill | Uncommon | Self | Block=5 |
| Conflagration | 1 | Attack | Rare | AllEnemies | Damage=2 |
| Corruption | 3 | Power | Ancient | Self |  |
| CrimsonMantle | 1 | Power | Rare | Self | CrimsonMantlePower=8 |
| Cruelty | 1 | Power | Rare | Self | CrueltyPower=25 |
| DarkEmbrace | 2 | Power | Rare | Self |  |
| DefendIronclad | 1 | Skill | Basic | Self | Block=5 |
| DemonForm | 3 | Power | Rare | Self | StrengthPower=2 |
| DemonicShield | 0 | Skill | Uncommon | AnyAlly |  |
| Dismantle | 1 | Attack | Uncommon | AnyEnemy | Damage=8 |
| Dominate | 1 | Skill | Uncommon | AnyEnemy | VulnerablePower=1 |
| DrumOfBattle | 1 | Skill | Uncommon | Self |  |
| EvilEye | 1 | Skill | Uncommon | Self | Block=8 |
| ExpectAFight | 2 | Skill | Uncommon | Self |  |
| Feed | 1 | Attack | Rare | AnyEnemy | Damage=10 |
| FeelNoPain | 1 | Power | Uncommon | Self |  |
| FiendFire | 2 | Attack | Rare | AnyEnemy | Damage=7 |
| FightMe | 2 | Attack | Uncommon | AnyEnemy | Damage=5, StrengthPower=3 |
| FlameBarrier | 2 | Skill | Uncommon | Self | Block=12 |
| ForgottenRitual | 1 | Skill | Uncommon | Self |  |
| Havoc | 1 | Skill | Common | Self |  |
| Headbutt | 1 | Attack | Common | AnyEnemy | Damage=9 |
| Hellraiser | 2 | Power | Rare | Self |  |
| Hemokinesis | 1 | Attack | Uncommon | AnyEnemy | Damage=15 |
| HowlFromBeyond | 3 | Attack | Uncommon | AllEnemies | Damage=16 |
| Impervious | 2 | Skill | Rare | Self | Block=30 |
| InfernalBlade | 1 | Skill | Uncommon | Self |  |
| Inferno | 1 | Power | Uncommon | Self | InfernoPower=6 |
| Inflame | 1 | Power | Uncommon | Self | StrengthPower=2 |
| IronWave | 1 | Attack | Common | AnyEnemy | Damage=5, Block=5 |
| Juggernaut | 2 | Power | Rare | Self | JuggernautPower=6 |
| Juggling | 1 | Power | Uncommon | Self |  |
| Mangle | 3 | Attack | Rare | AnyEnemy | Damage=15 |
| MoltenFist | 1 | Attack | Common | AnyEnemy | Damage=10 |
| NotYet | 2 | Skill | Rare | Self |  |
| Offering | 0 | Skill | Rare | Self |  |
| OneTwoPunch | 1 | Skill | Rare | Self |  |
| PactsEnd | 0 | Attack | Rare | AllEnemies | Damage=17 |
| PerfectedStrike | 2 | Attack | Common | AnyEnemy |  |
| Pillage | 1 | Attack | Uncommon | AnyEnemy | Damage=6 |
| PommelStrike | 1 | Attack | Common | AnyEnemy | Damage=9 |
| PrimalForce | 0 | Skill | Rare | Self |  |
| Pyre | 2 | Power | Rare | Self |  |
| Rage | 0 | Skill | Uncommon | Self |  |
| Rampage | 1 | Attack | Uncommon | AnyEnemy | Damage=9 |
| Rupture | 1 | Power | Uncommon | Self | StrengthPower=1 |
| SecondWind | 1 | Skill | Uncommon | Self | Block=5 |
| SetupStrike | 1 | Attack | Common | AnyEnemy | Damage=7, StrengthPower=2 |
| ShrugItOff | 1 | Skill | Common | Self | Block=8 |
| Spite | 0 | Attack | Uncommon | AnyEnemy | Damage=5 |
| Stampede | 2 | Power | Uncommon | Self |  |
| Stoke | 1 | Skill | Rare | Self |  |
| Stomp | 3 | Attack | Uncommon | AllEnemies | Damage=12 |
| StoneArmor | 1 | Power | Uncommon | Self | PlatingPower=4 |
| StrikeIronclad | 1 | Attack | Basic | AnyEnemy | Damage=6 |
| SwordBoomerang | 1 | Attack | Common | RandomEnemy | Damage=3 |
| Tank | 1 | Power | Rare | Self |  |
| Taunt | 1 | Skill | Uncommon | AnyEnemy | Block=7, VulnerablePower=1 |
| TearAsunder | 2 | Attack | Rare | AnyEnemy | Damage=5 |
| Thrash | 1 | Attack | Rare | AnyEnemy | Damage=4 |
| Thunderclap | 1 | Attack | Common | AllEnemies | Damage=4, VulnerablePower=1 |
| Tremble | 1 | Skill | Common | AnyEnemy | VulnerablePower=3 |
| TrueGrit | 1 | Skill | Common | Self | Block=7 |
| TwinStrike | 1 | Attack | Common | AnyEnemy | Damage=5 |
| Unmovable | 2 | Power | Rare | Self |  |
| Unrelenting | 2 | Attack | Uncommon | AnyEnemy | Damage=14 |
| Uppercut | 2 | Attack | Uncommon | AnyEnemy | Damage=13 |
| Vicious | 1 | Power | Uncommon | Self |  |
| Whirlwind | 0 | Attack | Uncommon | AllEnemies | Damage=5 |

## necrobinder (88)
| id | cost | type | rarity | target | vars |
| --- | ---: | --- | --- | --- | --- |
| Afterlife | 1 | Skill | Common | Self |  |
| BansheesCry | 9 | Attack | Rare | AllEnemies | Damage=33 |
| BlightStrike | 1 | Attack | Common | AnyEnemy | Damage=8 |
| Bodyguard | 1 | Skill | Basic | Self |  |
| BoneShards | 1 | Attack | Uncommon | AllEnemies | Block=9 |
| BorrowedTime | 1 | Skill | Uncommon | Self |  |
| Bury | 4 | Attack | Uncommon | AnyEnemy | Damage=52 |
| Calcify | 1 | Power | Uncommon | Self | CalcifyPower=4 |
| CallOfTheVoid | 1 | Power | Rare | Self |  |
| CaptureSpirit | 1 | Skill | Uncommon | AnyEnemy | Damage=3 |
| Cleanse | 1 | Skill | Uncommon | Self |  |
| Countdown | 1 | Power | Uncommon | Self | CountdownPower=6 |
| DanseMacabre | 1 | Power | Uncommon | Self | DanseMacabrePower=4 |
| DeathMarch | 1 | Attack | Uncommon | AnyEnemy |  |
| Deathbringer | 2 | Skill | Uncommon | AllEnemies | DoomPower=21, WeakPower=1 |
| DeathsDoor | 1 | Skill | Uncommon | Self | Block=6 |
| Debilitate | 1 | Attack | Uncommon | AnyEnemy | Damage=10, DebilitatePower=2 |
| DefendNecrobinder | 1 | Skill | Basic | Self | Block=5 |
| Defile | 1 | Attack | Common | AnyEnemy | Damage=13 |
| Defy | 1 | Skill | Common | AnyEnemy | Block=6, WeakPower=1 |
| Delay | 2 | Skill | Uncommon | Self | Block=11 |
| Demesne | 3 | Power | Rare | Self |  |
| DevourLife | 1 | Power | Rare | Self | DevourLifePower=1 |
| Dirge | 0 | Skill | Uncommon | Self |  |
| DrainPower | 1 | Attack | Common | AnyEnemy | Damage=10 |
| Dredge | 1 | Skill | Uncommon | Self |  |
| Eidolon | 2 | Skill | Rare | Self |  |
| EndOfDays | 3 | Skill | Rare | AllEnemies | DoomPower=29 |
| EnfeeblingTouch | 1 | Skill | Uncommon | AnyEnemy |  |
| Eradicate | 0 | Attack | Rare | AnyEnemy | Damage=11 |
| Fear | 1 | Attack | Common | AnyEnemy | Damage=7, VulnerablePower=1 |
| Fetch | 0 | Attack | Uncommon | AnyEnemy |  |
| Flatten | 2 | Attack | Common | AnyEnemy |  |
| ForbiddenGrimoire | 2 | Power | Ancient | Self |  |
| Friendship | 1 | Power | Uncommon | Self | StrengthPower=2 |
| GlimpseBeyond | 1 | Skill | Rare | AllAllies |  |
| GraveWarden | 1 | Skill | Common | Self | Block=8 |
| Graveblast | 1 | Attack | Common | AnyEnemy | Damage=4 |
| Hang | 1 | Attack | Rare | AnyEnemy | Damage=10 |
| Haunt | 1 | Power | Uncommon | Self |  |
| HighFive | 2 | Attack | Uncommon | AllEnemies | VulnerablePower=2 |
| Invoke | 1 | Skill | Common | Self |  |
| LegionOfBone | 2 | Skill | Uncommon | AllAllies |  |
| Lethality | 1 | Power | Uncommon | Self | LethalityPower=50 |
| Melancholy | 3 | Skill | Uncommon | Self | Block=13 |
| Misery | 0 | Attack | Rare | AnyEnemy | Damage=7 |
| NecroMastery | 2 | Power | Rare | Self |  |
| NegativePulse | 1 | Skill | Common | AllEnemies | Block=5, DoomPower=7 |
| Neurosurge | 0 | Power | Rare | Self | NeurosurgePower=3 |
| NoEscape | 1 | Skill | Uncommon | AnyEnemy |  |
| Oblivion | 0 | Skill | Rare | AnyEnemy | DoomPower=3 |
| Pagestorm | 1 | Power | Uncommon | Self |  |
| Parse | 1 | Skill | Uncommon | Self |  |
| Poke | 0 | Attack | Common | AnyEnemy |  |
| Protector | 1 | Attack | Ancient | AnyEnemy |  |
| PullAggro | 2 | Skill | Common | Self | Block=7 |
| PullFromBelow | 1 | Attack | Uncommon | AnyEnemy | Damage=5 |
| Putrefy | 1 | Skill | Uncommon | AnyEnemy |  |
| Rattle | 1 | Attack | Uncommon | AnyEnemy |  |
| Reanimate | 3 | Skill | Rare | Self |  |
| Reap | 3 | Attack | Common | AnyEnemy | Damage=27 |
| ReaperForm | 3 | Power | Rare | Self |  |
| Reave | 1 | Attack | Common | AnyEnemy | Damage=9 |
| RightHandHand | 0 | Attack | Uncommon | AnyEnemy |  |
| Sacrifice | 1 | Skill | Rare | Self |  |
| Scourge | 1 | Skill | Common | AnyEnemy | DoomPower=13 |
| SculptingStrike | 1 | Attack | Common | AnyEnemy | Damage=9 |
| Seance | 1 | Skill | Rare | Self |  |
| SentryMode | 2 | Power | Rare | Self | SentryModePower=1 |
| Severance | 2 | Attack | Uncommon | AnyEnemy | Damage=13 |
| SharedFate | 0 | Skill | Rare | AnyEnemy |  |
| Shroud | 1 | Power | Uncommon | Self | Block=2 |
| SicEm | 1 | Attack | Uncommon | AnyEnemy | SicEmPower=3 |
| SleightOfFlesh | 2 | Power | Uncommon | Self | SleightOfFleshPower=9 |
| Snap | 1 | Attack | Common | AnyEnemy |  |
| SoulStorm | 1 | Attack | Rare | AnyEnemy |  |
| Sow | 1 | Attack | Common | AllEnemies | Damage=8 |
| SpiritOfAsh | 1 | Power | Rare | Self |  |
| Spur | 1 | Skill | Uncommon | Self |  |
| Squeeze | 3 | Attack | Rare | AnyEnemy |  |
| StrikeNecrobinder | 1 | Attack | Basic | AnyEnemy | Damage=6 |
| TheScythe | 2 | Attack | Rare | AnyEnemy |  |
| TimesUp | 2 | Attack | Rare | AnyEnemy |  |
| Transfigure | 1 | Skill | Rare | Self |  |
| Undeath | 0 | Skill | Rare | Self | Block=7 |
| Unleash | 1 | Attack | Basic | AnyEnemy |  |
| Veilpiercer | 1 | Attack | Uncommon | AnyEnemy | Damage=10 |
| Wisp | 0 | Skill | Common | Self |  |

## quest (3)
| id | cost | type | rarity | target | vars |
| --- | ---: | --- | --- | --- | --- |
| ByrdonisEgg | -1 | Quest | Quest | None |  |
| LanternKey | -1 | Quest | Quest | Self |  |
| SpoilsMap | -1 | Quest | Quest | Self |  |

## regent (88)
| id | cost | type | rarity | target | vars |
| --- | ---: | --- | --- | --- | --- |
| Alignment | 0 | Skill | Uncommon | Self |  |
| Arsenal | 1 | Power | Rare | Self | ArsenalPower=1 |
| AstralPulse | 0 | Attack | Common | AllEnemies | Damage=6 |
| BeatIntoShape | 1 | Attack | Rare | AnyEnemy | Damage=5 |
| Begone | 1 | Skill | Common | Self |  |
| BigBang | 0 | Skill | Rare | Self |  |
| BlackHole | 1 | Power | Uncommon | Self | BlackHolePower=3 |
| Bombardment | 3 | Attack | Rare | AnyEnemy | Damage=18 |
| Bulwark | 2 | Skill | Uncommon | Self | Block=12 |
| BundleOfJoy | 1 | Skill | Rare | Self |  |
| CelestialMight | 2 | Attack | Common | AnyEnemy | Damage=6 |
| Charge | 1 | Skill | Uncommon | Self |  |
| ChildOfTheStars | 1 | Power | Uncommon | Self |  |
| CloakOfStars | 0 | Skill | Common | Self | Block=7 |
| CollisionCourse | 0 | Attack | Common | AnyEnemy | Damage=11 |
| Comet | 0 | Attack | Rare | AnyEnemy | Damage=33, VulnerablePower=3, WeakPower=3 |
| Conqueror | 1 | Skill | Uncommon | AnyEnemy |  |
| Convergence | 1 | Skill | Uncommon | Self |  |
| CosmicIndifference | 1 | Skill | Common | Self | Block=6 |
| CrashLanding | 1 | Attack | Rare | AllEnemies | Damage=21 |
| CrescentSpear | 1 | Attack | Common | AnyEnemy |  |
| CrushUnder | 1 | Attack | Common | AllEnemies | Damage=7 |
| DecisionsDecisions | 0 | Skill | Rare | Self |  |
| DefendRegent | 1 | Skill | Basic | Self | Block=5 |
| Devastate | 1 | Attack | Uncommon | AnyEnemy | Damage=30 |
| DyingStar | 1 | Attack | Rare | AllEnemies | Damage=9 |
| FallingStar | 0 | Attack | Basic | AnyEnemy | Damage=8, VulnerablePower=1, WeakPower=1 |
| ForegoneConclusion | 1 | Skill | Rare | Self |  |
| Furnace | 1 | Power | Uncommon | Self |  |
| GammaBlast | 0 | Attack | Uncommon | AnyEnemy | Damage=13, VulnerablePower=2, WeakPower=2 |
| GatherLight | 1 | Skill | Common | Self | Block=8 |
| Genesis | 2 | Power | Rare | Self |  |
| Glimmer | 1 | Skill | Uncommon | Self |  |
| Glitterstream | 2 | Skill | Common | Self | Block=11 |
| Glow | 1 | Skill | Common | Self |  |
| Guards | 2 | Skill | Rare | Self |  |
| GuidingStar | 1 | Attack | Common | AnyEnemy | Damage=12 |
| HammerTime | 2 | Power | Rare | Self |  |
| HeavenlyDrill | 0 | Attack | Rare | AnyEnemy | Damage=8 |
| Hegemony | 2 | Attack | Uncommon | AnyEnemy | Damage=15 |
| HeirloomHammer | 2 | Attack | Rare | AnyEnemy | Damage=20 |
| HiddenCache | 1 | Skill | Common | Self | StarNextTurnPower=3 |
| IAmInvincible | 1 | Skill | Rare | Self | Block=10 |
| KinglyKick | 4 | Attack | Uncommon | AnyEnemy | Damage=27 |
| KinglyPunch | 1 | Attack | Uncommon | AnyEnemy | Damage=8 |
| KnockoutBlow | 3 | Attack | Uncommon | AnyEnemy | Damage=30 |
| KnowThyPlace | 0 | Skill | Common | AnyEnemy | WeakPower=1, VulnerablePower=1 |
| Largesse | 0 | Skill | Uncommon | AnyAlly |  |
| LunarBlast | 0 | Attack | Uncommon | AnyEnemy | Damage=4 |
| MakeItSo | 0 | Attack | Rare | AnyEnemy | Damage=6 |
| ManifestAuthority | 1 | Skill | Uncommon | Self | Block=7 |
| MeteorShower | 0 | Attack | Ancient | AllEnemies | Damage=14, VulnerablePower=2, WeakPower=2 |
| MonarchsGaze | 2 | Power | Rare | Self |  |
| Monologue | 0 | Skill | Uncommon | Self |  |
| NeutronAegis | 1 | Power | Rare | Self | PlatingPower=8 |
| Orbit | 2 | Power | Uncommon | Self |  |
| PaleBlueDot | 1 | Power | Uncommon | Self |  |
| Parry | 1 | Power | Uncommon | Self | ParryPower=10 |
| ParticleWall | 0 | Skill | Uncommon | Self | Block=9 |
| Patter | 1 | Skill | Common | Self | Block=8, VigorPower=2 |
| PhotonCut | 1 | Attack | Common | AnyEnemy | Damage=10 |
| PillarOfCreation | 1 | Power | Uncommon | Self | Block=3 |
| Prophesize | 2 | Skill | Uncommon | Self |  |
| Quasar | 0 | Skill | Uncommon | Self |  |
| Radiate | 0 | Attack | Uncommon | AllEnemies | Damage=3 |
| RefineBlade | 1 | Skill | Common | Self |  |
| Reflect | 1 | Skill | Uncommon | Self | Block=15 |
| Resonance | 1 | Skill | Uncommon | AllEnemies | StrengthPower=1 |
| RoyalGamble | 0 | Skill | Uncommon | Self |  |
| Royalties | 1 | Power | Rare | Self |  |
| SeekingEdge | 1 | Power | Rare | Self |  |
| SevenStars | 2 | Attack | Rare | AllEnemies | Damage=7 |
| ShiningStrike | 1 | Attack | Uncommon | AnyEnemy | Damage=8 |
| SolarStrike | 1 | Attack | Common | AnyEnemy | Damage=9 |
| SpectrumShift | 2 | Power | Uncommon | Self |  |
| SpoilsOfBattle | 1 | Skill | Common | Self |  |
| Stardust | 0 | Attack | Uncommon | RandomEnemy | Damage=5 |
| StrikeRegent | 1 | Attack | Basic | AnyEnemy | Damage=6 |
| SummonForth | 1 | Skill | Uncommon | Self |  |
| Supermassive | 1 | Attack | Uncommon | AnyEnemy |  |
| SwordSage | 2 | Power | Rare | Self | SwordSagePower=1 |
| Terraforming | 1 | Skill | Uncommon | Self | VigorPower=6 |
| TheSealedThrone | 1 | Power | Ancient | Self |  |
| TheSmith | 1 | Skill | Rare | Self |  |
| Tyranny | 1 | Power | Rare | Self |  |
| Venerate | 1 | Skill | Basic | Self |  |
| VoidForm | 3 | Power | Rare | Self | VoidFormPower=2 |
| WroughtInWar | 1 | Attack | Common | AnyEnemy | Damage=7 |

## silent (88)
| id | cost | type | rarity | target | vars |
| --- | ---: | --- | --- | --- | --- |
| Abrasive | 3 | Power | Rare | Self | ThornsPower=4, DexterityPower=1 |
| Accelerant | 1 | Power | Rare | Self |  |
| Accuracy | 1 | Power | Uncommon | Self | AccuracyPower=4 |
| Acrobatics | 1 | Skill | Uncommon | Self |  |
| Adrenaline | 0 | Skill | Rare | Self |  |
| Afterimage | 1 | Power | Rare | Self | AfterimagePower=1 |
| Anticipate | 0 | Skill | Common | Self | DexterityPower=2 |
| Assassinate | 0 | Attack | Rare | AnyEnemy | Damage=10, VulnerablePower=1 |
| Backflip | 1 | Skill | Common | Self | Block=5 |
| Backstab | 0 | Attack | Uncommon | AnyEnemy | Damage=11 |
| BladeDance | 1 | Skill | Common | Self |  |
| BladeOfInk | 1 | Skill | Rare | Self |  |
| Blur | 1 | Skill | Uncommon | Self | Block=5 |
| BouncingFlask | 2 | Skill | Uncommon | RandomEnemy | PoisonPower=3 |
| BubbleBubble | 1 | Skill | Uncommon | AnyEnemy | PoisonPower=9 |
| BulletTime | 3 | Skill | Rare | Self |  |
| Burst | 1 | Skill | Rare | Self |  |
| CalculatedGamble | 0 | Skill | Uncommon | Self |  |
| CloakAndDagger | 1 | Skill | Common | Self | Block=6 |
| CorrosiveWave | 1 | Skill | Rare | Self |  |
| DaggerSpray | 1 | Attack | Common | AllEnemies | Damage=4 |
| DaggerThrow | 1 | Attack | Common | AnyEnemy | Damage=9 |
| Dash | 2 | Attack | Uncommon | AnyEnemy | Damage=10, Block=10 |
| DeadlyPoison | 1 | Skill | Common | AnyEnemy | PoisonPower=5 |
| DefendSilent | 1 | Skill | Basic | Self | Block=5 |
| Deflect | 0 | Skill | Common | Self | Block=4 |
| DodgeAndRoll | 1 | Skill | Common | Self | Block=4 |
| EchoingSlash | 1 | Attack | Rare | AllEnemies | Damage=10 |
| Envenom | 2 | Power | Rare | Self | EnvenomPower=1 |
| EscapePlan | 0 | Skill | Uncommon | Self | Block=3 |
| Expertise | 1 | Skill | Uncommon | Self |  |
| Expose | 0 | Skill | Uncommon | AnyEnemy |  |
| FanOfKnives | 2 | Power | Rare | Self |  |
| Finisher | 1 | Attack | Uncommon | AnyEnemy | Damage=6 |
| Flanking | 2 | Skill | Uncommon | AnyEnemy |  |
| Flechettes | 1 | Attack | Uncommon | AnyEnemy | Damage=5 |
| FlickFlack | 1 | Attack | Common | AllEnemies | Damage=6 |
| Footwork | 1 | Power | Uncommon | Self | DexterityPower=2 |
| GrandFinale | 0 | Attack | Rare | AllEnemies | Damage=60 |
| HandTrick | 1 | Skill | Uncommon | Self | Block=7 |
| Haze | 3 | Skill | Uncommon | AllEnemies | PoisonPower=4 |
| HiddenDaggers | 0 | Skill | Uncommon | Self |  |
| InfiniteBlades | 1 | Power | Uncommon | Self |  |
| KnifeTrap | 2 | Skill | Rare | AnyEnemy |  |
| LeadingStrike | 1 | Attack | Common | AnyEnemy | Damage=3 |
| LegSweep | 2 | Skill | Uncommon | AnyEnemy | Block=11, WeakPower=2 |
| Malaise | 0 | Skill | Rare | AnyEnemy |  |
| MasterPlanner | 2 | Power | Rare | Self |  |
| MementoMori | 1 | Attack | Uncommon | AnyEnemy |  |
| Mirage | 1 | Skill | Uncommon | Self |  |
| Murder | 3 | Attack | Rare | AnyEnemy |  |
| Neutralize | 0 | Attack | Basic | AnyEnemy | Damage=3, WeakPower=1 |
| Nightmare | 3 | Skill | Rare | Self |  |
| NoxiousFumes | 1 | Power | Uncommon | Self |  |
| Outbreak | 1 | Power | Uncommon | Self | OutbreakPower=11 |
| PhantomBlades | 1 | Power | Uncommon | Self | PhantomBladesPower=9 |
| PiercingWail | 1 | Skill | Common | AllEnemies |  |
| Pinpoint | 3 | Attack | Uncommon | AnyEnemy | Damage=15 |
| PoisonedStab | 1 | Attack | Common | AnyEnemy | Damage=6, PoisonPower=3 |
| Pounce | 2 | Attack | Uncommon | AnyEnemy | Damage=14 |
| PreciseCut | 0 | Attack | Uncommon | AnyEnemy |  |
| Predator | 2 | Attack | Common | AnyEnemy | Damage=15 |
| Prepared | 0 | Skill | Common | Self |  |
| Reflex | 3 | Skill | Uncommon | Self |  |
| Ricochet | 2 | Attack | Common | RandomEnemy | Damage=3 |
| Scare | 0 | Skill | Uncommon | AllEnemies |  |
| SerpentForm | 3 | Power | Rare | Self | SerpentFormPower=4 |
| ShadowStep | 1 | Skill | Rare | Self |  |
| Shadowmeld | 1 | Skill | Rare | Self |  |
| Skewer | 0 | Attack | Uncommon | AnyEnemy | Damage=8 |
| Slice | 0 | Attack | Common | AnyEnemy | Damage=6 |
| Snakebite | 2 | Skill | Common | AnyEnemy | PoisonPower=7 |
| Sneaky | 2 | Power | Rare | Self | SneakyPower=1 |
| Speedster | 2 | Power | Uncommon | Self | SpeedsterPower=2 |
| StormOfSteel | 1 | Skill | Rare | Self |  |
| Strangle | 1 | Attack | Uncommon | AnyEnemy | Damage=8, StranglePower=2 |
| StrikeSilent | 1 | Attack | Basic | AnyEnemy | Damage=6 |
| SuckerPunch | 1 | Attack | Common | AnyEnemy | Damage=8, WeakPower=1 |
| Suppress | 0 | Attack | Ancient | AnyEnemy | Damage=11, WeakPower=3 |
| Survivor | 1 | Skill | Basic | Self | Block=8 |
| Tactician | 3 | Skill | Uncommon | Self |  |
| TheHunt | 1 | Attack | Rare | AnyEnemy | Damage=10 |
| ToolsOfTheTrade | 1 | Power | Rare | Self |  |
| Tracking | 2 | Power | Rare | Self |  |
| Untouchable | 2 | Skill | Common | Self | Block=6 |
| UpMySleeve | 2 | Skill | Uncommon | Self |  |
| WellLaidPlans | 1 | Power | Uncommon | Self |  |
| WraithForm | 3 | Power | Ancient | Self | IntangiblePower=2, WraithFormPower=1 |

## status (12)
| id | cost | type | rarity | target | vars |
| --- | ---: | --- | --- | --- | --- |
| Beckon | 1 | Status | Status | None |  |
| Burn | -1 | Status | Status | None | Damage=2 |
| Dazed | -1 | Status | Status | None |  |
| Debris | 1 | Status | Status | None |  |
| FranticEscape | 1 | Status | Status | Self |  |
| Infection | -1 | Status | Status | None | Damage=3 |
| Slimed | 1 | Status | Status | None |  |
| Soot | -1 | Status | Status | None |  |
| Toxic | 1 | Status | Status | None | Damage=5 |
| Void | -1 | Status | Status | None |  |
| Wither | -1 | Status | Status | None | Damage=3 |
| Wound | -1 | Status | Status | None |  |

## token (13)
| id | cost | type | rarity | target | vars |
| --- | ---: | --- | --- | --- | --- |
| Disintegration | -1 | Status | Status | None | DisintegrationPower=6 |
| Fuel | 0 | Skill | Token | Self |  |
| GiantRock | 1 | Attack | Token | AnyEnemy | Damage=16 |
| Luminesce | 0 | Skill | Token | Self |  |
| MindRot | -1 | Status | Status | None | MindRotPower=1 |
| MinionDiveBomb | 0 | Attack | Token | AnyEnemy | Damage=13 |
| MinionSacrifice | 0 | Skill | Token | Self | Block=8 |
| MinionStrike | 0 | Attack | Token | AnyEnemy | Damage=6 |
| Shiv | 0 | Attack | Token | AnyEnemy | Damage=4 |
| Sloth | -1 | Status | Status | None | SlothPower=3 |
| Soul | 0 | Skill | Token | Self |  |
| SovereignBlade | 2 | Attack | Token | AnyEnemy | Damage=10 |
| WasteAway | -1 | Status | Status | None | WasteAwayPower=1 |
