/**
 * TextPact 游戏引擎核心 v0.6
 * 包含战斗系统 + 交易系统 + 化石系统 + 成就系统
 */

class TextPactEngine {
    constructor(theme) {
        this.theme = theme;
        this.state = this.createInitialState();
        this.logs = [];
    }

    createInitialState() {
        return {
            bubble_id: this.generateUUID(),
            parent_bubble: null,
            player: "探险者",
            contract_energy: this.theme.initial_state.contract_energy,
            gold: this.theme.initial_state.gold || 100,  // 金币系统
            location: this.theme.initial_state.location,
            inventory: [...this.theme.initial_state.inventory],
            knowledge: [...this.theme.initial_state.knowledge],
            fossils: [],
            explored_rooms: new Set(),
            turn_count: 0,
            combat: null,  // 战斗状态
            shop: null,    // 商店状态
            achievements: [],  // 成就系统
            // 动作冷却时间（回合制）
            action_cooldowns: {
                collect: 0,
                pray: 0,
                create: 0,
                explore: 0
            },
            // 连续幸运/不幸计数
            luck_counter: 0,
            stats: {
                battles_won: 0,
                rooms_explored: 0,
                fossils_created: 0,
                total_gold_earned: 0,
                items_collected: 0,
                biggest_win: 0
            }
        };
    }

    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    // 获取当前房间
    getCurrentRoom() {
        return this.theme.rooms.find(r => r.id === this.state.location);
    }

    // 是否在战斗中
    isInCombat() {
        return this.state.combat !== null;
    }

    // 更新冷却时间
    updateCooldowns() {
        const cooldowns = this.state.action_cooldowns;
        for (const key in cooldowns) {
            if (cooldowns[key] > 0) {
                cooldowns[key]--;
            }
        }
    }
    
    // 获取冷却状态文本
    getCooldownStatus() {
        const cd = this.state.action_cooldowns;
        const ready = [];
        const waiting = [];
        
        if (cd.collect <= 0) ready.push("收集");
        else waiting.push(`收集(${cd.collect})`);
        
        if (cd.pray <= 0) ready.push("祈祷");
        else waiting.push(`祈祷(${cd.pray})`);
        
        if (cd.create <= 0) ready.push("创造");
        else waiting.push(`创造(${cd.create})`);
        
        if (cd.explore <= 0) ready.push("探索");
        else waiting.push(`探索(${cd.explore})`);
        
        return { ready, waiting };
    }
    
    // 获取完整状态（供前端使用）
    getStatus() {
        const room = this.getCurrentRoom();
        return {
            energy: this.state.contract_energy,
            gold: this.state.gold,
            location: room ? room.name : '未知',
            fossils: this.state.fossils.length,
            turns: this.state.turn_count,
            inventory: this.state.inventory,
            enemy: this.state.combat ? this.state.combat.enemy.name : null,
            enemyHp: this.state.combat ? `${this.state.combat.enemy.hp}/${this.state.combat.enemy.maxHp}` : null,
            cooldowns: this.getCooldownStatus()
        };
    }

    // 处理玩家输入
    processAction(input) {
        const action = input.trim().toLowerCase();
        this.state.turn_count++;
        
        // 更新行动统计并检查成就
        this.updateStatsAndCheckAchievements('turn');
        
        // 更新动作冷却
        this.updateCooldowns();
        
        let result = null;

        // 战斗状态优先处理战斗指令
        if (this.isInCombat()) {
            if (this.isCombatAction(action)) {
                result = this.handleCombatAction(action);
            } else if (action.includes('逃跑') || action.includes('run') || action.includes('逃')) {
                result = this.handleCombatRun();
            } else {
                result = {
                    type: 'combat_info',
                    message: `⚔️ 战斗中！\n\n敌人: ${this.state.combat.enemy.name}\n生命: ${this.state.combat.enemy.hp}/${this.state.combat.enemy.maxHp}\n\n指令: 攻击 / 防御 / 必杀 / 逃跑`,
                    energy: 0
                };
            }
            this.logAction(input, result);
            return result;
        }

        // 1. 检查是否是背包相关
        if (this.isInventory(action)) {
            result = this.handleInventory();
        }
        // 2. 检查使用物品
        else if (this.isUseItem(action)) {
            const itemName = action.replace(/使用|use|喝|吃|用/g, '').trim();
            result = this.handleUseItem(itemName);
        }
        // 3. 检查丢弃物品
        else if (this.isDropItem(action)) {
            const itemName = action.replace(/丢弃|drop|扔/g, '').trim();
            result = this.handleDropItem(itemName);
        }
        // 4. 检查是否是移动
        else if (this.isMovement(action)) {
            result = this.handleMovement(action);
        }
        // 5. 检查是否是探索
        else if (this.isExplore(action)) {
            result = this.handleExplore();
        }
        // 6. 检查是否是休息
        else if (this.isRest(action)) {
            result = this.handleRest();
        }
        // 7. 检查是否是收集
        else if (this.isCollect(action)) {
            result = this.handleCollect();
        }
        // 8. 检查是否是祈祷
        else if (this.isPray(action)) {
            result = this.handlePray();
        }
        // 9. 检查是否是创造
        else if (this.isCreate(action)) {
            result = this.handleCreate();
        }
        // 10. 检查是否遭遇敌人
        else if (this.isTriggerCombat(action)) {
            result = this.handleTriggerCombat();
        }
        // 11. 检查是否进入商店
        else if (this.isShop(action)) {
            const npcName = action.replace(/商店|shop|买|交易|商人/g, '').trim();
            result = this.handleShop(npcName);
        }
        // 12. 商店内购买
        else if ((action.includes('购买') || action.includes('买') || action.includes('buy')) && this.state.shop) {
            const itemIndex = action.replace(/购买|买|buy/g, '').trim();
            result = this.handleBuy(itemIndex);
        }
        // 13. 商店内出售
        else if ((action.includes('出售') || action.includes('卖') || action.includes('sell')) && this.state.shop) {
            const itemName = action.replace(/出售|卖|sell/g, '').trim();
            result = this.handleSell(itemName);
        }
        // 14. 离开商店
        else if ((action.includes('离开') || action.includes('exit') || action.includes('quit')) && this.state.shop) {
            result = this.handleLeaveShop();
        }
        // 15. 查看化石
        else if (this.isFossilList(action)) {
            result = this.handleListFossils();
        }
        // 16. 回应化石
        else if (this.isFossilRespond(action)) {
            const match = action.match(/回应|respond|评论|comment(\d+)?/);
            const fossilIndex = match && match[1] ? parseInt(match[1]) - 1 : 0;
            const responseText = action.replace(/回应|respond|评论|comment/g, '').trim();
            result = this.handleFossilRespond(fossilIndex, responseText);
        }
        // 17. 共鸣化石
        else if (this.isFossilResonate(action)) {
            const fossilIndex = action.match(/\d+/)?.[0] || '1';
            result = this.handleFossilResonate(parseInt(fossilIndex) - 1);
        }
        // 18. 查看成就
        else if (this.isAchievement(action)) {
            result = this.handleAchievements();
        }
        // 19. 默认：未知行动
        else {
            result = this.handleUnknown(action);
        }

        // 记录日志
        this.logAction(input, result);
        
        return result;
    }

    // ==================== 物品系统 ====================
    
    // 物品模板（类属性）
    items = {
        "contract_potion": {
            name: "契约药水",
            type: "consumable",
            description: "散发蓝色荧光的药水，能恢复契约力",
            effect: { energy: 30 },
            usable: true
        },
        "power_elixir": {
            name: "力量之酒",
            type: "consumable",
            description: "辛辣的红色液体，能短暂提升攻击力",
            effect: { attack_boost: 5, duration: 3 },
            usable: true
        },
        "defense_charm": {
            name: "防御护符",
            type: "consumable",
            description: "刻有古老符文的护符，能减少伤害",
            effect: { defense_boost: 3, duration: 3 },
            usable: true
        },
        "mystic_key": {
            name: "神秘钥匙",
            type: "key",
            description: "一把古老的钥匙，似乎能打开某些门",
            effect: {},
            usable: false
        },
        "ancient_coin": {
            name: "古老硬币",
            type: "treasure",
            description: "一枚刻有神秘符号的硬币",
            effect: {},
            usable: false,
            value: 50
        },
        "shadow_orb": {
            name: "暗影宝珠",
            type: "rare",
            description: "蕴含深渊力量的宝珠",
            effect: { energy: 50 },
            usable: true
        }
    };

    // 物品掉落概率表
    itemDropTable = [
        { item: "contract_potion", weight: 30 },
        { item: "ancient_coin", weight: 25 },
        { item: "power_elixir", weight: 15 },
        { item: "defense_charm", weight: 15 },
        { item: "mystic_key", weight: 10 },
        { item: "shadow_orb", weight: 5 }
    ];

    // 判断是否是背包相关指令
    isInventory(action) {
        return action.includes('背包') || action.includes('背包') || action.includes('inventory') || 
               action.includes('物品') || action.includes('背包') || action === 'i';
    }
        // 判断使用物品
    isUseItem(action) {
        return action.includes('使用') || action.includes('use') || action.includes('喝') || 
               action.includes('吃') || action.includes('用');
    }
        // 判断丢弃物品
    isDropItem(action) {
        return action.includes('丢弃') || action.includes('drop') || action.includes('扔');
    }
        // 处理背包查看
    handleInventory() {
        const inventory = this.state.inventory || [];
        
        if (inventory.length === 0) {
            return {
                type: 'inventory',
                message: `🎒 背包\n\n你的背包空空如也...`,
                energy: 0
            };
        }

        let message = `🎒 背包\n\n`;
        let itemList = [];
        
        for (let i = 0; i < inventory.length; i++) {
            const itemId = inventory[i];
            const item = this.items[itemId];
            if (item) {
                itemList.push(`${i + 1}. ${item.name} - ${item.description}`);
            }
        }
        
        message += itemList.join('\n\n');
        message += `\n\n💡 使用物品: "使用 [物品名]"`;

        return {
            type: 'inventory',
            message: message,
            energy: 0,
            inventory: inventory
        };
    }
        // 处理使用物品
    handleUseItem(itemName) {
        const inventory = this.state.inventory || [];
        
        // 查找匹配的物品
        let itemIndex = -1;
        let matchedItem = null;
        
        for (let i = 0; i < inventory.length; i++) {
            const itemId = inventory[i];
            const item = this.items[itemId];
            if (item && (item.name.includes(itemName) || itemId.includes(itemName))) {
                itemIndex = i;
                matchedItem = item;
                break;
            }
        }
        
        if (!matchedItem) {
            return {
                type: 'error',
                message: `你背包里没有"${itemName}"这个物品。`,
                energy: 0
            };
        }
        
        if (!matchedItem.usable) {
            return {
                type: 'error',
                message: `"${matchedItem.name}"无法使用。`,
                energy: 0
            };
        }
        
        // 应用物品效果
        let message = `✨ 你使用了 "${matchedItem.name}"\n\n${matchedItem.description}\n\n`;
        
        // 契约力恢复
        if (matchedItem.effect.energy) {
            const gain = matchedItem.effect.energy;
            this.state.contract_energy = Math.min(100, this.state.contract_energy + gain);
            message += `契约力 +${gain}\n`;
        }
        
        // 攻击加成
        if (matchedItem.effect.attack_boost) {
            this.state.attack_boost = matchedItem.effect.attack_boost;
            message += `攻击力 +${matchedItem.effect.attack_boost} (持续${matchedItem.effect.duration}回合)\n`;
        }
        
        // 防御加成
        if (matchedItem.effect.defense_boost) {
            this.state.defense_boost = matchedItem.effect.defense_boost;
            message += `防御力 +${matchedItem.effect.defense_boost} (持续${matchedItem.effect.duration}回合)\n`;
        }
        
        // 移除物品
        inventory.splice(itemIndex, 1);
        
        return {
            type: 'use_item',
            message: message,
            energy: 0,
            energyChange: matchedItem.effect.energy || 0
        };
    }
        // 处理丢弃物品
    handleDropItem(itemName) {
        const inventory = this.state.inventory || [];
        
        // 查找匹配的物品
        let itemIndex = -1;
        let matchedItem = null;
        
        for (let i = 0; i < inventory.length; i++) {
            const itemId = inventory[i];
            const item = this.items[itemId];
            if (item && (item.name.includes(itemName) || itemId.includes(itemName))) {
                itemIndex = i;
                matchedItem = item;
                break;
            }
        }
        
        if (!matchedItem) {
            return {
                type: 'error',
                message: `你背包里没有"${itemName}"这个物品。`,
                energy: 0
            };
        }
        
        // 移除物品
        inventory.splice(itemIndex, 1);
        
        return {
            type: 'drop_item',
            message: `🗑️ 你丢弃了 "${matchedItem.name}"`,
            energy: 0
        };
    }
        // 随机掉落物品
    rollItemDrop() {
        const roll = Math.random() * 100;
        let cumulative = 0;
        
        for (const entry of this.itemDropTable) {
            cumulative += entry.weight;
            if (roll < cumulative) {
                return entry.item;
            }
        }
        
        return null;
    }
        // ==================== 交易系统 ====================
    
    // 商人模板
    merchants = {
        "老炼金师": {
            name: "老炼金师",
            greeting: "欢迎，欢迎！来看看我的宝贝吧。",
            items: [
                { id: "contract_potion", price: 30, stock: 5 },
                { id: "power_elixir", price: 50, stock: 3 },
                { id: "defense_charm", price: 40, stock: 3 }
            ]
        },
        "幽灵商人": {
            name: "幽灵商人",
            greeting: "咯咯咯...想买点什么？",
            items: [
                { id: "mystic_key", price: 100, stock: 1 },
                { id: "shadow_orb", price: 80, stock: 2 },
                { id: "ancient_coin", price: 25, stock: 10 }
            ]
        },
        "深渊守卫商": {
            name: "深渊守卫商",
            greeting: "守卫们也需要补给。",
            items: [
                { id: "contract_potion", price: 25, stock: 10 },
                { id: "power_elixir", price: 45, stock: 5 }
            ]
        }
    }
        // 商店折扣
    itemBasePrices = {
        "contract_potion": 25,
        "power_elixir": 40,
        "defense_charm": 35,
        "mystic_key": 80,
        "ancient_coin": 20,
        "shadow_orb": 60
    }
        // 判断是否进入商店
    isShop(action) {
        return action.includes('商店') || action.includes('shop') || action.includes('买') || 
               action.includes('交易') || action.includes('商人');
    }
        // 打开商店
    handleShop(npcName = null) {
        // 查找当前房间的商人
        const room = this.getCurrentRoom();
        let merchantId = null;
        
        if (room.merchant) {
            merchantId = room.merchant;
        } else if (npcName) {
            // 指定商人
            for (const id in this.merchants) {
                if (id.includes(npcName)) {
                    merchantId = id;
                    break;
                }
            }
        }
        
        if (!merchantId) {
            // 随机遇到商人（在危险区域）
            if (room.danger_level >= 2 && Math.random() < 0.15) {
                merchantId = Math.random() < 0.5 ? "老炼金师" : "幽灵商人";
            } else {
                return {
                    type: 'error',
                    message: '这里没有商人。',
                    energy: 0
                };
            }
        }
        
        const merchant = this.merchants[merchantId];
        this.state.shop = { merchantId: merchantId, merchant: merchant };
        
        let message = `🏪 ${merchant.name}\n\n"${merchant.greeting}"\n\n`;
        message += `💰 你的金币: ${this.state.gold}\n\n`;
        message += `📦 商品:\n\n`;
        
        for (let i = 0; i < merchant.items.length; i++) {
            const item = merchant.items[i];
            if (item.stock > 0) {
                const itemInfo = this.items[item.id];
                message += `${i + 1}. ${itemInfo.name} - ${item.price}金币`;
                message += ` (库存: ${item.stock})\n`;
                message += `   ${itemInfo.description}\n\n`;
            }
        }
        
        message += `💡 指令:\n`;
        message += `• "购买 [编号]" 或 "买 [编号]" - 购买商品\n`;
        message += `• "出售 [物品名]" - 出售物品\n`;
        message += `• "离开" - 退出商店`;
        
        return {
            type: 'shop',
            message: message,
            energy: 0,
            gold: this.state.gold,
            merchant: merchant
        };
    }
        // 购买物品
    handleBuy(itemIndex) {
        if (!this.state.shop) {
            return {
                type: 'error',
                message: '你没有在商店中。先说"商店"打开商店。',
                energy: 0
            };
        }
        
        const merchant = this.state.shop.merchant;
        const index = parseInt(itemIndex) - 1;
        
        if (isNaN(index) || index < 0 || index >= merchant.items.length) {
            return {
                type: 'error',
                message: '没有这个商品。',
                energy: 0
            };
        }
        
        const shopItem = merchant.items[index];
        
        if (shopItem.stock <= 0) {
            return {
                type: 'error',
                message: '这个商品已经卖完了。',
                energy: 0
            };
        }
        
        if (this.state.gold < shopItem.price) {
            return {
                type: 'error',
                message: `金币不足！需要 ${shopItem.price} 金币，你只有 ${this.state.gold} 金币。`,
                energy: 0
            };
        }
        
        // 执行购买
        this.state.gold -= shopItem.price;
        this.state.inventory = this.state.inventory || [];
        this.state.inventory.push(shopItem.id);
        shopItem.stock--;
        
        const itemInfo = this.items[shopItem.id];
        
        // 更新物品收集统计并检查成就
        const newUnlocks = this.updateStatsAndCheckAchievements('item');
        let unlockMsg = '';
        if (newUnlocks.length > 0) {
            unlockMsg = `\n\n🎉 解锁成就！\n`;
            for (const ach of newUnlocks) {
                unlockMsg += `${ach.icon} ${ach.name}\n`;
            }
        }
        
        return {
            type: 'buy',
            message: `✅ 购买成功！\n\n你购买了 "${itemInfo.name}"\n\n花费: ${shopItem.price} 金币\n剩余金币: ${this.state.gold}${unlockMsg}`,
            energy: 0,
            gold: this.state.gold,
            item: itemInfo.name
        };
    }
        // 出售物品
    handleSell(itemName) {
        if (!this.state.shop) {
            return {
                type: 'error',
                message: '你没有在商店中。先说"商店"打开商店。',
                energy: 0
            };
        }
        
        const inventory = this.state.inventory || [];
        let itemIndex = -1;
        let itemId = null;
        
        for (let i = 0; i < inventory.length; i++) {
            const id = inventory[i];
            const item = this.items[id];
            if (item && (item.name.includes(itemName) || id.includes(itemName))) {
                itemIndex = i;
                itemId = id;
                break;
            }
        }
        
        if (itemIndex === -1) {
            return {
                type: 'error',
                message: `你背包里没有"${itemName}"。`,
                energy: 0
            };
        }
        
        // 计算出售价格 (原价的50%)
        const basePrice = this.itemBasePrices[itemId] || 20;
        const sellPrice = Math.floor(basePrice * 0.5);
        
        this.state.gold += sellPrice;
        inventory.splice(itemIndex, 1);
        
        const itemInfo = this.items[itemId];
        
        // 更新金币统计并检查成就
        const newUnlocks = this.updateStatsAndCheckAchievements('gold', sellPrice);
        let unlockMsg = '';
        if (newUnlocks.length > 0) {
            unlockMsg = `\n\n🎉 解锁成就！\n`;
            for (const ach of newUnlocks) {
                unlockMsg += `${ach.icon} ${ach.name}\n`;
            }
        }
        
        return {
            type: 'sell',
            message: `✅ 出售成功！\n\n你出售了 "${itemInfo.name}"\n\n获得: ${sellPrice} 金币\n当前金币: ${this.state.gold}${unlockMsg}`,
            energy: 0,
            gold: this.state.gold,
            item: itemInfo.name,
            sellPrice: sellPrice
        };
    }
        // 离开商店
    handleLeaveShop() {
        if (!this.state.shop) {
            return {
                type: 'error',
                message: '你不在商店中。',
                energy: 0
            };
        }
        
        this.state.shop = null;
        
        return {
            type: 'leave_shop',
            message: '你离开了商店。',
            energy: 0
        };
    }
        // ==================== 战斗系统 ====================

    // 敌人模板
    enemies = {
        "shadow_beast": {
            name: "阴影怪兽",
            hp: 30,
            maxHp: 30,
            attack: 8,
            defense: 3,
            description: "一团漆黑的阴影，张牙舞爪地扑来"
        },
        "深渊守卫": {
            name: "深渊守卫",
            hp: 50,
            maxHp: 50,
            attack: 12,
            defense: 5,
            description: "身披黑甲的守卫，眼中燃烧着幽蓝的火焰"
        },
        "灵魂收割者": {
            name: "灵魂收割者",
            hp: 80,
            maxHp: 80,
            attack: 20,
            defense: 8,
            description: "巨大的镰刀闪烁着寒光，收割着亡者的灵魂"
        }
    }
        // 判断是否是战斗指令
    isCombatAction(action) {
        return action.includes('攻击') || action.includes('attack') || action.includes('打') ||
               action.includes('防御') || action.includes('defend') || action.includes('防') ||
               action.includes('必杀') || action.includes('skill') || action.includes('大招');
    }
        // 处理战斗指令
    handleCombatAction(action) {
        const enemy = this.state.combat.enemy;
        let playerDamage = 0;
        let enemyDamage = 0;
        let message = '';
        let resultType = 'combat';

        if (action.includes('攻击') || action.includes('attack') || action.includes('打')) {
            // 普通攻击
            playerDamage = Math.max(1, Math.floor(Math.random() * 10) + 10 - enemy.defense);
            enemy.hp -= playerDamage;
            message = `⚔️ 你发动攻击！\n\n对${enemy.name}造成了 ${playerDamage} 点伤害！`;
            
            // 敌人反击
            enemyDamage = Math.max(1, enemy.attack - 5);
            this.state.contract_energy = Math.max(0, this.state.contract_energy - enemyDamage);
            message += `\n\n${enemy.name}反击！你受到 ${enemyDamage} 点伤害。\n契约力 -${enemyDamage}`;

        } else if (action.includes('防御') || action.includes('defend') || action.includes('防')) {
            // 防御
            enemyDamage = Math.max(1, Math.floor(enemy.attack / 2));
            this.state.contract_energy = Math.max(0, this.state.contract_energy - enemyDamage);
            message = `🛡️ 你进入防御姿态！\n\n${enemy.name}的攻击被格挡部分。\n你受到 ${enemyDamage} 点伤害。\n契约力 -${enemyDamage}`;

        } else if (action.includes('必杀') || action.includes('skill') || action.includes('大招')) {
            // 必杀技
            if (this.state.contract_energy < 25) {
                return {
                    type: 'error',
                    message: '⚡ 你的契约力不足以使用必杀技！(需要25点)',
                    energy: 0
                };
            }
            
            playerDamage = Math.floor(enemy.maxHp * 0.6);
            enemy.hp -= playerDamage;
            this.state.contract_energy -= 25;
            
            message = `🔥💥 必杀技！！！\n\n你对${enemy.name}发动了毁灭性一击！\n造成 ${playerDamage} 点巨大伤害！\n\n消耗契约力 25`;

            // 敌人反击（必杀后摇）
            enemyDamage = Math.floor(enemy.attack * 0.7);
            this.state.contract_energy = Math.max(0, this.state.contract_energy - enemyDamage);
            message += `\n\n但${enemy.name}趁机反击！\n你受到 ${enemyDamage} 点伤害。`;
        }

        // 检查战斗结果
        if (enemy.hp <= 0) {
            // 胜利！
            const reward = 20 + Math.floor(Math.random() * 15);
            this.state.contract_energy = Math.min(100, this.state.contract_energy + reward);
            
            message += `\n\n🎉 ${enemy.name} 被击败了！\n\n✨ 获得契约力 +${reward}`;
            
            // 随机掉落物品
            const droppedItem = this.rollItemDrop();
            if (droppedItem) {
                const item = this.items[droppedItem];
                this.state.inventory = this.state.inventory || [];
                this.state.inventory.push(droppedItem);
                message += `\n\n🎁 战利品: ${item.name}`;
            }
            
            // 战斗结束
            const fossil = {
                id: this.generateUUID(),
                type: 'combat',
                content: `在${this.getCurrentRoom().name}击败了${enemy.name}`,
                creator: this.state.player,
                roomId: this.state.location,
                created_at: Date.now(),
                responses: [],
                resonance: 1
            };
            this.state.fossils.push(fossil);
            message += `\n\n【世界化石】你的战斗印记已被记录！`;
            
            this.state.combat = null;
            resultType = 'combat_win';
            
            // 更新统计并检查成就
            const newUnlocks = this.updateStatsAndCheckAchievements('battle_win', enemy.maxHp);
            if (newUnlocks.length > 0) {
                message += `\n\n🎉 解锁成就！\n`;
                for (const ach of newUnlocks) {
                    message += `${ach.icon} ${ach.name}\n`;
                }
            }

        } else if (this.state.contract_energy <= 0) {
            // 失败
            message += `\n\n💀 你的契约力耗尽...\n\n你跪倒在地，意识逐渐模糊...\n\n【警告】请快速休息恢复！`;
            this.state.combat = null;
            resultType = 'combat_lose';
        } else {
            // 继续战斗
            enemy.hp = Math.max(0, enemy.hp);
            message += `\n\n⚔️ ${enemy.name} 剩余生命: ${enemy.hp}/${enemy.maxHp}`;
        }

        return {
            type: resultType,
            message: message,
            energy: 0,
            enemyHp: enemy.hp,
            enemyMaxHp: enemy.maxHp
        };
    }
        // 逃跑
    handleCombatRun() {
        const enemy = this.state.combat.enemy;
        const success = Math.random() > 0.4;
        
        if (success) {
            // 逃跑成功
            this.state.combat = null;
            return {
                type: 'combat_run',
                message: `🏃 你转身就跑！\n\n成功摆脱了${enemy.name}！`,
                energy: 5
            };
        } else {
            // 逃跑失败，被反击
            const enemyDamage = enemy.attack;
            this.state.contract_energy = Math.max(0, this.state.contract_energy - enemyDamage);
            
            return {
                type: 'combat_run_fail',
                message: `🏃 你试图逃跑...\n\n但${enemy.name}追了上来！\n\n你受到 ${enemyDamage} 点伤害！\n契约力 -${enemyDamage}`,
                energy: 5
            };
        }
    }
        // 触发战斗
    isTriggerCombat(action) {
        return action.includes('战斗') || action.includes('fight') || action.includes('打') ||
               action.includes('攻击') || action.includes('attack') || action.includes('调查') ||
               action.includes('触发') || action.includes('触发');
    }
        // 处理触发战斗
    handleTriggerCombat() {
        const room = this.getCurrentRoom();
        
        // 检查房间是否危险
        if (!room.danger_level || room.danger_level < 2) {
            return {
                type: 'safe',
                message: '这里很安全，没有敌人。',
                energy: 5
            };
        }

        // 随机触发战斗
        if (Math.random() < room.danger_level * 0.15) {
            // 选择敌人
            let enemyTemplate;
            if (room.danger_level >= 4) {
                enemyTemplate = this.enemies["灵魂收割者"];
            } else if (room.danger_level >= 3) {
                enemyTemplate = this.enemies["深渊守卫"];
            } else {
                enemyTemplate = this.enemies["shadow_beast"];
            }

            // 创建敌人
            const enemy = { ...enemyTemplate };
            enemy.hp = enemy.maxHp;

            // 开始战斗
            this.state.combat = { enemy: enemy };

            return {
                type: 'combat_start',
                message: `⚔️ 遭遇敌人！\n\n${enemy.description}\n\n${enemy.name}\n生命: ${enemy.hp}/${enemy.maxHp}\n攻击: ${enemy.attack}\n防御: ${enemy.defense}\n\n指令: 攻击 / 防御 / 必杀 / 逃跑`,
                energy: 0,
                combat: true
            };
        }

        return {
            type: 'search',
            message: '你仔细搜索了四周，但没有发现敌人。',
            energy: 10
        };
    }
        // ==================== 移动系统 ====================

    // 判断移动
    isMovement(action) {
        const movementKeywords = ['north', 'south', 'east', 'west', '北', '南', '东', '西', '去', '走', '前进', '后退', '左', '右'];
        return movementKeywords.some(kw => action.includes(kw)) || 
               ['n', 's', 'e', 'w'].includes(action);
    }
        // 处理移动
    handleMovement(action) {
        const room = this.getCurrentRoom();
        let direction = '';
        
        if (action.includes('北') || action === 'n' || action.includes('north')) direction = 'north';
        else if (action.includes('南') || action === 's' || action.includes('south')) direction = 'south';
        else if (action.includes('东') || action === 'e' || action.includes('east')) direction = 'east';
        else if (action.includes('西') || action === 'w' || action.includes('west')) direction = 'west';
        else if (action.includes('前')) direction = 'north';
        else if (action.includes('后')) direction = 'south';
        else if (action.includes('左')) direction = 'west';
        else if (action.includes('右')) direction = 'east';

        if (!direction) {
            return {
                type: 'error',
                message: '你不知道该往哪里走。试着说"北"、"南"、"东"、"西"或"前进"、"后退"。',
                energy: 0
            };
        }

        if (!room.connections[direction]) {
            return {
                type: 'error',
                message: `你无法往${this.getDirectionName(direction)}走，那里没有路。`,
                energy: 0
            };
        }

        const newLocation = room.connections[direction];
        const newRoom = this.theme.rooms.find(r => r.id === newLocation);
        
        if (!newRoom) {
            return {
                type: 'error',
                message: '传送门故障了...',
                energy: 0
            };
        }

        this.state.location = newLocation;
        this.state.explored_rooms.add(newLocation);
        
        // 移动时检查是否遭遇敌人
        let encounterMsg = '';
        if (newRoom.danger_level >= 3 && Math.random() < 0.2) {
            const enemy = { ...this.enemies["shadow_beast"] };
            enemy.hp = enemy.maxHp;
            this.state.combat = { enemy: enemy };
            encounterMsg = `\n\n⚔️ 突然！${enemy.description}\n\n战斗开始！`;
        }
        
        return {
            type: 'move',
            message: `你朝${this.getDirectionName(direction)}走去...\n\n${newRoom.name}\n${newRoom.description}${encounterMsg}`,
            energy: 3,
            room: newRoom,
            combat: this.state.combat !== null
        };
    }
    getDirectionName(dir) {
        const names = { north: '北', south: '南', east: '东', west: '西' };
        return names[dir] || dir;
    }
        // ==================== 探索系统 ====================

    // 判断探索
    isExplore(action) {
        return action.includes('探索') || action.includes('search') || action.includes('look') || action.includes('看');
    }
        // 处理探索
    handleExplore() {
        // 检查冷却
        if (this.state.action_cooldowns.explore > 0) {
            return {
                type: 'cooldown',
                message: `⏳ 你刚刚探索过，需要休息一下。\n\n等待 ${this.state.action_cooldowns.explore} 回合后再探索吧。`,
                energy: 0,
                cooldown: this.state.action_cooldowns.explore
            };
        }
        
        // 设置冷却
        this.state.action_cooldowns.explore = 2;
        
        const room = this.getCurrentRoom();
        let message = `【${room.name}】\n${room.description}\n`;
        
        // 显示出口
        const exits = Object.keys(room.connections || {});
        if (exits.length > 0) {
            message += `\n📍 可移动方向：${exits.map(e => this.getDirectionName(e)).join('、')}`;
        }

        // 检查危险程度
        if (room.danger_level >= 4) {
            message += `\n\n💀 极度危险区域！`;
        } else if (room.danger_level >= 3) {
            message += `\n\n⚠️ 危险区域。`;
        } else if (room.danger_level >= 2) {
            message += `\n\n⚡ 有一定危险。`;
        }

        // 检查化石
        if (room.fossils && room.fossils.length > 0) {
            message += `\n\n🪨 这里似乎有前人留下的痕迹...`;
        }

        // 检查是否是第一次探索这个房间
        const isNewRoom = !this.state.explored_rooms.has(this.state.location);
        if (isNewRoom) {
            this.state.explored_rooms.add(this.state.location);
            const newUnlocks = this.updateStatsAndCheckAchievements('explore');
            if (newUnlocks.length > 0) {
                message += `\n\n🎉 解锁成就！\n`;
                for (const ach of newUnlocks) {
                    message += `${ach.icon} ${ach.name}\n`;
                }
            }
        }

        return {
            type: 'explore',
            message: message,
            energy: 5
        };
    }
        // ==================== 休息系统 ====================

    // 判断休息
    isRest(action) {
        return action.includes('休息') || action.includes('rest') || action.includes('sleep') || action.includes('睡');
    }
        // 处理休息
    handleRest() {
        const energyGain = 20;
        this.state.contract_energy = Math.min(100, this.state.contract_energy + energyGain);
        
        return {
            type: 'rest',
            message: `你找了个安全的地方休息了一会儿...\n\n✨ 契约力 +${energyGain} (当前: ${this.state.contract_energy})`,
            energy: 0,
            energyChange: energyGain
        };
    }
        // ==================== 收集系统 ====================

    // 判断收集
    isCollect(action) {
        return action.includes('收集') || action.includes('collect') || action.includes('拿') || action.includes('take');
    }
        // 处理收集
    handleCollect() {
        // 检查冷却
        if (this.state.action_cooldowns.collect > 0) {
            return {
                type: 'cooldown',
                message: `⏳ 你刚刚收集过，这里已经没有有价值的东西了。\n\n等待 ${this.state.action_cooldowns.collect} 回合后再来。`,
                energy: 0,
                cooldown: this.state.action_cooldowns.collect
            };
        }
        
        const room = this.getCurrentRoom();
        
        // 检查是否有可收集的事件
        const discoveryEvent = room.events?.find(e => e.type === 'discovery');
        
        // 设置冷却（3-5回合）
        this.state.action_cooldowns.collect = 3 + Math.floor(Math.random() * 3);
        
        if (discoveryEvent) {
            // 连续收集增加趣味性
            this.state.luck_counter++;
            const luckBonus = Math.min(this.state.luck_counter * 2, 20);
            const totalReward = discoveryEvent.reward + luckBonus;
            
            this.state.contract_energy = Math.min(100, this.state.contract_energy + totalReward);
            
            let flavorText = "";
            if (this.state.luck_counter >= 3) {
                flavorText = "\n\n🌟 幸运光环笼罩！你发现了更多！";
            } else if (this.state.luck_counter >= 2) {
                flavorText = "\n\n✨ 运气不错，发现了额外奖励！";
            }
            
            return {
                type: 'collect',
                message: `🔍 你仔细搜索着${room.name}...${flavorText}\n\n${discoveryEvent.description}\n\n✨ 契约力 +${totalReward} (基础+${luckBonus})`,
                energy: 10,
                energyChange: totalReward,
                cooldown: this.state.action_cooldowns.collect
            };
        }

        // 没有发现时增加不幸计数
        this.state.luck_counter = Math.max(0, this.state.luck_counter - 1);
        
        const emptyFlavors = [
            "\n\n💨 你只找到了一些灰尘...",
            "\n\n🔍 什么也没有发现...",
            "\n\n💭 这里是空荡荡的...",
            "\n\n🏜️ 除了一些碎石，什么都没有..."
        ];
        
        return {
            type: 'empty',
            message: `🔍 你搜索着${room.name}...${emptyFlavors[Math.floor(Math.random() * emptyFlavors.length)]}\n\n契约力 -10（消耗）`,
            energy: -10,
            cooldown: this.state.action_cooldowns.collect
        };
    }
        // ==================== 祈祷系统 ====================

    // 判断祈祷
    isPray(action) {
        return action.includes('祈祷') || action.includes('pray') || action.includes('祈求');
    }
        // 处理祈祷
    handlePray() {
        // 检查冷却
        if (this.state.action_cooldowns.pray > 0) {
            return {
                type: 'cooldown',
                message: `⏳ 深渊还没有回应你上次的祈祷。\n\n等待 ${this.state.action_cooldowns.pray} 回合后再祈祷吧。`,
                energy: 0,
                cooldown: this.state.action_cooldowns.pray
            };
        }
        
        // 设置冷却（4-6回合）
        this.state.action_cooldowns.pray = 4 + Math.floor(Math.random() * 3);
        
        const random = Math.random();
        
        // 连续好运/厄运会改变概率
        const luckModifier = this.state.luck_counter * 0.05;
        
        if (random < 0.1 + luckModifier) {
            // 大成功！
            const rewards = [
                { energy: 50, item: "ancient_coin", text: "✨ 一枚古老的硬币从虚空中落下！" },
                { energy: 40, item: "blessing_charm", text: "✨ 一个祝福护符出现在你手中！" },
                { energy: 60, item: null, text: "✨ 深渊之光笼罩了你！" }
            ];
            const result = rewards[Math.floor(Math.random() * rewards.length)];
            
            this.state.contract_energy = Math.min(100, this.state.contract_energy + result.energy);
            this.state.luck_counter++;
            
            let message = `🙏 你虔诚地向深渊祈祷...\n\n${result.text}\n\n💎 契约力 +${result.energy}`;
            
            if (result.item) {
                this.state.inventory = this.state.inventory || [];
                this.state.inventory.push(result.item);
                message += `\n\n🎁 获得物品: ${this.items[result.item].name}`;
            }
            
            return {
                type: 'pray_great',
                message: message,
                energy: 20,
                energyChange: result.energy,
                cooldown: this.state.action_cooldowns.pray
            };
        } else if (random < 0.4 + luckModifier) {
            // 小成功
            const reward = 15 + Math.floor(Math.random() * 10);
            this.state.contract_energy = Math.min(100, this.state.contract_energy + reward);
            this.state.luck_counter = Math.max(0, this.state.luck_counter + 1);
            
            const goodPrayers = [
                `🙏 你轻声祈祷，深渊微微点头...\n\n✨ 你感到一丝温暖。`,
                `🙏 你的祈祷化作微风...\n\n✨ 契约力缓慢增长。`,
                `🙏 黑暗中有什么回应了你...\n\n✨ 力量涌入身体。`
            ];
            
            return {
                type: 'pray_good',
                message: goodPrayers[Math.floor(Math.random() * goodPrayers.length)] + `\n\n💎 契约力 +${reward}`,
                energy: 20,
                energyChange: reward,
                cooldown: this.state.action_cooldowns.pray
            };
        } else {
            // 失败 - 可能招来不好的东西
            this.state.luck_counter = Math.max(-2, this.state.luck_counter - 1);
            
            const badPrayers = [
                `🙏 你祈祷着...\n\n🕳️ 深渊一片寂静...`,
                `🙏 你的声音消散在黑暗中...\n\n💨 什么都没有发生。`,
                `🙏 仿佛有一个声音在嘲笑你...\n\n🌑 契约力减少了...`
            ];
            
            // 祈祷失败也可能损失能量
            const energyLoss = 5 + Math.floor(Math.random() * 5);
            this.state.contract_energy = Math.max(0, this.state.contract_energy - energyLoss);
            
            return {
                type: 'pray_none',
                message: badPrayers[Math.floor(Math.random() * badPrayers.length)] + `\n\n💨 契约力 -${energyLoss}`,
                energy: -energyLoss,
                energyChange: -energyLoss,
                cooldown: this.state.action_cooldowns.pray
            };
        }
    }
        // ==================== 创造系统 ====================

    // 判断创造
    isCreate(action) {
        return action.includes('创造') || action.includes('create') || action.includes('建造');
    }
        // 处理创造
    handleCreate() {
        // 检查冷却
        if (this.state.action_cooldowns.create > 0) {
            return {
                type: 'cooldown',
                message: `⏳ 你刚刚创造过，空间还不稳定。\n\n等待 ${this.state.action_cooldowns.create} 回合后再尝试吧。`,
                energy: 0,
                cooldown: this.state.action_cooldowns.create
            };
        }
        
        if (this.state.contract_energy < 30) {
            return {
                type: 'error',
                message: '⚡ 你的契约力不足以创造新空间。(需要30点)\n\n先去收集一些能量吧！',
                energy: 0
            };
        }

        // 设置冷却（5-8回合）
        this.state.action_cooldowns.create = 5 + Math.floor(Math.random() * 4);
        
        this.state.contract_energy -= 30;
        
        // 创造事件 - 更多戏剧性
        const creationTypes = [
            {
                type: 'fossil',
                messages: [
                    "🪨 你用契约之力凝结出一块化石！",
                    "✨ 空间中浮现出过去的影像，化作化石！",
                    "💫 你的意志化作了永恒的印记！"
                ]
            },
            {
                type: 'memory',
                messages: [
                    "🌊 深渊中涌出一段被遗忘的记忆！",
                    "🌀 空间扭曲，露出一段久远的往事！",
                    "📜 墙壁上浮现出神秘的文字..."
                ]
            },
            {
                type: 'echo',
                messages: [
                    "🔮 你的声音在空间中回荡，产生了共鸣！",
                    "🎭 另一个时空的你留下了回声！",
                    "🌙 黑暗中有什麼在回应你..."
                ]
            }
        ];
        
        const creation = creationTypes[Math.floor(Math.random() * creationTypes.length)];
        const message = creation.messages[Math.floor(Math.random() * creation.messages.length)];
        
        const fossil = {
            id: this.generateUUID(),
            type: creation.type,
            content: message,
            creator: this.state.player,
            roomId: this.state.location,
            created_at: Date.now(),
            responses: [],
            resonance: 0
        };

        this.state.fossils.push(fossil);

        // 更新统计并检查成就
        const newUnlocks = this.updateStatsAndCheckAchievements('fossil');
        let unlockMsg = '';
        if (newUnlocks.length > 0) {
            unlockMsg = `\n\n🎉 解锁成就！\n`;
            for (const ach of newUnlocks) {
                unlockMsg += `${ach.icon} ${ach.name}\n`;
            }
        }

        return {
            type: 'create',
            message: `✨ 你消耗30点契约力，在虚空中创造了一个新空间...\n\n【世界化石形成】\n你的创造将被后来的探险者发现。${unlockMsg}`,
            energy: 30,
            energyChange: -30,
            fossil: fossil
        };
    }
        // ==================== 化石系统 ====================

    // 判断查看化石
    isFossilList(action) {
        return action.includes('化石') || action.includes('fossil') || action.includes('痕迹');
    }
        // 判断回应化石
    isFossilRespond(action) {
        return action.includes('回应') || action.includes('respond') || action.includes('评论') || action.includes('comment');
    }
        // 判断共鸣化石
    isFossilResonate(action) {
        return action.includes('共鸣') || action.includes('resonate') || action.includes('点赞');
    }
        // 列出当前房间的化石
    handleListFossils() {
        const room = this.getCurrentRoom();
        
        // 合并世界化石和本地化石
        const roomFossils = this.state.fossils.filter(f => f.roomId === this.state.location);
        const allFossils = [...roomFossils];
        
        if (allFossils.length === 0) {
            return {
                type: 'fossils',
                message: `🪨 ${room.name}\n\n这里还没有任何世界化石。\n\n输入"创造"可以留下你的印记！`,
                energy: 0
            };
        }
        
        let message = `🪨 ${room.name} - 世界化石\n\n`;
        
        for (let i = 0; i < allFossils.length; i++) {
            const fossil = allFossils[i];
            message += `【化石 ${i + 1}】\n`;
            message += `${fossil.content}\n`;
            message += `—— ${fossil.creator}\n`;
            message += `💫 共鸣: ${fossil.resonance || 0}\n`;
            
            // 显示回应数量
            const responses = fossil.responses || [];
            if (responses.length > 0) {
                message += `💬 ${responses.length} 条回应\n`;
                message += `最新: ${responses[responses.length - 1].text.substring(0, 30)}...\n`;
            }
            
            message += '\n';
        }
        
        message += `💡 指令:\n`;
        message += `• "回应 [化石编号] [内容]" - 留下评论\n`;
        message += `• "共鸣 [化石编号]" - 点赞获得奖励\n`;
        
        return {
            type: 'fossils',
            message: message,
            energy: 0,
            fossils: allFossils
        };
    }
        // 回应化石
    handleFossilRespond(fossilIndex, responseText) {
        const roomFossils = this.state.fossils.filter(f => f.roomId === this.state.location);
        
        if (roomFossils.length === 0) {
            return {
                type: 'error',
                message: '这里没有化石可以回应。先创造一个吧！',
                energy: 0
            };
        }
        
        if (fossilIndex < 0 || fossilIndex >= roomFossils.length) {
            return {
                type: 'error',
                message: `没有这个化石。编号1-${roomFossils.length}`,
                energy: 0
            };
        }
        
        if (!responseText || responseText.length < 2) {
            return {
                type: 'error',
                message: '请输入回应的内容。',
                energy: 0
            };
        }
        
        const fossil = roomFossils[fossilIndex];
        fossil.responses = fossil.responses || [];
        fossil.responses.push({
            player: this.state.player,
            text: responseText,
            timestamp: Date.now()
        });
        
        return {
            type: 'fossil_respond',
            message: `💬 你在化石【${fossilIndex + 1}】留下了回应：\n\n"${responseText}"\n\n化石创作者将收到你的共鸣！`,
            energy: 0
        };
    }
        // 共鸣化石
    handleFossilResonate(fossilIndex) {
        const roomFossils = this.state.fossils.filter(f => f.roomId === this.state.location);
        
        if (roomFossils.length === 0) {
            return {
                type: 'error',
                message: '这里没有化石可以共鸣。',
                energy: 0
            };
        }
        
        if (fossilIndex < 0 || fossilIndex >= roomFossils.length) {
            return {
                type: 'error',
                message: `没有这个化石。编号1-${roomFossils.length}`,
                energy: 0
            };
        }
        
        const fossil = roomFossils[fossilIndex];
        fossil.resonance = (fossil.resonance || 0) + 1;
        
        // 随机奖励
        const reward = 5 + Math.floor(Math.random() * 10);
        this.state.contract_energy = Math.min(100, this.state.contract_energy + reward);
        
        return {
            type: 'fossil_resonate',
            message: `✨ 你与化石产生了共鸣！\n\n"${fossil.content.substring(0, 50)}..."\n\n💫 共鸣 +1 (总计: ${fossil.resonance})\n\n🎁 获得了 ${reward} 点契约力！`,
            energy: 0,
            energyChange: reward
        };
    }
        // ==================== 成就系统 ====================
    
    // 成就定义
    achievements = {
        "first_battle": {
            id: "first_battle",
            name: "初战告捷",
            description: "赢得第一场战斗",
            icon: "⚔️",
            condition: (stats) => stats.battles_won >= 1
        },
        "battle_master": {
            id: "battle_master",
            name: "战斗大师",
            description: "赢得10场战斗",
            icon: "🎖️",
            condition: (stats) => stats.battles_won >= 10
        },
        "explorer": {
            id: "explorer",
            name: "探索者",
            description: "探索5个不同的房间",
            icon: "🧭",
            condition: (stats) => stats.rooms_explored >= 5
        },
        "world_builder": {
            id: "world_builder",
            name: "世界缔造者",
            description: "创造3个世界化石",
            icon: "🪨",
            condition: (stats) => stats.fossils_created >= 3
        },
        "rich": {
            id: "rich",
            name: "小富翁",
            description: "累计获得500金币",
            icon: "💰",
            condition: (stats) => stats.total_gold_earned >= 500
        },
        "collector": {
            id: "collector",
            name: "收藏家",
            description: "收集10件物品",
            icon: "📦",
            condition: (stats) => stats.items_collected >= 10
        },
        "survivor": {
            id: "survivor",
            name: "深渊生存者",
            description: "完成50次行动",
            icon: "🌟",
            condition: (stats) => stats.turn_count >= 50
        },
        "legend": {
            id: "legend",
            name: "传说英雄",
            description: "赢得100场战斗",
            icon: "👑",
            condition: (stats) => stats.battles_won >= 100
        }
    }
        // 判断成就指令
    isAchievement(action) {
        return action.includes('成就') || action.includes('achievement') || action.includes('🏆');
    }
        // 查看成就
    handleAchievements() {
        const unlocked = this.state.achievements || [];
        const stats = this.state.stats || {};
        
        let message = `🏆 成就系统\n\n`;
        message += `📊 统计数据:\n`;
        message += `  战斗胜利: ${stats.battles_won || 0}\n`;
        message += `  探索房间: ${stats.rooms_explored || 0}\n`;
        message += `  创造化石: ${stats.fossils_created || 0}\n`;
        message += `  累计金币: ${stats.total_gold_earned || 0}\n`;
        message += `  收集物品: ${stats.items_collected || 0}\n`;
        message += `  行动次数: ${stats.turn_count || 0}\n\n`;
        
        message += `🎖️ 已解锁成就 (${unlocked.length}/${Object.keys(this.achievements).length}):\n\n`;
        
        for (const achId of unlocked) {
            const ach = this.achievements[achId];
            if (ach) {
                message += `${ach.icon} ${ach.name}\n`;
                message += `   ${ach.description}\n\n`;
            }
        }
        
        // 显示可完成的成就
        const locked = Object.keys(this.achievements).filter(id => !unlocked.includes(id));
        if (locked.length > 0) {
            message += `🔒 未解锁成就:\n`;
            for (const achId of locked) {
                const ach = this.achievements[achId];
                if (ach && ach.condition(stats)) {
                    message += `${ach.icon} ${ach.name} - 条件达成！\n`;
                }
            }
        }
        
        return {
            type: 'achievements',
            message: message,
            energy: 0,
            unlocked: unlocked,
            stats: stats
        };
    }
        // 检查并解锁成就
    checkAchievements() {
        const unlocked = this.state.achievements || [];
        const stats = this.state.stats || {};
        const newUnlocks = [];
        
        for (const [achId, ach] of Object.entries(this.achievements)) {
            if (!unlocked.includes(achId) && ach.condition(stats)) {
                unlocked.push(achId);
                newUnlocks.push(ach);
            }
        }
        
        return newUnlocks;
    }
        // 更新统计并检查成就
    updateStatsAndCheckAchievements(type, value = 1) {
        const stats = this.state.stats || {};
        
        switch(type) {
            case 'battle_win':
                stats.battles_won = (stats.battles_won || 0) + 1;
                if (value > stats.biggest_win) {
                    stats.biggest_win = value;
                }
                break;
            case 'explore':
                stats.rooms_explored = (stats.rooms_explored || 0) + 1;
                break;
            case 'fossil':
                stats.fossils_created = (stats.fossils_created || 0) + 1;
                break;
            case 'gold':
                stats.total_gold_earned = (stats.total_gold_earned || 0) + value;
                break;
            case 'item':
                stats.items_collected = (stats.items_collected || 0) + value;
                break;
            case 'turn':
                stats.turn_count = (stats.turn_count || 0) + 1;
                break;
        }
        
        this.state.stats = stats;
        
        // 检查成就
        const newUnlocks = this.checkAchievements();
        return newUnlocks;
    }
        // ==================== 未知指令 ====================

    // 未知行动
    handleUnknown(action) {
        return {
            type: 'unknown',
            message: `你尝试"${action}"，但不知道该如何做...\n\n💡 试试这些指令：\n📋 基础指令：\n- 探索 / 查看 / look\n- 北 / 南 / 东 / 西 / 前进\n- 休息 / sleep\n\n🎒 物品指令：\n- 背包 / 物品 / inventory\n- 使用 [物品名]\n- 丢弃 [物品名]\n\n⚔️ 战斗指令：\n- 攻击 / 防御 / 必杀 / 逃跑\n- 调查 / 战斗 / 打\n\n🎁 其他指令：\n- 收集 / 拿\n- 祈祷 / pray\n- 创造 / create (需要30能量)\n\n🪨 化石指令：\n- 化石 / fossil - 查看化石\n- 回应 [编号] [内容] - 评论化石\n- 共鸣 [编号] - 点赞化石\n\n🏪 商店指令：\n- 商店 - 打开商店\n- 购买 [编号] - 购买商品\n- 出售 [物品名] - 出售物品\n- 离开 - 退出商店`,
            energy: 1
        };
    }
        // ==================== 存档系统 ====================

    // 记录日志
    logAction(input, result) {
        this.logs.push({
            turn: this.state.turn_count,
            input: input,
            result: result,
            timestamp: Date.now()
        });
        
        if (this.logs.length > 100) {
            this.logs.shift();
        }
    }
        // 导出存档
    exportSave() {
        const saveData = {
            bubble_id: this.state.bubble_id,
            parent_bubble: this.state.parent_bubble,
            player: this.state.player,
            contract_energy: this.state.contract_energy,
            gold: this.state.gold,
            location: this.state.location,
            inventory: this.state.inventory,
            knowledge: this.state.knowledge,
            fossils: this.state.fossils,
            explored_rooms: Array.from(this.state.explored_rooms),
            turn_count: this.state.turn_count,
            combat: this.state.combat,
            shop: this.state.shop,
            achievements: this.state.achievements,
            stats: this.state.stats,
            theme: this.theme.name,
            exported_at: Date.now()
        };
        
        return btoa(JSON.stringify(saveData));
    }
        // 导入存档
    importSave(encodedData) {
        try {
            const saveData = JSON.parse(atob(encodedData));
            
            if (saveData.theme !== this.theme.name) {
                return { success: false, message: '存档主题不匹配！' };
            }

            this.state.bubble_id = this.generateUUID();
            this.state.parent_bubble = saveData.bubble_id;
            this.state.player = saveData.player;
            this.state.contract_energy = Math.min(100, saveData.contract_energy + 20);
            this.state.gold = saveData.gold || 100;
            this.state.location = saveData.location;
            this.state.inventory = [...saveData.inventory, '共鸣碎片'];
            this.state.knowledge = [...new Set([...saveData.knowledge, 'resonance'])];
            this.state.fossils = [...saveData.fossils];
            this.state.explored_rooms = new Set(saveData.explored_rooms);
            this.state.turn_count = 0;
            this.state.combat = saveData.combat;
            this.state.shop = null; // 重置商店状态
            this.state.achievements = saveData.achievements || [];
            this.state.stats = saveData.stats || {};

            return { 
                success: true, 
                message: `✨ 气泡共鸣成功！\n\n你感受到了来自${saveData.player}的影响...\n\n契约力 +20\n获得物品：共鸣碎片\n金币: ${this.state.gold}` 
            };
        } catch (e) {
            return { success: false, message: '存档导入失败！' };
        }
    }
        // 获取状态
    getStatus() {
        let status = {
            energy: this.state.contract_energy,
            gold: this.state.gold,
            location: this.getCurrentRoom()?.name || '未知',
            fossils: this.state.fossils.length,
            turns: this.state.turn_count,
            inventory: this.state.inventory || []
        };
        
        if (this.state.combat) {
            status.enemy = this.state.combat.enemy.name;
            status.enemyHp = this.state.combat.enemy.hp;
        }
        
        if (this.state.shop) {
            status.shop = this.state.shop.merchantId;
        }
        
        return status;
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TextPactEngine };
}
