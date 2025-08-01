import json
import torch
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    TextDataset,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments
)
from datasets import Dataset
import os

class SkDuckyTrainingData:
    def __init__(self, data_path="data/training_data"):
        self.data_path = data_path
        self.advanced_examples = []
        
    def get_training_examples(self):
        return [
            {
                "category": "combat_systems",
                "examples": [
                    {
                        "prompt": "create advanced combat log system with timer",
                        "code": """options:
    combatlogenabled: true
    combatprefix: &e&lCombatLog &7⇒
    combattimer: 20 seconds
    allowescape: false
    allowcommands: false
    allowregionenter: false
    
function startCombat(victim: player, attacker: player):
    set {_victimWasInCombat} to false
    set {_attackerWasInCombat} to false
    
    if {combat::%{_victim}'s uuid%} is set:
        set {_victimWasInCombat} to true
    if {combat::%{_attacker}'s uuid%} is set:
        set {_attackerWasInCombat} to true
    
    set {combat::%{_victim}'s uuid%} to now
    set {combat::%{_attacker}'s uuid%} to now
    
    if {_victimWasInCombat} is false:
        send "{@combatprefix} &7You entered combat with &e%{_attacker}%!" to {_victim}
        if {combat::timer::%{_victim}'s uuid%} isn't set:
            set {combat::timer::%{_victim}'s uuid%} to true
            processCombat({_victim})
    
    if {_attackerWasInCombat} is false:
        send "{@combatprefix} &7You entered combat with &e%{_victim}%!" to {_attacker}
        if {combat::timer::%{_attacker}'s uuid%} isn't set:
            set {combat::timer::%{_attacker}'s uuid%} to true
            processCombat({_attacker})

function processCombat(p: player):
    while {combat::%{_p}'s uuid%} is set:
        if difference between now and {combat::%{_p}'s uuid%} >= {@combattimer}:
            endCombat({_p})
            stop
        set {_remaining} to {@combattimer} - (difference between now and {combat::%{_p}'s uuid%})
        send action bar "&cCombat: &e%{_remaining}%" to {_p}
        wait 0.5 seconds

function endCombat(p: player):
    send "{@combatprefix} &aYou are no longer in combat!" to {_p}
    delete {combat::%{_p}'s uuid%}
    delete {combat::timer::%{_p}'s uuid%}

on damage:
    attacker is player
    victim is player
    startCombat(victim, attacker)

on command:
    if {combat::%player's uuid%} is set:
        if {@allowcommands} is false:
            cancel event
            send "{@combatprefix} &cYou cannot use commands in combat!" to player

on quit:
    if {combat::%player's uuid%} is set:
        if {@allowescape} is false:
            kill player"""
                    },
                    {
                        "prompt": "pvp arena system with kits",
                        "code": """options:
    arena-world: world_pvp
    spawn-protection: 10
    
function Arena_JoinArena(p: player, arena: text):
    teleport {_p} to {arenas::%{_arena}%::spawn}
    clear {_p}'s inventory
    set {arena::%{_p}'s uuid%} to {_arena}
    set {arena::%{_p}'s uuid%::kills} to 0
    set {arena::%{_p}'s uuid%::deaths} to 0
    Arena_GiveKit({_p}, {arena::%{_p}'s uuid%::kit} ? "warrior")
    send "&aYou joined arena &e%{_arena}%!" to {_p}

function Arena_GiveKit(p: player, kit: text):
    clear {_p}'s inventory
    if {_kit} is "warrior":
        set helmet of {_p} to iron helmet
        set chestplate of {_p} to iron chestplate
        set leggings of {_p} to iron leggings
        set boots of {_p} to iron boots
        give {_p} 1 iron sword
        give {_p} 64 steak
    else if {_kit} is "archer":
        set helmet of {_p} to leather helmet
        set chestplate of {_p} to chainmail chestplate
        set leggings of {_p} to leather leggings
        set boots of {_p} to leather boots
        give {_p} 1 bow
        give {_p} 128 arrow
        give {_p} 1 stone sword
    else if {_kit} is "tank":
        set helmet of {_p} to diamond helmet
        set chestplate of {_p} to diamond chestplate
        set leggings of {_p} to diamond leggings
        set boots of {_p} to diamond boots
        give {_p} 1 stone sword
    apply slowness 1 to {_p} for 999 days if {_kit} is "tank"

on death:
    if {arena::%victim's uuid%} is set:
        add 1 to {arena::%victim's uuid%::deaths}
        if attacker is player:
            add 1 to {arena::%attacker's uuid%::kills}
            add 10 to {stats::%attacker's uuid%::coins}
            send "&aYou killed &e%victim% &aand earned &610 coins!" to attacker
        wait 1 tick
        Arena_Respawn(victim)

function Arena_Respawn(p: player):
    set {_arena} to {arena::%{_p}'s uuid%}
    teleport {_p} to {arenas::%{_arena}%::spawn}
    Arena_GiveKit({_p}, {arena::%{_p}'s uuid%::kit} ? "warrior")"""
                    }
                ]
            },
            {
                "category": "formatting_functions",
                "examples": [
                    {
                        "prompt": "format numbers with suffix like 1k, 1M, 1B",
                        "code": """function Formatter_NumberWithSuffix(n: number, places: integer = 1) :: text:
    set {_data} to "QT,18|Q,15|T,12|B,9|M,6|k,3"
    loop split {_data} at "|":
        set {_s::*} to split loop-value at ","
        {_n} >= 10 ^ {_s::2} parsed as number
        return "%round({_n} / 10 ^ {_s::2} parsed as number, {_places})%%{_s::1}%"
    return "%round({_n}, 1)%"""
                    },
                    {
                        "prompt": "format numbers with commas",
                        "code": """function Formatter_NumberWithCommas(n: object) :: text:
    if "%{_n}%" contains ".":
        set {_s::*} to split "%{_n}%" at "."
        set {_n} to "%a({_s::1})%.%last 2 characters of {_s::2}%"
        return "%{_n}%"
    else:
        set {_n} to a("%{_n}%")
        return "%{_n} ? 0%"
        
function a(b: text) :: text:
    if length of {_b} > 3:
        return "%a(first length of {_b} - 3 characters of {_b})%,%last 3 characters of {_b}%"
    return {_b}"""
                    },
                    {
                        "prompt": "convert hex colors to skript format",
                        "code": """function Formatter_HexToSkript(text: string) :: text:
    set {_s::*} to {_text} split at ""
    set {_i} to 1
    loop {_s::*}:
        set {_a} to {_s::%{_i}%}
        set {_b} to {_s::%{_i} + 1%}
        if {_a} is "&":
            if {_b} is "#":
                set {_replace} to ""
                loop 6 times:
                    set {_ind} to {_i} + 1 + loop-value-2
                    set {_replace} to "%{_replace}%%{_s::%{_ind}%}%"
                replace all "&#%{_replace}%" in {_text} with "<#%{_replace}%>"
        add 1 to {_i}
    return colored {_text}"""
                    }
                ]
            },
            {
                "category": "advanced_systems",
                "examples": [
                    {
                        "prompt": "stats system with custom nbt",
                        "code": """function Stats_LoadPlayer(p: player):
    set {_nbt} to custom nbt of {_p}
    set {stats::%{_p}'s uuid%::level} to int tag "level" of {_nbt} ? 1
    set {stats::%{_p}'s uuid%::exp} to int tag "exp" of {_nbt} ? 0
    set {stats::%{_p}'s uuid%::coins} to int tag "coins" of {_nbt} ? 0
    set {stats::%{_p}'s uuid%::playtime} to int tag "playtime" of {_nbt} ? 0

function Stats_SavePlayer(p: player):
    set int tag "level" of custom nbt of {_p} to {stats::%{_p}'s uuid%::level}
    set int tag "exp" of custom nbt of {_p} to {stats::%{_p}'s uuid%::exp}
    set int tag "coins" of custom nbt of {_p} to {stats::%{_p}'s uuid%::coins}
    set int tag "playtime" of custom nbt of {_p} to {stats::%{_p}'s uuid%::playtime}

function Stats_AddExp(p: player, amount: integer):
    add {_amount} to {stats::%{_p}'s uuid%::exp}
    set {_needed} to Stats_GetExpNeeded({stats::%{_p}'s uuid%::level})
    while {stats::%{_p}'s uuid%::exp} >= {_needed}:
        subtract {_needed} from {stats::%{_p}'s uuid%::exp}
        add 1 to {stats::%{_p}'s uuid%::level}
        Stats_LevelUp({_p})
        set {_needed} to Stats_GetExpNeeded({stats::%{_p}'s uuid%::level})
    Stats_SavePlayer({_p})

function Stats_GetExpNeeded(level: integer) :: integer:
    return round(100 * (1.5 ^ ({_level} - 1)))

function Stats_LevelUp(p: player):
    send "&6&lLEVEL UP! &eYou are now level &6%{stats::%{_p}'s uuid%::level}%!" to {_p}
    play sound "entity.player.levelup" to {_p}
    give {_p} 100 * {stats::%{_p}'s uuid%::level}
    send "&7Reward: &6$%100 * {stats::%{_p}'s uuid%::level}%" to {_p}"""
                    },
                    {
                        "prompt": "custom item system with nbt",
                        "code": """function Items_CreateCustomItem(id: text, name: text, lore: strings, material: itemtype) :: item:
    set {_item} to {_material}
    set string tag "customItem" of custom nbt of {_item} to {_id}
    set name of {_item} to colored {_name}
    set lore of {_item} to colored {_lore::*}
    return {_item}

function Items_GetCustomItemID(item: item) :: text:
    return string tag "customItem" of custom nbt of {_item}

function Items_CreateSword(tier: text) :: item:
    if {_tier} is "starter":
        set {_item} to Items_CreateCustomItem("sword_starter", "&7Starter Sword", ("&8A basic sword", "&7Damage: &c+5"), wooden sword)
        set int tag "damage" of custom nbt of {_item} to 5
    else if {_tier} is "warrior":
        set {_item} to Items_CreateCustomItem("sword_warrior", "&6Warrior Sword", ("&8A warrior's blade", "&7Damage: &c+15"), iron sword)
        set int tag "damage" of custom nbt of {_item} to 15
    else if {_tier} is "legendary":
        set {_item} to Items_CreateCustomItem("sword_legendary", "&6&lLegendary Sword", ("&8Forged by ancient smiths", "&7Damage: &c+50", "&7Special: &e20% Crit Chance"), diamond sword)
        set int tag "damage" of custom nbt of {_item} to 50
        set int tag "critChance" of custom nbt of {_item} to 20
    return {_item}

on damage:
    if attacker is player:
        set {_id} to Items_GetCustomItemID(attacker's tool)
        if {_id} is set:
            set {_damage} to int tag "damage" of custom nbt of attacker's tool
            set {_crit} to int tag "critChance" of custom nbt of attacker's tool
            if {_crit} > 0:
                chance of {_crit}%:
                    set {_damage} to {_damage} * 2
                    send action bar "&c&lCRITICAL HIT!" to attacker
            set damage to {_damage}"""
                    },
                    {
                        "prompt": "region protection with worldguard",
                        "code": """function Region_IsProtected(loc: location, p: player) :: boolean:
    set {_regions::*} to regions at {_loc}
    loop {_regions::*}:
        if loop-value contains "spawn" or "pvp_disabled":
            if {_p} doesn't have permission "region.bypass":
                return true
    return false

on block break:
    if Region_IsProtected(event-location, player) is true:
        cancel event
        send "&cYou cannot break blocks in this protected region!" to player

on block place:
    if Region_IsProtected(event-location, player) is true:
        cancel event
        send "&cYou cannot place blocks in this protected region!" to player

function Region_CreateRegion(p: player, name: text):
    if {region::creation::%{_p}'s uuid%::pos1} isn't set:
        send "&cPlease set position 1 first with /region pos1" to {_p}
        stop
    if {region::creation::%{_p}'s uuid%::pos2} isn't set:
        send "&cPlease set position 2 first with /region pos2" to {_p}
        stop
    
    set {regions::%{_name}%::pos1} to {region::creation::%{_p}'s uuid%::pos1}
    set {regions::%{_name}%::pos2} to {region::creation::%{_p}'s uuid%::pos2}
    set {regions::%{_name}%::owner} to {_p}'s uuid
    set {regions::%{_name}%::created} to now
    
    delete {region::creation::%{_p}'s uuid%::*}
    send "&aRegion &e%{_name}% &acreated successfully!" to {_p}"""
                    }
                ]
            },
            {
                "category": "optimization_patterns",
                "examples": [
                    {
                        "prompt": "efficient data handling with metadata",
                        "code": """function Data_SetTempValue(p: player, key: text, value: object):
    set metadata value {_key} of {_p} to {_value}

function Data_GetTempValue(p: player, key: text) :: object:
    return metadata value {_key} of {_p}

function Data_ClearTempValue(p: player, key: text):
    delete metadata value {_key} of {_p}

on right click:
    if Data_GetTempValue(player, "lastClick") is set:
        if difference between now and Data_GetTempValue(player, "lastClick") < 0.5 seconds:
            cancel event
            send "&cPlease don't spam click!" to player
            stop
    Data_SetTempValue(player, "lastClick", now)

on quit:
    loop metadata values of player:
        delete loop-value"""
                    },
                    {
                        "prompt": "async task processing",
                        "code": """function Task_ProcessAsync(task: text, data: objects):
    create new section stored in {_section}:
        if {_task} is "savePlayerData":
            loop {_data::*}:
                if loop-value is player:
                    Stats_SavePlayer(loop-value)
                    wait 1 tick
        else if {_task} is "loadChunks":
            loop {_data::*}:
                if loop-value is location:
                    load chunk at loop-value
                    wait 2 ticks
    run section {_section} async and wait

function Task_BatchProcess(items: objects, batchSize: integer = 10):
    set {_processed} to 0
    loop {_items::*}:
        add loop-value to {_batch::*}
        add 1 to {_processed}
        if size of {_batch::*} >= {_batchSize}:
            Task_ProcessBatch({_batch::*})
            delete {_batch::*}
            wait 1 tick
    if {_batch::*} is set:
        Task_ProcessBatch({_batch::*})"""
                    }
                ]
            },
            {
                "category": "event_handling",
                "examples": [
                    {
                        "prompt": "advanced join system with rewards",
                        "code": """options:
    firstjoin: "&8[&a+&8] %{_prefix}%%player% <#FFA545>(#%{_joinCount}%)"
    join: "&8[&a+&8] %{_prefix}%%player%"
    quit: "&8[&c-&8] %{_prefix}%%player%"

on first join:
    set {_prefix} to Formatter_HexToSkript(player's prefix)
    set {_joinCount} to size of offline players
    set join message to {@firstjoin}
    Join_FirstJoinSetup(player)
    
function Join_FirstJoinSetup(p: player):
    wait 1 tick
    send centered "<#FFA545>&lWELCOME TO THE SERVER" to {_p}
    send centered "<#ffde66>Thanks for joining us!" to {_p}
    wait 2 seconds
    teleport {_p} to {spawn}
    give {_p} 1 diamond sword named "&6Starter Sword"
    give {_p} 32 steak
    set {stats::%{_p}'s uuid%::firstJoin} to now
    add 1000 to {stats::%{_p}'s uuid%::coins}
    send "&aYou received &6$1,000 &aas a welcome bonus!" to {_p}
    
on join:
    set {_prefix} to Formatter_HexToSkript(player's prefix)
    set join message to {@join}
    Join_HandleReturning(player)
    
function Join_HandleReturning(p: player):
    Stats_LoadPlayer({_p})
    if {stats::%{_p}'s uuid%::lastJoin} is set:
        set {_offline} to difference between now and {stats::%{_p}'s uuid%::lastJoin}
        send "&7You were offline for &e%{_offline}%" to {_p}
    set {stats::%{_p}'s uuid%::lastJoin} to now
    
    if {dailyReward::%{_p}'s uuid%::lastClaim} is not set:
        send "&6&lDAILY REWARD! &eType /daily to claim!" to {_p}
    else:
        set {_nextDaily} to {dailyReward::%{_p}'s uuid%::lastClaim} + 24 hours
        if now >= {_nextDaily}:
            send "&6&lDAILY REWARD! &eType /daily to claim!" to {_p}"""
                    }
                ]
            }
        ]

class SkDuckyModelTrainer:
    def __init__(self):
        self.model_name = "microsoft/DialoGPT-medium"
        self.output_dir = "./models/skducky-gpt"
        
    def prepare_dataset(self, examples):
        formatted_data = []
        
        for category in examples:
            for example in category["examples"]:
                conversation = f"Human: {example['prompt']}\nAssistant: Here's the advanced Skript code:\n```skript\n{example['code']}\n```\n"
                formatted_data.append(conversation)
                
        return formatted_data
    
    def train(self):
        data = SkDuckyTrainingData()
        examples = data.get_training_examples()
        
        formatted_data = self.prepare_dataset(examples)
        
        with open(f"{self.output_dir}/training_data.txt", "w") as f:
            f.write("\n\n".join(formatted_data))
            
        tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
        model = GPT2LMHeadModel.from_pretrained(self.model_name)
        
        tokenizer.pad_token = tokenizer.eos_token
        
        special_tokens = {
            "additional_special_tokens": [
                "[SKRIPT]", "[FUNCTION]", "[OPTIONS]", "[EVENT]", 
                "[COMMAND]", "[NBT]", "[UUID]", "[ASYNC]"
            ]
        }
        tokenizer.add_special_tokens(special_tokens)
        model.resize_token_embeddings(len(tokenizer))
        
        dataset = Dataset.from_dict({"text": formatted_data})
        
        def tokenize_function(examples):
            return tokenizer(
                examples["text"], 
                truncation=True, 
                padding=True, 
                max_length=512
            )
            
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            save_steps=1000,
            save_total_limit=2,
            prediction_loss_only=True,
            logging_steps=100,
            logging_dir=f"{self.output_dir}/logs",
            warmup_steps=500,
            learning_rate=5e-5,
            fp16=torch.cuda.is_available(),
        )
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
        )
        
        trainer = Trainer(
            model=model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=tokenized_dataset,
        )
        
        trainer.train()
        trainer.save_model()
        tokenizer.save_pretrained(self.output_dir)
        
        print(f"SkDucky AI model trained and saved to {self.output_dir}")

if __name__ == "__main__":
    trainer = SkDuckyModelTrainer()
    trainer.train()