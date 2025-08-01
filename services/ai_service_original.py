import torch
import json
import re
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    GPT2LMHeadModel,
    GPT2Tokenizer
)
from typing import List, Dict, Optional
import numpy as np
from models import AIRequest, AIResponse

class SkDuckyAIService:
    def __init__(self, model_path: str = "./models/skducky-gpt"):
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.load_model()
        self.load_advanced_knowledge()
        
    def load_model(self):
        try:
            self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_path)
            self.model = GPT2LMHeadModel.from_pretrained(self.model_path)
        except:
            print("Loading base model...")
            self.tokenizer = GPT2Tokenizer.from_pretrained("microsoft/DialoGPT-medium")
            self.model = GPT2LMHeadModel.from_pretrained("microsoft/DialoGPT-medium")
            
        self.model.to(self.device)
        self.model.eval()
        
        special_tokens = {
            "additional_special_tokens": [
                "[SKRIPT]", "[FUNCTION]", "[OPTIONS]", "[EVENT]", 
                "[COMMAND]", "[NBT]", "[UUID]", "[ASYNC]", "[METADATA]"
            ]
        }
        self.tokenizer.add_special_tokens(special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))
        
    def load_advanced_knowledge(self):
        self.knowledge = {
            "patterns": {
                "combat_log_advanced": {
                    "description": "Professional combat log system with full customization",
                    "template": """options:
    combatprefix: &e&lCombat &7⇒
    combattimer: 20 seconds
    allowescape: false
    allowcommands: false
    allowregionenter: false
    waitprocesscombat: 0.5 seconds
    
function startCombat(victim: player, attacker: player):
    set {_victimWasInCombat} to {combat::%{_victim}'s uuid%} is set
    set {_attackerWasInCombat} to {combat::%{_attacker}'s uuid%} is set
    
    set {combat::%{_victim}'s uuid%} to now
    set {combat::%{_attacker}'s uuid%} to now
    
    if {_victimWasInCombat} is false:
        send "{@combatprefix} &7Entered combat with &e%{_attacker}%!" to {_victim}
        play sound "entity.experience_orb.pickup" with pitch 0.5 to {_victim}
        if {combat::timer::%{_victim}'s uuid%} isn't set:
            set {combat::timer::%{_victim}'s uuid%} to true
            processCombat({_victim})
    
    if {_attackerWasInCombat} is false:
        send "{@combatprefix} &7Entered combat with &e%{_victim}%!" to {_attacker}
        play sound "entity.experience_orb.pickup" with pitch 0.5 to {_attacker}
        if {combat::timer::%{_attacker}'s uuid%} isn't set:
            set {combat::timer::%{_attacker}'s uuid%} to true
            processCombat({_attacker})

function processCombat(p: player):
    while {combat::%{_p}'s uuid%} is set:
        if difference between now and {combat::%{_p}'s uuid%} >= {@combattimer}:
            endCombat({_p})
            stop
        set {_timer} to difference between now and {combat::%{_p}'s uuid%}
        set {_remaining} to {@combattimer} - {_timer}
        send action bar "&c⚔ Combat: &e%{_remaining}% &c⚔" to {_p}
        wait {@waitprocesscombat}

function endCombat(p: player):
    play sound "entity.player.levelup" with pitch 2 to {_p}
    send "{@combatprefix} &aYou are no longer in combat!" to {_p}
    delete {combat::%{_p}'s uuid%}
    delete {combat::timer::%{_p}'s uuid%}

function onCommandCombat(p: player) :: boolean:
    if {combat::%{_p}'s uuid%} isn't set:
        return true
    if {@allowcommands} is false:
        send "{@combatprefix} &cYou cannot use commands in combat!" to {_p}
        play sound "entity.villager.no" to {_p}
        return false
    return true

on damage:
    attacker is player
    victim is player
    "%region at attacker%" doesn't contain "spawn" or "safezone"
    "%region at victim%" doesn't contain "spawn" or "safezone"
    startCombat(victim, attacker)

on command:
    onCommandCombat(player) is false
    cancel event

on quit:
    if {combat::%player's uuid%} is set:
        if {@allowescape} is false:
            kill player
            broadcast "&c%player% &7logged out during combat and died!"

on death:
    victim is player
    delete {combat::%victim's uuid%}
    delete {combat::timer::%victim's uuid%}"""
                },
                "advanced_stats_nbt": {
                    "description": "Player stats system using custom NBT storage",
                    "template": """function Stats_LoadPlayer(p: player):
    set {_nbt} to custom nbt of {_p}
    set {stats::%{_p}'s uuid%::level} to int tag "stats.level" of {_nbt} ? 1
    set {stats::%{_p}'s uuid%::exp} to int tag "stats.exp" of {_nbt} ? 0
    set {stats::%{_p}'s uuid%::coins} to int tag "stats.coins" of {_nbt} ? 0
    set {stats::%{_p}'s uuid%::kills} to int tag "stats.kills" of {_nbt} ? 0
    set {stats::%{_p}'s uuid%::deaths} to int tag "stats.deaths" of {_nbt} ? 0
    set {stats::%{_p}'s uuid%::playtime} to int tag "stats.playtime" of {_nbt} ? 0

function Stats_SavePlayer(p: player):
    set int tag "stats.level" of custom nbt of {_p} to {stats::%{_p}'s uuid%::level}
    set int tag "stats.exp" of custom nbt of {_p} to {stats::%{_p}'s uuid%::exp}
    set int tag "stats.coins" of custom nbt of {_p} to {stats::%{_p}'s uuid%::coins}
    set int tag "stats.kills" of custom nbt of {_p} to {stats::%{_p}'s uuid%::kills}
    set int tag "stats.deaths" of custom nbt of {_p} to {stats::%{_p}'s uuid%::deaths}
    set int tag "stats.playtime" of custom nbt of {_p} to {stats::%{_p}'s uuid%::playtime}

function Stats_AddExp(p: player, amount: integer):
    add {_amount} to {stats::%{_p}'s uuid%::exp}
    set {_needed} to Stats_GetExpNeeded({stats::%{_p}'s uuid%::level})
    set {_leveledUp} to false
    
    while {stats::%{_p}'s uuid%::exp} >= {_needed}:
        subtract {_needed} from {stats::%{_p}'s uuid%::exp}
        add 1 to {stats::%{_p}'s uuid%::level}
        set {_leveledUp} to true
        Stats_OnLevelUp({_p})
        set {_needed} to Stats_GetExpNeeded({stats::%{_p}'s uuid%::level})
    
    Stats_SavePlayer({_p})
    Stats_UpdateScoreboard({_p})

function Stats_GetExpNeeded(level: integer) :: integer:
    return round(100 * (1.5 ^ ({_level} - 1)))

function Stats_OnLevelUp(p: player):
    send title "&6&lLEVEL UP!" with subtitle "&eYou are now level %{stats::%{_p}'s uuid%::level}%!" to {_p}
    play sound "entity.player.levelup" to {_p}
    set {_reward} to 100 * {stats::%{_p}'s uuid%::level}
    add {_reward} to {stats::%{_p}'s uuid%::coins}
    send "&7Rewards: &6$%Formatter_NumberWithCommas({_reward})%" to {_p}
    broadcast "&e%{_p}% &7reached level &6%{stats::%{_p}'s uuid%::level}%!"

on join:
    Stats_LoadPlayer(player)
    wait 5 ticks
    Stats_UpdateScoreboard(player)

on quit:
    Stats_SavePlayer(player)

every 5 minutes:
    loop all players:
        add 300 to {stats::%loop-player's uuid%::playtime}
        Stats_SavePlayer(loop-player)"""
                },
                "formatter_functions": {
                    "description": "Advanced number and text formatting utilities",
                    "template": """function Formatter_NumberWithSuffix(n: number, places: integer = 1) :: text:
    set {_data} to "QT,18|Q,15|T,12|B,9|M,6|k,3"
    loop split {_data} at "|":
        set {_s::*} to split loop-value at ","
        {_n} >= 10 ^ {_s::2} parsed as number
        return "%round({_n} / 10 ^ {_s::2} parsed as number, {_places})%%{_s::1}%"
    return "%round({_n}, 1)%"

function Formatter_NumberWithCommas(n: object) :: text:
    if "%{_n}%" contains ".":
        set {_s::*} to split "%{_n}%" at "."
        set {_n} to "%Formatter_AddCommas({_s::1})%.%last 2 characters of {_s::2}%"
        return "%{_n}%"
    else:
        set {_n} to Formatter_AddCommas("%{_n}%")
        return "%{_n} ? 0%"

function Formatter_AddCommas(b: text) :: text:
    if length of {_b} > 3:
        return "%Formatter_AddCommas(first length of {_b} - 3 characters of {_b})%,%last 3 characters of {_b}%"
    return {_b}

function Formatter_HexToSkript(text: string) :: text:
    set {_s::*} to {_text} split at ""
    set {_i} to 1
    loop {_s::*}:
        set {_a} to {_s::%{_i}%}
        set {_b} to {_s::%{_i} + 1%}
        if {_a} is "&" and {_b} is "#":
            set {_replace} to ""
            loop 6 times:
                set {_ind} to {_i} + 1 + loop-value-2
                set {_replace} to "%{_replace}%%{_s::%{_ind}%}%"
            replace all "&#%{_replace}%" in {_text} with "<#%{_replace}%>"
        add 1 to {_i}
    return colored {_text}

function Formatter_TimeSpan(seconds: number) :: text:
    set {_days} to floor({_seconds} / 86400)
    set {_hours} to floor(mod({_seconds}, 86400) / 3600)
    set {_minutes} to floor(mod({_seconds}, 3600) / 60)
    set {_secs} to floor(mod({_seconds}, 60))
    
    set {_result} to ""
    if {_days} > 0:
        set {_result} to "%{_days}%d "
    if {_hours} > 0:
        set {_result} to "%{_result}%%{_hours}%h "
    if {_minutes} > 0:
        set {_result} to "%{_result}%%{_minutes}%m "
    if {_secs} > 0 or {_result} is "":
        set {_result} to "%{_result}%%{_secs}%s"
    
    return {_result}"""
                },
                "custom_items_nbt": {
                    "description": "Advanced custom item system with NBT data",
                    "template": """function Items_CreateCustom(id: text, name: text, lore: strings, material: itemtype, data: objects = {}) :: item:
    set {_item} to {_material}
    set string tag "id" of custom nbt of {_item} to {_id}
    set string tag "tier" of custom nbt of {_item} to {_data::tier} ? "common"
    set name of {_item} to Formatter_HexToSkript({_name})
    
    set {_finalLore::*} to {_lore::*}
    loop {_data::*}:
        set {_key} to loop-index
        set {_value} to loop-value
        if {_key} is "damage":
            add "&7Damage: &c+%{_value}%" to {_finalLore::*}
            set int tag "stats.damage" of custom nbt of {_item} to {_value}
        else if {_key} is "defense":
            add "&7Defense: &a+%{_value}%" to {_finalLore::*}
            set int tag "stats.defense" of custom nbt of {_item} to {_value}
        else if {_key} is "speed":
            add "&7Speed: &b+%{_value}%%%" to {_finalLore::*}
            set int tag "stats.speed" of custom nbt of {_item} to {_value}
        else if {_key} is "ability":
            add "" to {_finalLore::*}
            add "&6Ability: &e%{_value}%" to {_finalLore::*}
            set string tag "ability" of custom nbt of {_item} to {_value}
    
    set lore of {_item} to colored {_finalLore::*}
    return {_item}

function Items_GetStat(item: item, stat: text) :: number:
    return int tag "stats.%{_stat}%" of custom nbt of {_item} ? 0

function Items_GetID(item: item) :: text:
    return string tag "id" of custom nbt of {_item}

function Items_CreateTieredSword(tier: text) :: item:
    if {_tier} is "starter":
        return Items_CreateCustom("sword_starter", "&7Starter Sword", ("&8A basic training sword"), wooden sword, {damage: 5})
    else if {_tier} is "iron":
        return Items_CreateCustom("sword_iron", "&fIron Sword", ("&8A standard iron blade"), iron sword, {damage: 10, tier: "common"})
    else if {_tier} is "enchanted":
        return Items_CreateCustom("sword_enchanted", "&b&lEnchanted Sword", ("&8Infused with magical power"), diamond sword, {damage: 25, speed: 10, tier: "rare", ability: "10% chance to heal on hit"})
    else if {_tier} is "legendary":
        return Items_CreateCustom("sword_legendary", "&6&lLegendary Blade", ("&8Forged by ancient masters", "&8Contains untold power"), netherite sword, {damage: 50, defense: 10, speed: 20, tier: "legendary", ability: "Lightning Strike"})

on damage:
    if attacker is player:
        set {_id} to Items_GetID(attacker's tool)
        if {_id} is set:
            set {_damage} to Items_GetStat(attacker's tool, "damage")
            set {_ability} to string tag "ability" of custom nbt of attacker's tool
            
            if {_damage} > 0:
                set damage to {_damage}
                
            if {_ability} is "10% chance to heal on hit":
                chance of 10%:
                    heal attacker by 2
                    send action bar "&a&l+ HEAL" to attacker
                    
            else if {_ability} is "Lightning Strike":
                chance of 15%:
                    strike lightning at victim
                    send action bar "&e&l⚡ LIGHTNING STRIKE" to attacker"""
                },
                "advanced_gui_system": {
                    "description": "Professional GUI system with pagination",
                    "template": """function GUI_Create(p: player, title: text, rows: integer) :: inventory:
    set {_gui} to chest inventory with {_rows} rows named Formatter_HexToSkript({_title})
    set metadata value "gui" of {_p} to {_gui}
    return {_gui}

function GUI_SetItem(gui: inventory, slot: integer, item: item, action: text = ""):
    set slot {_slot} of {_gui} to {_item}
    if {_action} is not "":
        set {gui::actions::%{_gui}%::%{_slot}%} to {_action}

function GUI_FillBorder(gui: inventory, item: item):
    set {_rows} to rows of {_gui}
    loop integers from 0 to 8:
        set slot loop-value of {_gui} to {_item}
    loop integers from ({_rows} * 9 - 9) to ({_rows} * 9 - 1):
        set slot loop-value of {_gui} to {_item}
    loop integers from 1 to ({_rows} - 2):
        set slot (loop-value * 9) of {_gui} to {_item}
        set slot (loop-value * 9 + 8) of {_gui} to {_item}

function GUI_Paginate(p: player, title: text, items: items, page: integer = 1):
    set {_gui} to GUI_Create({_p}, {_title}, 6)
    set {_border} to black stained glass pane named "&7"
    GUI_FillBorder({_gui}, {_border})
    
    set {_perPage} to 28
    set {_start} to ({_page} - 1) * {_perPage} + 1
    set {_end} to min({_start} + {_perPage} - 1, size of {_items::*})
    
    set {_slot} to 10
    loop integers from {_start} to {_end}:
        if {_items::%loop-value%} is set:
            set slot {_slot} of {_gui} to {_items::%loop-value%}
            add 1 to {_slot}
            if mod({_slot}, 9) = 8:
                add 2 to {_slot}
    
    set {_maxPage} to ceil(size of {_items::*} / {_perPage})
    
    if {_page} > 1:
        set slot 48 of {_gui} to arrow named "&ePrevious Page" with lore "&7Page %{_page} - 1%"
        set {gui::actions::%{_gui}%::48} to "page:%{_page} - 1%"
    
    set slot 49 of {_gui} to book named "&ePage %{_page}%/%{_maxPage}%"
    
    if {_page} < {_maxPage}:
        set slot 50 of {_gui} to arrow named "&eNext Page" with lore "&7Page %{_page} + 1%"
        set {gui::actions::%{_gui}%::50} to "page:%{_page} + 1%"
    
    open {_gui} to {_p}

on inventory click:
    if metadata value "gui" of player is event-inventory:
        cancel event
        if {gui::actions::%event-inventory%::%index of event-slot%} is set:
            set {_action} to {gui::actions::%event-inventory%::%index of event-slot%}
            if {_action} starts with "page:":
                set {_page} to last element of split {_action} at ":"
                GUI_Paginate(player, name of event-inventory, {shop::items::*}, {_page} parsed as integer)"""
                },
                "async_data_processing": {
                    "description": "Asynchronous data processing for performance",
                    "template": """function Async_SaveAllPlayers():
    create section stored in {_section}:
        loop all players:
            Stats_SavePlayer(loop-player)
            wait 2 ticks
        send "[System] All player data saved" to console
    run section {_section} async

function Async_LoadChunks(locations: locations):
    create section stored in {_section}:
        loop {_locations::*}:
            load chunk at loop-value
            wait 1 tick
    run section {_section} async

function Async_ProcessQueue(queue: text):
    create section stored in {_section}:
        while {queue::%{_queue}%::*} is set:
            set {_item} to first element of {queue::%{_queue}%::*}
            remove {_item} from {queue::%{_queue}%::*}
            
            if {_queue} is "rewards":
                Process_Reward({_item})
            else if {_queue} is "saves":
                Stats_SavePlayer({_item})
            
            wait 1 tick
    run section {_section} async

every 5 minutes:
    Async_SaveAllPlayers()

on quit:
    add player to {queue::saves::*}
    Async_ProcessQueue("saves")"""
                },
                "metadata_optimization": {
                    "description": "Using metadata for temporary storage optimization",
                    "template": """function Meta_Set(p: player, key: text, value: object):
    set metadata value {_key} of {_p} to {_value}

function Meta_Get(p: player, key: text) :: object:
    return metadata value {_key} of {_p}

function Meta_Delete(p: player, key: text):
    delete metadata value {_key} of {_p}

function Meta_Has(p: player, key: text) :: boolean:
    return metadata value {_key} of {_p} is set

function Meta_Clear(p: player):
    loop metadata values of {_p}:
        delete loop-value

on inventory click:
    if Meta_Get(player, "clickCooldown") is set:
        if difference between now and Meta_Get(player, "clickCooldown") < 0.2 seconds:
            cancel event
            stop
    Meta_Set(player, "clickCooldown", now)

on quit:
    Meta_Clear(player)

function Cooldown_Check(p: player, action: text, time: timespan) :: boolean:
    set {_key} to "cooldown_%{_action}%"
    if Meta_Has({_p}, {_key}):
        set {_last} to Meta_Get({_p}, {_key})
        if difference between now and {_last} < {_time}:
            set {_remaining} to {_time} - (difference between now and {_last})
            send "&cPlease wait %{_remaining}% before using this again!" to {_p}
            return false
    Meta_Set({_p}, {_key}, now)
    return true"""
                }
            },
            "modern_syntax": {
                "custom_nbt": "Use 'custom nbt' for all NBT operations in Skript 2.12.0+",
                "metadata": "Metadata is more efficient than variables for temporary data",
                "uuid_storage": "Always use player's uuid for persistent storage",
                "async_sections": "Use async sections for heavy operations",
                "function_returns": "Functions can return values with :: type syntax",
                "options": "Use options for configuration at the top of scripts"
            },
            "best_practices": [
                "Use functions for all reusable code blocks",
                "Store player data with UUID, not player name",
                "Use metadata for temporary data that doesn't need persistence",
                "Implement options for easy configuration",
                "Add custom NBT tags to items instead of lore parsing",
                "Use async sections for file I/O and heavy operations",
                "Batch process data to avoid lag spikes",
                "Cache frequently accessed data in metadata",
                "Use proper error handling with function returns",
                "Implement cooldowns with metadata instead of variables",
                "Format numbers for better readability",
                "Use hex colors with the Formatter_HexToSkript function",
                "Separate event handlers from logic with functions",
                "Use descriptive function names with underscore notation",
                "Always validate user input before processing"
            ]
        }
        
    def generate_code(self, request: AIRequest) -> AIResponse:
        prompt = request.prompt.lower()
        
        for pattern_key, pattern_data in self.knowledge["patterns"].items():
            keywords = pattern_key.replace('_', ' ').split()
            if any(keyword in prompt for keyword in keywords):
                suggestions = self.generate_advanced_suggestions(pattern_data["template"])
                return AIResponse(
                    code=pattern_data["template"],
                    explanation=pattern_data["description"] if request.include_explanation else None,
                    confidence=0.98,
                    suggestions=suggestions,
                    related_snippets=[k for k in self.knowledge["patterns"].keys() if k != pattern_key][:3]
                )
        
        formatted_prompt = self.format_advanced_prompt(request.prompt, request.context)
        code = self.generate_from_model(formatted_prompt, request)
        
        return AIResponse(
            code=code,
            explanation=self.generate_explanation(request.prompt, code) if request.include_explanation else None,
            confidence=self.calculate_confidence(code),
            suggestions=self.generate_advanced_suggestions(code),
            related_snippets=self.find_related_snippets(request.prompt)
        )
        
    def format_advanced_prompt(self, prompt: str, context: str) -> str:
        formatted = f"""[SKDUCKY] Generate advanced Skript code for: {prompt}
Remember to:
- Use functions for modularity
- Store data with player's UUID
- Use custom NBT for item data
- Implement proper error handling
- Use metadata for temporary data
- Add options for configuration

"""
        if context:
            formatted += f"Context:\n{context}\n\n"
            
        formatted += "Advanced Skript code:\n"
        return formatted
        
    def generate_from_model(self, formatted_prompt: str, request: AIRequest) -> str:
        inputs = self.tokenizer.encode(
            formatted_prompt, 
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=len(inputs[0]) + request.max_tokens,
                temperature=request.temperature,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                top_p=0.9,
                top_k=50
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return self.extract_code(generated_text)
        
    def extract_code(self, generated_text: str) -> str:
        lines = generated_text.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            if "Advanced Skript code:" in line or "[SKDUCKY]" in line:
                in_code = True
                continue
            if in_code and line.strip():
                code_lines.append(line)
                
        return '\n'.join(code_lines) if code_lines else generated_text
        
    def calculate_confidence(self, code: str) -> float:
        confidence = 0.6
        
        advanced_patterns = [
            ('function', 0.05),
            ('uuid%}', 0.05),
            ('custom nbt', 0.08),
            ('metadata', 0.05),
            ('options:', 0.05),
            (':: text', 0.03),
            (':: number', 0.03),
            (':: player', 0.03),
            ('async', 0.04),
            ('create section', 0.04)
        ]
        
        for pattern, weight in advanced_patterns:
            if pattern in code:
                confidence += weight
                
        if 'function' in code and '::' in code:
            confidence += 0.05
            
        return min(confidence, 0.98)
        
    def generate_explanation(self, prompt: str, code: str) -> str:
        explanation = f"Generated advanced Skript code for: {prompt}\n\n"
        
        if 'function' in code:
            functions = re.findall(r'function (\w+)', code)
            if functions:
                explanation += f"Functions created: {', '.join(functions)}\n"
                
        if 'custom nbt' in code:
            explanation += "Uses custom NBT for data storage (Skript 2.12.0+)\n"
            
        if 'metadata' in code:
            explanation += "Uses metadata for optimized temporary storage\n"
            
        if 'uuid%}' in code:
            explanation += "Implements UUID-based persistent storage\n"
            
        if 'options:' in code:
            explanation += "Includes configuration options for customization\n"
            
        if 'async' in code:
            explanation += "Uses asynchronous processing for better performance\n"
            
        return explanation.strip()
        
    def generate_advanced_suggestions(self, code: str) -> List[str]:
        suggestions = []
        
        if 'function' not in code:
            suggestions.append("Consider using functions for better code organization")
            
        if '{' in code and '%player%}' in code and "%player's uuid%}" not in code:
            suggestions.append("Use %player's uuid% instead of %player% for persistent storage")
            
        if 'set {' in code and 'metadata' not in code:
            suggestions.append("Consider using metadata for temporary data storage")
            
        if 'wait' in code and 'async' not in code:
            suggestions.append("Use async sections for operations with waits")
            
        if 'loop all players' in code and 'wait' not in code:
            suggestions.append("Add small waits in loops to prevent lag")
            
        if 'on damage' in code and 'custom nbt' not in code:
            suggestions.append("Consider using custom NBT for weapon stats")
            
        if len(suggestions) < 3:
            suggestions.extend(self.knowledge["best_practices"][:3-len(suggestions)])
            
        return suggestions[:5]
        
    def find_related_snippets(self, prompt: str) -> List[str]:
        related = []
        prompt_lower = prompt.lower()
        
        keywords = {
            "combat": ["combat_log_advanced", "advanced_stats_nbt"],
            "format": ["formatter_functions"],
            "item": ["custom_items_nbt"],
            "gui": ["advanced_gui_system"],
            "menu": ["advanced_gui_system"],
            "stats": ["advanced_stats_nbt"],
            "async": ["async_data_processing"],
            "metadata": ["metadata_optimization"]
        }
        
        for keyword, patterns in keywords.items():
            if keyword in prompt_lower:
                related.extend(patterns)
                
        return list(set(related))[:5]
        
    def autocomplete(self, code: str, cursor_position: int) -> List[Dict]:
        suggestions = []
        
        lines = code[:cursor_position].split('\n')
        current_line = lines[-1] if lines else ""
        indent = len(current_line) - len(current_line.lstrip())
        
        if not current_line.strip():
            suggestions.extend([
                {"text": "function ", "description": "Create advanced function", "type": "structure"},
                {"text": "options:", "description": "Configuration options", "type": "structure"},
                {"text": "command /", "description": "Create command", "type": "structure"},
                {"text": "on join:", "description": "Player join event", "type": "event"},
                {"text": "every 1 minute:", "description": "Periodic event", "type": "event"}
            ])
            
        elif current_line.strip().startswith('function'):
            suggestions.extend([
                {"text": " :: text:", "description": "Return text", "type": "return_type"},
                {"text": " :: number:", "description": "Return number", "type": "return_type"},
                {"text": " :: player:", "description": "Return player", "type": "return_type"},
                {"text": " :: boolean:", "description": "Return boolean", "type": "return_type"},
                {"text": " :: item:", "description": "Return item", "type": "return_type"}
            ])
            
        elif 'custom nbt' in current_line:
            suggestions.extend([
                {"text": " of player", "description": "Player's custom NBT", "type": "nbt"},
                {"text": " of player's tool", "description": "Item NBT", "type": "nbt"},
                {"text": " of {_item}", "description": "Variable item NBT", "type": "nbt"}
            ])
            
        elif current_line.strip() == 'set':
            suggestions.extend([
                {"text": " metadata value ", "description": "Set metadata (temporary)", "type": "storage"},
                {"text": " {stats::%player's uuid%::", "description": "Set persistent stat", "type": "storage"},
                {"text": " int tag \"\" of custom nbt of ", "description": "Set NBT integer", "type": "nbt"},
                {"text": " string tag \"\" of custom nbt of ", "description": "Set NBT string", "type": "nbt"}
            ])
            
        elif 'metadata' in current_line:
            suggestions.extend([
                {"text": " value \"\" of player", "description": "Player metadata", "type": "metadata"},
                {"text": " values of player", "description": "All metadata", "type": "metadata"}
            ])
            
        return suggestions