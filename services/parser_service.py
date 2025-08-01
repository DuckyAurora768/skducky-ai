import re
from typing import Dict, List, Tuple, Optional, Any
from models import ParseResult, ValidationResult

class SkriptParser:
    def __init__(self):
        self.load_syntax_rules()
        
    def load_syntax_rules(self):
        self.syntax = {
            "events": {
                "on join": {"description": "When a player joins the server", "since": "1.0"},
                "on quit": {"description": "When a player leaves the server", "since": "1.0"},
                "on death": {"description": "When an entity dies", "since": "1.0"},
                "on respawn": {"description": "When a player respawns", "since": "1.0"},
                "on chat": {"description": "When a player sends a chat message", "since": "1.0"},
                "on command": {"description": "When a command is executed", "since": "1.0"},
                "on block break": {"description": "When a block is broken", "since": "1.0"},
                "on block place": {"description": "When a block is placed", "since": "1.0"},
                "on damage": {"description": "When an entity takes damage", "since": "1.0"},
                "on right click": {"description": "Right click on block or air", "since": "1.0"},
                "on left click": {"description": "Left click on block or air", "since": "1.0"},
                "on inventory click": {"description": "Click in an inventory", "since": "1.0"},
                "on drop": {"description": "When a player drops an item", "since": "1.0"},
                "on pick up": {"description": "When a player picks up an item", "since": "1.0"},
                "on consume": {"description": "When a player consumes an item", "since": "1.0"},
                "on craft": {"description": "When a player crafts an item", "since": "1.0"},
                "on move": {"description": "When a player moves", "since": "2.0"},
                "on sneak toggle": {"description": "When a player toggles sneak", "since": "1.0"},
                "on sprint toggle": {"description": "When a player toggles sprint", "since": "1.0"},
                "on world change": {"description": "When a player changes world", "since": "1.0"},
                "on hunger meter change": {"description": "When hunger changes", "since": "1.0"},
                "on gamemode change": {"description": "When gamemode changes", "since": "1.0"},
                "on server list ping": {"description": "Server list ping event", "since": "2.3"}
            },
            "effects": {
                "send": {"syntax": "send %texts% to %players%", "description": "Send message"},
                "broadcast": {"syntax": "broadcast %texts%", "description": "Broadcast message"},
                "teleport": {"syntax": "teleport %entities% to %location%", "description": "Teleport entities"},
                "give": {"syntax": "give %items% to %players%", "description": "Give items"},
                "set": {"syntax": "set %~objects% to %objects%", "description": "Set value"},
                "add": {"syntax": "add %objects% to %~objects%", "description": "Add value"},
                "remove": {"syntax": "remove %objects% from %~objects%", "description": "Remove value"},
                "delete": {"syntax": "delete %~objects%", "description": "Delete variable"},
                "clear": {"syntax": "clear %~objects%", "description": "Clear variable"},
                "wait": {"syntax": "wait %timespan%", "description": "Delay execution"},
                "execute": {"syntax": "execute %players% command %texts%", "description": "Execute command"},
                "stop": {"syntax": "stop [trigger]", "description": "Stop execution"},
                "cancel": {"syntax": "cancel [the] event", "description": "Cancel event"},
                "kick": {"syntax": "kick %players% [(by reason of|because [of]|on account of|due to) %text%]", "description": "Kick player"},
                "ban": {"syntax": "ban %players% [(by reason of|because [of]|on account of|due to) %text%]", "description": "Ban player"},
                "kill": {"syntax": "kill %entities%", "description": "Kill entities"},
                "spawn": {"syntax": "spawn %entitytypes% [at %locations%]", "description": "Spawn entities"},
                "drop": {"syntax": "drop %items% [at %locations%]", "description": "Drop items"},
                "play": {"syntax": "play %sounds% [to %players%]", "description": "Play sound"},
                "shoot": {"syntax": "shoot %entitytype% [from %entity%] [at speed %number%]", "description": "Shoot projectile"}
            },
            "conditions": {
                "is": {"syntax": "%objects% (is|are) %objects%", "description": "Equality check"},
                "is not": {"syntax": "%objects% (is|are) not %objects%", "description": "Inequality check"},
                "contains": {"syntax": "%texts% contain[s] %texts%", "description": "Text contains"},
                "has permission": {"syntax": "%players% (has|have) permission %text%", "description": "Permission check"},
                "is online": {"syntax": "%offlineplayers% (is|are) online", "description": "Online check"},
                "exists": {"syntax": "%~objects% (exist[s]|is set)", "description": "Variable exists"},
                "is between": {"syntax": "%number% is between %number% and %number%", "description": "Range check"},
                "is wearing": {"syntax": "%entities% (is|are) wearing %itemtypes%", "description": "Armor check"},
                "is holding": {"syntax": "%players% (is|are) holding %itemtypes%", "description": "Item in hand"},
                "can see": {"syntax": "%players% can see %entities%", "description": "Visibility check"},
                "is op": {"syntax": "%players% (is|are) op[s]", "description": "Operator check"},
                "is banned": {"syntax": "%offlineplayers% (is|are) banned", "description": "Ban check"},
                "is flying": {"syntax": "%players% (is|are) flying", "description": "Flying check"},
                "is sneaking": {"syntax": "%players% (is|are) sneaking", "description": "Sneak check"},
                "is sprinting": {"syntax": "%players% (is|are) sprinting", "description": "Sprint check"}
            },
            "expressions": {
                "player": {"returns": "player", "description": "Event player"},
                "victim": {"returns": "entity", "description": "Event victim"},
                "attacker": {"returns": "entity", "description": "Event attacker"},
                "event-block": {"returns": "block", "description": "Event block"},
                "event-location": {"returns": "location", "description": "Event location"},
                "event-item": {"returns": "item", "description": "Event item"},
                "all players": {"returns": "players", "description": "All online players"},
                "world": {"returns": "world", "description": "World of entity"},
                "now": {"returns": "date", "description": "Current date/time"},
                "location": {"returns": "location", "description": "Location of entity"},
                "uuid": {"returns": "text", "description": "UUID of entity"},
                "name": {"returns": "text", "description": "Name of object"},
                "health": {"returns": "number", "description": "Health of entity"},
                "max health": {"returns": "number", "description": "Maximum health"},
                "food level": {"returns": "number", "description": "Hunger level"},
                "level": {"returns": "number", "description": "Experience level"},
                "gamemode": {"returns": "gamemode", "description": "Player gamemode"},
                "inventory": {"returns": "inventory", "description": "Entity inventory"},
                "balance": {"returns": "number", "description": "Economy balance"}
            }
        }
        
    def parse(self, code: str) -> ParseResult:
        lines = code.split('\n')
        ast = {
            "type": "SkriptFile",
            "body": [],
            "metadata": {
                "lineCount": len(lines),
                "events": 0,
                "commands": 0,
                "functions": 0,
                "options": {}
            }
        }
        
        errors = []
        warnings = []
        current_block = None
        block_stack = []
        indent_size = None
        
        for line_num, line in enumerate(lines):
            indent = len(line) - len(line.lstrip())
            stripped = line.strip()
            
            if not stripped or stripped.startswith('#'):
                continue
                
            if indent > 0 and indent_size is None:
                indent_size = indent
                
            indent_level = indent // indent_size if indent_size else 0
            
            if stripped.startswith('options:'):
                current_block = {
                    "type": "Options",
                    "line": line_num,
                    "values": {}
                }
                ast["body"].append(current_block)
                block_stack = [current_block]
                
            elif re.match(r'^on\s+', stripped):
                event_match = re.match(r'^on\s+(.+?):', stripped)
                if event_match:
                    event_name = event_match.group(1)
                    current_block = {
                        "type": "Event",
                        "trigger": event_name,
                        "line": line_num,
                        "body": []
                    }
                    ast["body"].append(current_block)
                    ast["metadata"]["events"] += 1
                    block_stack = [current_block]
                else:
                    errors.append({
                        "line": line_num + 1,
                        "message": "Event missing colon at end",
                        "severity": "error"
                    })
                    
            elif re.match(r'^command\s+/', stripped):
                cmd_match = re.match(r'^command\s+/(\S+)(?:\s+(.+?))?:', stripped)
                if cmd_match:
                    cmd_name = cmd_match.group(1)
                    cmd_args = cmd_match.group(2) or ""
                    current_block = {
                        "type": "Command",
                        "name": cmd_name,
                        "arguments": self.parse_command_args(cmd_args),
                        "line": line_num,
                        "body": [],
                        "properties": {}
                    }
                    ast["body"].append(current_block)
                    ast["metadata"]["commands"] += 1
                    block_stack = [current_block]
                else:
                    errors.append({
                        "line": line_num + 1,
                        "message": "Command syntax error",
                        "severity": "error"
                    })
                    
            elif re.match(r'^function\s+', stripped):
                func_match = re.match(r'^function\s+(\w+)\s*\((.*?)\)(?:\s*::\s*(\w+))?:', stripped)
                if func_match:
                    func_name = func_match.group(1)
                    func_params = func_match.group(2)
                    return_type = func_match.group(3)
                    current_block = {
                        "type": "Function",
                        "name": func_name,
                        "parameters": self.parse_function_params(func_params),
                        "return_type": return_type,
                        "line": line_num,
                        "body": []
                    }
                    ast["body"].append(current_block)
                    ast["metadata"]["functions"] += 1
                    block_stack = [current_block]
                    
            elif current_block and indent_level > 0:
                if current_block["type"] == "Command" and indent_level == 1:
                    prop_match = re.match(r'^(permission|description|usage|aliases|executable by|cooldown|cooldown message|cooldown bypass|cooldown storage):\s*(.+)', stripped)
                    if prop_match:
                        prop_name = prop_match.group(1)
                        prop_value = prop_match.group(2)
                        current_block["properties"][prop_name] = prop_value
                        continue
                        
                if re.match(r'^trigger:', stripped):
                    trigger_block = {
                        "type": "Trigger",
                        "line": line_num,
                        "body": []
                    }
                    current_block["trigger"] = trigger_block
                    block_stack.append(trigger_block)
                    continue
                    
                while len(block_stack) > indent_level:
                    block_stack.pop()
                    
                if block_stack:
                    statement = self.parse_statement(stripped, line_num)
                    if statement:
                        if "body" in block_stack[-1]:
                            block_stack[-1]["body"].append(statement)
                        elif block_stack[-1].get("type") == "Trigger" and "body" in block_stack[-1]:
                            block_stack[-1]["body"].append(statement)
                            
                        if statement["type"] in ["IfStatement", "ElseStatement", "Loop"]:
                            block_stack.append(statement)
                            
        validation_errors = self.validate_ast(ast)
        errors.extend(validation_errors)
        
        return ParseResult(
            success=len(errors) == 0,
            ast=ast,
            errors=errors,
            warnings=warnings,
            syntax_tree=self.generate_syntax_tree(ast)
        )
        
    def parse_command_args(self, args_string: str) -> List[Dict]:
        if not args_string:
            return []
            
        args = []
        pattern = r'<([^:>]+)(?::([^>]+))?(?:=([^>]+))?>'
        
        for match in re.finditer(pattern, args_string):
            arg_name = match.group(1)
            arg_type = match.group(2) or "text"
            default_value = match.group(3)
            
            args.append({
                "name": arg_name,
                "type": arg_type,
                "required": default_value is None,
                "default": default_value
            })
            
        return args
        
    def parse_function_params(self, params_string: str) -> List[Dict]:
        if not params_string.strip():
            return []
            
        params = []
        param_pattern = r'(\w+):\s*(\w+(?:\s*\[\])?)\s*(?:=\s*(.+?))?(?:,|$)'
        
        for match in re.finditer(param_pattern, params_string):
            param_name = match.group(1)
            param_type = match.group(2)
            default_value = match.group(3)
            
            params.append({
                "name": param_name,
                "type": param_type,
                "required": default_value is None,
                "default": default_value
            })
            
        return params
        
    def parse_statement(self, line: str, line_num: int) -> Optional[Dict]:
        if line.startswith('if '):
            condition_match = re.match(r'^if\s+(.+?):', line)
            if condition_match:
                return {
                    "type": "IfStatement",
                    "condition": self.parse_expression(condition_match.group(1)),
                    "line": line_num,
                    "body": []
                }
                
        elif line == 'else:':
            return {
                "type": "ElseStatement",
                "line": line_num,
                "body": []
            }
            
        elif line.startswith('else if '):
            condition_match = re.match(r'^else\s+if\s+(.+?):', line)
            if condition_match:
                return {
                    "type": "ElseIfStatement",
                    "condition": self.parse_expression(condition_match.group(1)),
                    "line": line_num,
                    "body": []
                }
                
        elif line.startswith('loop '):
            loop_match = re.match(r'^loop\s+(.+?):', line)
            if loop_match:
                return {
                    "type": "Loop",
                    "iterator": loop_match.group(1),
                    "line": line_num,
                    "body": []
                }
                
        elif line.startswith('while '):
            condition_match = re.match(r'^while\s+(.+?):', line)
            if condition_match:
                return {
                    "type": "WhileLoop",
                    "condition": self.parse_expression(condition_match.group(1)),
                    "line": line_num,
                    "body": []
                }
                
        else:
            return self.parse_effect(line, line_num)
            
    def parse_effect(self, line: str, line_num: int) -> Dict:
        for effect_name, effect_info in self.syntax["effects"].items():
            if line.startswith(effect_name):
                return {
                    "type": "Effect",
                    "effect": effect_name,
                    "line": line_num,
                    "raw": line,
                    "parsed": self.parse_effect_arguments(line, effect_name)
                }
                
        return {
            "type": "Effect",
            "effect": "unknown",
            "line": line_num,
            "raw": line
        }
        
    def parse_expression(self, expr: str) -> Dict:
        if '{' in expr and '}' in expr:
            var_matches = re.findall(r'\{([^}]+)\}', expr)
            variables = []
            for var in var_matches:
                is_local = var.startswith('_')
                is_list = '::' in var or var.endswith('*')
                variables.append({
                    "name": var,
                    "local": is_local,
                    "list": is_list
                })
            
            return {
                "type": "Expression",
                "raw": expr,
                "variables": variables
            }
            
        for op in ['is not', 'is', 'contains', '>=', '<=', '>', '<', '=']:
            if f' {op} ' in expr:
                parts = expr.split(f' {op} ', 1)
                return {
                    "type": "Comparison",
                    "operator": op,
                    "left": self.parse_expression(parts[0].strip()),
                    "right": self.parse_expression(parts[1].strip())
                }
                
        return {
            "type": "Literal",
            "value": expr.strip()
        }
        
    def parse_effect_arguments(self, line: str, effect_name: str) -> Dict:
        args = {}
        
        if effect_name == "send":
            match = re.match(r'send\s+(.+?)\s+to\s+(.+)', line)
            if match:
                args["message"] = match.group(1)
                args["target"] = match.group(2)
                
        elif effect_name == "set":
            match = re.match(r'set\s+(.+?)\s+to\s+(.+)', line)
            if match:
                args["target"] = match.group(1)
                args["value"] = match.group(2)
                
        elif effect_name == "teleport":
            match = re.match(r'teleport\s+(.+?)\s+to\s+(.+)', line)
            if match:
                args["entity"] = match.group(1)
                args["location"] = match.group(2)
                
        elif effect_name == "give":
            match = re.match(r'give\s+(.+?)\s+to\s+(.+)', line)
            if match:
                args["item"] = match.group(1)
                args["player"] = match.group(2)
                
        elif effect_name == "wait":
            match = re.match(r'wait\s+(.+)', line)
            if match:
                args["duration"] = match.group(1)
                
        return args
        
    def validate_ast(self, ast: Dict) -> List[Dict]:
        errors = []
        
        for node in ast["body"]:
            if node["type"] in ["Event", "Command", "Function"]:
                if "body" not in node or len(node["body"]) == 0:
                    if node["type"] == "Command":
                        if "trigger" not in node or not node.get("trigger", {}).get("body"):
                            errors.append({
                                "line": node["line"] + 1,
                                "message": f"{node['type']} '{node.get('name', node.get('trigger', ''))}' has no trigger or is empty",
                                "severity": "warning"
                            })
                    else:
                        errors.append({
                            "line": node["line"] + 1,
                            "message": f"{node['type']} is empty",
                            "severity": "warning"
                        })
                        
        command_names = set()
        for node in ast["body"]:
            if node["type"] == "Command":
                if node["name"] in command_names:
                    errors.append({
                        "line": node["line"] + 1,
                        "message": f"Command /{node['name']} is already defined",
                        "severity": "error"
                    })
                command_names.add(node["name"])
                
        function_names = set()
        for node in ast["body"]:
            if node["type"] == "Function":
                if node["name"] in function_names:
                    errors.append({
                        "line": node["line"] + 1,
                        "message": f"Function {node['name']} is already defined",
                        "severity": "error"
                    })
                function_names.add(node["name"])
                
        return errors
        
    def generate_syntax_tree(self, ast: Dict) -> Dict:
        return {
            "root": ast["type"],
            "children": [self.node_to_tree(node) for node in ast["body"]]
        }
        
    def node_to_tree(self, node: Dict) -> Dict:
        tree_node = {
            "type": node["type"],
            "line": node.get("line", -1)
        }
        
        if "name" in node:
            tree_node["name"] = node["name"]
        elif "trigger" in node:
            tree_node["trigger"] = node["trigger"]
            
        if "body" in node:
            tree_node["children"] = [self.node_to_tree(child) for child in node["body"]]
            
        if node["type"] == "Command" and "trigger" in node:
            tree_node["children"] = [self.node_to_tree(node["trigger"])]
            
        return tree_node