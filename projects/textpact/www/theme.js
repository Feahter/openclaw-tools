/**
 * 深渊迷城主题包
 * 从 theme.yaml 转换而来
 */

const abyssTheme = {
    name: "深渊迷城",
    description: "被困在深渊城市的探险者，寻找真相与出口",
    setting: `你是一名探险者，在一次意外中掉入了深渊迷城。
这座城市被遗忘，充满的危险与机遇。
只有找到传说中的"光之门"，才能逃出这里。`,
    mood: "孤独/神秘/危险",
    
    initial_state: {
        contract_energy: 100,
        location: "abyss_entrance",
        inventory: [],
        knowledge: ["basic_actions"]
    },
    
    rooms: [
        {
            id: "abyss_entrance",
            name: "深渊入口",
            description: "你站在深渊的入口处，巨大的石门半开半合，门后传来阵阵寒意。墙壁上刻着古老的文字，似乎在警告着什么。",
            connections: { north: "dark_corridor" },
            events: [],
            fossils: [],
            danger_level: 1
        },
        {
            id: "dark_corridor",
            name: "黑暗走廊",
            description: "一条狭长的走廊，墙壁上长满发光的苔藓。空气中弥漫着腐朽的气息。你注意到地上有一些散落的契约碎片。",
            connections: { south: "abyss_entrance", east: "ancient_square", north: "forbidden_chamber" },
            events: [
                { type: "discovery", description: "契约碎片", reward: 10 }
            ],
            fossils: [],
            danger_level: 2
        },
        {
            id: "ancient_square",
            name: "古老广场",
            description: "一个巨大的圆形广场，中心矗立着一座破损的雕像。四周布满废墟，看起来曾经是个繁华的地方。",
            connections: { west: "dark_corridor", north: "merchant_cave" },
            events: [
                { 
                    type: "random", 
                    possibilities: [
                        { weight: 10, description: "一切平静" },
                        { weight: 3, description: "发现商人", action: "trade" },
                        { weight: 1, description: "遭遇阴影怪物", action: "combat" }
                    ]
                }
            ],
            fossils: [],
            danger_level: 2
        },
        {
            id: "merchant_cave",
            name: "商人洞穴",
            description: "一个隐蔽的洞穴，里面住着一位神秘的商人。他可以与你交易各种物品。",
            connections: { south: "ancient_square" },
            events: [
                { 
                    type: "trade",
                    items: [
                        { name: "契约符石", price: 30, description: "增加契约力" },
                        { name: "光明火把", price: 50, description: "照亮黑暗" }
                    ]
                }
            ],
            fossils: [],
            danger_level: 1
        },
        {
            id: "forbidden_chamber",
            name: "禁忌密室",
            description: "你推开一扇沉重的石门，进入了一间布满灰尘的密室。空气中有着不祥的气息...",
            connections: { south: "dark_corridor", east: "treasure_vault", north: "gate_of_light" },
            events: [
                {
                    type: "fossil_choice",
                    description: "密室中的选择",
                    choices: [
                        { text: "仔细搜索", fossil: "searched_forbidden", energy_cost: 20 },
                        { text: "快速离开", fossil: "fled_forbidden", energy_cost: 5 }
                    ]
                }
            ],
            fossils: [],
            danger_level: 5
        },
        {
            id: "treasure_vault",
            name: "宝藏库",
            description: "一间堆满宝物的密室，金光闪闪。但你注意到警戒机关仍然有效...",
            connections: { west: "forbidden_chamber" },
            events: [
                { type: "risk_reward", description: "宝藏与危险", reward: 50, danger: 5 }
            ],
            fossils: [],
            danger_level: 4
        },
        {
            id: "gate_of_light",
            name: "光之门",
            description: "传说中的光之门！门上散发着柔和的光芒，似乎在召唤着你。这是离开深渊的唯一途径...",
            connections: { south: "forbidden_chamber" },
            events: [
                { type: "final", description: "光之门挑战" }
            ],
            fossils: [],
            danger_level: 3
        }
    ],
    
    actions: {
        basic: [
            { name: "探索", keywords: ["探索", "search", "look"], cost: 5, description: "仔细查看当前房间" },
            { name: "移动", keywords: ["north", "south", "east", "west", "北", "南", "东", "西", "去", "走"], cost: 3, description: "移动到相邻房间" },
            { name: "休息", keywords: ["休息", "rest", "sleep"], cost: 0, description: "恢复契约力", effect: "energy_regen" }
        ],
        advanced: [
            { name: "收集", keywords: ["收集", "collect", "拿", "take"], cost: 10, description: "收集房间中的物品" },
            { name: "祈祷", keywords: ["祈祷", "pray", "祈求"], cost: 20, description: "向深渊祈祷，可能获得回应" },
            { name: "创造", keywords: ["创造", "create", "建造"], cost: 30, description: "创造新房间" }
        ]
    }
};
